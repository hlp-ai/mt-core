"""Preprocess text before training"""
import argparse
import os

from yimt.core.ex.sp import train_spm, load_spm, tokenize_file
from yimt.corpus.tokenize_file import tokenize_single


def get_file_name(p):
    return os.path.basename(p)


def get_sp_prefix(corpus_path, vocab_size):
    corpus_path = get_file_name(corpus_path)
    return "{}-sp-{}".format(corpus_path, vocab_size)


def get_tok_file(corpus_path):
    corpus_path = get_file_name(corpus_path)
    return corpus_path + ".tok"


def get_vocab_file(tok_corpus_path):
    corpus_path = get_file_name(tok_corpus_path)
    return corpus_path + ".vocab"


def pretrain_corpus(raw_train_fn, raw_dev_fn=None, pretok_lang=None, vocab_size=32000, output_path=None,
                    max_sent=10000000, coverage=0.9999):
    if output_path is None:
        output_path = os.path.dirname(raw_train_fn)

    sp_prefix = os.path.join(output_path, get_sp_prefix(raw_train_fn, vocab_size))

    if pretok_lang:
        print("Pretokenizing file {}".format(raw_train_fn))
        raw_train_fn = tokenize_single(raw_train_fn, pretok_lang)
        if raw_dev_fn:
            print("Pretokenizing file {}".format(raw_dev_fn))
            raw_dev_fn = tokenize_single(raw_dev_fn, pretok_lang)

    print("Training SentencePiece on", raw_train_fn, "and writing SP model into", sp_prefix)
    train_spm(raw_train_fn, sp_prefix, vocab_size, num_sentences=max_sent, coverage=coverage)

    print()

    tokenizer_sp = load_spm(sp_prefix + ".model")
    train_tok = os.path.join(output_path, get_tok_file(raw_train_fn))
    print("Tokenizing {} into {}".format(raw_train_fn, train_tok))
    tokenize_file(tokenizer_sp, raw_train_fn, train_tok)
    if raw_dev_fn:
        dev_tok = os.path.join(output_path, get_tok_file(raw_dev_fn))
        print("Tokenizing {} into {}".format(raw_dev_fn, dev_tok))
        tokenize_file(tokenizer_sp, raw_dev_fn, dev_tok)

    print()

    build_vocab_cmd = "python -m yimt.core.bin.build_vocab --size {} --save_vocab {} {}"

    vocab = os.path.join(output_path, get_vocab_file(train_tok))
    print("Building vocab {} from {}...".format(vocab, train_tok))
    os.popen(build_vocab_cmd.format(vocab_size, vocab, train_tok)).readlines()


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("src_fn")
    argparser.add_argument("src_vocab_size", type=int)
    argparser.add_argument("tgt_fn")
    argparser.add_argument("tgt_vocab_size", type=int)
    argparser.add_argument("dev_src_fn")
    argparser.add_argument("dev_tgt_fn")
    argparser.add_argument("output_path")
    argparser.add_argument("max_sent", type=int, default=5000000)
    argparser.add_argument("coverage", type=float, default=0.9999)
    args = argparser.parse_args()

    output_path = args.output_path

    src_sp_prefix = os.path.join(output_path, get_sp_prefix(args.src_fn, args.src_vocab_size))
    tgt_sp_prefix =os.path.join(output_path, get_sp_prefix(args.tgt_fn, args.tgt_vocab_size))

    src_train_tok = os.path.join(output_path, get_tok_file(args.src_fn))
    src_dev_tok = os.path.join(output_path, get_tok_file(args.dev_src_fn))

    tgt_train_tok = os.path.join(output_path, get_tok_file(args.tgt_fn))
    tgt_dev_tok = os.path.join(output_path, get_tok_file(args.dev_tgt_fn))

    print("Training SentencePiece on", args.src_fn, "and writing SP model into", src_sp_prefix)
    train_spm(args.src_fn, src_sp_prefix, args.src_vocab_size, num_sentences=args.max_sent, coverage=args.coverage)

    print()

    src_tokenizer_sp = load_spm(src_sp_prefix + ".model")
    print("Tokenizing train and dev file for source language...")
    tokenize_file(src_tokenizer_sp, args.src_fn, src_train_tok)
    tokenize_file(src_tokenizer_sp, args.dev_src_fn, src_dev_tok)

    print()

    print("Training SentencePiece on", args.tgt_fn, "and writing SP model into", tgt_sp_prefix)
    train_spm(args.tgt_fn, tgt_sp_prefix, args.tgt_vocab_size, num_sentences=args.max_sent, coverage=args.coverage)

    print()

    tgt_tokenizer_sp = load_spm(tgt_sp_prefix + ".model")
    print("Tokenizing train and dev file for target language...")
    tokenize_file(tgt_tokenizer_sp, args.tgt_fn, tgt_train_tok)
    tokenize_file(tgt_tokenizer_sp, args.dev_tgt_fn, tgt_dev_tok)

    print()

    build_vocab_cmd = "python -m yimt.core.bin.build_vocab --size {} --save_vocab {} {}"

    src_vocab = os.path.join(output_path, get_vocab_file(src_train_tok))
    print("Building vocab {} from {}...".format(src_vocab, src_train_tok))
    os.popen(build_vocab_cmd.format(args.src_vocab_size, src_vocab, src_train_tok)).readlines()

    print()

    tgt_vocab = os.path.join(output_path, get_vocab_file(tgt_train_tok))
    print("Building vocab {} from {}...".format(tgt_vocab, tgt_train_tok))
    os.popen(build_vocab_cmd.format(args.tgt_vocab_size, tgt_vocab, tgt_train_tok)).readlines()

    print()

    print("Preparing config file...")
    config_fn = os.path.join(output_path, "config.yml")
    model_dir = os.path.join(output_path, "model")
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
