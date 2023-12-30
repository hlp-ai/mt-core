from yimt.api.translator import Translator, get_model_from_checkpoint


class MTranslator(Translator):
    """Translator base class"""

    def __init__(self, sp_src_path, batch_size=64):
        super().__init__(sp_src_path, None, batch_size)

        self.to_lang = ""

    def _tokenize(self, text):
        """Tokenize string

        Args:
            text: string or list of string

        Returns:
             list of token list
        """
        if not isinstance(text, (list, tuple)):
            text = [text]

        text = [self.to_lang+t for t in text]

        return super(MTranslator, self)._tokenize(text)


class MTranslatorCkpt(MTranslator):
    """A checkpoint based translator with SentencePieced tokenization"""

    def __init__(self, config_file, sp_src_path, batch_size=64):
        """Load model

        :param config_file: configuration file path
        :param sp_src_path: SentencePiece model file for source language
        """
        super().__init__(sp_src_path, batch_size)
        self._model = get_model_from_checkpoint(config_file)

    def _translate_batch(self, texts):
        # tokenize
        inputs = self._preprocess(texts)

        # encode
        features = self._model.features_inputter.make_features(features=inputs.copy())

        # translate
        _, outputs = self._model(features)

        # detokenize
        texts = self._postprocess(outputs)
        return texts


if __name__ == "__main__":
    mt = MTranslatorCkpt(r"D:\dataset\mnmt\zh-x\avg.yml",
                           r"D:\dataset\mnmt\sp\en-zh.tsv.zh-sp-32000.model")

    text = "你在做什么？"
    mt.to_lang = "<toja>"
    trans = mt.translate_paragraph(text)
    print(trans)

    mt.to_lang = "<toen>"
    trans = mt.translate_paragraph(text)
    print(trans)
