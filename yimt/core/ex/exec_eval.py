"""Evaluation pipeline with tokenizing and translating source, detokenizing prediction and sacrebleu"""
import argparse
import os

from yimt.core.ex.sp import tokenize_file, detokenize_file


def run_eval(config_path, src_path, ref_path, sp_src, sp_tgt, lang_pair):
    infer_cmd_str = "python ../bin/main.py --config {} --auto_config infer --features_file {} --predictions_file {}"
    bleu_cmd_str = "sacrebleu -l {} {} -i {}"

    src_path_tok = src_path + ".tok"

    pred_path = src_path_tok + ".pred"
    pred_path_detok = pred_path + ".det"

    print("Tokenizing {} into {}...".format(src_path, src_path_tok))
    # os.popen(tok_cmd_str.format(sp_src, src_path, src_path_tok)).readlines()
    tokenize_file(sp_src, src_path, src_path_tok)

    print()

    print("Translating {} into {}...".format(src_path_tok, pred_path))
    os.popen(infer_cmd_str.format(config_path, src_path_tok, pred_path)).readlines()

    print()

    print("Detokenizing {} into {}...".format(pred_path, pred_path_detok))
    # os.popen(detok_cmd_str.format(sp_tgt, pred_path, pred_path_detok)).readlines()
    detokenize_file(sp_tgt, pred_path, pred_path_detok)

    print()

    print("Computing BLEU for {} on Ref {}...".format(pred_path_detok, ref_path))
    ret = os.popen(bleu_cmd_str.format(lang_pair, ref_path, pred_path_detok)).readlines()
    for line in ret:
        print(line.strip())


def run_infer(config_path, src_path, sp_src, sp_tgt):
    infer_cmd_str = "python ../bin/main.py --config {} --auto_config infer --features_file {} --predictions_file {}"

    src_path_tok = src_path + ".tok"

    pred_path = src_path_tok + ".pred"
    pred_path_detok = pred_path + ".det"

    print("Tokenizing {} into {}...".format(src_path, src_path_tok))
    tokenize_file(sp_src, src_path, src_path_tok)

    print()

    print("Translating {} into {}...".format(src_path_tok, pred_path))
    os.popen(infer_cmd_str.format(config_path, src_path_tok, pred_path)).readlines()

    print()

    print("Detokenizing {} into {}...".format(pred_path, pred_path_detok))
    detokenize_file(sp_tgt, pred_path, pred_path_detok)

    return pred_path_detok


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--lang", default="en-zh", help="language direction")
    argparser.add_argument("--sp_src", default= r"D:\kidden\mt\open\ex-data-29m\spm-bpe-en-32000.model",
                           help="SentencePiece model path for source language")
    argparser.add_argument("--sp_tgt", default=r"D:\kidden\mt\open\ex-data-29m\spm-bpe-zh-32000.model",
                           help="SentencePiece model path for target language")
    argparser.add_argument("--src", default=r"D:\kidden\mt\open-mt-data\wmt21\dev\newstest2020-enzh-src.en",
                           help="Source eval file path")
    argparser.add_argument("--ref", default=r"D:\kidden\mt\open-mt-data\wmt21\dev\newstest2020-enzh-ref.zh",
                           help="Reference file path")
    argparser.add_argument("--config", default=r"D:\kidden\mt\open\OpenNMT-tf\ex\run-29m-enzh-big\deploy.yml",
                           help="Config file path")
    args = argparser.parse_args()

    tok_cmd_str = "python sp_tokenize.py {} {} {}"
    detok_cmd_str = "python sp_detokenize.py {} {} {}"
    infer_cmd_str = "python ../bin/main.py --model_type TransformerBig --config {} --auto_config infer --features_file {} --predictions_file {}"
    bleu_cmd_str = "sacrebleu -l {} {} -i {}"

    sp_src = args.sp_src
    sp_tgt = args.sp_tgt

    src_path = args.src
    src_path_tok = src_path + ".tok"
    ref_path = args.ref

    pred_path = src_path_tok + ".pred"
    pred_path_detok = pred_path + ".det"

    config_path = args.config

    lang_pair = args.lang

    print("Tokenizing {} into {}...".format(src_path, src_path_tok))
    os.popen(tok_cmd_str.format(sp_src, src_path, src_path_tok)).readlines()

    print()

    print("Translating {} into {}...".format(src_path_tok, pred_path))
    os.popen(infer_cmd_str.format(config_path, src_path_tok, pred_path)).readlines()

    print()

    print("Detokenizing {} into {}...".format(pred_path, pred_path_detok))
    os.popen(detok_cmd_str.format(sp_tgt, pred_path, pred_path_detok)).readlines()

    print()

    print("Computing BLEU for {} on Ref {}...".format(pred_path_detok, ref_path))
    ret = os.popen(bleu_cmd_str.format(lang_pair, ref_path, pred_path_detok)).readlines()
    for line in ret:
        print(line.strip())
