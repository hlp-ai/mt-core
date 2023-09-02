import os
import yaml

from yimt.api.translator import load_translator, Translator, DummyTranslator


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

        lang_pair = source_lang + "-" + target_lang
        translator = self.translators.get(lang_pair)
        if translator is None:
            return None
        elif isinstance(translator, Translator):
            return translator
        else:
            print("Loading translator for {}...".format(lang_pair))
            self.translators[lang_pair] = load_translator(model_or_config_dir=translator["model_or_config_dir"],
                                                          sp_src_path=translator["sp_src_path"],
                                                          lang_pair=lang_pair)
            return self.translators[lang_pair]
