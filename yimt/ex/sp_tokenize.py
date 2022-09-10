"""Tokenize file with SentencePiece"""
import argparse

from yimt.ex.sp import load_spm, tokenize_file

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("sp_model")
    argparser.add_argument("in_fn")
    argparser.add_argument("out_fn")
    args = argparser.parse_args()

    sp = load_spm(args.sp_model)
    tokenize_file(sp, args.in_fn, args.out_fn)
