"""Combine two files with different language into one TSV file"""
import argparse
import os

from yimt.utils.misc import single_to_pair

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("src_fn")
    parser.add_argument("tgt_fn")
    parser.add_argument("out_fn")
    args = parser.parse_args()

    src_fn = args.src_fn
    tgt_fn = args.tgt_fn
    out_fn = args.out_fn

    out_path = os.path.dirname(out_fn)
    if not os.path.exists(out_path):
        os.makedirs(out_path, exist_ok=True)

    single_to_pair(src_fn, tgt_fn, out_fn)

