import argparse

from yimt.corpus.tokenize_file import tokenize_tsv


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tsv_file", required=True, help="bitext file")
    parser.add_argument("--from_lang", required=True, help="Source language")
    parser.add_argument("--to_lang", default="zh", help="Target language")
    parser.add_argument("--out", default=None, help="Segemented output file")
    parser.add_argument("--max", type=int, default=None, help="Max number of sentences to be used")
    args = parser.parse_args()

    tokenize_tsv(args.tsv_file, args.from_lang, args.to_lang, args.out, max_sentences=args.max)
