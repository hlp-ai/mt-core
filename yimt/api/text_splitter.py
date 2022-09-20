"""Split sentences and paragraphs"""
import re

import pysbd
from sentence_splitter import split_text_into_sentences
from indicnlp.tokenize.sentence_tokenize import sentence_split


tokenizers = {}


def _get_tokenizer(lang):
    """Get tokenizer for given language

    Args:
        lang: language code string

    Returns:
        tokenizer of some type
    """
    if lang in tokenizers:
        return tokenizers.get(lang)

    print("Loading tokenizer for", lang)

    if lang == "ko":
        # from konlpy.tag import Mecab
        # tokenizer = Mecab()
        from hangul.tokenizer import WordSegmenter
        tokenizer = WordSegmenter()
    elif lang == "ja":
        import fugashi
        tokenizer = fugashi.Tagger()
        # import Mykytea
        # opt = "-model jp-0.4.7-1.mod"
        # tokenizer = Mykytea.Mykytea(opt)
    elif lang == "zh_cn" or lang == "zh":
        # import Mykytea
        # opt = "-model ctb-0.4.0-1.mod"
        # tokenizer = Mykytea.Mykytea(opt)
        # import jieba
        # tokenizer = jieba
        import spacy
        tokenizer = spacy.load("zh_core_web_md", exclude=["tagger", "ner", "parser"])
    elif lang == "zh_tw":
        import jieba
        tokenizer = jieba
    elif lang == "vi":
        from pyvi import ViTokenizer
        tokenizer = ViTokenizer
    elif lang == "th":
        from pythainlp.tokenize import word_tokenize
        tokenizer = word_tokenize
    elif lang == "ar":
        import pyarabic.araby as araby
        tokenizer = araby
    # elif lang=="en":
    #     from nltk import word_tokenize
    #     tokenizer = word_tokenize
    else:
        from nltk.tokenize import ToktokTokenizer
        tokenizer = ToktokTokenizer()

    tokenizers[lang] = tokenizer

    return tokenizer


def word_segment(sentence, lang):
    """Segment sentence into tokens
    
    Args:
        sentence: sentence
        lang: language code string
        
    Returns:
        token list
    """
    tokenizer = _get_tokenizer(lang)
    if lang == 'ko':
        # words = [word for word, _ in tokenizer.pos(sent)]
        tokenizer.inputAsString(sentence)
        tokenizer.doSegment()
        toks = tokenizer.segmentedOutput
        words = toks.split()
    elif lang == 'ja':
        # words = [elem for elem in tokenizer.getWS(sent)]
        words = [word.surface for word in tokenizer(sentence)]
    elif lang == 'th':
        words = tokenizer(sentence, engine='mm')
    elif lang == 'vi':
        words = tokenizer.tokenize(sentence).split()
    elif lang == 'zh_cn' or lang == "zh":
        # words = [elem for elem in tokenizer.getWS(sent)]
        # words = list(tokenizer.cut(sent, cut_all=False))
        doc = tokenizer(sentence)
        words = [t.text for t in doc]
    elif lang == "zh_tw":
        words = list(tokenizer.cut(sentence, cut_all=False))
    elif lang == "ar":
        words = tokenizer.tokenize(sentence)
    # elif lang=="en":
    #     words = tokenizer(sent)
    else:  # Most european languages
        sentence = re.sub("([A-Za-z])(\.[ .])", r"\1 \2", sentence)
        words = tokenizer.tokenize(sentence)

    return words


def split_sentences(text, lang="en"):
    """Segment paragraph into sentences

    Args:
        text: paragraph string
        lang: language code string

    Returns:
        list of sentences
    """
    languages_splitter = ["ca", "cs", "da", "de", "el", "en", "es", "fi", "fr", "hu", "is", "it",
                          "lt", "lv", "nl", "no", "pl", "pt", "ro", "ru", "sk", "sl", "sv", "tr"]
    languages_indic = ["as", "bn", "gu", "hi", "kK", "kn", "ml", "mr", "ne", "or", "pa", "sa",
                       "sd", "si", "ta", "te"]
    languages_pysbd = ["en", "hi", "mr", "zh", "es", "am", "ar", "hy", "bg", "ur", "ru", "pl",
                       "fa", "nl", "da", "fr", "my", "el", "it", "ja", "de", "kk", "sk"]

    languages = languages_splitter + languages_indic + languages_pysbd
    lang = lang if lang in languages else "en"

    text = text.strip()

    if lang in languages_pysbd:
        segmenter = pysbd.Segmenter(language=lang, clean=True)
        sentences = segmenter.segment(text)
    elif lang in languages_splitter:
        sentences = split_text_into_sentences(text, lang)
    elif lang in languages_indic:
        sentences = sentence_split(text, lang)

    return sentences


def paragraph_tokenizer(text, lang="en"):
    """Replace sentences with their indexes, and store indexes of newlines
    Args:
        text (str): Text to be indexed

    Returns:
        sentences (list): List of sentences
        breaks (list): List of indexes of sentences and newlines
    """
    text = text.strip()
    paragraphs = text.splitlines(True)

    breaks = []
    sentences = []

    for paragraph in paragraphs:
        if paragraph == "\n":
            breaks.append("\n")
        else:
            paragraph_sentences = split_sentences(paragraph, lang)

            breaks.extend(
                list(range(len(sentences), +len(sentences) + len(paragraph_sentences)))
            )
            breaks.append("\n")
            sentences.extend(paragraph_sentences)

    # Remove the last newline
    breaks = breaks[:-1]

    return sentences, breaks


def paragraph_detokenizer(sentences, breaks):
    """Restore original paragraph format from indexes of sentences and newlines

    Args:
        sentences (list): List of sentences
        breaks (list): List of indexes of sentences and newlines

    Returns:
        text (str): Text with original format
    """
    output = []

    for br in breaks:
        if br == "\n":
            output.append("\n")
        else:
            output.append(sentences[br] + " ")

    text = "".join(output)
    return text


def may_combine_paragraph(text):
    paragraphs = text.split("\n")
    txt = ""
    i = 0
    while i < len(paragraphs):
        p = paragraphs[i].strip()
        i += 1
        if len(p) == 0:  # blank paragraph
            txt = txt + "\r\n"
        else:
            txt = txt + " " + p

    return txt
