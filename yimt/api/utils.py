from langid import langid


def detect_lang(text):
    """Detect language of text

    Args:
        text: text to be detected

    Returns:
        language code string
    """
    # text = remove_lang_independent(text)
    if all([c.isascii() for c in text]):
        return "en"
    return langid.classify(text)[0]
