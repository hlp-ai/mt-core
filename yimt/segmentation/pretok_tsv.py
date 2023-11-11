import argparse
from tqdm import tqdm

from yimt.segmentation.text_splitter import word_segment


def pretokenize_tsv(corpus_fn, lang1=None, lang2=None, out=None):
    assert lang1 is not None or lang2 is not None

    if out is None:
        tok_fn = corpus_fn + ".pretok"
    else:
        tok_fn = out

    if lang1 is not None:
        tok_fn += "-" + lang1
    if lang2 is not None:
        tok_fn += "-" + lang2

    with open(corpus_fn, encoding="utf-8") as f, open(tok_fn, "w", encoding="utf-8") as out:
        for line in tqdm(f):
            pair = line.strip().split("\t")
            if len(pair) != 2:
                continue
            src, tgt = pair

            if lang1:
                src = " ".join(word_segment(src, lang1))
            if lang2:
                tgt = " ".join(word_segment(tgt, lang2))

            out.write(src + "\t" + tgt + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tsv_file", required=True, help="bitext file")
    parser.add_argument("--sl", default=None, help="Source language")
    parser.add_argument("--tl", default=None, help="Target language")
    parser.add_argument("--out", default=None, help="Segemented output file")
    args = parser.parse_args()

    pretokenize_tsv(args.tsv_file, args.sl, args.tl, args.out)
