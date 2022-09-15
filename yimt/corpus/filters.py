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