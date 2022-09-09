"""Catalog of predefined models."""

from yimt.models import (
    model,
    sequence_to_sequence,
    transformer,
)
from yimt.utils import misc

_CATALOG_MODELS_REGISTRY = misc.ClassRegistry(base_class=model.Model)

register_model_in_catalog = _CATALOG_MODELS_REGISTRY.register


def list_model_names_from_catalog():
    """Lists the models name registered in the catalog."""
    return _CATALOG_MODELS_REGISTRY.class_names


def get_model_from_catalog(name, as_builder=False):
    """Gets a model from the catalog.

    Args:
      name: The model name in the catalog.
      as_builder: If ``True``, return a callable building the model on call.

    Returns:
      A :class:`yimt.models.Model` instance or a callable returning such
      instance.

    Raises:
      ValueError: if the model :obj:`name` does not exist in the catalog.
    """
    model_class = _CATALOG_MODELS_REGISTRY.get(name)
    if model_class is None:
        raise ValueError("The model '%s' does not exist in the model catalog" % name)
    if as_builder:
        return model_class
    return model_class()


@register_model_in_catalog(alias="Transformer")
class TransformerBase(transformer.Transformer):
    """Defines a base Transformer model as described in https://arxiv.org/abs/1706.03762."""


@register_model_in_catalog
class TransformerBaseSharedEmbeddings(transformer.Transformer):
    """Defines a base Transformer model with shared embeddings as described in
    https://arxiv.org/abs/1706.03762.
    """

    def __init__(self):
        super().__init__(
            share_embeddings=sequence_to_sequence.EmbeddingsSharingLevel.ALL,
        )


@register_model_in_catalog(alias="TransformerRelative")
class TransformerBaseRelative(transformer.Transformer):
    """Defines a base Transformer model using relative position representations as
    described in https://arxiv.org/abs/1803.02155.
    """

    def __init__(self):
        super().__init__(position_encoder_class=None, maximum_relative_position=20)


# Backward compatibility with model descriptions that directly accessed the catalog module.
Transformer = TransformerBase
TransformerRelative = TransformerBaseRelative


@register_model_in_catalog
class TransformerBig(transformer.Transformer):
    """Defines a big Transformer model as described in https://arxiv.org/abs/1706.03762."""

    def __init__(self):
        super().__init__(num_units=1024, num_heads=16, ffn_inner_dim=4096)


@register_model_in_catalog
class TransformerBigSharedEmbeddings(transformer.Transformer):
    """Defines a big Transformer model with shared embeddings as described in
    https://arxiv.org/abs/1706.03762.
    """

    def __init__(self):
        super().__init__(
            num_units=1024,
            num_heads=16,
            ffn_inner_dim=4096,
            share_embeddings=sequence_to_sequence.EmbeddingsSharingLevel.ALL,
        )


@register_model_in_catalog
class TransformerBigRelative(transformer.Transformer):
    """Defines a big Transformer model using relative position representations as
    described in https://arxiv.org/abs/1803.02155.
    """

    def __init__(self):
        super().__init__(
            num_units=1024,
            num_heads=16,
            ffn_inner_dim=4096,
            position_encoder_class=None,
            maximum_relative_position=20,
        )


@register_model_in_catalog
class TransformerTiny(transformer.Transformer):
    """Defines a tiny Transformer model."""

    def __init__(self):
        super().__init__(
            num_layers=2,
            num_units=64,
            num_heads=2,
            ffn_inner_dim=64,
        )
