"""Module defining tokenizers.

Tokenizers can work on string ``tf.Tensor`` as in-graph transformation.
"""

try:
    import pyonmttok

    from yimt.core.tokenizers.opennmt_tokenizer import OpenNMTTokenizer
except ImportError:
    pass

from yimt.core.tokenizers.tokenizer import (
    CharacterTokenizer,
    SpaceTokenizer,
    Tokenizer,
    make_tokenizer,
    register_tokenizer,
)

