import argparse
import re

from yimt.utils.misc import is_ascii_char, is_en_punct


def detok_zh_str(s):
    result = ""
    i = 0
    while i < len(s):
        if s[i] == " ":
            if (i > 0 and is_en_punct(s[i-1])) or (i < len(s)-1 and is_en_punct(s[i+1])):
                i += 1
                continue

            if (i > 0 and is_ascii_char(s[i-1])) and (i < len(s)-1 and is_ascii_char(s[i+1])):
                result += " "
        else:
            result += s[i]
        i += 1

    return result


def detok_zh_file(in_file, out_file=None):
    if out_file is None:
        out_file = in_file + ".detok"

    outf = open(out_file, "w", encoding="utf-8")

    with open(in_file, encoding="utf-8") as inf:
        for line in inf:
            line = line.strip()
            line = re.sub(r"\s{2,}", " ", line)
            line = line.strip()
            line = detok_zh_str(line)
            outf.write(line + "\n")

    outf.close()


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--input", type=str, required=True, help="input file")
    argparser.add_argument("--output", type=str, default=None, help="output file")
    args = argparser.parse_args()

    corpus_fn = args.input
    out_fn = args.output

    detok_zh_file(corpus_fn, out_fn)
