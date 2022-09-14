"""Convert sgm file of WMT into plain text"""
import argparse

from yimt.corpus.utils import from_sgm

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--input", type=str, required=True, help="input file")
    argparser.add_argument("--output", type=str, required=True, help="output file")
    args = argparser.parse_args()

    corpus_fn = args.input
    out_fn = args.output

    from_sgm(corpus_fn, out_fn)
