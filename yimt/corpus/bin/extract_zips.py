"""Extract OPUS zip files"""
import argparse

from yimt.corpus.utils import extract_zips, extract_gzips

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--dir", type=str, required=True, help="zip file dir")
    argparser.add_argument("--output", type=str, default=None, help="output dir")
    argparser.add_argument("--format", type=str, default="zip", help="compression format")
    args = argparser.parse_args()

    if args.format == "zip":
        extract_zips(args.dir, args.output)
    elif args.format == "gz":
        extract_gzips(args.dir, args.output)
