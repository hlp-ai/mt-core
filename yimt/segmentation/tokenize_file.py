from yimt.segmentation.text_splitter import word_segment
from yimt.api.utils import detect_lang


def tokenize_single(in_fn, lang=None, out_fn=None):
    if out_fn is None:
        out_fn = in_fn + ".pretok"

    if lang is None:
        with open(in_fn, encoding="utf-8") as in_f:
            txt = in_f.read(128)
            lang = detect_lang(txt)
            print("Language detected:", lang)

    out_f = open(out_fn, "w", encoding="utf-8")
    n = 0
    with open(in_fn, encoding="utf-8") as in_f:
        for line in in_f:
            line = line.strip()
            toks = word_segment(line, lang=lang)
            out_f.write(" ".join(toks) + "\n")
            n += 1
            if n % 50000 == 0:
                print(n)
    print(n)
    out_f.close()

    return out_fn


if __name__ == "__main__":
    import argparse
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--input", required=True, help="Input file path")
    argparser.add_argument("--lang", default="zh", help="language for input text")
    argparser.add_argument("--output", default=None, help="Output file path")
    args = argparser.parse_args()

    tokenize_single(args.input, args.lang, args.output)

