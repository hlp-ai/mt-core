import sys

from yimt.corpus.bitext_scorers import LaBSEScorer


def main(in_path, out_path):
    scorer = LaBSEScorer("D:/kidden/mt/open/mt-ex/mt/data/labse1", 48)

    srcs = []
    tgts = []
    n_buf = 8  # consume GPU very much
    cnt = 0
    with open(in_path, encoding="utf-8") as in_f, open(out_path, "w", encoding="utf-8") as out_f:
        lines = in_f.readlines()
        print("# of lines:", len(lines))
        for line in lines:
            line = line.strip()
            pair = line.split("\t")
            src = pair[0]
            tgt = pair[1]

            if len(srcs) < n_buf:
                srcs.append(src)
                tgts.append(tgt)
            else:
                ss = scorer.score(srcs, tgts)
                for i in range(len(ss)):
                    out_f.write("{:.4f}\t{}\t{}\n".format(ss[i], srcs[i], tgts[i]))
                srcs.clear()
                tgts.clear()
                print(cnt)

            cnt += 1

        if len(srcs) > 0:
            ss = scorer.score(srcs, tgts)
            for i in range(len(ss)):
                out_f.write("{:.4f}\t{}\t{}\n".format(ss[i], srcs[i], tgts[i]))
        print(cnt)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])