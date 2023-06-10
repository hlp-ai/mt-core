import tensorflow as tf

from yimt.core import decoders


def _generate_source_context(batch_size, depth, num_sources=1, dtype=tf.float32):
    memory_sequence_length = [
        tf.random.uniform([batch_size], minval=1, maxval=20, dtype=tf.int32)
        for _ in range(num_sources)
    ]
    memory_time = [tf.reduce_max(length) for length in memory_sequence_length]
    memory = [
        tf.random.uniform([batch_size, time, depth], dtype=dtype)
        for time in memory_time
    ]
    initial_state = tuple(None for _ in range(num_sources))
    if num_sources == 1:
        memory_sequence_length = memory_sequence_length[0]
        memory = memory[0]
        initial_state = initial_state[0]
    return memory, memory_sequence_length, initial_state


class DecoderTest(tf.test.TestCase):

    def _testDecoder(
        self, decoder, initial_state_fn=None, num_sources=1, dtype=tf.float32
    ):
        batch_size = 4
        vocab_size = 10
        time_dim = 5
        depth = 6
        memory, memory_sequence_length, initial_state = _generate_source_context(
            batch_size, depth, num_sources=num_sources, dtype=dtype
        )

        decoder.initialize(vocab_size=vocab_size)
        initial_state = decoder.initial_state(
            memory=memory,
            memory_sequence_length=memory_sequence_length,
            dtype=dtype,
        )

        # Test 3D inputs.
        inputs = tf.random.uniform([batch_size, time_dim, depth], dtype=dtype)
        # Allow max(sequence_length) to be less than time_dim.
        sequence_length = tf.constant([1, 3, 4, 2], dtype=tf.int32)
        outputs, _, attention = decoder(
            inputs, sequence_length, state=initial_state, training=True
        )
        self.assertEqual(outputs.dtype, dtype)
        output_time_dim = tf.shape(outputs)[1]
        if decoder.support_alignment_history:
            self.assertIsNotNone(attention)
        else:
            self.assertIsNone(attention)
        output_time_dim_val = self.evaluate(output_time_dim)
        self.assertEqual(time_dim, output_time_dim_val)
        if decoder.support_alignment_history:
            first_memory = memory[0] if isinstance(memory, list) else memory
            attention_val, memory_time = self.evaluate(
                [attention, tf.shape(first_memory)[1]]
            )
            self.assertAllEqual(
                [batch_size, time_dim, memory_time], attention_val.shape
            )

        # Test 2D inputs.
        inputs = tf.random.uniform([batch_size, depth], dtype=dtype)
        step = tf.constant(0, dtype=tf.int32)
        outputs, _, attention = decoder(inputs, step, state=initial_state)
        self.assertEqual(outputs.dtype, dtype)
        if decoder.support_alignment_history:
            self.assertIsNotNone(attention)
        else:
            self.assertIsNone(attention)
        self.evaluate(outputs)

    def testSelfAttentionDecoder(self):
        decoder = decoders.SelfAttentionDecoder(
            num_layers=2,
            num_units=6,
            num_heads=2,
            ffn_inner_dim=12,
            vocab_size=10,
        )
        self.assertTrue(decoder.initialized)
        self._testDecoder(decoder)

    def testSelfAttentionDecoderWithoutSourceLength(self):
        batch_size = 4
        depth = 6
        decoder = decoders.SelfAttentionDecoder(
            num_layers=2,
            num_units=depth,
            num_heads=2,
            ffn_inner_dim=depth * 2,
            vocab_size=10,
        )

        memory, _, _ = _generate_source_context(batch_size, depth)
        inputs = tf.random.uniform([batch_size, depth])
        step = tf.constant(0)
        initial_state = decoder.initial_state(memory)
        decoder(inputs, step, state=initial_state)


if __name__ == "__main__":
    tf.test.main()
