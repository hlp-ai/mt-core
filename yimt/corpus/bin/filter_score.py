import sys


def main(in_path, out_path, min_score):
    with open(in_path, encoding="utf-8") as in_f, open(out_path, "w", encoding="utf-8") as out_f:
        lines = in_f.readlines()
        print(len(lines))
        records = [line.strip().split("\t") for line in lines]
        records = list(filter(lambda r: float(r[0]) > min_score, records))
        print(len(records))

        for r in records:
            out_f.write(r[1] + "\t" + r[2] + "\n")


if __name__ == "__main__":
    in_path = sys.argv[1]
    out_path = sys.argv[2]
    min_score = float(sys.argv[3])

    main(in_path, out_path, min_score)
