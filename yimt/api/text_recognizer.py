import os

import yaml
from ocr.detect import OCRImpl


class TextRecognizer:

    def __init__(self, ctpn_model_path, densenet_model_path, vocab_path,
                 name, langs):
        self._ctpn_model_path = ctpn_model_path
        self._densenet_model_path = densenet_model_path
        self._vocab_path = vocab_path
        self._name = name
        self._langs = langs
        self._ocr = None

    def support_lang(self, lang):
        return lang in self._langs

    def name(self):
        return self._name

    def recognize(self, img):
        if self._ocr is None:
            print("Loadig OCR for", self._name)
            self._ocr = OCRImpl(ctpn_weight_path=self._ctpn_model_path,
                          densenet_weight_path=self._densenet_model_path,
                          dict_path=self._vocab_path)

        texts = self._ocr.detect(img)
        return '\n'.join(texts)


class TextRecognizers:

    def __init__(self, conf_file=os.path.join(os.path.dirname(__file__), "ocr.yml")):
        with open(conf_file, encoding="utf-8") as config_f:
            config = yaml.safe_load(config_f.read())

        self._recognizers = {}

        for name, params in config.get("recognizers").items():
            ctpn_path = params["ctpn_model_path"]
            densenet_path = params["densenet_model_path"]
            vocab_path = params["vocab_path"]
            langs = params["langs"]

            self._recognizers[name] = TextRecognizer(ctpn_path, densenet_path, vocab_path,
                                                     name, langs)

    def recognize(self, img, lang):
        for name, ocr in self._recognizers.items():
            if ocr.support_lang(lang):
                return ocr.recognize(img)

        return None


if __name__ == "__main__":
    recognizers = TextRecognizers()
    image_path = "./examples/en1.png"

    print(recognizers.recognize(image_path, "en"))
