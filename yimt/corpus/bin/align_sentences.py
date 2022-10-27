import sys

from yimt.api.text_splitter import split_sentences
from yimt.api.utils import detect_lang
from yimt.corpus.aligner import SentenceEmbeddingAligner


def get_paragraph_pair(in_fn):
    paragraphs = open(in_fn, encoding="utf-8").readlines()
    paragraphs = [p.strip() for p in paragraphs]
    paragraphs = list(filter(lambda p:len(p)>0, paragraphs))
    assert len(paragraphs) % 2 == 0

    src_p = paragraphs[0::2]
    tgt_p = paragraphs[1::2]

    print("# of paragraphs:", len(src_p))

    src_lang = detect_lang("".join(src_p))
    tgt_lang = detect_lang("".join(tgt_p))

    print(src_lang, "->", tgt_lang)

    src_p_list = [split_sentences(p, src_lang) for p in src_p]
    tgt_p_list = [split_sentences(p, tgt_lang) for p in tgt_p]

    print("# of source sentences:", sum([len(p) for p in src_p_list]))
    print("# of target sentences:", sum([len(p) for p in tgt_p_list]))

    return src_p_list, tgt_p_list


if __name__ == "__main__":
    in_fn = sys.argv[1]
    out_fn = sys.argv[2]

    src_p, tgt_p = get_paragraph_pair(in_fn)

    out_f = open(out_fn, "a+", encoding="utf-8")

    aligner = SentenceEmbeddingAligner();
    for sp, tp in zip(src_p, tgt_p):
        align = aligner.align(sp, tp)
        for a in align:
            out_f.write(a[0] + "\t" + a[1] + "\n")

