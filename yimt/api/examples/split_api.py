from yimt.api.text_splitter import split_sentences, may_combine_paragraph, word_segment

if __name__ == "__main__":
    t1 = "How are you? Mr. White is working."
    print(word_segment(t1, lang="en"))
    print(split_sentences(t1))

    t2 = "好好学习，天天向上。运动很重要，坚持运动！"
    print(word_segment(t2, lang="zh"))
    print(split_sentences(t2, lang="zh"))

    t3 = "「日本語が話せの170理由」。タイトル：THE INFORMANT!"
    print(word_segment(t3, lang="ja"))
    print(split_sentences(t3, lang="ja"))

    t4 = '''
    The intent of this book is to introduce readers to the latest version of the
TensorFlow library. Therefore, this first chapter focuses mainly on what has
changed in the TensorFlow library since its first version, TensorFlow 1.0.
We will cover the various changes, in addition to highlighting the specific
parts for which changes are yet to be introduced. This chapter is divided
into three sections: the first discusses the internals of TensorFlow; the
second focuses on the changes that have been implemented in TensorFlow
2.0 after TensorFlow 1.0; and the final section covers TensorFlow 2.0
installation methods and basic operations.
    '''

    print(may_combine_paragraph(t4))