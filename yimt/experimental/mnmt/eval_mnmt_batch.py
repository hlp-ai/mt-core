import argparse
import os

from yimt.utils.bin.exec_eval import run_eval
from yimt.utils.misc import pair_to_single

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--tsv_dir", default=r"D:\dataset\mnmt\dev\tsv2", help="eval files dir")
    argparser.add_argument("--direction", default="x2zh", help="x2zh or zh2x")
    argparser.add_argument("--sp_x", default= r"D:\dataset\mnmt\sp\cc50.x.sampled-sp-48000.model",
                           help="SentencePiece model path for x language")
    argparser.add_argument("--sp_zh", default=r"D:\dataset\mnmt\sp\en-zh.tsv.zh-sp-32000.model",
                           help="SentencePiece model path for zh language")
    argparser.add_argument("--config", required=True, help="Config file path")
    args = argparser.parse_args()

    if args.direction == "x2zh":
        x2zh = True
        sp_src = args.sp_x
        sp_tgt = args.sp_zh
    else:
        x2zh = False
        sp_src = args.sp_zh
        sp_tgt = args.sp_x

    conf = args.config

    in_dir = args.tsv_dir
    tsv_files = os.listdir(in_dir)

    for f in tsv_files:
        xlang = f[3:5]

        f = os.path.join(in_dir, f)
        zh_fn = f + ".zh"
        x_fn = f + "." + xlang

        if x2zh:
            lang_pair = xlang + "-zh"
            src_path = x_fn
            ref_path = zh_fn
        else:
            lang_pair = "zh-" + xlang
            src_path = zh_fn
            ref_path = x_fn

        print(lang_pair, f, zh_fn, x_fn)

        pair_to_single(f, zh_fn, x_fn)

        run_eval(conf, src_path, ref_path, sp_src, sp_tgt, lang_pair)