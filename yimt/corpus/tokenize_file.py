from yimt.api.text_splitter import word_segment
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


def tokenize_tsv(corpus_fn, lang1, lang2="zh"):
    tok_fn = corpus_fn + ".tok"

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
        print(n)
