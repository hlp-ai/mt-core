import sys

from yimt.corpus.utils import diff

if __name__ == "__main__":
    f1 = sys.argv[1]
    f2 = sys.argv[2]
    out = sys.argv[3]

    diff(f1, f2, out, "SRC")
