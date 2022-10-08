import sys

from yimt.corpus.bin import filter_score, score_bitext


def process(raw_filter_path, min_score):
    path_s = raw_filter_path + "-s"
    path_sf = raw_filter_path + "-sf"

    print("Scoring {} into {}...".format(raw_filter_path, path_s))
    score_bitext.main(raw_filter_path, path_s)
    print()

    print("Filtering-by-socre {} into {}...".format(path_s, path_sf))
    filter_score.main(path_s, path_sf, min_score)
    print()


if __name__ == "__main__":
    path_pattern = sys.argv[1]
    from_no = int(sys.argv[2])
    to_no = int(sys.argv[3])
    min_score = float(sys.argv[4])

    for i in range(from_no, to_no):
        p = path_pattern.format(i)
        process(p, min_score)
