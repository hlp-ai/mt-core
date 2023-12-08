import argparse
import os

from yimt.utils.misc import pair_to_single

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tsv_dir", required=True, help="tsv file dir")
    args = parser.parse_args()

    input = args.tsv_dir
    tsv_files = os.listdir(input)
    for f in tsv_files:
        i = f.index(".")
        name = f[:i]
        src, tgt = name.split("-")
        f = os.path.join(input, f)
        src_fn = f + "." + src
        tgt_fn = f + "." + tgt

        print(f, src_fn, tgt_fn)

        pair_to_single(f, src_fn, tgt_fn)
