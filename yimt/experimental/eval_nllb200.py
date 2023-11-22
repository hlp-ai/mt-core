import argparse
import os

import ctranslate2  # 3.11
import sentencepiece as spm
from tqdm import tqdm

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--nllb", default=r"D:\kidden\mt\nllb200\nllb-200-distilled-600M-int8",
                           help="NLLB200 ct2 model path")
    argparser.add_argument("--sp", default=r"D:\kidden\mt\nllb200\flores200_sacrebleu_tokenizer_spm.model",
                           help="NLLB200 sentencepiece model path")
    argparser.add_argument("-gt", required=True, help="zh-x tsv test file")
    argparser.add_argument("-sl", required=True, help="NLLB language code, for example afr_Latn")
    argparser.add_argument("-sl2", required=True, help="two-letter source language code")
    argparser.add_argument("-tl", default="zho_Hans", help="NLLB language code")
    argparser.add_argument("-tl2", default="zh", help="two-letter target language code")

    args = argparser.parse_args()

    nllb_dir = args.nllb
    sp_model_file = args.sp

    print("Loading NLLB SentencePiece model...")
    sp = spm.SentencePieceProcessor(sp_model_file)

    print("Loading NLLB model...")
    translator = ctranslate2.Translator(nllb_dir, device="cpu")

    gt_tsv = args.gt
    srcs = []
    zhs = []
    with open(gt_tsv, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            parts = line.split("\t")
            srcs.append(parts[1])
            zhs.append(parts[0])

    print("# of pairs:", len(srcs))

    src_lang = args.sl
    tgt_lang = args.tl
    lang_pair = args.sl2 + "-" + args.tl2

    translations = []

    batch_size = 8
    for i in tqdm(range(0, len(srcs), batch_size), desc="Translating"):
        split = srcs[i:i + batch_size]

        source_sentences = [sent.strip() for sent in split]
        target_prefix = [[tgt_lang]] * len(source_sentences)

        source_sents_subworded = [sp.encode_as_pieces(ss) for ss in source_sentences]
        source_sents_subworded = [[src_lang] + sent + ["</s>"] for sent in source_sents_subworded]

        translations_subworded = translator.translate_batch(source_sents_subworded,
                                                            batch_type="tokens",
                                                            max_batch_size=1024,
                                                            beam_size=4,
                                                            target_prefix=target_prefix)
        translations_subworded = [translation.hypotheses[0] for translation in translations_subworded]
        for translation in translations_subworded:
            if tgt_lang in translation:
                translation.remove(tgt_lang)

        # Desubword the target sentences
        translations_so_far = sp.decode(translations_subworded)

        translations.extend(translations_so_far)

    ref_file = "ref-" + lang_pair + ".txt"
    hyp_file = "hyp-" + lang_pair + ".txt"

    with open(hyp_file, "w", encoding="utf-8") as f:
        for trans in translations:
            f.write(trans + "\n")

    with open(ref_file, "w", encoding="utf-8") as f:
        for i in range(len(translations)):
            f.write(zhs[i] + "\n")

    cal_cmd = "sacrebleu {} -i {} -l {} -f text -m bleu"
    cf = os.popen(cal_cmd.format(ref_file, hyp_file, lang_pair))
    lines = cf.readlines()
    for line in lines:
        print(line.strip())
