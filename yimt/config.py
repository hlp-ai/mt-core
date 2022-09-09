"""Defines functions related to configuration files."""

import copy
import importlib
import os
import sys

import tensorflow as tf
import yaml

from yimt.models import catalog
from yimt.utils.misc import merge_dict

MODEL_DESCRIPTION_FILENAME = "model_description.py"


def load_model_module(path):
    """Loads a model configuration file.

    Args:
      path: The relative path to the configuration file.

    Returns:
      A Python module.

    Raises:
      ValueError: if :obj:`path` is invalid.
      ImportError: if the module in :obj:`path` does not define a model.
    """
    if not os.path.exists(path):
        raise ValueError("Model configuration not found in %s" % path)
    dirname, filename = os.path.split(path)
    module_name, _ = os.path.splitext(filename)
    sys.path.insert(0, os.path.abspath(dirname))
    module = importlib.import_module(module_name)
    sys.path.pop(0)

    if not hasattr(module, "model"):
        raise ImportError("No model defined in {}".format(path))

    return module


def load_model_from_file(path, as_builder=False):
    """Loads a model from a configuration file.

    Args:
      path: The relative path to the configuration file.
      as_builder: If ``True``, return a callable building the model on call.

    Returns:
      A :class:`yimt.models.Model` instance or a callable returning such
      instance.
    """
    module = load_model_module(path)
    model = module.model
    if not as_builder:
        model = model()
    del sys.path_importer_cache[os.path.dirname(module.__file__)]
    del sys.modules[module.__name__]
    return model


def load_model_from_catalog(name, as_builder=False):
    """Loads a model from the catalog.

    Args:
      name: The model name.
      as_builder: If ``True``, return a callable building the model on call.

    Returns:
      A :class:`yimt.models.Model` instance or a callable returning such
      instance.

    Raises:
      ValueError: if the model :obj:`name` does not exist in the model catalog.
    """
    return catalog.get_model_from_catalog(name, as_builder=as_builder)


def load_model(
    model_dir, model_file=None, model_name=None, serialize_model=True, as_builder=False
):
    """Loads the model from the catalog or a definition file.

    Args:
      model_dir: The model directory.
      model_file: An optional model configuration.
        Mutually exclusive with :obj:`model_name`.
      model_name: An optional model name from the catalog.
        Mutually exclusive with :obj:`model_file`.
      serialize_model: Serialize the model definition in the model directory to
        make it optional for future runs.
      as_builder: If ``True``, return a callable building the model on call.

    Returns:
      A :class:`yimt.models.Model` instance or a callable returning such
      instance.

    Raises:
      ValueError: if both :obj:`model_file` and :obj:`model_name` are set.
    """
    if model_file and model_name:
        raise ValueError("only one of model_file and model_name should be set")
    model_description_path = os.path.join(model_dir, MODEL_DESCRIPTION_FILENAME)

    if model_file:
        model = load_model_from_file(model_file, as_builder=as_builder)
        if serialize_model:
            tf.io.gfile.copy(model_file, model_description_path, overwrite=True)
    elif model_name:
        model = load_model_from_catalog(model_name, as_builder=as_builder)
        if serialize_model:
            with tf.io.gfile.GFile(
                model_description_path, mode="w"
            ) as model_description_file:
                model_description_file.write(
                    "from yimt import models\n"
                    'model = lambda: models.get_model_from_catalog("%s")\n' % model_name
                )
    elif tf.io.gfile.exists(model_description_path):
        tf.get_logger().info(
            "Loading model description from %s", model_description_path
        )
        model = load_model_from_file(model_description_path, as_builder=as_builder)
    else:
        raise RuntimeError(
            "A model configuration is required: you probably need to "
            "set --model or --model_type on the command line."
        )

    return model


def load_config(config_paths, config=None):
    """Loads YAML configuration files.

    Args:
      config_paths: A list of configuration files that will be merged to a single
        configuration. The rightmost configuration takes priority.
      config: A (possibly non empty) config dictionary to fill.

    Returns:
      The configuration as Python dictionary.
    """
    if config is None:
        config = {}

    for config_path in config_paths:
        with tf.io.gfile.GFile(config_path) as config_file:
            subconfig = yaml.safe_load(config_file.read())
            # Add or update section in main configuration.
            merge_config(config, subconfig)

    return config


def merge_config(a, b):
    """Merges the configuration :obj:`b` into the configuration :obj:`a`."""
    override_keys = {"optimizer_params", "decay_params"}
    return merge_dict(a, b, override_keys=override_keys)


def _map_config_values(config, fn):
    """Applies the function ``fn`` on each value of the configuration."""
    if isinstance(config, dict):
        return {key: _map_config_values(value, fn) for key, value in config.items()}
    elif isinstance(config, list):
        return [_map_config_values(elem, fn) for elem in config]
    else:
        return fn(config)


def try_prefix_paths(prefix, config):
    """Recursively tries to prefix paths in the configuration.

    The path is unchanged if the prefixed path does not exist.

    Args:
      prefix: The prefix to apply.
      config: The configuration.

    Returns:
      The updated configuration.
    """

    def _fn(path):
        if isinstance(path, str):
            new_path = os.path.join(prefix, path)
            if tf.io.gfile.exists(new_path):
                return new_path
        return path

    return _map_config_values(config, _fn)
