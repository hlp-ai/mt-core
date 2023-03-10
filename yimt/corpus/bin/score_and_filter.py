import sys

from yimt.corpus.bin import filter_score, score_bitext


def process(raw_filter_path, min_score, model_path, block):
    path_s = raw_filter_path + ".score"
    path_sf = raw_filter_path + ".sfilter"

    print("Scoring {} into {}...".format(raw_filter_path, path_s))
    score_bitext.main(raw_filter_path, path_s, model_path, block)
    print()

    print("Filtering-by-socre {} into {}...".format(path_s, path_sf))
    filter_score.main(path_s, path_sf, min_score)
    print()


if __name__ == "__main__":
    path_pattern = sys.argv[1]
    from_no = int(sys.argv[2])
    to_no = int(sys.argv[3])
    min_score = float(sys.argv[4])
    model_path = sys.argv[5]
    block = int(sys.argv[6])

    for i in range(from_no, to_no):
        p = path_pattern.format(i)
        process(p, min_score, model_path, block)
