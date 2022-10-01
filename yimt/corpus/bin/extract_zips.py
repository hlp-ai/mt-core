"""Extract OPUS zip files"""
import argparse

from yimt.corpus.utils import extract_zips


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--dir", type=str, required=True, help="zip file dir")
    argparser.add_argument("--output", type=str, default=None, help="output dir")
    args = argparser.parse_args()

    extract_zips(args.dir, args.output)
