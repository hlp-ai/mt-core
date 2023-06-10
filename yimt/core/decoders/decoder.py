"""Base class and functions for dynamic decoders."""

import abc

import tensorflow as tf

from yimt.core import constants
from yimt.core.inputters import text_inputter
from yimt.core.layers import common
from yimt.core.utils import decoding, misc


class Decoder(tf.keras.layers.Layer):
    """Base class for decoders."""

    def __init__(
        self,
        vocab_size=None,
        output_layer=None,
        output_layer_bias=True,
        **kwargs
    ):
        """Initializes the decoder parameters.

        If you don't set one of :obj:`vocab_size` or :obj:`output_layer` here,
        you should later call the method :meth:`yimt.decoders.Decoder.initialize`
        to initialize this decoder instance.

        Args:
          vocab_size: The output vocabulary size (optional if :obj:`output_layer` is set).
          output_layer: The output projection layer (optional).
          output_layer_bias: Add bias after the output projection layer.
          **kwargs: Additional layer arguments.

        Raises:
          ValueError: if the number of source contexts :obj:`num_sources` is not
            supported by this decoder.
        """
        super().__init__(**kwargs)
        self.num_sources = 1
        self.output_layer = None
        self.output_layer_bias = output_layer_bias
        self.memory = None
        self.memory_sequence_length = None
        if vocab_size is not None or output_layer is not None:
            self.initialize(vocab_size=vocab_size, output_layer=output_layer)

    @property
    def support_alignment_history(self):
        """Returns ``True`` if this decoder can return the attention as alignment
        history."""
        return True

    @property
    def initialized(self):
        """Returns ``True`` if this decoder is initialized."""
        return self.output_layer is not None

    def initialize(self, vocab_size=None, output_layer=None):
        """Initializes the decoder configuration.

        Args:
          vocab_size: The target vocabulary size.
          output_layer: The output layer to use.

        Raises:
          ValueError: if both :obj:`vocab_size` and :obj:`output_layer` are not set.
        """
        if self.initialized:
            return
        if output_layer is not None:
            self.output_layer = output_layer
        else:
            if vocab_size is None:
                raise ValueError("One of vocab_size and output_layer must be set")
            self.output_layer = common.Dense(
                vocab_size, use_bias=self.output_layer_bias
            )

    def reuse_embeddings(self, embeddings):
        """Reuses embeddings in the decoder output layer.

        Args:
          embeddings: The embeddings matrix to reuse.

        Raises:
          RuntimeError: if the decoder was not initialized.
        """
        self._assert_is_initialized()
        self.output_layer.set_kernel(embeddings, transpose=True)

    def initial_state(
        self,
        memory=None,
        memory_sequence_length=None,
        batch_size=None,
        dtype=None,
    ):
        """Returns the initial decoder state.

        Args:
          memory: Memory values to query.
          memory_sequence_length: Memory values length.
          batch_size: The batch size to use.
          dtype: The dtype of the state.

        Returns:
          A nested structure of tensors representing the decoder state.

        Raises:
          RuntimeError: if the decoder was not initialized.
          ValueError: if one of :obj:`batch_size` or :obj:`dtype` is not set and
            neither :obj:`initial_state` nor :obj:`memory` are not passed.
          ValueError: if the number of source contexts (:obj:`memory`) does not
            match the number defined at the decoder initialization.
        """
        self._assert_is_initialized()
        self._assert_memory_is_compatible(memory, memory_sequence_length)
        self.memory = memory
        self.memory_sequence_length = memory_sequence_length
        if batch_size is None or dtype is None:
            sentinel = tf.nest.flatten(memory)[0]
            if sentinel is None:
                raise ValueError(
                    "If batch_size or dtype are not set, then either "
                    "memory or initial_state should be set"
                )
            if batch_size is None:
                batch_size = tf.shape(sentinel)[0]
            if dtype is None:
                dtype = sentinel.dtype
        return self._get_initial_state(batch_size, dtype)

    def call(
        self,
        inputs,
        length_or_step=None,
        state=None,
        input_fn=None,
        training=None,
    ):
        """Runs the decoder layer on either a complete sequence (e.g. for training
        or scoring), or a single timestep (e.g. for iterative decoding).

        Args:
          inputs: The inputs to decode, can be a 3D (training) or 2D (iterative
            decoding) tensor.
          length_or_step: For 3D :obj:`inputs`, the length of each sequence. For 2D
            :obj:`inputs`, the current decoding timestep.
          state: The decoder state.
          input_fn: A callable taking sampled ids and returning the decoding inputs.
          training: Run in training mode.

        Returns:
          A tuple with the logits, the decoder state, and an attention vector.

        Raises:
          RuntimeError: if the decoder was not initialized.
          ValueError: if the :obj:`inputs` rank is different than 2 or 3.
          ValueError: if :obj:`length_or_step` is invalid.
        """
        self._assert_is_initialized()
        rank = inputs.shape.ndims
        if rank == 2:
            if length_or_step.shape.ndims != 0:
                raise ValueError(
                    "length_or_step should be a scalar with the current timestep"
                )
            outputs, state, attention = self.step(
                inputs,
                length_or_step,
                state=state,
                memory=self.memory,
                memory_sequence_length=self.memory_sequence_length,
                training=training,
            )
            logits = self.output_layer(outputs)
        elif rank == 3:
            if length_or_step.shape.ndims != 1:
                raise ValueError(
                    "length_or_step should contain the length of each sequence"
                )
            logits, state, attention = self.forward(
                inputs,
                sequence_length=length_or_step,
                initial_state=state,
                memory=self.memory,
                memory_sequence_length=self.memory_sequence_length,
                input_fn=input_fn,
                training=training,
            )
        else:
            raise ValueError("Unsupported input rank %d" % rank)
        return logits, state, attention

    def forward(
        self,
        inputs,
        sequence_length=None,
        initial_state=None,
        memory=None,
        memory_sequence_length=None,
        input_fn=None,
        training=None,
    ):
        """Runs the decoder on full sequences.

        Args:
          inputs: The 3D decoder input.
          sequence_length: The length of each input sequence.
          initial_state: The initial decoder state.
          memory: Memory values to query.
          memory_sequence_length: Memory values length.
          input_fn: A callable taking sampled ids and returning the decoding inputs.
          training: Run in training mode.

        Returns:
          A tuple with the logits, the decoder state, and the attention
          vector.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def step(
        self,
        inputs,
        timestep,
        state=None,
        memory=None,
        memory_sequence_length=None,
        training=None,
    ):
        """Runs one decoding step.

        Args:
          inputs: The 2D decoder input.
          timestep: The current decoding step.
          state: The decoder state.
          memory: Memory values to query.
          memory_sequence_length: Memory values length.
          training: Run in training mode.

        Returns:
          A tuple with the decoder outputs, the decoder state, and the attention
          vector.
        """
        raise NotImplementedError()

    def dynamic_decode(
        self,
        embeddings,
        start_ids,
        end_id=constants.END_OF_SENTENCE_ID,
        initial_state=None,
        decoding_strategy=None,
        sampler=None,
        maximum_iterations=None,
        minimum_iterations=0,
        tflite_output_size=None,
    ):
        """Decodes dynamically from :obj:`start_ids`.

        Args:
          embeddings: Target embeddings or :class:`yimt.inputters.WordEmbedder`
            to apply on decoded ids.
          start_ids: Initial input IDs of shape :math:`[B]`.
          end_id: ID of the end of sequence token.
          initial_state: Initial decoder state.
          decoding_strategy: A :class:`yimt.utils.DecodingStrategy`
            instance that define the decoding logic. Defaults to a greedy search.
          sampler: A :class:`yimt.utils.Sampler` instance that samples
            predictions from the model output. Defaults to an argmax sampling.
          maximum_iterations: The maximum number of iterations to decode for.
          minimum_iterations: The minimum number of iterations to decode for.
          tflite_output_size: If not None will run TFLite safe, is the size of 1D output tensor.

        Returns:
          A :class:`yimt.utils.DecodingResult` instance.

        See Also:
          :func:`yimt.utils.dynamic_decode`
        """
        if isinstance(embeddings, text_inputter.WordEmbedder):
            input_fn = lambda ids: embeddings({"ids": ids})
        else:
            input_fn = lambda ids: tf.nn.embedding_lookup(embeddings, ids)

        # TODO: find a better way to pass the state reorder flags.
        if hasattr(decoding_strategy, "_set_state_reorder_flags"):
            state_reorder_flags = self._get_state_reorder_flags()
            decoding_strategy._set_state_reorder_flags(state_reorder_flags)

        return decoding.dynamic_decode(
            lambda ids, step, state: self(input_fn(ids), step, state),
            start_ids,
            end_id=end_id,
            initial_state=initial_state,
            decoding_strategy=decoding_strategy,
            sampler=sampler,
            maximum_iterations=maximum_iterations,
            minimum_iterations=minimum_iterations,
            attention_history=self.support_alignment_history,
            attention_size=tf.shape(self.memory)[1]
            if self.support_alignment_history
            else None,
            tflite_output_size=tflite_output_size,
        )

    @abc.abstractmethod
    def _get_initial_state(self, batch_size, dtype):
        """Returns the decoder initial state.

        Args:
          batch_size: The batch size of the returned state.
          dtype; The data type of the state.

        Returns:
          The decoder state as a nested structure of tensors.
        """
        raise NotImplementedError()

    def _get_state_reorder_flags(self):
        """Returns a structure that marks states that should be reordered during beam search.
        By default all states are reordered.

        Returns:
          The same structure as the decoder state with tensors replaced by booleans.
        """
        return None

    def _assert_is_initialized(self):
        """Raises an expection if the decoder was not initialized."""
        if not self.initialized:
            raise RuntimeError("The decoder was not initialized")

    def _assert_memory_is_compatible(self, memory, memory_sequence_length):
        """Raises an expection if the memory layout is not compatible with this decoder."""

        def _num_elements(obj):
            if obj is None:
                return 0
            elif isinstance(obj, (list, tuple)):
                return len(obj)
            else:
                return 1

        num_memory = _num_elements(memory)
        num_length = _num_elements(memory_sequence_length)
        if num_memory != num_length and memory_sequence_length is not None:
            raise ValueError(
                "got %d memory values but %d length vectors" % (num_memory, num_length)
            )
        if num_memory != self.num_sources:
            raise ValueError(
                "expected %d source contexts, but got %d"
                % (self.num_sources, num_memory)
            )
