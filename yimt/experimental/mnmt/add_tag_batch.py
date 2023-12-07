import argparse
import os

from yimt.experimental.mnmt.add_tag import add_token

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tsv_dir", required=True, help="tsv file dir")
    parser.add_argument("--to", default="tgt", type=str, help="add token to src or tag of tsv file")
    args = parser.parse_args()

    input = args.tsv_dir
    tosrc = True
    if args.to == "tgt":
        tosrc = False

    tsv_files = os.listdir(input)
    for f in tsv_files:
        i = f.index("-")
        lang = f[:i]
        token = "<to" + lang + ">"
        f = os.path.join(input, f)
        print(f, tosrc, token)
        add_token(f, tosrc, token)