import argparse

from yimt.corpus.tokenize_file import tokenize_single

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("in_fn")
    argparser.add_argument("lang")
    argparser.add_argument("out_fn")
    args = argparser.parse_args()

    tokenize_single(args.in_fn, args.lang, args.out_fn)
