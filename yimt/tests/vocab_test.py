import os

import tensorflow as tf

from yimt.data import vocab as vocab_lib
from yimt.tests import test_util


class VocabTest(tf.test.TestCase):
    def testSimpleVocab(self):
        vocab = vocab_lib.Vocab()

        self.assertEqual(0, vocab.size)

        vocab.add("toto")
        vocab.add("toto")
        vocab.add("toto")
        vocab.add("titi")
        vocab.add("titi")
        vocab.add("tata")

        self.assertEqual(3, vocab.size)
        self.assertEqual(1, vocab.lookup("titi"))
        self.assertEqual("titi", vocab.lookup(1))

        pruned_size = vocab.prune(max_size=2)

        self.assertEqual(2, pruned_size.size)
        self.assertEqual(None, pruned_size.lookup("tata"))

        pruned_frequency = vocab.prune(min_frequency=3)

        self.assertEqual(1, pruned_frequency.size)
        self.assertEqual(0, pruned_frequency.lookup("toto"))

    def testVocabWithSpecialTokens(self):
        vocab = vocab_lib.Vocab(special_tokens=["foo", "bar"])

        self.assertEqual(2, vocab.size)

        vocab.add("toto")
        vocab.add("toto")
        vocab.add("toto")
        vocab.add("titi")
        vocab.add("titi")
        vocab.add("tata")

        self.assertEqual(5, vocab.size)
        self.assertEqual(3, vocab.lookup("titi"))

        pruned_size = vocab.prune(max_size=3)

        self.assertEqual(3, pruned_size.size)
        self.assertEqual(0, pruned_size.lookup("foo"))
        self.assertEqual(1, pruned_size.lookup("bar"))

    def testVocabSaveAndLoad(self):
        vocab1 = vocab_lib.Vocab(special_tokens=["foo", "bar"])
        vocab1.add("toto")
        vocab1.add("toto")
        vocab1.add("toto")
        vocab1.add("titi")
        vocab1.add("titi")
        vocab1.add("tata")

        vocab_file = os.path.join(self.get_temp_dir(), "vocab.txt")

        vocab1.serialize(vocab_file)
        vocab2 = vocab_lib.Vocab.from_file(vocab_file)

        self.assertEqual(vocab1.size, vocab2.size)
        self.assertEqual(vocab1.lookup("titi"), vocab2.lookup("titi"))

    def testLoadSentencePieceVocab(self):
        vocab_path = test_util.make_data_file(
            os.path.join(self.get_temp_dir(), "vocab_sp"),
            [
                "<unk>	0",
                "<s>	0",
                "</s>	0",
                ",	-3.0326",
                ".	-3.41093",
                "▁the	-3.85169",
                "s	-4.05468",
                "▁die	-4.15914",
                "▁in	-4.2419",
                "▁der	-4.36135",
            ],
        )

        vocab = vocab_lib.Vocab.from_file(vocab_path, file_format="sentencepiece")
        self.assertEqual(len(vocab), 7)
        self.assertNotIn("<unk>", vocab)
        self.assertNotIn("<s>", vocab)
        self.assertNotIn("</s>", vocab)
        self.assertIn("▁the", vocab)

    def testVocabPadding(self):
        vocab = vocab_lib.Vocab()
        vocab.add("toto")
        vocab.add("titi")
        vocab.add("tata")
        self.assertEqual(vocab.size, 3)
        vocab.pad_to_multiple(6, num_oov_buckets=1)
        self.assertEqual(vocab.size, 6 - 1)

    def testVocabNoPadding(self):
        vocab = vocab_lib.Vocab()
        vocab.add("toto")
        vocab.add("titi")
        vocab.add("tata")
        self.assertEqual(vocab.size, 3)
        vocab.pad_to_multiple(4, num_oov_buckets=1)
        self.assertEqual(vocab.size, 3)

    def _saveVocab(self, name, words):
        vocab = vocab_lib.Vocab()
        for word in words:
            vocab.add(str(word))
        vocab_file = os.path.join(self.get_temp_dir(), name)
        vocab.serialize(vocab_file)
        return vocab_file


if __name__ == "__main__":
    tf.test.main()
