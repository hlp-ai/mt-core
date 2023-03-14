import argparse
import io
import os
import re
import shutil
from pprint import pprint

import yaml
from yimt.core.utils.misc import merge_dict


def copy_to_dir(fn, dst):
    fpath, fname = os.path.split(fn)
    if not os.path.exists(dst):
        os.mkdir(dst)
    dfname = os.path.join(dst, fname)
    shutil.copyfile(fn, dfname)
    return dfname


if __name__ == "__main__":
    argparser = argparse.ArgumentParser("Fine-tune existing NMT model.")
    argparser.add_argument("--corpus_fn", required=True, help="in-domain parallel corpus file")
    argparser.add_argument("--src_sp_model", required=True, help="sentencepiece model for source text")
    argparser.add_argument("--tgt_sp_model", required=True, help="sentencepiece model for target text")
    argparser.add_argument("--src_vocab", required=True, help="source vocabulary file")
    argparser.add_argument("--tgt_vocab", required=True, help="target vocabulary file")
    argparser.add_argument("--ckpt_dir", required=True, help="checkpoint directory containing checkpoint to be fine-tuned")
    argparser.add_argument("--output_dir", required=True, help="output directory")
    argparser.add_argument("--steps", type=int, required=True, help="steps for fine-tuning")
    argparser.add_argument("--config", default=None, help="additional config file")
    argparser.add_argument("--continue_from_checkpoint", default=False,
        action="store_true",
        help="Continue the training from the checkpoint.")
    args = argparser.parse_args()

    corpus_fn = args.corpus_fn  # r"D:\kidden\mt\exp\en-zh\ft\data\pe.tsv"
    corpus_fn_src = corpus_fn + ".src"
    corpus_fn_tgt = corpus_fn + ".tgt"

    sp_src = args.src_sp_model  # r"D:\kidden\mt\exp\sp\spm-bpe-en-32000.model"
    sp_tgt = args.tgt_sp_model  # r"D:\kidden\mt\exp\sp\spm-bpe-zh-32000.model"
    src_vocab = args.src_vocab
    tgt_vocab = args.tgt_vocab  # r"D:\kidden\mt\exp\sp\zh-vocab.txt"

    output_dir = args.output_dir
    ckpt_dir = args.ckpt_dir

    step_fine_tune = args.steps

    step_trained = 0

    extra_conf = {}
    if args.config is not None:
        extra_conf = yaml.load(io.open(args.config, encoding="utf-8"), Loader=yaml.FullLoader)
        pprint(extra_conf)

    print("Copying checkpoint {} into {}...".format(ckpt_dir, output_dir))
    for f in os.listdir(ckpt_dir):
        m = re.search("ckpt-(\\d+)", f)
        if m:
            step_trained = int(m.group(1))
            print("Checkpoint to be fine-tuned has trained for {} stpes".format(step_trained))
        src = os.path.join(ckpt_dir, f)
        if os.path.isfile(src):
            copy_to_dir(src, output_dir)

    print("Copying source sp model and vocab...")
    sp_src = copy_to_dir(sp_src, output_dir)
    src_vocab = copy_to_dir(src_vocab, output_dir)

    print("Copying target sp model and vocab...")
    sp_tgt = copy_to_dir(sp_tgt, output_dir)
    tgt_vocab = copy_to_dir(tgt_vocab, output_dir)

    split_cmd_str = "python -m yimt.corpus.bin.to_single {} {} {}"
    print("Splitting {} into {} and {}...".format(corpus_fn, corpus_fn_src, corpus_fn_tgt))
    os.popen(split_cmd_str.format(corpus_fn, corpus_fn_src, corpus_fn_tgt)).readlines()
    print()

    tok_cmd_str = "python -m yimt.core.ex.sp_tokenize --sp_model {} --in_fn {} --out_fn {}"
    corpus_fn_src_tok = corpus_fn_src + ".tok"
    corpus_fn_tgt_tok = corpus_fn_tgt + ".tok"
    print("Tokenizing {} into {}...".format(corpus_fn_src, corpus_fn_src_tok))
    os.popen(tok_cmd_str.format(sp_src, corpus_fn_src, corpus_fn_src_tok)).readlines()
    print()
    print("Tokenizing {} into {}...".format(corpus_fn_tgt, corpus_fn_tgt_tok))
    os.popen(tok_cmd_str.format(sp_tgt, corpus_fn_tgt, corpus_fn_tgt_tok)).readlines()
    print()

    config = {
        "model_dir": output_dir,
        "data": {
            "train_features_file": corpus_fn_src_tok,
            "train_labels_file": corpus_fn_tgt_tok,
            "source_vocabulary": src_vocab,
            "target_vocabulary": tgt_vocab,
        },
        "train": {
            "max_step": step_trained + step_fine_tune,
            "average_last_checkpoints": 0
        }
    }
    merge_dict(config, extra_conf)
    pprint(config)
    config_fn = os.path.join(output_dir, "ft.yml")
    with open(config_fn, "w") as f:
        yaml.safe_dump(config, f, encoding='utf-8', allow_unicode=True)

    train_cmd_str = "python -m yimt.core.bin.main --config {} --auto_config --mixed_precision train"
    if args.continue_from_checkpoint:
        train_cmd_str += " --continue_from_checkpoint"
    print("Training...")
    os.popen(train_cmd_str.format(config_fn)).readlines()
    print()
