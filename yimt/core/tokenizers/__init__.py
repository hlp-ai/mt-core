"""Module defining tokenizers.

Tokenizers can work on string ``tf.Tensor`` as in-graph transformation.
"""

from yimt.core.tokenizers.tokenizer import (
    SpaceTokenizer,
    Tokenizer,
    make_tokenizer,
    register_tokenizer,
)

