from yimt.api.utils import detect_lang
from yimt.corpus.utils import is_ascii


class Filter(object):
    """Parallel corpus filter base class"""

    def filter(self, src, tgt):
        """

        Args:
            src: source sentence
            tgt: target sentence
        Returns:
            None if invalid, otherwise pair
        """
        pass


class SameFilter(Filter):
    """Filter pair with same source and target"""

    def filter(self, src, tgt):
        if src.strip() == tgt.strip():
            return None

        return src, tgt


class OverlapFilter(Filter):
    """Filter pair whose source and target have too much overlap"""

    def __init__(self, ratio=0.8):
        self.ratio = ratio

    def filter(self, src, tgt):
        import difflib

        s = difflib.SequenceMatcher(None, src, tgt)
        if s.ratio() > self.ratio:
            return None
        return src, tgt


class EmptyFilter(Filter):
    """Filter pair whose source or target is empty"""

    def filter(self, src, tgt):
        if len(src.strip()) == 0 or len(tgt.strip()) == 0:
            return None

        return src, tgt


class AllASCII(Filter):
    """Filter pair whose src and target are english"""

    def filter(self, src, tgt):
        is_src_en = is_ascii(src)
        is_tgt_en = is_ascii(tgt)

        if is_src_en and is_tgt_en:
            return None
        return src, tgt


class LangFilter(Filter):
    """Filter pair with wrong language"""

    def __init__(self, src_lang, tgt_lang):
        self.src_lang = src_lang
        self.tgt_lang = tgt_lang

    def filter(self, src, tgt):
        if detect_lang(src) != self.src_lang or detect_lang(tgt) != self.tgt_lang:
            return None

        return src, tgt


class LenFilter(Filter):
    """Filter pair which is too long or short"""

    def __init__(self, src_lens=(None, None), tgt_lens=(None, None), src_len_fn=len, tgt_len_fn=len):
        self.src_min_len = src_lens[0]
        self.src_max_len = src_lens[1]
        self.tgt_min_len = tgt_lens[0]
        self.tgt_max_len = tgt_lens[1]

        self.src_len_fn = src_len_fn
        self.tgt_len_fn = tgt_len_fn

    def filter(self, src, tgt):
        src_len = self.src_len_fn(src)
        tgt_len = self.tgt_len_fn(tgt)

        if self.src_min_len is not None and src_len < self.src_min_len:
            return None
        if self.src_max_len is not None and src_len > self.src_max_len:
            return None
        if self.tgt_min_len is not None and tgt_len < self.tgt_min_len:
            return None
        if self.tgt_max_len is not None and tgt_len > self.tgt_max_len:
            return None
        return src, tgt


class LenDiffFilter(Filter):
    """Filter pair whose source and target have big length difference"""

    def __init__(self, ratio, src_len_fn=len, tgt_len_fn=len):
        self.ratio = ratio
        self.src_len_fn = src_len_fn
        self.tgt_len_fn = tgt_len_fn

    def filter(self, src, tgt):
        len_src = self.src_len_fn(src)
        len_tgt = self.tgt_len_fn(tgt)

        if len_src <= self.ratio * len_tgt and len_tgt <= self.ratio * len_src:
            return src, tgt
        else:
            return None
