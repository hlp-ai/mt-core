"""PDF file translation"""
import argparse
import os
import re

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBoxHorizontal
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Frame, KeepInFrame
from yimt.api.utils import detect_lang
pdf_progress = ""
pdfmetrics.registerFont(TTFont('SimSun', os.path.join(os.path.dirname(__file__), 'SimSun.ttf')))
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(fontName='SimSun', name='Song', fontSize=9, wordWrap='CJK'))


p_chars_lang_independent = re.compile(r"[0123456789+\-*/=~!@$%^()\[\]{}<>\|,\.\?\"]")

p_en_chars = re.compile(r"[a-zA-Z]+")
pdf_progress = ""

def remove_lang_independent(t):
    return re.sub(p_chars_lang_independent, "", t)


def has_en_char(t):
    return re.search(p_en_chars, t) is not None


def should_translate_en(txt):
    if not has_en_char(txt):
        return False

    tokens = txt.split()

    def is_translatable(token):
        if len(token) == 1:
            return False
        token = remove_lang_independent(token)
        if len(token) <= 1:
            return False

        # en_zh_word_translator = WordTranslator("en", "zh_cn")
        # if not en_zh_word_translator.has(token):
        #     return False

        return True

    return any(list(map(is_translatable, tokens)))


def preprocess_txt(t):
    return t.replace("-\n", "").replace("\n", " ").replace("<", "&lt;").strip()


def print_to_canvas(t, x, y, w, h, c):
    if h < 24:
        h = 24
    if w < 24:
        w = 24
    frame = Frame(x, y, w, h, showBoundary=0)

    story = [Paragraph(t, styles['Song'])]
    story_inframe = KeepInFrame(w, h, story)
    frame.addFromList([story_inframe], c)


def translate_pdf_auto(pdf_fn, source_lang="auto", target_lang="zh", translation_file=None):
    if translation_file is None:
        paths = os.path.splitext(pdf_fn)
        translated_fn = paths[0] + "-translated" + paths[1]
    else:
        translated_fn = translation_file

    translator = None

    pdf = canvas.Canvas(translated_fn)
    p = 1
    global pdf_progress  #######
    pdf_progress = ""
    for page_layout in extract_pages(pdf_fn):  # for each page in pdf file
        print("*"*20, "Page", p, "*"*20, "\n")
        pdf_progress = "#" * p
        for element in page_layout:
            if isinstance(element, LTTextBoxHorizontal):
                x, y, w, h = int(element.x0), int(element.y0), int(element.width), int(element.height)
                t = element.get_text()
                print(t)
                t = preprocess_txt(t)
                block = (x, y, w, h, t)

                if w < 9 or h < 9:
                    print("***TooSmall", block)
                    print_to_canvas(t, x, y, 11, 11, pdf)
                    continue

                print("***Translate", block)

                # translate and print
                if translator is None:
                    if source_lang == "auto":
                        source_lang = detect_lang(t)

                    if source_lang == "en" and not should_translate_en(t):
                        print("***Skipping", block)
                        print_to_canvas(t, x, y, w, h, pdf)
                        continue

                    from yimt.api.translators import Translators
                    translator = Translators().get_translator(source_lang, target_lang)

                translation = translator.translate_paragraph(t)
                print_to_canvas(translation, x, y, w, h, pdf)

        pdf.showPage()
        p += 1

    pdf.save()
    pdf_progress = ""
    return translated_fn


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser("PDF File Translator")
    arg_parser.add_argument("--to_lang", type=str, default="zh", help="target language")
    arg_parser.add_argument("--input_file", type=str, required=True, help="file to be translated")
    arg_parser.add_argument("--output_file", type=str, default=None, help="translation file")
    args = arg_parser.parse_args()

    to_lang = args.to_lang
    in_file = args.input_file
    out_file = args.output_file

    translated_fn = translate_pdf_auto(in_file, target_lang=to_lang, translation_file=out_file)

    import webbrowser

    webbrowser.open(in_file)
    webbrowser.open(translated_fn)
