#Usage

## Command Line Usage
### 0. Prepare datasets
Training parallel corpus is required and development parallel corpus is optional. Each corpus contains two text files with one sentence each line.

### 1. Train SentencePiece model
For source and target training corpus, train source and target SentencePiece models. 
```shell script
yimt/core/ex/sp_train.py [-h] --corpus CORPUS [--sp_prefix SP_PREFIX]
                   [--vocab_size VOCAB_SIZE] [--max_sentences MAX_SENTENCES]
                   [--coverage COVERAGE]
```

### 2. Tokenize corpus
Tokenize training and development corpora (if provided).
```shell script
yimt/core/ex/sp_tokenize.py [-h] --sp_model SP_MODEL --in_fn IN_FN [--out_fn OUT_FN]
```

### 3. Build vocabulary
Build source and target vocabularies from tokenized corpora
```shell script
yimt/core/bin/build_vocab.py [-h] [--from_vocab FROM_VOCAB]
                      [--from_format {default,sentencepiece}] --save_vocab
                      SAVE_VOCAB [--min_frequency MIN_FREQUENCY] [--size SIZE]
                      [--size_multiple SIZE_MULTIPLE]
                      [--without_sequence_tokens]
                      [data [data ...]]
```

### 4. Make config file
The document for config file is [here](./configuration.md). The minimum config file is as follows.
```yaml
model_dir: toy-enzh/model

data:
  # (required for train run type).
  train_features_file: data/en.train.tok
  train_labels_file: data/zh.train.tok

  # (optional) (required for train_end_eval run types).
  eval_features_file: data/en.dev.tok
  eval_labels_file: data/zh.dev.tok

  source_vocabulary: data/en-vocab.txt
  target_vocabulary: data/zh-vocab.txt
```

### Export model
```shell script
python yimt.core.bin.main.py 
--config <config_file_path> --auto_config 
export
--output_dir <output_dir> 
--format <saved_model|checkpoint|ctranslate2|tflite_dynamic_range|tflite_float16>
```