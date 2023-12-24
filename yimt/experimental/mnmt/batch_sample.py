import argparse
import os

from yimt.utils.misc import sample

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True, help="input directory")
    parser.add_argument("-n", "--num", type=int, default=50, help="num of samples sampled from each file")
    args = parser.parse_args()

    root = args.input
    files = os.listdir(root)
    files = [os.path.join(root, f) for f in files]

    for f in files:
        print("Sampling", f)
        sample([f], args.num)
