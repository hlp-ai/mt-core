import argparse
import os

import ctranslate2
import sentencepiece as spm
from tqdm import tqdm

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--m2m", default=r"D:\kidden\mt\m2m100_418m", help="m2m-100 ct2 model path")
    argparser.add_argument("-gt", required=True, help="zh-x tsv test file")
    argparser.add_argument("--sl", required=True, help="two-letter source language code")
    argparser.add_argument("--tl", default="zh", help="two-letter target language code")

    args = argparser.parse_args()

    m2m100_dir = args.m2m
    sp_model_file = os.path.join(m2m100_dir, "sentencepiece.model")

    print("Loading m2m100 SentencePiece model...")
    sp_source_model = spm.SentencePieceProcessor(sp_model_file)

    print("Loading m2m100 model...")
    translator = ctranslate2.Translator(m2m100_dir, device="cpu")

    gt_tsv = args.gt
    x = []
    zhs = []
    with open(gt_tsv, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            parts = line.split("\t")
            x.append(parts[1])
            zhs.append(parts[0])

    print("# of pairs:", len(x))

    src_lang = args.sl
    tgt_lang = args.tl
    lang_pair = src_lang + "-" + tgt_lang

    src_prefix = "__" + src_lang + "__"
    tgt_prefix = "__" + tgt_lang + "__"

    if src_lang == "zh":
        srcs = zhs
        refs = x
    else:
        srcs = x
        refs = zhs

    translations = []

    batch_size = 8
    for i in tqdm(range(0, len(srcs), batch_size), desc="Translating"):
        split = srcs[i:i + batch_size]
        source_sents_tok = sp_source_model.encode(split, out_type=str)
        source_sents_tok = [[src_prefix] + sent for sent in source_sents_tok]

        translations_tok = translator.translate_batch(
            source=source_sents_tok,
            beam_size=5,
            batch_type="tokens",
            max_batch_size=1024,
            replace_unknowns=True,
            repetition_penalty=1.2,
            target_prefix=[[tgt_prefix]] * len(split),
        )

        translations_so_far = [
            " ".join(translation[0]["tokens"])
                .replace(" ", "")
                .replace("▁", " ")
                .replace(tgt_prefix, "")
                .strip()
            for translation in translations_tok
        ]
        translations.extend(translations_so_far)

    ref_file = "ref-" + lang_pair + ".txt"
    hyp_file = "hyp-" + lang_pair + ".txt"

    with open(hyp_file, "w", encoding="utf-8") as f:
        for trans in translations:
            f.write(trans + "\n")

    with open(ref_file, "w", encoding="utf-8") as f:
        for i in range(len(refs)):
            f.write(refs[i] + "\n")

    cal_cmd = "sacrebleu {} -i {} -l {} -f text -m bleu"
    cf = os.popen(cal_cmd.format(ref_file, hyp_file, lang_pair))
    lines = cf.readlines()
    for line in lines:
        print(line.strip())