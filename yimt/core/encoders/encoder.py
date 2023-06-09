"""Base class for encoders and generic multi encoders."""

import abc

import tensorflow as tf


class Encoder(tf.keras.layers.Layer):
    """Base class for encoders."""

    def build_mask(self, inputs, sequence_length=None, dtype=tf.bool):
        """Builds a boolean mask for :obj:`inputs`."""
        if sequence_length is None:
            return None
        return tf.sequence_mask(
            sequence_length, maxlen=tf.shape(inputs)[1], dtype=dtype
        )

    @abc.abstractmethod
    def call(self, inputs, sequence_length=None, training=None):
        """Encodes an input sequence.

        Args:
          inputs: The inputs to encode of shape :math:`[B, T, ...]`.
          sequence_length: The length of each input with shape :math:`[B]`.
          training: Run in training mode.

        Returns:
          A tuple ``(outputs, sequence_length)``.
        """
        raise NotImplementedError()

    def __call__(self, inputs, sequence_length=None, **kwargs):
        """Encodes an input sequence.

        Args:
          inputs: A 3D ``tf.Tensor`` or ``tf.RaggedTensor``.
          sequence_length: A 1D ``tf.Tensor`` (optional if :obj:`inputs` is a
            ``tf.RaggedTensor``).
          training: Run the encoder in training mode.

        Returns:
          If :obj:`inputs` is a ``tf.Tensor``, the encoder returns a tuple
          ``(outputs, sequence_length)``. If :obj:`inputs` is a
          ``tf.RaggedTensor``, the encoder returns a tuple ``(outputs, state)``,
          where ``outputs`` is a ``tf.RaggedTensor``.
        """
        if isinstance(inputs, tf.RaggedTensor):
            is_ragged = True
            inputs, sequence_length = inputs.to_tensor(), inputs.row_lengths()
        else:
            is_ragged = False
        outputs, sequence_length = super().__call__(
            inputs, sequence_length=sequence_length, **kwargs
        )
        if is_ragged:
            outputs = tf.RaggedTensor.from_tensor(outputs, lengths=sequence_length)
            return outputs
        else:
            return outputs, sequence_length
