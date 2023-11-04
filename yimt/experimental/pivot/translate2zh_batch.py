import time
from argparse import ArgumentParser

import ctranslate2

from yimt.segmentation.sp import load_spm, tokenize_file_sp, detokenize_file_sp
from yimt.segmentation.detok_zh import detok_zh_file
from yimt.corpus.misc import pair_to_single, single_to_pair


def _translate(translator, in_file, out_file, batch_size = 48):
    with open(in_file, encoding="utf-8") as f:
        lines = f.readlines()

    out = open(out_file, "w", encoding="utf-8")

    start = time.time()
    n = 0
    for i in range(0, len(lines), batch_size):
        if i + batch_size < len(lines):
            to_translate = lines[i:i + batch_size]
        else:
            to_translate = lines[i:]

        to_translate = [s.strip().split() for s in to_translate]

        translations_tok = translator.translate_batch(
            source=to_translate,
            beam_size=5,
            batch_type="tokens",
            max_batch_size=1024,
            replace_unknowns=True,
            repetition_penalty=1.2,
            target_prefix=None,
        )

        translations = [" ".join(translation[0]["tokens"])
                        for translation in translations_tok]

        n += len(to_translate)

        if n%(batch_size*10) == 0:
            etime = time.time() - start
            speed = float(n) / etime
            print("{} sentences, {:.2f} sentences/sec, {:.2f} sec".format(n, speed, etime))

        for t in translations:
            out.write(t + "\n")

    out.close()

    etime = time.time() - start
    speed = float(n) / etime
    print("{} sentences, {:.2f} sentences/sec, {:.2f} sec".format(n, speed, etime))


if __name__ == "__main__":
    argparser = ArgumentParser()
    argparser.add_argument("-i", "--input", required=True, help="TSV file pattern to be translate")
    argparser.add_argument("-b", "--begin", default=0, type=int, help="start number for pattern")
    argparser.add_argument("-e", "--end", required=True, type=int, help="end number for pattern")
    argparser.add_argument("-s", "--src", required=True, help="Souce language")
    argparser.add_argument("-t", "--tgt", required=True, help="Target language")
    argparser.add_argument("-se", "--sp_en_model",
                           default= r"/home/liuxf/hdisk/exp/sp/opus-enzh-all-sf.en-sp-32000.model",
                           help="EN sp model path")
    argparser.add_argument("-sz", "--sp_zh_model",
                           default= r"/home/liuxf/hdisk/exp/sp/opus-enzh-all-sf.zh.pretok-sp-32000.model",
                           help="ZH sp model path")
    argparser.add_argument("-m", "--ct2_zh_model",
                           default=r"/home/liuxf/hdisk/exp/en-zh/opus/run2/model/ct2",
                           help="en-to-zh ct2 model path")

    args = argparser.parse_args()

    tsv_file_pattern = args.input  # r"/home/liuxf/hdisk/exp/hi-en/score/sf/opus-en-hi.raw.tsv.norm.dedup.filter-{}-sf"
    from_no = args.begin
    end_no = args.end

    sp_en_file = args.sp_en_model  # r"/home/liuxf/hdisk/exp/sp/opus-enzh-all-sf.en-sp-32000.model"
    sp_en = load_spm(sp_en_file)

    sp_zh_file = args.sp_zh_model  # r"/home/liuxf/hdisk/exp/sp/opus-enzh-all-sf.zh.pretok-sp-32000.model"
    sp_zh = load_spm(sp_zh_file)

    src_lang = args.src
    tgt_lang = args.tgt

    for i in range(from_no, end_no):
        tsv_file = tsv_file_pattern.format(i)
        print("\nProcessing", tsv_file)
        src_file = tsv_file + "." + src_lang
        tgt_file = tsv_file + "." + tgt_lang

        if src_lang == "en":
            to_translate = src_file
            un_translate = tgt_file
        else:
            to_translate = tgt_file
            un_translate = src_file

        print("Splitting {} into {} and {}...".format(tsv_file, src_file, tgt_file))
        pair_to_single(tsv_file, src_file, tgt_file)

        model_dir = args.ct2_zh_model  # r"/home/liuxf/hdisk/exp/en-zh/opus/run2/model/ct2"
        translator = ctranslate2.Translator(
            model_dir,
            device="cuda"
        )

        tok_output = to_translate + ".tok"
        print("Tokenizing {} into {}...".format(to_translate, tok_output))
        tokenize_file_sp(sp_en, to_translate, tok_output)

        out_file = tok_output + ".tozh"
        print("Translating {} into {}...".format(tok_output, out_file))
        _translate(translator, tok_output, out_file)

        detok_file = out_file + ".det"

        print("Detokenizing {} into {}...".format(out_file, detok_file))
        detokenize_file_sp(sp_zh, out_file, detok_file)

        zh_file = detok_file + ".zh"
        detok_zh_file(detok_file, zh_file)

        single_to_pair(un_translate, zh_file, tsv_file + ".aug2zh")
