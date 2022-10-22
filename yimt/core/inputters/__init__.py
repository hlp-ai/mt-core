"""Module defining inputters.

Inputters implement the logic of transforming raw data to vectorized inputs,
e.g., from a line of text to a sequence of embeddings.
"""

from yimt.core.inputters.inputter import (
    ExampleInputter,
    ExampleInputterAdapter,
    Inputter,
    MixedInputter,
    MultiInputter,
    ParallelInputter,
)
from yimt.core.inputters.text_inputter import (
    TextInputter,
    WordEmbedder,
    add_sequence_controls,
    load_pretrained_embeddings,
)
