import tensorflow as tf

from parameterized import parameterized

from yimt.core import encoders


class DenseEncoder(encoders.Encoder):
    def __init__(self, num_layers, num_units):
        super().__init__()
        self.layers = [tf.keras.layers.Dense(num_units) for _ in range(num_layers)]

    def call(self, inputs, sequence_length=None, training=None):
        for layer in self.layers:
            inputs = layer(inputs)
        return inputs, sequence_length


class EncoderTest(tf.test.TestCase):
    def testRaggedInput(self):
        ragged_tensor = tf.ragged.constant([[1, 2, 3], [4], [5, 6]])
        test_case = self

        class _Encoder(encoders.Encoder):
            def call(self, inputs, sequence_length=None, training=None):
                test_case.assertAllEqual(inputs, [[1, 2, 3], [4, 0, 0], [5, 6, 0]])
                test_case.assertAllEqual(sequence_length, [3, 1, 2])
                test_case.assertTrue(training)
                return inputs + 1, sequence_length

        ragged_output = _Encoder()(ragged_tensor, training=True)
        self.assertIsInstance(ragged_output, tf.RaggedTensor)
        self.assertAllEqual(ragged_output, [[2, 3, 4], [5], [6, 7]])


    @parameterized.expand([[tf.float32], [tf.float16]])
    def testSelfAttentionEncoder(self, dtype):
        tf.keras.backend.set_floatx(dtype.name)
        encoder = encoders.SelfAttentionEncoder(
            3, num_units=20, num_heads=4, ffn_inner_dim=40
        )
        inputs = tf.random.uniform([4, 5, 10], dtype=dtype)
        lengths = tf.constant([4, 3, 5, 2])
        outputs, _ = encoder(inputs, sequence_length=lengths, training=True)
        self.assertListEqual(outputs.shape.as_list(), [4, 5, 20])
        self.assertEqual(outputs.dtype, dtype)
        tf.keras.backend.set_floatx("float32")


if __name__ == "__main__":
    tf.test.main()
