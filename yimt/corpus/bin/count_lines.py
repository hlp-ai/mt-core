import sys

from yimt.corpus import utils

if __name__ == "__main__":
    corpus_fn = sys.argv[1]
    utils.count_lines(corpus_fn)
