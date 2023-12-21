"""PDF file translation"""
import argparse
import os
import re
import fitz

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBoxHorizontal, LTTextLine, LTChar
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Frame, KeepInFrame
from yimt.api.utils import detect_lang

pdfmetrics.registerFont(TTFont('SimSun', os.path.join(os.path.dirname(__file__), 'SimSun.ttf')))
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(fontName='SimSun', name='Song', fontSize=9, wordWrap='CJK'))


p_chars_lang_independent = re.compile(r"[0123456789+\-*/=~!@$%^()\[\]{}<>\|,\.\?\"]")

p_en_chars = re.compile(r"[a-zA-Z]+")
pdf_progress = ""


font_size_list = []
dimlimit = 0  # 100  # each image side must be greater than this
relsize = 0  # 0.05  # image : image size ratio must be larger than this (5%)
abssize = 0  # 2048  # absolute image size limit 2 KB: ignore if smaller
imgdir = "output"  # found images are stored in this subfolder

if not os.path.exists(imgdir):  # make subfolder if necessary
    os.mkdir(imgdir)


def recoverpix(doc, item):
    xref = item[0]  # xref of PDF image
    smask = item[1]  # xref of its /SMask

    # special case: /SMask or /Mask exists
    if smask > 0:
        pix0 = fitz.Pixmap(doc.extract_image(xref)["image"])
        if pix0.alpha:  # catch irregular situation
            pix0 = fitz.Pixmap(pix0, 0)  # remove alpha channel
        mask = fitz.Pixmap(doc.extract_image(smask)["image"])

        try:
            pix = fitz.Pixmap(pix0, mask)
        except:  # fallback to original base image in case of problems
            pix = fitz.Pixmap(doc.extract_image(xref)["image"])

        if pix0.n > 3:
            ext = "pam"
        else:
            ext = "png"

        return {  # create dictionary expected by caller
            "ext": ext,
            "colorspace": pix.colorspace.n,
            "image": pix.tobytes(ext),
        }

    # special case: /ColorSpace definition exists
    # to be sure, we convert these cases to RGB PNG images
    if "/ColorSpace" in doc.xref_object(xref, compressed=True):
        pix = fitz.Pixmap(doc, xref)
        pix = fitz.Pixmap(fitz.csRGB, pix)
        return {  # create dictionary expected by caller
            "ext": "png",
            "colorspace": 3,
            "image": pix.tobytes("png"),
        }
    return doc.extract_image(xref)


def extract_draw_save(translate_file, translated_file=None):
    if translated_file is None:
        paths = os.path.splitext(translate_file)
        translated_fn = paths[0] + "-translated" + paths[1]
    else:
        translated_fn = translated_file

    doc = fitz.open(translate_file)
    page_count = doc.page_count
    outpdf = fitz.open(translated_fn)
    for i in range(page_count):
        page = doc[i]
        paths = page.get_drawings()  # extract existing drawings

        outpage = outpdf[i]
        shape = outpage.new_shape()  # make a drawing canvas for the output page
        # define some output page with the same dimensions
        # --------------------------------------
        # loop through the paths and draw them
        # --------------------------------------
        for path in paths:
            # ------------------------------------
            # draw each entry of the 'items' list
            # ------------------------------------
            for item in path["items"]:  # these are the draw commands
                if item[0] == "l":  # line
                    shape.draw_line(item[1], item[2])
                elif item[0] == "re":  # rectangle
                    shape.draw_rect(item[1])
                elif item[0] == "qu":  # quad
                    shape.draw_quad(item[1])
                elif item[0] == "c":  # curve
                    shape.draw_bezier(item[1], item[2], item[3], item[4])
                else:
                    raise ValueError("unhandled drawing", item)
            # ------------------------------------------------------
            # all items are drawn, now apply the common properties
            # to finish the path
            # ------------------------------------------------------
            shape.finish(
                fill=path["fill"],  # fill color
                color=path["color"],  # line color
                dashes=path["dashes"],  # line dashing
                even_odd=path.get("even_odd", True),  # control color of overlaps
                closePath=path["closePath"],  # whether to connect last and first point
                lineJoin=path["lineJoin"],  # how line joins should look like
                lineCap=max(path["lineCap"]),  # how line ends should look like
                width=path["width"],  # line width
                stroke_opacity=path.get("stroke_opacity", 1),  # same value for both
                fill_opacity=path.get("fill_opacity", 1),  # opacity parameters
            )
        shape.commit()
    return outpdf


