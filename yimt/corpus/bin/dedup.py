"""Delete duplicate pairs from parallel corpus"""
import argparse

from yimt.corpus.utils import dedup

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--input", type=str, required=True, help="input file")
    argparser.add_argument("--output", type=str, required=True, help="output file")
    args = argparser.parse_args()

    corpus_fn = args.input
    out_fn = args.output

    dedup(corpus_fn, out_fn)
