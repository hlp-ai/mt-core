import sys

from yimt.corpus.tokenize_file import tokenize_tsv


if __name__ == "__main__":
    fn = sys.argv[1]
    lang1 = sys.argv[2]

    if len(sys.argv) > 3:
        max_sentences = int(sys.argv[3])

    tokenize_tsv(fn, lang1, max_sentences=max_sentences)
