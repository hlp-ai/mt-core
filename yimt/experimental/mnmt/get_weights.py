import argparse

from yimt.experimental.mnmt.resample import resample_prob

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, help="monolingual files directory")
    parser.add_argument("--t", type=float, default=3.0, help="sampling temperature")
    args = parser.parse_args()

    root = args.root

    res = resample_prob(root, args.t)
    for r in res:
        print(r)
