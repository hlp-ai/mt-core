import argparse
import io

from yimt.api.utils import get_logger
from yimt.corpus.filters import SameFilter, OverlapFilter, LengthFilter, \
    EmptyFilter, AlphabetRatioFilter, CharacterRatioFilter, ASCIIRatioFilter, AugumentForZhFilter


def main(in_path, out_path, lang_pair):
    in_f = io.open(in_path, encoding="utf-8")
    out_f = io.open(out_path, "w", encoding="utf-8")

    logger = get_logger("filter")

    src_lang, tgt_lang = lang_pair.split("-")

    if src_lang == "ja" or src_lang == "zh" or src_lang == "ko":
        src_len = LengthFilter.char_len_f
    else:
        src_len = LengthFilter.space_sep_len_f

    if tgt_lang == "ja" or tgt_lang == "zh" or tgt_lang == "ko":
        tgt_len = LengthFilter.char_len_f
    else:
        tgt_len = LengthFilter.space_sep_len_f

    filters = [EmptyFilter(),
               SameFilter(),
               # ASCIIRatioFilter(threshold=0.8),
               LengthFilter(src_len, tgt_len, (2, 200), (2, 200), ratio=4),
               OverlapFilter(),
               AlphabetRatioFilter(threshold=0.5, exclude_whitespace=True),
               #AugumentForZhFilter()
               ]
               # CharacterRatioFilter(scripts=(script_src, script_tgt), thresholds=(0.33, 0.33))]

    if tgt_lang == "ja" or tgt_lang == "zh" or tgt_lang == "ko":
        filters.append(ASCIIRatioFilter())

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
    argparser.add_argument("lang_pair", default="en-zh")
    args = argparser.parse_args()

    fn = args.in_fn
    out_fn = args.out_fn

    main(fn, out_fn, args.lang_pair)
