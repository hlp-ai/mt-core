"""Sample some lines from corpus"""
import argparse

from yimt.utils.misc import sample

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", type=str, nargs="+", required=True, help="one or two files to be sampled")
    parser.add_argument("--num", type=int,required=True, help="the number of samples to be sampled")
    args = parser.parse_args()

    inputs = args.inputs
    sample_num = args.num

    if len(inputs) > 2:
        raise ValueError("Parallel corpus have at most two files.")

    sample(inputs, sample_num)
