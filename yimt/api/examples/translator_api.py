from yimt.api.translators import Translators

if __name__ == "__main__":
    translators = Translators()
    print(translators.support_languages())

    translator = translators.get_translator("aaa", "bbb")
    assert translator==None

    translator = translators.get_translator("en", "zh")
    print(translator.translate_paragraph("This is a book. Is this right?"))
