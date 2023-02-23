import re

from yimt.corpus.chars import clean_text
from yimt.corpus.tokenize_file import detok_zh_str
from yimt.corpus.utils import hant_2_hans


class Normalizer(object):

    def normalize(self, s):
        """Normalize text

        Args:
            s: string
        Returns:
            the normalize string
        """
        pass


class Cleaner(Normalizer):
    def normalize(self, s):
        s = s.strip()
        pair = s.split("\t")
        if len(pair) != 2:
            return ""

        src = pair[0]
        tgt = pair[1]

        src = clean_text(src)
        tgt = clean_text(tgt)

        src = re.sub(r"\s{2,}", " ", src)
        src = src.strip()

        tgt = re.sub(r"\s{2,}", " ", tgt)
        tgt = tgt.strip()

        return src + "\t" + tgt


class DeTokenizer(Normalizer):
    """Remove unnecessary spaces"""

    def __init__(self, detok_src=False, detok_tgt=True):
        self.detok_tgt = detok_tgt
        self.detok_src = detok_src

    def normalize(self, s):
        s = s.strip()

        if self.detok_tgt or self.detok_src:
            pair = s.split("\t")
            if len(pair) != 2:
                return ""
            src = pair[0]
            tgt = pair[1]

            if self.detok_tgt:
                tgt = detok_zh_str(tgt)  # remove space between CJK characters

            if self.detok_src:
                src = detok_zh_str(src)

            return src + "\t" + tgt

        return s


punct_pairs = [('“', '”'), ('"', '"'), ("‘", "’"), ("（", "）"), ("《", "》"), ("(", ")")]


def normalize_pair_punct(s, left_punct, right_punct):
    s = s.replace(left_punct + left_punct, "")
    s = s.replace(left_punct + left_punct + left_punct, left_punct)

    s = s.replace(right_punct + right_punct, "")
    s = s.replace(right_punct + right_punct + right_punct, right_punct)

    idx = s.find(left_punct)
    if idx >= 0:
        has_pair = s.find(right_punct, idx + 1)
        if has_pair == -1:
            s = s[:idx] + s[idx + 1:]
            # s = s.replace(left_punct, "")

    idx = s.find(right_punct)
    if idx >= 0:
        has_pair = s.find(left_punct, 0, idx)
        if has_pair == -1:
            s = s[:idx] + s[idx + 1:]
            # s = s.replace(right_punct, "")

    return s


class PairPunctNormalizer(Normalizer):

    def normalize_pair(self, src, tgt):
        for p in punct_pairs:
            src = normalize_pair_punct(src, p[0], p[1])
            tgt = normalize_pair_punct(tgt, p[0], p[1])

        return src, tgt

    def normalize(self, s):
        pair = s.split("\t")
        if len(pair) != 2:
            return ""
        src = pair[0]
        tgt = pair[1]

        src, tgt = self.normalize_pair(src, tgt)

        return src + "\t" + tgt


class Hant2Hans(Normalizer):
    """Traditional Chinese to Simplified Chinese"""

    def __init__(self, norm_src=True, norm_tgt=True):
        self.norm_src = norm_src
        self.norm_tgt = norm_tgt

    def normalize(self, s):
        if not self.norm_src and not self.norm_tgt:
            return s

        pair = s.split("\t")
        if len(pair) != 2:
            return ""
        src = pair[0]
        tgt = pair[1]
        if self.norm_src:
            src = hant_2_hans(src)

        if self.norm_tgt:
            tgt = hant_2_hans(tgt)

        return src + "\t" + tgt
