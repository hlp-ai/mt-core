import tensorflow as tf

from parameterized import parameterized

from yimt.core.data import text


class TextTest(tf.test.TestCase):
    def _testTokensToChars(self, tokens, expected_chars):
        expected_chars = tf.nest.map_structure(tf.compat.as_bytes, expected_chars)
        chars = text.tokens_to_chars(tf.constant(tokens, dtype=tf.string))
        self.assertListEqual(chars.to_list(), expected_chars)

    def testTokensToCharsEmpty(self):
        self._testTokensToChars([], [])

    def testTokensToCharsSingle(self):
        self._testTokensToChars(["Hello"], [["H", "e", "l", "l", "o"]])

    def testTokensToCharsMixed(self):
        self._testTokensToChars(
            ["Just", "a", "测试"], [["J", "u", "s", "t"], ["a"], ["测", "试"]]
        )

    @parameterized.expand(
        [
            [["a￭", "b", "c￭", "d", "￭e"], [["a￭", "b"], ["c￭", "d", "￭e"]]],
            [
                ["a", "￭", "b", "c￭", "d", "￭", "e"],
                [["a", "￭", "b"], ["c￭", "d", "￭", "e"]],
            ],
        ]
    )
    def testToWordsWithJoiner(self, tokens, expected):
        expected = tf.nest.map_structure(tf.compat.as_bytes, expected)
        tokens = tf.constant(tokens)
        words = text.tokens_to_words(tokens)
        self.assertAllEqual(words.to_list(), expected)

    @parameterized.expand(
        [
            [["▁a", "b", "▁c", "d", "e"], [["▁a", "b"], ["▁c", "d", "e"]]],
            [
                ["▁", "a", "b", "▁", "c", "d", "e"],
                [["▁", "a", "b"], ["▁", "c", "d", "e"]],
            ],
            [["a▁", "b", "c▁", "d", "e"], [["a▁"], ["b", "c▁"], ["d", "e"]]],
            [
                ["a", "▁b▁", "c", "d", "▁", "e"],
                [["a"], ["▁b▁"], ["c", "d"], ["▁", "e"]],
            ],
        ]
    )
    def testToWordsWithSpacer(self, tokens, expected):
        expected = tf.nest.map_structure(tf.compat.as_bytes, expected)
        tokens = tf.constant(tokens)
        words = text.tokens_to_words(tokens, subword_token="▁", is_spacer=True)
        self.assertAllEqual(words.to_list(), expected)


if __name__ == "__main__":
    tf.test.main()
