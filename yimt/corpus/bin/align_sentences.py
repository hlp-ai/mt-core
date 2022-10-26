import sys

from yimt.corpus.aligner import SentenceEmbeddingAligner


def get_paragraph_pair(in_fn):
    paragraphs = open(in_fn, encoding="utf-8").readlines()
    paragraphs = [p.strip() for p in paragraphs]
    paragraphs = list(filter(lambda p:len(p)>0, paragraphs))
    assert len(paragraphs) % 2 == 0

    src_p = paragraphs[0::2]
    tgt_p = paragraphs[1::2]

    return src_p, tgt_p


if __name__ == "__main__":
    in_fn = sys.argv[1]
    out_fn = sys.argv[2]

    src_p, tgt_p = get_paragraph_pair(in_fn)

    out_f = open(out_fn, "a", encoding="utf-8")

    aligner = SentenceEmbeddingAligner();
    align = aligner.align(src_p, tgt_p)
    for a in align:
        out_f.write(a[0] + "\t" + a[1] + "\n")
