"""Normalize bitext"""
import argparse
import io

from yimt.corpus.normalizers import ToZhNormalizer, NoZhNormalizer


def main(in_path, out_path, nozh=False):
    in_f = io.open(in_path, encoding="utf-8")
    out_f = io.open(out_path, "w", encoding="utf-8")

    normalizers = [ToZhNormalizer()]
    if nozh:
        normalizers = [NoZhNormalizer()]

    print(normalizers)

    cnt = 0
    for line in in_f:
        line = line.strip()
        if len(line) == 0:
            continue
        pair = line.split("\t")
        if len(pair) != 2:
            print(line)
            continue
        for normalizer in normalizers:
            if len(line.strip()) == 0:
                continue
            line = normalizer.normalize(line)

        out_f.write(line + "\n")

        cnt += 1
        if cnt % 100000 == 0:
            print(cnt)

    print(cnt)
    out_f.close()


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--input", required=True, help="Input file path")
    argparser.add_argument("--output", required=True, help="Ouput file path")
    argparser.add_argument("--nozh", default=False, action="store_true", help="Non-Chinese")
    args = argparser.parse_args()

    main(args.input, args.output, args.nozh)
