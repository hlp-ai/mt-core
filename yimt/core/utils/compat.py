"""Functions for compatibility with different TensorFlow versions."""

import tensorflow as tf


def tf_supports(symbol):
    """Returns ``True`` if TensorFlow defines :obj:`symbol`."""
    return _string_to_tf_symbol(symbol) is not None


def _string_to_tf_symbol(symbol):
    modules = symbol.split(".")
    namespace = tf
    for module in modules:
        namespace = getattr(namespace, module, None)
        if namespace is None:
            return None
    return namespace
