import os

import ctranslate2
import sentencepiece as spm
from tqdm import tqdm

m2m100_dir = r"D:\kidden\mt\m2m100_418m"
sp_model_file = os.path.join(m2m100_dir, "sentencepiece.model")

print("Loading m2m100 SentencePiece model...")
sp_source_model = spm.SentencePieceProcessor(sp_model_file)

print("Loading m2m100 model...")
translator = ctranslate2.Translator(m2m100_dir, device="cuda")

gt_tsv = r"D:\dataset\zh-x-val\flores\flores101_dev\zho_simpl-lao_dev.txt"
srcs = []
zhs = []
with open(gt_tsv, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        parts = line.split("\t")
        srcs.append(parts[1])
        zhs.append(parts[0])

print("# of pairs:", len(srcs))

src_lang = "lo"
tgt_lang = "zh"
lang_pair = src_lang + "-" + tgt_lang

src_prefix = "__" + src_lang + "__"
tgt_prefix = "__" + tgt_lang + "__"

translations = []

batch_size = 8
for i in tqdm(range(0, len(srcs), batch_size)):
    split = srcs[i:(i+1)*batch_size]
    source_sents_tok = sp_source_model.encode(split, out_type=str)
    source_sents_tok = [[src_prefix] + sent for sent in source_sents_tok]

    translations_tok = translator.translate_batch(
        source=source_sents_tok,
        beam_size=5,
        batch_type="tokens",
        max_batch_size=1024,
        replace_unknowns=True,
        repetition_penalty=1.2,
        target_prefix=[[tgt_prefix]]*len(split),
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
    for i in range(len(translations)):
        f.write(zhs[i] + "\n")

cal_cmd = "sacrebleu {} -i {} -l {} -f text -m bleu"
cf = os.popen(cal_cmd.format(ref_file, hyp_file, lang_pair))
lines = cf.readlines()
for line in lines:
    print(line.strip())