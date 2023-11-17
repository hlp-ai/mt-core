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
同时切分源语言和目标语言句子：
```shell script
python -m yimt.segmentation.pretok_tsv --tsv_file <平行语料TSV文件路径> --tl zh --sl th
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

### 1.4 拆分TSV语料为单语语料
将每个语言对的TSV平行语料拆分为两个单语语料，为SentencePiece准备训练语料。命令如下：
```shell script
python -m yimt.utils.bin.to_single <TSV file> <src file> <tgt file>
```

### 1.5 重采样单语语料
各种语言语料大小差别较大，为了更好的训练SentencePiece模型，需要对各语言单语语言进行重采样，使得高资源语言下采样，低资源语言上采样。将各个语言单语语料放到一个目录，执行以下命令：
```shell script
python -m yimt.experimental.mnmt.resample --root <语料目录> [--t <采样温度, 5.0>] [--total <最后采样样本总数,15000000>]
```

### 1.6 合并采样后单语语料
将各个单语语料采样的文件拷贝到一个目录，执行以下命令将它们合并为一个文件：
```shell script
python -m yimt.experimental.mnmt.merge -i <input directory> -o <output file>
```

### 1.7 训练SetencePiece模型
可以所有语言一起训练一个SP模型。也可以中文单独训练一个SP模型，其他所有语言训练一个SP模型。
<p>如果中文句子部分已经添加目标语言标记（1.3步），这些目标语言标记需要作为用户定义符号提供给SP训练器。将所有目标语言标记每行一个放入一个文本文件，并执行以下命令：</p>

```shell script
python -m yimt.segmentation.sp_train --corpus <文件路径> [--user_sym_file <自定义符号文件路径>]
```