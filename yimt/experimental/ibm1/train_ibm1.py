import pickle

from nltk import AlignedSent, IBMModel1


def get_bitext(tok_fn):
    bitext = []

    with open(tok_fn, encoding="utf-8") as f:
        for line in f:
            pair = line.strip().split("\t")
            src = pair[0].split()
            tgt = pair[1].split()

            bitext.append(AlignedSent(tgt, src))

    return bitext


def train_ibm1(tok_fn, outpu_fn=None):
    corpus = get_bitext(tok_fn)

    print("Training...")
    ibm1 = IBMModel1(corpus, 10)

    print(len(ibm1.src_vocab), len(ibm1.trg_vocab))

    print("Converting translation table...")
    t_table = {}
    for t, sources in ibm1.translation_table.items():
        for s, p in sources.items():
            if s not in t_table:
                t_table[s] = {}
            t_table[s][t] = p

    print("Saving...")

    if outpu_fn is None:
        outpu_fn = tok_fn + ".ibm1"

    md = [ibm1.src_vocab, ibm1.trg_vocab, t_table]
    with open(outpu_fn, "wb") as f:
        pickle.dump(md, f)


if __name__ == "__main__":
    train_ibm1("../weiber-cmn.txt.tok")
