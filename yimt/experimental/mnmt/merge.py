"""将一个目录下的文件合并成一个文件"""
import argparse
import os

from tqdm import tqdm


def merge(source, out_fn):
    files = os.listdir(source)
    files = [os.path.join(source, f) for f in files]

    with open(out_fn, "w", encoding="utf-8") as out:
        for fn in files:
            with open(fn, encoding="utf-8") as f:
                print("Merging", fn)
                for line in tqdm(f):
                    out.write(line.strip() + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True, help="input directory")
    parser.add_argument("-o", "--output", required=True, help="output file")
    args = parser.parse_args()

    merge(args.input, args.output)
