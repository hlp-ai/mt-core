import argparse
import io

from yimt.api.utils import get_logger
from yimt.corpus.filters import JK2ZhFilter, LatinZhFilter


def main(in_path, out_path, from_lang):
    in_f = io.open(in_path, encoding="utf-8")
    out_f = io.open(out_path, "w", encoding="utf-8")

    logger = get_logger("filter")

    if from_lang == "latin":
        filters = [LatinZhFilter()]
    else:
        filters = [JK2ZhFilter()]

    print(filters)

    total = 0
    passed = 0

    for line in in_f:
        total += 1
        if total % 10000 == 0:
            print("# pairs:", total, "# valid pairs:", passed)
        line = line.strip()
        cols = line.split("\t")
        if len(cols) >= 2:
            src, tgt = cols[:2]
        else:
            logger.debug("NO Pair: {}".format(line))
            continue

        valid = True
        for f in filters:
            if f.filter(src, tgt) is None:
                logger.debug("{}: {}".format(f.__class__, line))
                valid = False
                break
        if valid:
            passed += 1
            out_f.write(line + "\n")

    print("# pairs:", total, "# valid pairs:", passed)
    out_f.close()


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("in_fn")
    argparser.add_argument("out_fn")
    argparser.add_argument("from_lang", default="latin")
    args = argparser.parse_args()

    fn = args.in_fn
    out_fn = args.out_fn

    main(fn, out_fn, args.from_lang)
