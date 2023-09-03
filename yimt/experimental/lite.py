import os

import numpy as np

import tensorflow as tf

from yimt.core import data, layers
from yimt.core.models import catalog
from yimt.core.tests import test_util
from yimt.core.utils import exporters


def _create_vocab(temp_dir):
    vocab_path = os.path.join(temp_dir, "vocab.txt")
    vocab = test_util.make_vocab(vocab_path, ["a", "b", "c"])
    return vocab, vocab_path


def _make_model(model_template, vocab, params=None):
    model = model_template()
    model.initialize(
        dict(source_vocabulary=vocab, target_vocabulary=vocab), params=params
    )
    return model


def _convert_tflite(model_template, export_dir, params=None, quantization=None):
    vocab, _ = _create_vocab(export_dir)
    model = _make_model(model_template, vocab, params)
    exporter = exporters.TFLiteExporter(quantization=quantization)
    exporter.export(model, export_dir)


def tryTFLiteInterpreter(model, params=None, quantization=None):
    if params is None:
        params = {}
    export_dir = "d:/tmp"

    print("Converting TFLite model...")
    _convert_tflite(model, export_dir, params, quantization)

    print("Loading model...")
    export_file = os.path.join(export_dir, "yimt.tflite")
    interpreter = tf.lite.Interpreter(model_path=export_file)

    print("Preparing data...")
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    input_ids = [2, 3, 4, 5, 6]
    interpreter.resize_tensor_input(0, [len(input_ids)], strict=True)
    interpreter.allocate_tensors()
    np_in_data = np.array(input_ids, dtype=np.int32)
    interpreter.set_tensor(input_details[0]["index"], np_in_data)

    print("Invoking...")
    interpreter.invoke()
    output_ids = interpreter.get_tensor(output_details[0]["index"])
    return output_ids


# class TFLiteTest(tf.test.TestCase):
#     @parameterized.expand(
#         [
#             [catalog.TransformerBase, {"beam_width": 3}],
#             [catalog.TransformerRelative, {"replace_unknown_target": True}],
#             [
#                 catalog.TransformerBaseSharedEmbeddings,
#                 {"replace_unknown_target": True, "beam_width": 3},
#             ],
#         ]
#     )
#     def testTFLiteOutput(self, model, params):
#         vocab, vocab_path = _create_vocab(self.get_temp_dir())
#         created_model = _make_model(model, vocab, params)
#         dataset = _create_dataset(created_model, self.get_temp_dir())
#         pred, tflite_pred = _get_predictions(created_model, dataset, vocab_path)
#         self.assertAllEqual(pred, tflite_pred)
#
#     @parameterized.expand(
#         [
#             [catalog.TransformerBase, {"beam_width": 3}],
#             [catalog.TransformerRelative, {"replace_unknown_target": True}],
#             [
#                 catalog.TransformerBaseSharedEmbeddings,
#                 {"replace_unknown_target": True, "beam_width": 3},
#             ],
#             [
#                 lambda: catalog.Transformer(
#                     position_encoder_class=layers.PositionEmbedder
#                 )
#             ],
#         ]
#     )
#     def testTFLiteInterpreter(self, model, params=None, quantization=None):
#         if params is None:
#             params = {}
#         export_dir = self.get_temp_dir()
#         _convert_tflite(model, export_dir, params, quantization)
#         self.assertTrue(dir_has_tflite_file(export_dir))
#         export_file = os.path.join(export_dir, "yimt.tflite")
#         interpreter = tf.lite.Interpreter(model_path=export_file, num_threads=1)
#         input_details = interpreter.get_input_details()
#         output_details = interpreter.get_output_details()
#         input_ids = [2, 3, 4, 5, 6]
#         interpreter.resize_tensor_input(0, [len(input_ids)], strict=True)
#         interpreter.allocate_tensors()
#         np_in_data = np.array(input_ids, dtype=np.int32)
#         interpreter.set_tensor(input_details[0]["index"], np_in_data)
#         interpreter.invoke()
#         output_ids = interpreter.get_tensor(output_details[0]["index"])
#         return output_ids


if __name__ == "__main__":
    tryTFLiteInterpreter(catalog.TransformerBase, {"beam_width": 3}, "dynamic_range")
