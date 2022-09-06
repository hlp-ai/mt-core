import functools
import sys

import tensorflow as tf


class ClassRegistry(object):
    """Helper class to create a registry of classes."""

    def __init__(self, base_class=None):
        """Initializes the class registry.

        Args:
          base_class: Ensure that classes added to this registry are a subclass of
            :obj:`base_class`.
        """
        self._base_class = base_class
        self._registry = {}

    @property
    def class_names(self):
        """Class names registered in this registry."""
        return set(self._registry.keys())

    def register(self, cls=None, name=None, alias=None):
        """Registers a class.

        Args:
          cls: The class to register. If not set, this method returns a decorator for
            registration.
          name: The class name. Defaults to ``cls.__name__``.
          alias: An optional alias or list of alias for this class.

        Returns:
          :obj:`cls` if set, else a class decorator.

        Raises:
          TypeError: if :obj:`cls` does not extend the expected base class.
          ValueError: if the class name is already registered.
        """
        if cls is None:
            return functools.partial(self.register, name=name, alias=alias)
        if self._base_class is not None and not issubclass(cls, self._base_class):
            raise TypeError(
                "Class %s does not extend %s"
                % (cls.__name__, self._base_class.__name__)
            )
        if name is None:
            name = cls.__name__
        self._register(cls, name)
        if alias is not None:
            if not isinstance(alias, (list, tuple)):
                alias = (alias,)
            for alias_name in alias:
                self._register(cls, alias_name)
        return cls

    def _register(self, cls, name):
        if name in self._registry:
            raise ValueError("Class name %s is already registered" % name)
        self._registry[name] = cls

    def get(self, name):
        """Returns the class with name :obj:`name` or ``None`` if it does not exist
        in the registry.
        """
        return self._registry.get(name)


def shape_list(x):
    """Return list of dims, statically where possible."""
    x = tf.convert_to_tensor(x)
    if tf.executing_eagerly():
        return x.shape.as_list()

    # If unknown rank, return dynamic shape
    if x.shape.dims is None:
        return tf.shape(x)

    static = x.shape.as_list()
    shape = tf.shape(x)

    ret = []
    for i, _ in enumerate(static):
        dim = static[i]
        if dim is None:
            dim = shape[i]
        ret.append(dim)
    return ret


def print_as_bytes(text, stream=None):
    """Prints a string as bytes to not rely on :obj:`stream` default encoding.

    Args:
      text: The text to print.
      stream: The stream to print to (``sys.stdout`` if not set).
    """
    if stream is None:
        stream = sys.stdout
    write_buffer = stream.buffer if hasattr(stream, "buffer") else stream
    write_buffer.write(tf.compat.as_bytes(text))
    write_buffer.write(b"\n")
    stream.flush()
