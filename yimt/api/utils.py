from langid import langid


def is_en(s):
    """Judge whether the characters in s are ASCII"""
    return all([c.isascii() for c in s])


def detect_lang(text):
    """Detect language of text

    Args:
        text: text to be detected

    Returns:
        language code string
    """
    # text = remove_lang_independent(text)
    if is_en(text):
        return "en"
    return langid.classify(text)[0]
