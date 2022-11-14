import argparse

from yimt.corpus.tokenize_file import detok_zh

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--input", type=str, required=True, help="input file")
    argparser.add_argument("--output", type=str, default=None, help="output file")
    args = argparser.parse_args()

    corpus_fn = args.input
    out_fn = args.output

    detok_zh(corpus_fn, out_fn)
