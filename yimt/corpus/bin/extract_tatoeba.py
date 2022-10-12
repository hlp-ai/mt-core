import sys

if __name__ == "__main__":
    in_fn = sys.argv[1]
    out_fn = sys.argv[2]

    tgt_lang = ["cmn_Hans", "cmn_Hant"]

    outf = open(out_fn, "w", encoding="utf-8")

    with open(in_fn, encoding="utf-8") as inf:
        for line in inf:
            line = line.strip()
            segs = line.split("\t")
            if segs[1] in tgt_lang:
                outf.write(segs[2] + "\t" + segs[3] + "\n")
