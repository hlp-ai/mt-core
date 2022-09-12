import os
import yaml

from yimt.api.translator import WordTranslator, load_translator, Translator


class Translators(object):

    def __init__(self, config_path=os.path.join(os.path.dirname(__file__), "translators.yml")):
        self.config_file = config_path

        self.translators, self.lang_pairs = self.available_translators()

        self.from_langs = list(set([p.split("-")[0] for p in self.lang_pairs]))
        self.to_langs = list(set([p.split("-")[1] for p in self.lang_pairs]))

        print("Available translators:", self.translators)
        print("Available language pairs:", self.lang_pairs)

        self.word_translators = {}

    def available_translators(self):
        """Get translators from config file

        Returns:
             dictionary from language pair to translator parameter, language pairs
        """
        translators = {}
        lang_pairs = []
        with open(self.config_file, encoding="utf-8") as config_f:
            config = yaml.safe_load(config_f.read())

        for lang_pair, params in config.get("translators").items():
            translators[lang_pair] = params
            lang_pairs.append(lang_pair)

        return translators, lang_pairs

    def support_languages(self):
        return self.lang_pairs, self.from_langs, self.to_langs

    def get_translator(self, source_lang, target_lang):
        """ Get and load translator for lang pair

        Args:
             source_lang: source language
             target_lang: target language

        Returns:
            Translator if exist for language pair, otherwise None
        """
        lang_pair = source_lang + "-" + target_lang
        translator = self.translators.get(lang_pair)
        if translator is None:
            return None
        elif isinstance(translator, Translator):
            return translator
        else:
            print("Loading translator {}...".format(lang_pair))
            self.translators[lang_pair] = load_translator(model_or_config_dir=translator["model_or_config_dir"],
                                                          sp_src_path=translator["sp_src_path"],
                                                          lang_pair=lang_pair)
            return self.translators[lang_pair]

    def get_word_translator(self, source_lang, target_lang):
        if source_lang == "zh":
            source_lang = "zh_cn"

        if target_lang == "zh":
            target_lang = "zh_cn"

        lang = source_lang + "-" + target_lang
        if lang not in self.word_translators:
            print("Loading WordTranslator {}-{}".format(source_lang, target_lang))
            self.word_translators[lang] = WordTranslator(source_lang, target_lang)

        return self.word_translators.get(lang)
