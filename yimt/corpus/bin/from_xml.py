"""Convert XML file of WMT into plain text"""
import argparse

from yimt.corpus.utils import from_xml

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--input", type=str, required=True, help="input file")
    args = argparser.parse_args()

    corpus_fn = args.input

    from_xml(corpus_fn)
