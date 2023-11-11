"""为One-to-Many添加翻译方向标记，例如<toen>"""
import argparse
from tqdm import tqdm


def add_token(tsv_file, add_src, token):
    """给TSV格式平行语料添加翻译方向标记

    :param tsv_file: src\ttgt格式平行语料
    :param add_src: 在src部分添加标记，否则在tgt部分添加标记
    :param token: 添加的标记
    :return:
    """
    out_file = tsv_file + ".tag"
    with open(tsv_file, encoding="utf-8") as raw, open(out_file, "w", encoding="utf-8") as out:
        for line in tqdm(raw):
            parts = line.strip().split("\t")
            if len(parts) != 2:
                continue

            src, tgt = parts
            if add_src:
                src = token + src
            else:
                tgt = token + tgt

            out.write(src + "\t" + tgt + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tsv_file", required=True, help="tsv file")
    parser.add_argument("--to", default="tgt", type=str, help="add token to src or tag of tsv file")
    parser.add_argument("--token", required=True, help="token to add")
    args = parser.parse_args()

    input = args.tsv_file
    tosrc = True
    if args.to == "tgt":
        tosrc = False

    add_token(input, tosrc, args.token)