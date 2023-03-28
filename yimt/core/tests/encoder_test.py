import tensorflow as tf

from parameterized import parameterized

from yimt.core import encoders
from yimt.core.layers import reducer


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

    def testParallelEncoder(self):
        sequence_lengths = [[3, 5, 2], [6, 6, 4]]
        inputs = [tf.zeros([3, 5, 10]), tf.zeros([3, 6, 10])]
        encoder = encoders.ParallelEncoder(
            [DenseEncoder(1, 20), DenseEncoder(2, 20)],
            outputs_reducer=reducer.ConcatReducer(axis=1),
        )
        outputs, encoded_length = encoder(
            inputs, sequence_length=sequence_lengths
        )
        outputs, encoded_length = self.evaluate([outputs, encoded_length])
        self.assertAllEqual([3, 11, 20], outputs.shape)
        self.assertAllEqual([9, 11, 6], encoded_length)

    def _encodeInParallel(
        self,
        inputs,
        sequence_length=None,
        outputs_layer_fn=None,
        combined_output_layer_fn=None,
    ):
        columns = [DenseEncoder(1, 20), DenseEncoder(1, 20)]
        encoder = encoders.ParallelEncoder(
            columns,
            outputs_reducer=reducer.ConcatReducer(),
            outputs_layer_fn=outputs_layer_fn,
            combined_output_layer_fn=combined_output_layer_fn,
        )
        outputs, _ = encoder(inputs, sequence_length=sequence_length)
        return self.evaluate(outputs)

    def testParallelEncoderSameInput(self):
        sequence_length = tf.constant([2, 5, 4], dtype=tf.int32)
        inputs = tf.zeros([3, 5, 10])
        outputs = self._encodeInParallel(inputs, sequence_length=sequence_length)
        self.assertAllEqual(outputs.shape, [3, 5, 40])

    def testParallelEncoderCombinedOutputLayer(self):
        sequence_length = tf.constant([2, 5, 4], dtype=tf.int32)
        inputs = tf.zeros([3, 5, 10])
        outputs = self._encodeInParallel(
            inputs,
            sequence_length=sequence_length,
            combined_output_layer_fn=tf.keras.layers.Dense(15),
        )
        self.assertEqual(outputs.shape[-1], 15)

    def _encodeAndProjectInParallel(self, outputs_size):
        sequence_length = tf.constant([2, 5, 4], dtype=tf.int32)
        inputs = tf.zeros([3, 5, 10])
        if isinstance(outputs_size, list):
            outputs_layer_fn = [tf.keras.layers.Dense(s) for s in outputs_size]
            combined_output_size = sum(outputs_size)
        else:
            outputs_layer_fn = tf.keras.layers.Dense(outputs_size)
            combined_output_size = outputs_size * 2
        outputs = self._encodeInParallel(
            inputs, sequence_length=sequence_length, outputs_layer_fn=outputs_layer_fn
        )
        self.assertEqual(outputs.shape[-1], combined_output_size)

    def testParallelEncoderSameOutputsLayer(self):
        self._encodeAndProjectInParallel(15)

    def testParallelEncoderOutputsLayer(self):
        self._encodeAndProjectInParallel([14, 15])

    def testParallelEncoderOutputsLayerInvalid(self):
        with self.assertRaises(ValueError):
            self._encodeAndProjectInParallel([15])

    def testParallelEncoderReuse(self):
        lengths = [
            tf.constant([2, 5, 4], dtype=tf.int32),
            tf.constant([6, 6, 3], dtype=tf.int32),
        ]
        inputs = [tf.zeros([3, 5, 10]), tf.zeros([3, 6, 10])]
        encoder = encoders.ParallelEncoder(DenseEncoder(2, 20), outputs_reducer=None)
        outputs, _ = encoder(inputs, sequence_length=lengths)
        outputs = self.evaluate(outputs)
        self.assertIsInstance(outputs, tuple)
        self.assertEqual(len(outputs), 2)

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
