"""Split a big corpus into a number of files with fixed length"""
import argparse

from yimt.corpus.utils import split

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", type=str, nargs="+", required=True, help="one or two files to be splitted")
    parser.add_argument("--num", type=int,required=True, help="the number of samples in each file")
    args = parser.parse_args()

    inputs = args.inputs
    sample_num = args.num

    if len(inputs) > 2:
        raise ValueError("Parallel corpus have at most two files.")

    split(inputs, sample_num)
