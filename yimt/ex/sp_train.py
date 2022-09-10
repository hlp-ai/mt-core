"""Train SentencePiece model from corpus"""
import argparse

from yimt.ex.sp import train_spm

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("corpus_fn")
    argparser.add_argument("sp_model")
    argparser.add_argument("vocab_size", type=int)
    args = argparser.parse_args()

    train_spm(args.corpus_fn, args.sp_model, args.vocab_size)
