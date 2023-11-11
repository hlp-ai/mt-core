# 以中文为中心的多语神经机器翻译
以中文为中心的多语神经机器翻译的目标是构建中文和其他语言间的X-ZH和ZH-X翻译系统。
## 1. 训练步骤
### 1.1 准备语料
准备各种语言和中文间的TSV格式平行语料，每个语言对的语料一个文件。
### 1.2 （可选）预切分
对源语言或/和目标语言句子进行预切分，例如，对中文句子在训练SentencePiece模型前进行分词。以下对平行语料目标语言中文句子进行分词：
```shell script
python -m yimt.segmentation.pretok_tsv --tsv_file <平行语料TSV文件路径> --tl zh
```
### 1.3 （可选）添加目标语言标记
若要训练中文到其他语言翻译系统，需要为各个语言对的平行语料中文句子部分添加相对应的其他语言标记。例如，英中平行语料平行句子：
```
This is a book.  这是一本书。
```
添加目标语言标记\<toen>后为:
```
This is a book.  <toen>这是一本书。
```
目标语言标记是自定义的，其他语言对类似。以下对英中平行语料中目标中文句子添加\<toen>目标语言句子。
```shell script
python -m yimt.experimental.mnmt.add_tag --tsv_file <平行语料TSV文件路径> --to tgt --token <toen>
```