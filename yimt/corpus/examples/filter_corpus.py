from yimt.corpus.filters import SameFilter, EmptyFilter, OverlapFilter, AllASCII, LangFilter, LenDiffFilter, LenFilter

if __name__ == "__main__":
    same_filter = SameFilter()
    print(same_filter.filter("i like it", "i like it"))
    print(same_filter.filter("i like it", " like it"))
    print(same_filter.filter("i like it", "I like it "))
    print(same_filter.filter("我喜欢", "我喜欢"))

    print()

    empty_filter = EmptyFilter()
    print(empty_filter.filter("", " "))
    print(empty_filter.filter(" a test", " "))
    print(empty_filter.filter("a test", "just a test"))

    print()

    overlap_filter = OverlapFilter()
    print(overlap_filter.filter("abcdef", "abcdef"))
    print(overlap_filter.filter("啊啊啊", "啊啊啊"))
    print(overlap_filter.filter("aaaaaaa", "aaa啊啊啊啊啊啊阿"))

    print()

    ascii_filter = AllASCII()
    print(ascii_filter.filter("abcdeffggg fff", "abcdeffggg"))
    print(overlap_filter.filter("啊啊啊", "abccc"))

    print()
    lang_filter = LangFilter("en", "zh")
    print(lang_filter.filter("i like it", "i like it"))
    print(lang_filter.filter("i like it", "我真的很喜欢它。"))

    print()

    en_len = lambda s: len(s.split())
    zh_len = lambda s: len(s)
    lendiff_filter = LenDiffFilter(3, en_len, en_len)
    print(lendiff_filter.filter("like", "what what are wrong"))
    print(lendiff_filter.filter("a b", "aaaaa bbbb cccc"))
    lendiff_filter2 = LenDiffFilter(3, en_len, zh_len)
    print(lendiff_filter2.filter("a b a b c d cd cc f", "啊啊"))

    print()

    len_filter = LenFilter((2, 3), (2, 4), en_len, zh_len)
    print(len_filter.filter("a b", "啊啊啊啊啊啊啊啊啊啊啊啊"))
    print(len_filter.filter("a b", "啊啊啊啊"))

