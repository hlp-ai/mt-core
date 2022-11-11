import argparse
import pickle
import sys

from nltk import AlignedSent, IBMModel1


def get_bitext(tok_fn, revert=False):
    bitext = []

    with open(tok_fn, encoding="utf-8") as f:
        for line in f:
            pair = line.strip().split("\t")
            src = pair[0].split()
            tgt = pair[1].split()

            if not revert:
                bitext.append(AlignedSent(tgt, src))
            else:
                bitext.append(AlignedSent(src, tgt))

    return bitext


def train_ibm1(tok_fn, outpu_fn=None, iterations=5, revert=False, ntrans=None):
    corpus = get_bitext(tok_fn, revert)

    print("Training...")
    ibm1 = IBMModel1(corpus, iterations)

    print(len(ibm1.src_vocab), len(ibm1.trg_vocab))

    print("Converting translation table...")
    t_table = {}
    for t, sources in ibm1.translation_table.items():
        trans = zip(sources.values(), sources.keys())  # (prob, source)
        # if ntrans is not None:
        #     trans = sorted(trans, reverse=True)
        #     trans = trans[:ntrans]
        for p, s in trans:
            if s not in t_table:
                t_table[s] = {}
            t_table[s][t] = p

    t_table_s = {}
    for s, ts in t_table.items():
        tt = [(t, p) for t, p in ts.items()]
        tt = sorted(tt, reverse=True, key=lambda r: r[1])
        t_table_s[s] = tt[:ntrans]

    print("Saving...")

    if outpu_fn is None:
        outpu_fn = tok_fn + ".ibm1"

    md = [ibm1.src_vocab, ibm1.trg_vocab, t_table_s]
    with open(outpu_fn, "wb") as f:
        pickle.dump(md, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seg_file", required=True, help="Segmented file to train IBM1 model")
    parser.add_argument("--out", required=True, help="IBM1 model file")
    parser.add_argument("--iters", type=int, default=5, help="The number of iterations for training")
    parser.add_argument("--ntrans", type=int, default=None, help="The max number of translations for each word")
    parser.add_argument("--revert", action="store_true", default=True, help="Build backward IBM1 model")
    args = parser.parse_args()

    tok_fn = args.seg_file

    out_fn = args.out

    train_ibm1(tok_fn, out_fn, iterations=args.iters, ntrans=args.ntrans)
    if args.revert:
        train_ibm1(tok_fn, out_fn + "-r", iterations=args.iters, revert=True, ntrans=args.ntrans)
