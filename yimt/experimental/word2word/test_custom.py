from yimt.experimental.word2word.word2word import Word2word

my_en2zh_cn = Word2word.load("zh_cn", "ja", f"D:\kidden\mt\open-mt-data\w2w\ccm-ja-zh1m")
print(my_en2zh_cn("学生"))
