import collections
import copy
import functools
import sys

import tensorflow as tf
from tensorflow.python.training.tracking import graph_view


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


def item_or_tuple(x):
    """Returns :obj:`x` as a tuple or its single element."""
    x = tuple(x)
    if len(x) == 1:
        return x[0]
    else:
        return x


def count_lines(filename, buffer_size=65536):
    """Returns the number of lines of the file :obj:`filename`."""
    with tf.io.gfile.GFile(filename, mode="rb") as f:
        num_lines = 0
        while True:
            data = f.read(buffer_size)
            if not data:
                return num_lines
            num_lines += data.count(b"\n")


class RelativeConfig(collections.abc.Mapping):
    """Helper class to lookup keys relative to a prefix."""

    def __init__(self, config, prefix=None, config_name=None):
        """Initializes the relative configuration.

        Args:
          config: The configuration.
          prefix: The prefix. Keys will be looked up relative to this prefix.
          config_name: The name of the configuration, mostly used to make error
            messages more explicit.
        """
        self._config = config
        self._prefix = prefix or ""
        self._config_name = config_name

    def __getitem__(self, relative_key):
        absolute_key = "%s%s" % (self._prefix, relative_key)
        value = self._config.get(absolute_key)
        if value is not None:
            return value
        value = self._config.get(relative_key)
        if value is not None:
            return value
        raise KeyError(
            "Missing field '%s' in the %sconfiguration"
            % (absolute_key, self._config_name + " " if self._config_name else "")
        )

    def __len__(self):
        return len(self._config)

    def __iter__(self):
        return iter(self._config)


def is_gzip_file(filename):
    """Returns ``True`` if :obj:`filename` is a GZIP file."""
    return filename.endswith(".gz")


def extract_prefixed_keys(dictionary, prefix):
    """Returns a dictionary with all keys from :obj:`dictionary` that are prefixed
    with :obj:`prefix`.
    """
    sub_dict = {}
    for key, value in dictionary.items():
        if key.startswith(prefix):
            original_key = key[len(prefix) :]
            sub_dict[original_key] = value
    return sub_dict


def extract_suffixed_keys(dictionary, suffix):
    """Returns a dictionary with all keys from :obj:`dictionary` that are suffixed
    with :obj:`suffix`.
    """
    sub_dict = {}
    for key, value in dictionary.items():
        if key.endswith(suffix):
            original_key = key[: -len(suffix)]
            sub_dict[original_key] = value
    return sub_dict


def get_variables_name_mapping(root, root_key=None):
    """Returns mapping between variables and their name in the object-based
    representation.

    Args:
      root: The root layer.
      root_key: Key that was used to save :obj:`root`, if any.

    Returns:
      A dict mapping names to variables.
    """
    # TODO: find a way to implement this function using public APIs.
    names_to_variables = {}
    _, path_to_root = graph_view.ObjectGraphView(root)._breadth_first_traversal()
    for path in path_to_root.values():
        if not path:
            continue
        variable = path[-1].ref
        if not isinstance(variable, tf.Variable):
            continue
        name = "%s/%s" % (
            "/".join(field.name for field in path),
            ".ATTRIBUTES/VARIABLE_VALUE",
        )
        if root_key is not None:
            name = "%s/%s" % (root_key, name)
        names_to_variables[name] = variable
    return names_to_variables


def clone_layer(layer):
    """Clones a layer."""
    return copy.deepcopy(layer)
