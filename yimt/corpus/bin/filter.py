import argparse

from yimt.api.text_splitter import word_segment
from yimt.corpus.filters import SameFilter, OverlapFilter, LengthFilter, \
    EmptyFilter, AlphabetRatioFilter, CharacterRatioFilter, ASCIIRatioFilter, AugumentForZhFilter


def main(in_path, out_path, lang_pair):
    src_lang, tgt_lang = lang_pair.split("-")

    if src_lang == "ja" or src_lang == "zh" or src_lang == "ko":
        src_len = LengthFilter.char_len_f
    elif src_lang == "th":
        src_len = lambda t: len(word_segment(t, lang="th"))
    else:
        src_len = LengthFilter.space_sep_len_f

    if tgt_lang == "ja" or tgt_lang == "zh" or tgt_lang == "ko":
        tgt_len = LengthFilter.char_len_f
    elif tgt_lang == "th":
        tgt_len = lambda t: len(word_segment(t, lang="th"))
    else:
        tgt_len = LengthFilter.space_sep_len_f

    filters = [EmptyFilter(),
               SameFilter(),
               # ASCIIRatioFilter(threshold=0.8),
               LengthFilter(src_len, tgt_len, (2, 256), (2, 256), ratio=4),
               OverlapFilter(),
               AlphabetRatioFilter(threshold=0.5, exclude_whitespace=True),
               #AugumentForZhFilter()
               ]
               # CharacterRatioFilter(scripts=(script_src, script_tgt), thresholds=(0.33, 0.33))]

    if tgt_lang == "ja" or tgt_lang == "zh" or tgt_lang == "ko" or tgt_lang == "th":
        filters.append(ASCIIRatioFilter(filter_tgt=True, filter_src=False))

    if src_lang == "ja" or src_lang == "zh" or src_lang == "ko" or src_lang == "th":
        filters.append(ASCIIRatioFilter(filter_tgt=False, filter_src=True))

    print(filters)

    total = 0
    passed = 0

    with open(in_path, encoding="utf-8") as in_f, open(out_path, "w", encoding="utf-8") as out_f, \
            open(in_path+".filtered", "w", encoding="utf-8") as filtered_f:
        for line in in_f:
            total += 1
            if total % 10000 == 0:
                print("# pairs:", total, "# valid pairs:", passed)
            line = line.strip()
            cols = line.split("\t")
            if len(cols) >= 2:
                src, tgt = cols[:2]
            else:
                # logger.debug("NO Pair: {}".format(line))
                filtered_f.write(line + "\n")
                continue

            valid = True
            for f in filters:
                if f.filter(src, tgt) is None:
                    # logger.debug("{}: {}".format(f.__class__, line))
                    filtered_f.write(line + "\n")
                    valid = False
                    break
            if valid:
                passed += 1
                out_f.write(line + "\n")

    print("# pairs:", total, "# valid pairs:", passed)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("in_fn")
    argparser.add_argument("out_fn")
    argparser.add_argument("lang_pair", default="en-zh")
    args = argparser.parse_args()

    fn = args.in_fn
    out_fn = args.out_fn

    main(fn, out_fn, args.lang_pair)
