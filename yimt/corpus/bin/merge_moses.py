import argparse

from yimt.corpus.utils import merge_moses

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--in_dir", type=str, required=True, help="input dir")
    argparser.add_argument("--output", type=str, default=None, help="output dir")
    argparser.add_argument("--src_lang", type=str, default=None, help="source language")
    argparser.add_argument("--tgt_lang", type=str, default=None, help="target language")
    args = argparser.parse_args()

    merge_moses(args.in_dir, args.src_lang, args.tgt_lang, args.output)
