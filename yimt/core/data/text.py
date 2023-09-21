"""Text manipulation."""

import tensorflow as tf


def tokens_to_chars(tokens):
    """Splits tokens into unicode characters.

    Example:

      >>> yimt.data.tokens_to_chars(["hello", "world"])
      <tf.RaggedTensor [[b'h', b'e', b'l', b'l', b'o'], [b'w', b'o', b'r', b'l', b'd']]>

    Args:
      tokens: A string ``tf.Tensor`` of shape :math:`[T]`.

    Returns:
      The characters as a 2D string ``tf.RaggedTensor``.
    """
    return tf.strings.unicode_split(tokens, "UTF-8")


def tokens_to_words(tokens, subword_token="￭", is_spacer=None):
    """Converts a sequence of tokens to a sequence of words.

    Example:

      >>> yimt.data.tokens_to_words(["He@@", "llo", "W@@", "orld", "@@!"], subword_token="@@")
      <tf.RaggedTensor [[b'He@@', b'llo'], [b'W@@', b'orld', b'@@!']]>

    Args:
      tokens: A 1D string ``tf.Tensor``.
      subword_token: The special token used by the subword tokenizer.
      is_spacer: Whether :obj:`subword_token` is used as a spacer (as in
        SentencePiece) or a joiner (as in BPE). If ``None``, will infer
        directly from :obj:`subword_token`.

    Returns:
      The words as a 2D string ``tf.RaggedTensor``.
    """
    if is_spacer is None:
        is_spacer = subword_token == "▁"
    if is_spacer:
        # First token implicitly starts with a spacer.
        left_and_single = tf.logical_or(
            tf.strings.regex_full_match(tokens, "%s.*" % subword_token),
            tf.one_hot(0, tf.shape(tokens)[0], on_value=True, off_value=False),
        )
        right = tf.strings.regex_full_match(tokens, ".+%s" % subword_token)
        word_start = tf.logical_or(tf.roll(right, shift=1, axis=0), left_and_single)
    else:
        right = tf.strings.regex_full_match(tokens, ".*%s" % subword_token)
        left = tf.strings.regex_full_match(tokens, "%s.*" % subword_token)
        subword = tf.logical_or(tf.roll(right, shift=1, axis=0), left)
        word_start = tf.logical_not(subword)
    start_indices = tf.squeeze(tf.where(word_start), -1)
    return tf.RaggedTensor.from_row_starts(tokens, start_indices)
