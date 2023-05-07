import os

import tensorflow as tf

from parameterized import parameterized

from yimt.core import encoders, models
from yimt.core import inputters, decoders
from yimt.core.tests import test_util
from yimt.core.utils import misc


def _seq2seq_model(training=None, shared_embeddings=False):
    model = models.SequenceToSequence(
        inputters.WordEmbedder(16),
        inputters.WordEmbedder(16),
        encoders.SelfAttentionEncoder(2, 16, 4, 32),
        decoders.SelfAttentionDecoder(2, 16, 4, 32),
        share_embeddings=(
            models.sequence_to_sequence.EmbeddingsSharingLevel.ALL
            if shared_embeddings
            else models.EmbeddingsSharingLevel.NONE
        ),
    )
    params = {}
    if training:
        params["optimizer"] = "SGD"
        params["learning_rate"] = 0.1
    return model, params


class ModelTest(tf.test.TestCase):
    def _makeToyEnDeData(self, with_alignments=False, with_weights=False):
        data_config = {}
        features_file = test_util.make_data_file(
            os.path.join(self.get_temp_dir(), "src.txt"),
            [
                "Parliament Does Not Support Amendment Freeing Tymoshenko",
                "Today , the Ukraine parliament dismissed , within the Code of Criminal Procedure "
                "amendment , the motion to revoke an article based on which the opposition leader "
                ", Yulia Tymoshenko , was sentenced .",
                "The amendment that would lead to freeing the imprisoned former Prime Minister was "
                "revoked during second reading of the proposal for mitigation of sentences for "
                "economic offences .",
            ],
        )
        labels_file = test_util.make_data_file(
            os.path.join(self.get_temp_dir(), "tgt.txt"),
            [
                "Keine befreiende Novelle für Tymoshenko durch das Parlament",
                "Das ukrainische Parlament verweigerte heute den Antrag , im Rahmen einer Novelle "
                "des Strafgesetzbuches denjenigen Paragrafen abzuschaffen , auf dessen Grundlage "
                "die Oppositionsführerin Yulia Timoshenko verurteilt worden war .",
                "Die Neuregelung , die den Weg zur Befreiung der inhaftierten Expremierministerin "
                "hätte ebnen können , lehnten die Abgeordneten bei der zweiten Lesung des Antrags "
                "auf Milderung der Strafen für wirtschaftliche Delikte ab .",
            ],
        )
        data_config["source_vocabulary"] = test_util.make_vocab_from_file(
            os.path.join(self.get_temp_dir(), "src_vocab.txt"), features_file
        )
        data_config["target_vocabulary"] = test_util.make_vocab_from_file(
            os.path.join(self.get_temp_dir(), "tgt_vocab.txt"), labels_file
        )
        if with_alignments:
            # Dummy and incomplete alignments.
            data_config["train_alignments"] = test_util.make_data_file(
                os.path.join(self.get_temp_dir(), "alignments.txt"),
                [
                    "0-0 1-0 2-2 3-4 4-4 5-6",
                    "0-1 1-1 1-3 2-3 4-4",
                    "0-0 1-0 2-2 3-4 4-4 5-6",
                ],
            )
        if with_weights:
            data_config["example_weights"] = test_util.make_data_file(
                os.path.join(self.get_temp_dir(), "weights.txt"), ["0.6", "1", "1e-2"]
            )
        return features_file, labels_file, data_config

    def _makeToyLMData(self):
        features_file, _, data_config = self._makeToyEnDeData()
        return features_file, {"vocabulary": data_config["source_vocabulary"]}

    def _makeToyClassifierData(self):
        data_config = {}
        features_file = test_util.make_data_file(
            os.path.join(self.get_temp_dir(), "src.txt"),
            [
                "This product was not good at all , it broke on the first use !",
                "Perfect , it does everything I need .",
                "How do I change the battery ?",
            ],
        )
        labels_file = test_util.make_data_file(
            os.path.join(self.get_temp_dir(), "labels.txt"),
            ["negative", "positive", "neutral"],
        )
        data_config["source_vocabulary"] = test_util.make_vocab_from_file(
            os.path.join(self.get_temp_dir(), "src_vocab.txt"), features_file
        )
        data_config["target_vocabulary"] = test_util.make_data_file(
            os.path.join(self.get_temp_dir(), "labels_vocab.txt"),
            ["negative", "positive", "neutral"],
        )
        return features_file, labels_file, data_config

    def _testGenericModel(
        self,
        model,
        mode,
        features_file,
        labels_file=None,
        data_config=None,
        batch_size=16,
        prediction_heads=None,
        metrics=None,
        params=None,
    ):
        # Mainly test that the code does not throw.
        if params is None:
            params = model.auto_config()["params"]
        if data_config is None:
            data_config = {}
        model.initialize(data_config, params=params)
        model.create_variables()
        # Build a dataset for mode.
        if mode == tf.estimator.ModeKeys.PREDICT:
            dataset = model.examples_inputter.make_inference_dataset(
                features_file, batch_size
            )
        elif mode == tf.estimator.ModeKeys.EVAL:
            dataset = model.examples_inputter.make_evaluation_dataset(
                features_file, labels_file, batch_size
            )
        elif mode == tf.estimator.ModeKeys.TRAIN:
            dataset = model.examples_inputter.make_training_dataset(
                features_file, labels_file, batch_size
            )
        # Forward first batch into the model.
        data = iter(dataset).next()
        if mode != tf.estimator.ModeKeys.PREDICT:
            features, labels = data
        else:
            features, labels = data, None
        training = mode == tf.estimator.ModeKeys.TRAIN
        outputs, predictions = model(features, labels=labels, training=training)
        if mode != tf.estimator.ModeKeys.PREDICT:
            _ = model.compute_loss(outputs, labels, training=training)
            if mode == tf.estimator.ModeKeys.EVAL:
                # Check that returned evaluation metrics are expected.
                eval_metrics = model.get_metrics()
                if eval_metrics is not None:
                    model.update_metrics(eval_metrics, predictions, labels)
                    for metric in metrics:
                        self.assertIn(metric, eval_metrics)
                try:
                    # Check that scores can be computed and printed without errors.
                    scores = model.score(features, labels)
                    first_score = tf.nest.map_structure(
                        lambda x: x.numpy(), next(misc.extract_batches(scores))
                    )
                    with open(os.devnull, "w") as devnull:
                        model.print_score(first_score, stream=devnull)
                except NotImplementedError:
                    pass
        else:
            # Check that all prediction heads are returned.
            self.assertIsInstance(predictions, dict)
            if prediction_heads is not None:
                for head in prediction_heads:
                    self.assertIn(head, predictions)
            # Check that the prediction can be printed without errors.
            first_prediction = tf.nest.map_structure(
                lambda x: x.numpy(), next(misc.extract_batches(predictions))
            )
            with open(os.devnull, "w") as devnull:
                model.print_prediction(first_prediction, stream=devnull)

    @parameterized.expand(
        [
            [tf.estimator.ModeKeys.TRAIN],
            [tf.estimator.ModeKeys.EVAL],
            [tf.estimator.ModeKeys.PREDICT],
        ]
    )
    def testSequenceToSequence(self, mode):
        model, params = _seq2seq_model(mode)
        features_file, labels_file, data_config = self._makeToyEnDeData()
        self._testGenericModel(
            model,
            mode,
            features_file,
            labels_file,
            data_config,
            prediction_heads=["tokens", "length", "log_probs"],
            params=params,
        )

    @parameterized.expand(
        [
            (models.EmbeddingsSharingLevel.ALL, True, True, True),
            (models.EmbeddingsSharingLevel.AUTO, True, True, True),
            (models.EmbeddingsSharingLevel.AUTO, False, False, True),
        ]
    )
    def testSequenceToSequenceWithSharedEmbedding(
            self, share_embeddings, reuse_vocab, input_is_shared, target_is_shared
    ):
        model = models.SequenceToSequence(
            inputters.WordEmbedder(16),
            inputters.WordEmbedder(16),
            encoders.SelfAttentionEncoder(2, 16, 4, 32),
            decoders.SelfAttentionDecoder(2, 16, 4, 32),
            share_embeddings=share_embeddings,
        )
        _, _, data_config = self._makeToyEnDeData()
        if reuse_vocab:
            data_config["target_vocabulary"] = data_config["source_vocabulary"]
        model.initialize(data_config)
        model.create_variables()

        self.assertEqual(
            model.features_inputter.embedding.ref()
            == model.labels_inputter.embedding.ref(),
            input_is_shared,
        )
        self.assertEqual(
            model.labels_inputter.embedding.ref()
            == model.decoder.output_layer.kernel.ref(),
            target_is_shared,
        )

    @parameterized.expand(
        [[tf.estimator.ModeKeys.EVAL], [tf.estimator.ModeKeys.PREDICT]]
    )
    def testSequenceToSequenceWithInGraphTokenizer(self, mode):
        model, params = _seq2seq_model(mode)
        features_file, labels_file, data_config = self._makeToyEnDeData()
        tokenization_config = {"type": "SpaceTokenizer"}
        data_config["source_tokenization"] = tokenization_config
        data_config["target_tokenization"] = tokenization_config
        self._testGenericModel(
            model,
            mode,
            features_file,
            labels_file,
            data_config,
            prediction_heads=["text", "log_probs"],
            params=params,
        )

    @parameterized.expand([["ce"], ["mse"]])
    def testSequenceToSequenceWithGuidedAlignment(self, ga_type):
        model, params = _seq2seq_model(training=True)
        params["guided_alignment_type"] = ga_type
        features_file, labels_file, data_config = self._makeToyEnDeData(
            with_alignments=True
        )
        model.initialize(data_config, params=params)
        model.create_variables()
        dataset = model.examples_inputter.make_training_dataset(
            features_file, labels_file, 16
        )
        features, labels = next(iter(dataset))
        self.assertIn("alignment", labels)
        outputs, _ = model(features, labels=labels, training=True)
        loss = model.compute_loss(outputs, labels, training=True)
        loss = loss[0] / loss[1]

    def testSequenceToSequenceWithGuidedAlignmentAndWeightedDataset(self):
        model, _ = _seq2seq_model()
        features_file, labels_file, data_config = self._makeToyEnDeData(
            with_alignments=True
        )
        model.initialize(data_config)
        with self.assertRaisesRegex(ValueError, "expected to match"):
            model.examples_inputter.make_training_dataset(
                [features_file, features_file], [labels_file, labels_file], 16
            )
        data_config["train_alignments"] = [
            data_config["train_alignments"],
            data_config["train_alignments"],
        ]
        model.initialize(data_config)
        dataset = model.examples_inputter.make_training_dataset(
            [features_file, features_file], [labels_file, labels_file], 16
        )
        self.assertIsInstance(dataset, tf.data.Dataset)

    def testSequenceToSequenceWithWeightedExamples(self):
        model, params = _seq2seq_model(training=True)
        features_file, labels_file, data_config = self._makeToyEnDeData(
            with_weights=True
        )
        model.initialize(data_config, params=params)
        dataset = model.examples_inputter.make_training_dataset(
            features_file, labels_file, 16
        )
        features, labels = next(iter(dataset))
        self.assertIn("weight", labels)
        outputs, _ = model(features, labels=labels, training=True)
        weighted_loss, _, _ = model.compute_loss(outputs, labels, training=True)
        labels.pop("weight")
        default_loss, _, _ = model.compute_loss(outputs, labels, training=True)
        self.assertNotEqual(weighted_loss, default_loss)

    def testSequenceToSequenceWithReplaceUnknownTarget(self):
        model, params = _seq2seq_model()
        params["replace_unknown_target"] = True
        params["beam_width"] = 2
        features_file, labels_file, data_config = self._makeToyEnDeData()
        data_config["source_sequence_controls"] = {"start": True, "end": True}
        model.initialize(data_config, params=params)
        dataset = model.examples_inputter.make_inference_dataset(features_file, 16)
        features = next(iter(dataset))
        _, predictions = model(features)

    def testSequenceToSequenceWithNoisyDecoding(self):
        model, params = _seq2seq_model()
        params["maximum_decoding_length"] = 20
        params["beam_width"] = 2
        params["decoding_noise"] = [
            {"dropout": 0.1},
            {"replacement": [0.1, "<unk>"]},
            {"permutation": 3},
        ]
        features_file, labels_file, data_config = self._makeToyEnDeData()
        model.initialize(data_config, params=params)
        dataset = model.examples_inputter.make_inference_dataset(features_file, 16)
        features = next(iter(dataset))
        _, predictions = model(features)

    def testSequenceToSequenceWithContrastiveLearning(self):
        model, params = _seq2seq_model()
        params["contrastive_learning"] = True
        features_file, labels_file, data_config = self._makeToyEnDeData()
        model.initialize(data_config, params=params)
        dataset = model.examples_inputter.make_training_dataset(
            features_file, labels_file, 16
        )
        features, labels = next(iter(dataset))
        self.assertIn("noisy_ids", labels)
        self.assertIn("noisy_ids_out", labels)
        self.assertIn("noisy_length", labels)
        outputs, _ = model(features, labels=labels, training=True)
        self.assertIn("noisy_logits", outputs)
        loss = model.compute_loss(outputs, labels, training=True)
        self.assertGreaterEqual(self.evaluate(loss), 0)

    def testSequenceToSequenceServing(self):
        # Test that serving features can be forwarded into the model.
        _, _, data_config = self._makeToyEnDeData()
        model, params = _seq2seq_model()
        params["beam_width"] = 4
        model.initialize(data_config, params=params)
        function = model.serve_function()
        concrete_function = function.get_concrete_function()
        # Check that we don't use the GatherTree custom op from Addons.
        op_types = set(op.type for op in concrete_function.graph.get_operations())
        self.assertNotIn("Addons>GatherTree", op_types)

    def testCreateVariables(self):
        _, _, data_config = self._makeToyEnDeData()
        model, params = _seq2seq_model()
        model.initialize(data_config, params=params)
        model.create_variables()
        self.assertTrue(len(model.trainable_variables) > 0)

    def testInitializeWithDropoutOverride(self):
        model = models.SequenceToSequence(
            inputters.WordEmbedder(16),
            inputters.WordEmbedder(16),
            encoders.SelfAttentionEncoder(2, 16, 4, 32),
            decoders.SelfAttentionDecoder(2, 16, 4, 32),
        )
        self.assertEqual(model.encoder.dropout, 0.1)
        _, _, data_config = self._makeToyClassifierData()
        params = dict(dropout=0.3)
        model.initialize(data_config, params=params)
        self.assertEqual(model.encoder.dropout, 0.3)

    def testFreezeLayers(self):
        model, _ = _seq2seq_model(training=True)
        params = {"freeze_layers": ["decoder/output_layer", "encoder/layers/0"]}
        _, _, data_config = self._makeToyEnDeData()
        model.initialize(data_config, params=params)
        model.create_variables()
        trainable_variables = model.trainable_variables
        self.assertNotEmpty(trainable_variables)
        trainable_variables_ref = set(
            variable.ref() for variable in trainable_variables
        )

        def _assert_layer_not_trainable(layer):
            self.assertFalse(layer.trainable)
            for variable in layer.variables:
                self.assertNotIn(variable.ref(), trainable_variables_ref)

        _assert_layer_not_trainable(model.decoder.output_layer)
        _assert_layer_not_trainable(model.encoder.layers[0])
        self.assertEqual(model.encoder.layers[0].ffn.output_dropout, 0)
        self.assertEqual(model.encoder.layers[0].self_attention.output_dropout, 0)

    @parameterized.expand(
        [
            [models.TransformerBase()],
            [models.TransformerBaseRelative()],
            [models.TransformerBig()],
            [models.TransformerBigRelative()],
            [
                models.Transformer(
                    num_layers=(6, 3),
                    num_units=32,
                    num_heads=8,
                    ffn_inner_dim=64,
                )
            ],
            [models.Transformer(ffn_activation=tf.nn.gelu)],
            [models.Transformer(ffn_activation=tf.nn.silu)],
        ]
    )
    def testCTranslate2Spec(self, model):
        try:
            spec = model.ctranslate2_spec
            self.assertIsNotNone(spec)
            self.assertIs(spec.with_source_bos, False)
            self.assertIs(spec.with_source_eos, False)
        except ImportError:
            self.skipTest("ctranslate2 module is not available")

    def testCTranslate2SpecSequenceControls(self):
        _, _, data_config = self._makeToyEnDeData()
        data_config["source_sequence_controls"] = {"start": False, "end": True}
        model = models.TransformerBase()
        model.initialize(data_config)
        spec = model.ctranslate2_spec
        self.assertIs(spec.with_source_bos, False)
        self.assertIs(spec.with_source_eos, True)

    def testTransformerWithDifferentEncoderDecoderLayers(self):
        model = models.Transformer(
            inputters.WordEmbedder(32),
            inputters.WordEmbedder(32),
            num_layers=(6, 3),
            num_units=32,
            num_heads=8,
            ffn_inner_dim=64,
        )
        self.assertLen(model.encoder.layers, 6)
        self.assertLen(model.decoder.layers, 3)

    def testTransformerNoOutputBias(self):
        _, _, data_config = self._makeToyEnDeData()
        model = models.Transformer(output_layer_bias=False)
        model.initialize(data_config)
        self.assertFalse(model.decoder.output_layer.use_bias)

    def testBeamSearchWithMultiSourceEncoder(self):
        shared_vocabulary = test_util.make_vocab(
            os.path.join(self.get_temp_dir(), "vocab.txt"), ["1", "2", "3"]
        )
        data_config = {
            "source_1_vocabulary": shared_vocabulary,
            "source_2_vocabulary": shared_vocabulary,
            "target_vocabulary": shared_vocabulary,
        }
        params = {
            "beam_width": 2,
        }
        model = models.Transformer(
            inputters.ParallelInputter(
                [inputters.WordEmbedder(32), inputters.WordEmbedder(32)]
            ),
            inputters.WordEmbedder(32),
            num_layers=3,
            num_units=32,
            num_heads=8,
            ffn_inner_dim=64,
        )
        model.initialize(data_config, params=params)
        model.serve_function().get_concrete_function()

    def testTrainModelOnBatch(self):
        _, _, data_config = self._makeToyEnDeData()
        optimizer = tf.keras.optimizers.Adam()
        model = models.TransformerTiny()
        model.initialize(data_config)
        features = model.features_inputter.make_features(
            ["hello world !", "how are you ?"]
        )
        labels = model.labels_inputter.make_features(
            ["hallo welt !", "wie geht es dir ?"]
        )
        loss1 = model.train(features, labels, optimizer)
        loss2 = model.train(features, labels, optimizer)
        self.assertLess(loss2, loss1)


if __name__ == "__main__":
    tf.test.main()
