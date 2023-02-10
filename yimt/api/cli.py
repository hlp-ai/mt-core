"""Translation cmd"""
import argparse
import sys

from yimt.api.translators import Translators


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("src_lang", help="source language")
    argparser.add_argument("tgt_lang", help="target language")
    args = argparser.parse_args()

    translator = Translators().get_translator(args.src_lang, args.tgt_lang)
    if translator is None:
        print("Language pair {} is wrong or not supported!".format(args.lang))
        sys.exit(-1)

    while True:
        text = input("Source: ")
        output = translator.translate_paragraph(text)
        print("Translation: %s" % output)
        print("")
