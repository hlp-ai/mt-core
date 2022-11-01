import pickle


class IBM1:

    def __init__(self, model_dir):
        with open(model_dir, "rb") as f:
            self.src_vocab, self.tgt_vocab, self.t_table = pickle.load(f)

        print(len(self.src_vocab), len(self.tgt_vocab))

    def lookup(self, w, topk=3):
        if w not in self.src_vocab:
            return None
        else:
            tt = [(t, p) for t, p in self.t_table[w].items()]
            tt = sorted(tt, reverse=True, key=lambda r: r[1])
            return tt[:topk]


if __name__ == "__main__":
    ibm1 = IBM1("../weiber-cmn.txt.tok.ibm1")

    while True:
        w = input("input word: ")
        trans = ibm1.lookup(w)
        if trans is None:
            print("not exist")
        else:
            print(trans)



