import os
import threading

import ctranslate2
import yaml

from yimt.api.translator import Translator, DummyTranslator, TranslatorCT2, TranslatorSaved, TranslatorCkpt, \
    TranslatorMNMT
from yimt.experimental.mnmt.mtranslator import MTranslatorCkpt


def load_translator(model_or_config_dir, sp_src_path, lang_pair=None, pretok_src=False, pretok_tgt=False):
    """Create translator form config or model

    Args:
        param model_or_config_dir: model directory or config yaml file
        sp_src_path: SentencePiece model file for source language
        lang_pair: lang pair supported by translator

    Returns:
        a Translator
    """
    if ctranslate2.contains_model(model_or_config_dir):  # CTranslate2 model
        return TranslatorCT2(model_or_config_dir, sp_src_path, lang_pair, pretok_src=pretok_src, pretok_tgt=pretok_tgt)
    elif os.path.exists(os.path.join(model_or_config_dir, "saved_model.pb")):  # SavedModel
        return TranslatorSaved(model_or_config_dir, sp_src_path, lang_pair, pretok_src=pretok_src, pretok_tgt=pretok_tgt)
    else:  # checkpoint
        return TranslatorCkpt(model_or_config_dir, sp_src_path, lang_pair, pretok_src=pretok_src, pretok_tgt=pretok_tgt)


mutex = threading.Lock()


class Translators(object):

    def __init__(self, config_path=os.path.join(os.path.dirname(__file__), "translators.yml")):
        if not os.path.exists(config_path):
            raise ValueError("Translator config file {} not exist.".format(config_path))

        self.config_file = config_path

        self.translators, self.lang_pairs, self.langs_api = self.available_translators()

        self.from_langs = list(set([p.split("-")[0] for p in self.lang_pairs]))
        self.to_langs = list(set([p.split("-")[1] for p in self.lang_pairs]))

        print("Available translators:", self.translators)
        print("Available language pairs:", self.lang_pairs)

        self.x2zh = None
        self.zh2x = None

        if "x" in self.from_langs:
            self.from_langs.clear()
            for d in self.langs_api:
                self.from_langs.append(d["code"])

        if "x" in self.to_langs:
            self.to_langs.clear()
            for d in self.langs_api:
                self.to_langs.append(d["code"])

    def available_translators(self):
        """Get translators from config file

        Returns:
             dictionary from language pair to translator parameter, list of language pairs
        """
        translators = {}
        lang_pairs = []
        with open(self.config_file, encoding="utf-8") as config_f:
            config = yaml.safe_load(config_f.read())

        for lang_pair, params in config.get("translators").items():
            translators[lang_pair] = params
            lang_pairs.append(lang_pair)

        langs_api = []
        for lang in config.get("languages"):
            langs_api.append(lang)

        return translators, lang_pairs, langs_api

    def support_languages(self):
        return self.lang_pairs, self.from_langs, self.to_langs, self.langs_api

    def get_translator(self, source_lang, target_lang, debug=False):
        """ Get and load translator for lang pair

        Args:
             source_lang: source language
             target_lang: target language

        Returns:
            Translator if exist for language pair, otherwise None
        """
        if debug:
            return DummyTranslator()

        with mutex:
            lang_pair = source_lang + "-" + target_lang
            translator = self.translators.get(lang_pair)
            if translator is None:
                if target_lang == "zh":
                    if self.x2zh is None:
                        print("Loading x-zh translator for {}...".format(lang_pair))

                        conf = self.translators.get("x-zh")
                        self.x2zh = MTranslatorCkpt(conf["model_or_config_dir"], conf["sp_src_path"])

                    print("Create instance for {}".format(lang_pair))
                    self.translators[lang_pair] = TranslatorMNMT(lang_pair, self.x2zh)
                    return self.translators[lang_pair]
                elif source_lang == "zh":
                    if self.zh2x is None:
                        print("Loading zh-x translator for {}...".format(lang_pair))

                        conf = self.translators.get("zh-x")
                        self.zh2x = MTranslatorCkpt(conf["model_or_config_dir"], conf["sp_src_path"])

                    print("Create instance for {}".format(lang_pair))
                    self.translators[lang_pair] = TranslatorMNMT(lang_pair, self.zh2x)
                    return self.translators[lang_pair]
                else:
                    return None
            elif isinstance(translator, Translator):
                return translator
            else:
                print("Loading translator for {}...".format(lang_pair))
                translator["lang_pair"] = lang_pair
                self.translators[lang_pair] = load_translator(**translator)
                return self.translators[lang_pair]


translator_factory = Translators()
