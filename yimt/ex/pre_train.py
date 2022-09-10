"""Preprocess text before training"""
import argparse
import os

from yimt.ex.sp import train_spm, load_spm, tokenize_file

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("src_fn")
    argparser.add_argument("src_vocab_size", type=int)
    argparser.add_argument("tgt_fn")
    argparser.add_argument("tgt_vocab_size", type=int)
    argparser.add_argument("dev_src_fn")
    argparser.add_argument("dev_tgt_fn")
    args = argparser.parse_args()

    src_sp_prefix = args.src_fn + ".sp"
    tgt_sp_prefix = args.tgt_fn + ".sp"

    src_train_tok = args.src_fn + ".tok"
    src_dev_tok = args.dev_src_fn + ".tok"

    tgt_train_tok = args.tgt_fn + ".tok"
    tgt_dev_tok = args.dev_tgt_fn + ".tok"

    print("Training SentencePiece on", args.src_fn, "and writing SP model into", src_sp_prefix)
    train_spm(args.src_fn, src_sp_prefix, args.src_vocab_size)

    print()

    src_tokenizer_sp = load_spm(src_sp_prefix + ".model")
    print("Tokenizing train and dev file for source language...")
    tokenize_file(src_tokenizer_sp, args.src_fn, src_train_tok)
    tokenize_file(src_tokenizer_sp, args.dev_src_fn, src_dev_tok)

    print()

    print("Training SentencePiece on", args.tgt_fn, "and writing SP model into", tgt_sp_prefix)
    train_spm(args.tgt_fn, tgt_sp_prefix, args.tgt_vocab_size)

    print()

    tgt_tokenizer_sp = load_spm(tgt_sp_prefix + ".model")
    print("Tokenizing train and dev file for target language...")
    tokenize_file(tgt_tokenizer_sp, args.tgt_fn, tgt_train_tok)
    tokenize_file(tgt_tokenizer_sp, args.dev_tgt_fn, tgt_dev_tok)

    print()

    build_vocab_cmd = "python ../bin/build_vocab.py --size {} --save_vocab {} {}"

    src_vocab = args.src_fn + ".voc"
    print("Building vocab {} from {}...".format(src_vocab, src_train_tok))
    os.popen(build_vocab_cmd.format(args.src_vocab_size, src_vocab, src_train_tok)).readlines()

    print()

    tgt_vocab = args.tgt_fn + ".voc"
    print("Building vocab {} from {}...".format(tgt_vocab, tgt_train_tok))
    os.popen(build_vocab_cmd.format(args.tgt_vocab_size, tgt_vocab, tgt_train_tok)).readlines()

    print()

    print("Preparing config file...")
    config_fn = os.path.join(os.path.dirname(args.src_fn), "config.yml")
    model_dir = os.path.join(os.path.dirname(args.src_fn), "run")
    config_str = """
model_dir: {}

data:
  train_features_file: {}
  train_labels_file: {}

  eval_features_file: {}
  eval_labels_file: {}

  source_vocabulary: {}
  target_vocabulary: {}
train:
  batch_size: 4096
  max_step: 2000
  save_summary_steps: 100
  save_checkpoints_steps: 200
eval:
  steps: 200
  scorers: bleu
    """.format(model_dir, src_train_tok, tgt_train_tok, src_dev_tok, tgt_dev_tok, src_vocab, tgt_vocab)

    open(config_fn, mode="w", encoding="utf-8").write(config_str)
