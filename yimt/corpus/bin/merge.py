"""Merge files in a directory into a file"""
import argparse
from yimt.corpus.utils import merge


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("in_dir")
    parser.add_argument("out_fn")
    args = parser.parse_args()

    merge(args.in_dir, args.out_fn)
