from yimt.api.word2word.word2word import Word2word

lang_src = input("Source language: ")
lang_tgt = input("Target language: ")

lexicon = Word2word(lang_src, lang_tgt)

print(len(lexicon.word2x), len(lexicon.y2word), len(lexicon.x2ys))

while True:
    word = input("Input word: ")
    print(lexicon(word.lower()))