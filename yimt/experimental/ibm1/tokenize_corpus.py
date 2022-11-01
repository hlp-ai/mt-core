import sys

from yimt.api.text_splitter import word_segment


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


if __name__ == "__main__":
    fn = sys.argv[1]
    lang1 = sys.argv[2]

    tokenize_tsv(fn, lang1)
