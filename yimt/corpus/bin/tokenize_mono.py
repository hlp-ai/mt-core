import argparse

from yimt.corpus.tokenize_file import tokenize_single

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--input", required=True, help="Input file path")
    argparser.add_argument("--lang", default="zh", help="language for input text")
    argparser.add_argument("--output", default=None, help="Output file path")
    args = argparser.parse_args()

    tokenize_single(args.input, args.lang, args.output)
