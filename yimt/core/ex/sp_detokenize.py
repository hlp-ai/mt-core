"""Detokenize file into file"""
import argparse

from yimt.core.ex.sp import load_spm, detokenize_file

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("sp_model")
    argparser.add_argument("in_fn")
    argparser.add_argument("out_fn")
    args = argparser.parse_args()

    sp = load_spm(args.sp_model)
    detokenize_file(sp, args.in_fn, args.out_fn)
