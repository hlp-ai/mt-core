import os

import tensorflow as tf

from yimt.core import tokenizers


class TokenizerTest(tf.test.TestCase):
    def _testTokenizerOnTensor(self, tokenizer, text, ref_tokens, training):
        ref_tokens = [tf.compat.as_bytes(token) for token in ref_tokens]
        text = tf.constant(text)
        tokens = tokenizer.tokenize_sp(text, training=training)
        self.assertIsInstance(tokens, tf.Tensor)
        if not ref_tokens:
            self.assertEmpty(tokens)
        else:
            self.assertAllEqual(ref_tokens, tokens)

    def _testTokenizerOnBatchTensor(self, tokenizer, text, ref_tokens, training):
        text = tf.constant(text)
        tokens = tokenizer.tokenize_sp(text, training=training)
        self.assertIsInstance(tokens, tf.RaggedTensor)
        self.assertAllEqual(
            tokens.to_list(), tf.nest.map_structure(tf.compat.as_bytes, ref_tokens)
        )

    def _testTokenizerOnStream(self, tokenizer, text, ref_tokens, training):
        input_path = os.path.join(self.get_temp_dir(), "input.txt")
        output_path = os.path.join(self.get_temp_dir(), "output.txt")
        with open(input_path, "w", encoding="utf-8") as input_file:
            for line in text:
                input_file.write(line)
                input_file.write("\n")
        with open(input_path, encoding="utf-8") as input_file, open(output_path, "w", encoding="utf-8") as output_file:
            tokenizer.tokenize_stream(input_file, output_file, training=training)
        with open(output_path, encoding="utf-8") as output_file:
            for output, ref in zip(output_file, ref_tokens):
                self.assertEqual(output.strip().split(), ref)

    def _testTokenizerOnString(self, tokenizer, text, ref_tokens, training):
        tokens = tokenizer.tokenize_sp(text, training=training)
        self.assertAllEqual(ref_tokens, tokens)

    def _testTokenizer(self, tokenizer, text, ref_tokens, training=True):
        self.assertAllEqual(tokenizer.tokenize_sp(text, training), ref_tokens)
        self._testTokenizerOnBatchTensor(tokenizer, text, ref_tokens, training)
        self._testTokenizerOnStream(tokenizer, text, ref_tokens, training)
        for txt, ref in zip(text, ref_tokens):
            self._testTokenizerOnTensor(tokenizer, txt, ref, training)
            self._testTokenizerOnString(tokenizer, txt, ref, training)

    def _testDetokenizerOnTensor(self, tokenizer, tokens, ref_text):
        ref_text = tf.compat.as_bytes(ref_text)
        tokens = tf.constant(tokens, dtype=tf.string)
        text = tokenizer.detokenize_sp(tokens)
        self.assertEqual(ref_text, self.evaluate(text))

    def _testDetokenizerOnBatchTensor(self, tokenizer, tokens, ref_text):
        ref_text = [tf.compat.as_bytes(t) for t in ref_text]
        sequence_length = [len(x) for x in tokens]
        max_length = max(sequence_length)
        tokens = [tok + [""] * (max_length - len(tok)) for tok in tokens]
        tokens = tf.constant(tokens)
        sequence_length = tf.constant(sequence_length)
        text = tokenizer.detokenize_sp(tokens, sequence_length=sequence_length)
        self.assertAllEqual(ref_text, self.evaluate(text))

    def _testDetokenizerOnBatchRaggedTensor(self, tokenizer, tokens, ref_text):
        lengths = tf.constant([len(x) for x in tokens])
        flat_tokens = tf.constant(tf.nest.flatten(tokens))
        ragged_tokens = tf.RaggedTensor.from_row_lengths(flat_tokens, lengths)
        text = tokenizer.detokenize_sp(ragged_tokens)
        self.assertAllEqual(
            self.evaluate(text), tf.nest.map_structure(tf.compat.as_bytes, ref_text)
        )

    def _testDetokenizerOnStream(self, tokenizer, tokens, ref_text):
        input_path = os.path.join(self.get_temp_dir(), "input.txt")
        output_path = os.path.join(self.get_temp_dir(), "output.txt")
        with open(input_path, "w", encoding="utf-8") as input_file:
            for tok in tokens:
                input_file.write(" ".join(tok))
                input_file.write("\n")
        with open(input_path, encoding="utf-8") as input_file, open(output_path, "w", encoding="utf-8") as output_file:
            tokenizer.detokenize_stream(input_file, output_file)
        with open(output_path, encoding="utf-8") as output_file:
            for output, ref in zip(output_file, ref_text):
                self.assertEqual(output.strip(), ref)

    def _testDetokenizerOnString(self, tokenizer, tokens, ref_text):
        text = tokenizer.detokenize_sp(tokens)
        self.assertAllEqual(ref_text, text)

    def _testDetokenizer(self, tokenizer, tokens, ref_text):
        self.assertAllEqual(tokenizer.detokenize_sp(tokens), ref_text)
        self._testDetokenizerOnBatchTensor(tokenizer, tokens, ref_text)
        self._testDetokenizerOnBatchRaggedTensor(tokenizer, tokens, ref_text)
        self._testDetokenizerOnStream(tokenizer, tokens, ref_text)
        for tok, ref in zip(tokens, ref_text):
            self._testDetokenizerOnTensor(tokenizer, tok, ref)
            self._testDetokenizerOnString(tokenizer, tok, ref)

    def testSpaceTokenizer(self):
        self._testTokenizer(
            tokenizers.SpaceTokenizer(),
            ["Hello world !", "How are you ?", "", "Good !"],
            [["Hello", "world", "!"], ["How", "are", "you", "?"], [], ["Good", "!"]],
        )
        self._testDetokenizer(
            tokenizers.SpaceTokenizer(),
            [["Hello", "world", "!"], ["Test"], [], ["My", "name"]],
            ["Hello world !", "Test", "", "My name"],
        )

    def testMakeTokenizer(self):
        tokenizer = tokenizers.make_tokenizer()
        self.assertIsInstance(tokenizer, tokenizers.SpaceTokenizer)
        self.assertFalse(tokenizer.in_graph)
        tokenizer = tokenizers.make_tokenizer({"type": "SpaceTokenizer"})
        self.assertIsInstance(tokenizer, tokenizers.SpaceTokenizer)
        self.assertTrue(tokenizer.in_graph)

        with self.assertRaisesRegex(ValueError, "is not in list of"):
            tokenizers.make_tokenizer({"type": "UnknownTokenizer"})
        with self.assertRaisesRegex(ValueError, "is not in list of"):
            tokenizers.make_tokenizer({"type": "Tokenizer"})


if __name__ == "__main__":
    tf.test.main()
