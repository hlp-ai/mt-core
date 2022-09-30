import time

import numpy as np
from laserembeddings import Laser


class LaserScorer(object):
    """Filter based on similarity of pair with Laser sentence embedding"""
    laser = Laser()

    def __init__(self, lang1="en", lang2="zh"):
        self.lang1 = lang1
        self.lang2 = lang2

    def score(self, src, tgt):
        """

        :param src: string or list of string
        :param tgt: string or list of string
        :return:
        """
        if isinstance(src, str) and isinstance(tgt, str):
            src = [src]
            tgt = [tgt]
        assert len(src) == len(tgt)

        embeddings_src = self.laser.embed_sentences(src, lang=self.lang1)
        embeddings_tgt = self.laser.embed_sentences(tgt, lang=self.lang2)
        # print(embeddings_en.shape, embeddings_zh.shape)

        norms_en = [np.linalg.norm(embeddings_src[i]) for i in range(embeddings_src.shape[0])]
        # print(norms_en)
        norms_zh = [np.linalg.norm(embeddings_tgt[i]) for i in range(embeddings_tgt.shape[0])]
        # print(norms_zh)

        # sim = np.matmul(embeddings_en, embeddings_zh.T)
        sim = [np.dot(embeddings_src[i], embeddings_tgt[i]) for i in range(embeddings_src.shape[0])]
        # print(sim.shape)

        for i in range(len(norms_en)):
            sim[i] = sim[i] / (norms_en[i] * norms_zh[i])

        return sim


if __name__ == "__main__":
    scorer = LaserScorer()

    english_sentences = ["dog", "Puppies are nice.", "I enjoy taking long walks along the beach with my dog."]
    chinese_sentences = ["狗", "小狗很好。", "我喜欢带着我的狗沿着海滩散步。"]

    start = time.time()
    print(scorer.score(english_sentences, chinese_sentences))
    print(time.time() - start)

    src1 = ["I enjoy taking long walks along the beach with my dog."] * 16
    tgt1 = ["我喜欢带着我的狗沿着海滩散步。"] * 16

    start = time.time()
    print(scorer.score(src1, tgt1))
    print(time.time() - start)

    src1 = ["I enjoy taking long walks along the beach with my dog."] * 32
    tgt1 = ["我喜欢带着我的狗沿着海滩散步。"] * 32

    start = time.time()
    print(scorer.score(src1, tgt1))
    print(time.time() - start)

    src1 = ["I enjoy taking long walks along the beach with my dog."] * 64
    tgt1 = ["我喜欢带着我的狗沿着海滩散步。"] * 64

    start = time.time()
    print(scorer.score(src1, tgt1))
    print(time.time() - start)

    src1 = ["I enjoy taking long walks along the beach with my dog."] * 128
    tgt1 = ["我喜欢带着我的狗沿着海滩散步。"] * 128

    start = time.time()
    print(scorer.score(src1, tgt1))
    print(time.time() - start)

    src1 = ["I enjoy taking long walks along the beach with my dog."] * 256
    tgt1 = ["我喜欢带着我的狗沿着海滩散步。"] * 256

    start = time.time()
    print(scorer.score(src1, tgt1))
    print(time.time() - start)
