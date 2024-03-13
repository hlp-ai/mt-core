from yimt.api.translators import translator_factory

if __name__ == "__main__":
    translators = translator_factory
    print(translators.support_languages())

    translator = translators.get_translator("aaa", "bbb")
    assert translator==None

    translator = translators.get_translator("en", "zh")
    print(translator.translate_paragraph("This is a book. Is this right?"))
