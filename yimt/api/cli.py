"""Translation cmd"""
import sys

from yimt.api.translators import Translators


if __name__ == "__main__":
    translators = Translators("./mnmt.yml")

    while True:
        sl = input("sl: ")
        tl = input("tl: ")
        text = input("Source: ")

        translator = translators.get_translator(sl, tl)
        if translator is None:
            print("Language pair {}-{} is wrong or not supported!".format(sl, tl))
            sys.exit(-1)
        output = translator.translate_paragraph(text)
        print("Translation: %s" % output)
        print()

