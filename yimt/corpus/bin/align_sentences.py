import sys

from yimt.api.text_splitter import split_sentences
from yimt.api.utils import detect_lang
from yimt.corpus.aligner import SentenceEmbeddingAligner


def get_paragraph_pair(in_fn):
    """Get two paragraphs from file with text of two languages

    In file, text of two languages interleaves and has the same number of paragraphs.

    Args:
        in_fn: input text file

    Returns:
        tuple of paragraph list of two languages

    """
    paragraphs = open(in_fn, encoding="utf-8").readlines()
    paragraphs = [p.strip() for p in paragraphs]
    paragraphs = list(filter(lambda p:len(p)>0, paragraphs))  # filter empty paragraphs or lines
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
    pairs = aligner.align_paragraphs(src_p, tgt_p)
    num_align = 0
    for ss, ts in pairs:
        out_f.write(ss + "\t" + ts + "\n")
        num_align += 1

    print("# of pairs aligned:", num_align)
    out_f.close()
