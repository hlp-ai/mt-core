"""Checkpoint utilities."""

import tempfile

import tensorflow as tf

from yimt.core.utils import misc


class Checkpoint(object):
    """Wrapper around TensorFlow checkpoints utilities."""

    def __init__(self, model, optimizer=None, model_dir=None, keep_checkpoint_max=8):
        """Initializes the wrapper.

        Args:
          model: A :class:`yimt.models.Model` to save.
          optimizer: The optimizer instance.
          model_dir: The directory where checkpoints will be saved. If not set, a
            temporary directory will be used.
          keep_checkpoint_max: The maximum number of checkpoints to keep.
        """
        if model_dir is None:
            model_dir = tempfile.mkdtemp()
        trackables = {}
        trackables["model"] = model
        if optimizer is not None:
            trackables["optimizer"] = optimizer
        self._model = model
        self._optimizer = optimizer
        self._model_dir = model_dir
        self._checkpoint = tf.train.Checkpoint(**trackables)
        self._checkpoint_manager = tf.train.CheckpointManager(
            self._checkpoint, model_dir, keep_checkpoint_max
        )

    @classmethod
    def from_config(cls, config, model, optimizer=None):
        """Creates a checkpoint wrapper from the configuration.

        Args:
          config: The user configuration.
          model: A :class:`yimt.models.Model` to save.
          optimizer: The optimizer instance.

        Returns:
          A :class:`yimt.utils.Checkpoint` instance.
        """
        train_config = config.get("train")
        if train_config is None:
            train_config = {}
        keep_checkpoint_max = max(
            train_config.get("keep_checkpoint_max", 8),
            train_config.get("average_last_checkpoints", 0),
        )
        return cls(
            model,
            optimizer=optimizer,
            model_dir=config.get("model_dir"),
            keep_checkpoint_max=keep_checkpoint_max,
        )

    @property
    def model(self):
        """The managed model."""
        return self._model

    @property
    def optimizer(self):
        """The managed optimizer."""
        return self._optimizer

    @property
    def model_dir(self):
        """The model directory."""
        return self._model_dir

    @property
    def last_saved_step(self):
        """The last training step that was saved."""
        latest_checkpoint = self._checkpoint_manager.latest_checkpoint
        if latest_checkpoint is None:
            return None
        return get_step_from_checkpoint_prefix(latest_checkpoint)

    def save(self, step=None):
        """Saves a checkpoint.

        Args:
          step: The step to save for. If ``None``, get the value from ``optimizer.iterations``.

        Returns:
          The path to the saved checkpoint.
        """
        if step is None:
            step = self._optimizer.iterations
        path = self._checkpoint_manager.save(checkpoint_number=step)
        tf.get_logger().info("Saved checkpoint %s", path)
        return path

    def restore(self, checkpoint_path=None, weights_only=False):
        """Restores a checkpoint.

        Args:
          checkpoint_path: Path a checkpoint to restore. If not set, the latest
            checkpoint from :obj:`model_dir` will be restored.
          weights_only: Only restore model weights.

        Returns:
          Path to the restored checkpoint.
        """
        if weights_only:
            checkpoint = tf.train.Checkpoint(model=self._model)
        else:
            checkpoint = self._checkpoint
        if checkpoint_path is not None:
            if tf.io.gfile.isdir(checkpoint_path):
                checkpoint_path = tf.train.latest_checkpoint(checkpoint_path)
        elif self._checkpoint_manager.latest_checkpoint is not None:
            checkpoint_path = self._checkpoint_manager.latest_checkpoint
        if checkpoint_path is None:
            tf.get_logger().warning("No checkpoint to restore in %s", self._model_dir)
            return None

        load_status = checkpoint.restore(checkpoint_path)
        load_status.expect_partial()
        tf.get_logger().info("Restored checkpoint %s", checkpoint_path)
        return checkpoint_path


def get_step_from_checkpoint_prefix(prefix):
    """Extracts the training step from the checkpoint file prefix."""
    return int(prefix.split("-")[-1])


def average_checkpoints(
    model_dir, output_dir, trackables, max_count=8, model_key="model"
):
    """Averages object-based checkpoints.

    Args:
      model_dir: The directory containing checkpoints.
      output_dir: The directory that will contain the averaged checkpoint.
      trackables: A dictionary containing the trackable objects included in the
        checkpoint.
      max_count: The maximum number of checkpoints to average.
      model_key: The key in :obj:`trackables` that references the model.

    Returns:
      The path to the directory containing the averaged checkpoint.

    Raises:
      ValueError: if :obj:`output_dir` is the same as :obj:`model_dir`.
      ValueError: if a model is not found in :obj:`trackables` or is not already
        built.
      ValueError: if no checkpoints are found in :obj:`model_dir`.

    See Also:
      :func:`yimt.utils.average_checkpoints_into_layer`
    """
    if model_dir == output_dir:
        raise ValueError("Model and output directory must be different")
    model = trackables.get(model_key)
    if model is None:
        raise ValueError("%s not found in trackables %s" % (model_key, trackables))

    checkpoint_state = tf.train.get_checkpoint_state(model_dir)
    if checkpoint_state is None:
        raise ValueError("No checkpoints found in %s" % model_dir)
    checkpoints_path = checkpoint_state.all_model_checkpoint_paths
    if len(checkpoints_path) > max_count:
        checkpoints_path = checkpoints_path[-max_count:]

    average_checkpoints_into_layer(checkpoints_path, model, model_key)

    last_step = get_step_from_checkpoint_prefix(checkpoints_path[-1])
    checkpoint = tf.train.Checkpoint(**trackables)
    new_checkpoint_manager = tf.train.CheckpointManager(
        checkpoint, output_dir, max_to_keep=None
    )
    path = new_checkpoint_manager.save(checkpoint_number=last_step)
    tf.get_logger().info("Saved averaged checkpoint to %s", path)
    return output_dir


def average_checkpoints_into_layer(checkpoints, layer, layer_prefix):
    """Updates the layer weights with their average value in the checkpoints.

    Args:
      checkpoints: A non empty list of checkpoint paths.
      layer: A ``tf.keras.layers.Layer`` instance.
      layer_prefix: The name/scope that prefixes the layer variables names in the
        checkpoints.

    Raises:
      ValueError: if :obj:`checkpoints` is empty.
      ValueError: if :obj:`layer` is not already built.

    See Also:
      :func:`yimt.utils.average_checkpoints`
    """
    if not checkpoints:
        raise ValueError("There should be at least one checkpoint")
    if not layer.built:
        raise ValueError("The layer should be built before calling this function")

    # Reset the layer variables to 0.
    for variable in layer.variables:
        variable.assign(tf.zeros_like(variable))

    # Get a map from variable names in the checkpoint to variables in the layer.
    names_to_variables = misc.get_variables_name_mapping(layer, root_key=layer_prefix)

    num_checkpoints = len(checkpoints)
    tf.get_logger().info("Averaging %d checkpoints...", num_checkpoints)
    for checkpoint_path in checkpoints:
        tf.get_logger().info("Reading checkpoint %s...", checkpoint_path)
        reader = tf.train.load_checkpoint(checkpoint_path)
        for path in reader.get_variable_to_shape_map().keys():
            if not path.startswith(layer_prefix) or ".OPTIMIZER_SLOT" in path:
                continue
            variable = names_to_variables[path]
            value = reader.get_tensor(path)
            variable.assign_add(value / num_checkpoints)

