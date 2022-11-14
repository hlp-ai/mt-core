from yimt.api.text_splitter import word_segment
from yimt.api.utils import detect_lang
from yimt.corpus.utils import is_ascii_char


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


def tokenize_tsv(corpus_fn, lang1, lang2="zh", out=None, max_sentences=None):
    if out is None:
        tok_fn = corpus_fn + ".seg"
    else:
        tok_fn = out

    with open(corpus_fn, encoding="utf-8") as f, open(tok_fn, "w", encoding="utf-8") as out:
        n = 0
        for line in f:
            pair = line.strip().split("\t")
            if len(pair) != 2:
                continue
            src, tgt = pair

            tokens_src = word_segment(src, lang1)
            tokens_src = [t.lower() for t in tokens_src]
            tokens_tgt = word_segment(tgt, lang2)

            out.write(" ".join(tokens_src) + "\t" + " ".join(tokens_tgt) + "\n")

            n += 1
            if n % 1000 == 0:
                print(n)
            if max_sentences is not None and n >= max_sentences:
                break
        print(n)


def detok_zh_str(s):
    result = ""
    i = 0
    while i < len(s):
        if s[i] == " ":
            if (i > 0 and is_ascii_char(s[i-1])) and (i < len(s)-1 and is_ascii_char(s[i+1])):
                result += " "
        else:
            result += s[i]
        i += 1

    return result


def detok_zh(in_file, out_file=None):
    if out_file is None:
        out_file = in_file + ".detok"

    outf = open(out_file, "w", encoding="utf-8")

    with open(in_file, encoding="utf-8") as inf:
        for line in inf:
            line = line.strip()
            line = detok_zh_str(line)
            outf.write(line + "\n")

    outf.close()
