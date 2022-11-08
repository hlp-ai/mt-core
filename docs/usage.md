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

### 2. Export model
```shell script
python yimt.core.bin.main.py 
--config <config_file_path> --auto_config 
export
--output_dir <output_dir> 
--format <saved_model|checkpoint|ctranslate2|tflite_dynamic_range|tflite_float16>
```