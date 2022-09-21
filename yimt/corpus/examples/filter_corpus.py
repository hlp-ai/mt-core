from yimt.corpus.filters import SameFilter, EmptyFilter, OverlapFilter

if __name__ == "__main__":
    same_filter = SameFilter()
    print(same_filter.filter("i like it", "i like it"))
    print(same_filter.filter("i like it", " like it"))
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