"""Define learning rate decay functions."""

import inspect
import tensorflow as tf

from yimt.core.utils import misc

_LR_SCHEDULES_REGISTRY = misc.ClassRegistry(
    base_class=tf.keras.optimizers.schedules.LearningRateSchedule
)

register_learning_rate_schedule = _LR_SCHEDULES_REGISTRY.register


def get_lr_schedule_class(name):
    """Returns the learning rate schedule class.

    Args:
      name: The schedule class name.

    Returns:
      A class extending ``tf.keras.optimizers.schedules.LearningRateSchedule``.

    Raises:
      ValueError: if :obj:`name` can not be resolved to an existing schedule.
    """
    schedule_class = None
    if schedule_class is None:
        schedule_class = getattr(tf.keras.optimizers.schedules, name, None)
    if schedule_class is None:
        schedule_class = _LR_SCHEDULES_REGISTRY.get(name)
    if schedule_class is None:
        raise ValueError("Unknown learning rate schedule: %s" % name)
    return schedule_class


def make_learning_rate_schedule(
    initial_learning_rate,
    schedule_type,
    schedule_params=None,
    schedule_step_duration=1,
    start_step=0,
    minimum_learning_rate=0,
):
    """Creates the learning rate schedule.

    Args:
      initial_learning_rate: The initial learning rate value. This can be
        ``None`` if the learning rate is fully defined by the schedule.
      schedule_type: The type of learning rate schedule. A class name from
        ``tf.keras.optimizers.schedules`` or :mod:`yimt.schedules` as a string.
      schedule_params: Additional parameters passed to the schedule constructor.
      schedule_step_duration: The number of training steps that make 1 schedule step.
      start_step: Start the schedule after this many steps.
      minimum_learning_rate: Do not decay past this learning rate value.

    Returns:
      A ``tf.keras.optimizers.schedules.LearningRateSchedule`` instance.

    Raises:
      ValueError: if :obj:`schedule_type` can not be resolved to an existing
        schedule.

    See Also:
      :class:`yimt.schedules.ScheduleWrapper`
    """
    if schedule_params is None:
        schedule_params = {}
    schedule_class = get_lr_schedule_class(schedule_type)
    first_arg = inspect.getfullargspec(schedule_class)[0][1]
    if first_arg not in schedule_params:
        schedule_params[first_arg] = initial_learning_rate
    schedule = schedule_class(**schedule_params)
    schedule = ScheduleWrapper(
        schedule,
        step_start=start_step,
        step_duration=schedule_step_duration,
        minimum_learning_rate=minimum_learning_rate,
    )
    return schedule


class ScheduleWrapper(tf.keras.optimizers.schedules.LearningRateSchedule):
    """Wrapper to augment a learning rate scheduler behavior."""

    def __init__(
        self, schedule, step_start=0, step_duration=1, minimum_learning_rate=0
    ):
        """Initializes the decay function.

        Args:
          schedule: A ``tf.keras.optimizers.schedules.LearningRateSchedule``.
          step_duration: The number of training steps that make 1 decay step.
          start_step: Start decay after this many steps.
          minimum_learning_rate: Do not decay past this learning rate value.

        See Also:
          :class:`yimt.schedules.make_learning_rate_schedule`
        """
        self.schedule = schedule
        self.step_start = step_start
        self.step_duration = step_duration
        self.minimum_learning_rate = minimum_learning_rate

    def __call__(self, step):
        # Map the training step to a decay step.
        step = tf.maximum(step - self.step_start, 0)
        step //= self.step_duration
        learning_rate = self.schedule(step)
        return tf.maximum(learning_rate, self.minimum_learning_rate)


@register_learning_rate_schedule
class NoamDecay(tf.keras.optimizers.schedules.LearningRateSchedule):
    """Defines the decay function described in https://arxiv.org/abs/1706.03762."""

    def __init__(self, scale, model_dim, warmup_steps):
        """Initializes the decay function.

        Args:
          scale: The scale constant.
          model_dim: The model dimension.
          warmup_steps: The number of warmup steps.
        """
        self.scale = tf.cast(scale, tf.float32)
        self.model_dim = tf.cast(model_dim, tf.float32)
        self.warmup_steps = tf.cast(warmup_steps, tf.float32)

    def __call__(self, step):
        step = tf.cast(step + 1, tf.float32)
        return (
            self.scale
            * tf.pow(self.model_dim, -0.5)
            * tf.minimum(tf.pow(step, -0.5), step * tf.pow(self.warmup_steps, -1.5))
        )
