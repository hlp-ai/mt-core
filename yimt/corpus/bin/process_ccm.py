from yimt.corpus import labse_scorer
from yimt.corpus.bin import normalize, dedup, filter_score


def process(cc_path, lang, min_score):
    cc_path_n = cc_path + "-n"
    cc_path_u = cc_path + "-u"
    cc_path_f = cc_path + "-f"
    cc_path_s = cc_path + "-s"
    cc_path_sf = cc_path + "-sf"

    print("Normalizing {} into {}...".format(cc_path, cc_path_n))
    normalize.main(cc_path, cc_path_n)
    print()

    print("Deduping {} into {}...".format(cc_path_n, cc_path_u))
    dedup.main(cc_path_n, cc_path_u)
    print()

    print("Filtering {} into {}...".format(cc_path_u, cc_path_f))
    filter.main(cc_path_u, cc_path_f, lang)
    print()

    print("Scoring {} into {}...".format(cc_path_f, cc_path_s))
    labse_scorer.main(cc_path_f, cc_path_s)
    print()

    print("Filtering-by-socre {} into {}...".format(cc_path_s, cc_path_sf))
    filter_score.main(cc_path_s, cc_path_sf, min_score)
    print()


if __name__ == "__main__":
    cc_path_pattern = r"D:\kidden\mt\open-mt-data\en-zh\ccm1\f\CCMatrix.en-zh-{}.tsv"
    # cc_path_pattern = r"D:\kidden\mt\open-mt-data\ja-zh\ccm1\CCMatrix.ja-zh-{}.tsv"
    # cc_path_pattern = r"D:\kidden\mt\open-mt-data\fr-zh\all\tsv\ccwiki\ccwiki-{}.tsv"
    lang = "en-zh"
    min_score = 0.70
    from_no = 67
    to_no = 70

    for i in range(from_no, to_no):
        cc_p = cc_path_pattern.format(i)
        process(cc_p, lang, min_score)
