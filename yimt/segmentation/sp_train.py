"""Train SentencePiece model from corpus"""
import argparse

from yimt.segmentation.sp import train_spm

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--corpus", required=True, help="Corpus file path")
    argparser.add_argument("--sp_prefix", default=None, help="SentencePiece model path prefix")
    argparser.add_argument("--vocab_size", type=int, default=32000, help="Vocab size")
    argparser.add_argument("--max_sentences", type=int, default=5000000, help="Max number of sentences for training")
    argparser.add_argument("--coverage", type=float, default=0.9999, help="Vocab coverage")
    argparser.add_argument("--normalization", default="nmt_nfkc", help="normalization_rule_name:nmt_nfkc/identity")
    argparser.add_argument("--remove_sp", type=bool, default=True, help="remove_extra_whitespaces")
    argparser.add_argument("--user_sym_file", type=str, default=None, help="user_defined_symbols_file")
    args = argparser.parse_args()

    if args.sp_prefix is None:
        sp_prefix = "{}-sp-{}".format(args.corpus, args.vocab_size)
    else:
        sp_prefix = args.sp_prefix

    train_spm(args.corpus, sp_prefix, args.vocab_size,
              coverage=args.coverage, num_sentences=args.max_sentences,
              normalization_rule_name=args.normalization,
              remove_extra_whitespaces=args.remove_sp,
              user_defined_symbols_file=args.user_sym_file)