def extract_img_save(translate_file, translated_file):
    if translated_file is None:
        paths = os.path.splitext(translate_file)
        translated_fn = paths[0] + "-translated" + paths[1]
    else:
        translated_fn = translated_file
    doc = fitz.open(translate_file)
    page_count = doc.page_count  # number of pages
    doc_new = fitz.open(translated_fn)

    xreflist = []
    imglist = []
    for pno in range(page_count):
        page = doc[pno]
        il = doc.get_page_images(pno)
        # print(il)
        imglist.extend([x[0] for x in il])
        for img in il:
            xref = img[0]
            img_rect = page.get_image_rects(xref)
            # print(img_rect)
            if xref in xreflist:
                continue
            width = img[2]
            height = img[3]
            if min(width, height) <= dimlimit:
                continue
            image = recoverpix(doc, img)
            n = image["colorspace"]
            imgdata = image["image"]

            if len(imgdata) <= abssize:
                continue
            if len(imgdata) / (width * height * n) <= relsize:
                continue

            # imgfile = os.path.join(imgdir, "img%05i.%s" % (xref, image["ext"]))
            # print(imgfile)
            # fout = open(imgfile, "wb")
            # fout.write(imgdata)
            # fout.close()
            xreflist.append(xref)
            doc_new[pno].insert_image(rect=img_rect[0], stream=imgdata)

    imglist = list(set(imglist))
    # print(len(set(imglist)), "images in total")
    # print(imglist)
    # print(len(xreflist), "images extracted")
    # print(xreflist)
    return doc_new


def get_fontsize(block):
    for line in block:
        if isinstance(line, LTTextLine):
            for char in line:
                if isinstance(char, LTChar):
                    return char.size


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


def print_to_canvas(t, x, y, w, h, c, ft):
    if h < 24:
        h = 24
    if w < 24:
        w = 24
    frame = Frame(x, y, w, h, showBoundary=0)

    if ft not in font_size_list:
        font_size_list.append(ft)
        styles.add(ParagraphStyle(fontName='SimSun', name='Song' + str(ft), fontSize=ft, wordWrap='CJK'))
    story = [Paragraph(t, styles['Song' + str(ft)])]
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
                ft = get_fontsize(element)
                print(t)
                t = preprocess_txt(t)
                block = (x, y, w, h, t)

                if w < 9 or h < 9:
                    print("***TooSmall", block)
                    # print_to_canvas(t, x, y, 11, 11, pdf, ft)
                    print_to_canvas(t, x, y, w, h, pdf, ft)
                    continue

                print("***Translate", block)

                # translate and print
                if translator is None:
                    if source_lang == "auto":
                        source_lang = detect_lang(t)

                    if source_lang == "en" and not should_translate_en(t):
                        print("***Skipping", block)
                        print_to_canvas(t, x, y, w, h, pdf, ft)
                        continue

                    from yimt.api.translators import Translators
                    translator = Translators().get_translator(source_lang, target_lang)

                translation = translator.translate_paragraph(t)
                print_to_canvas(translation, x, y, w, h, pdf, ft)
                # print_to_canvas(t, x, y, w, h, pdf, ft)

        pdf.showPage()
        p += 1

    pdf.save()

    pdf_progress = ""

    tf_draw = extract_draw_save(pdf_fn, translated_fn)
    print(type(tf_draw))

    tf_draw.saveIncr()
    translated_file = extract_img_save(pdf_fn, tf_draw)

    translated_file.saveIncr()

    return translated_file.name


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
