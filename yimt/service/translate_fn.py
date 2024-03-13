import multiprocessing
from yimt.api.text_recognizer import TextRecognizers
from yimt.api.text_to_speech import Text2Speeches
from yimt.api.translators import translator_factory
from yimt.segmentation.text_splitter import may_combine_paragraph


recognizers = TextRecognizers()
synthesizers = Text2Speeches()
translators = translator_factory


def run_ocr(img, source_lang, queue):
    text = recognizers.recognize(img, source_lang)
    queue.put(text)


def run_tts(txt, lang, queue):
    audio, rate = synthesizers.synthesize(txt, lang)
    queue.put((audio, rate))


def tts_fn(txt, lang, process=False):
    if process:
        queue = multiprocessing.Queue()
        p = multiprocessing.Process(target=run_tts, args=(txt, lang, queue,))
        p.start()
        p.join()
        result = queue.get()
    else:
        result = synthesizers.synthesize(txt, lang)

    return result


def run_translate(src, source_lang, target_lang, queue):
    translator = translators.get_translator(source_lang, target_lang)
    if translator is None:
        return None

    src = may_combine_paragraph(src)
    translation = translator.translate_paragraph(src)
    queue.put(translation)


def translate_image_fn(img, source_lang, target_lang, process=False):
    if process:
        queue = multiprocessing.Queue()
        p = multiprocessing.Process(target=run_ocr, args=(img, source_lang, queue,))
        p.start()
        p.join()
        text = queue.get()
    else:
        text = recognizers.recognize(img, source_lang)

    if text is None:
        return None

    if process:
        queue = multiprocessing.Queue()
        p = multiprocessing.Process(target=run_translate, args=(text, source_lang, target_lang, queue,))
        p.start()
        p.join()
        translation = queue.get()
    else:
        translator = translators.get_translator(source_lang, target_lang)
        if translator is None:
            return None

        src = may_combine_paragraph(text)
        translation = translator.translate_paragraph(src)

    return text, translation
