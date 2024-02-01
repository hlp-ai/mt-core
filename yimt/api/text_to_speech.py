import os
import tempfile

import yaml
from tts.interface import FS2MBMelGAN, save_wav, play_wav


class Text2Speech:

    def __init__(self,
                 txt2mel_conf_fn, txt2mel_model_fn,
                 mel2wav_conf_fn, mel2wav_model_fn,
                 mapper_fn,
                 language,
                 rate):
        self.txt2mel_conf_fn = txt2mel_conf_fn
        self.txt2mel_model_fn = txt2mel_model_fn
        self.mel2wav_conf_fn = mel2wav_conf_fn
        self.mel2wav_model_fn = mel2wav_model_fn
        self.mapper_fn = mapper_fn
        self.language = language
        self.rate = rate
        self.tts = None

    def support_lang(self, lang):
        return lang == self.language

    def synthesize(self, txt):
        if self.tts is None:
            print("Loading TTS for", self.language)
            self.tts = FS2MBMelGAN(self.txt2mel_conf_fn, self.txt2mel_model_fn,
                 self.mel2wav_conf_fn, self.mel2wav_model_fn,
                 self.mapper_fn,
                 self.language)

        audio = self.tts.txt2wav(txt)
        return audio, self.rate


class Text2Speeches:

    def __init__(self, conf_file=os.path.join(os.path.dirname(__file__), "tts.yml")):
        with open(conf_file, encoding="utf-8") as config_f:
            config = yaml.safe_load(config_f.read())

        self._synthesizers = {}
        self._languages = []

        for lang, params in config.get("synthesizers").items():
            self._synthesizers[lang] = Text2Speech(**params)
            self._languages.append(lang)

    def synthesize(self, txt, lang):
        for name, tts in self._synthesizers.items():
            if tts.support_lang(lang):
                return tts.synthesize(txt)

        return None

    def languages(self):
        return self._languages


if __name__ == "__main__":
    synthesizers = Text2Speeches()

    while True:
        lang = input("输入要合成语音的语言(en/zh): ")
        txt = input("输入要合成语音的文本: ")

        print("Synthsizing wave...")
        audio, rate = synthesizers.synthesize(txt, lang)

        print("Saving wav...")
        tmp_wav_fn = os.path.join(tempfile.gettempdir(), str(hash(txt)) + ".wav")
        save_wav(audio, tmp_wav_fn, 22050)

        print("Playing wav...")
        play_wav(tmp_wav_fn)
