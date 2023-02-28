import gzip
import io
import os
import random
import re
import zipfile

import regex
import zhconv
import lxml.etree as ET


def is_ascii_char(s):
    """Is it an ASCII char"""
    return len(s) == 1 and '\u0000' < s[0] < '\u00ff'


def is_ascii(s):
    """All are ASCII chars"""
    return all(map(is_ascii_char, s))


def is_zh_char(s):
    """Is it a Chinese char"""
    return len(s) == 1 and '\u4e00' <= s[0] <= '\u9fa5'


def has_zh(s):
    """Does it contain Chinese char?"""
    for c in s:
        if is_zh_char(c):
            return True
    return False


def same_lines(path1, path2):
    """Two text files have the same numbers of lines?"""
    lines1 = 0
    lines2 = 0
    with open(path1, encoding="utf-8") as f:
        for _ in f:
            lines1 += 1

    with open(path2, encoding="utf-8") as f:
        for _ in f:
            lines2 += 1

    if lines1 == lines2:
        return True
    else:
        return False


def is_bitext(file_path):
    """The file is bitext?"""
    with open(file_path, encoding="utf-8") as f:
        for line in f:
            if len(line.split("\t")) != 2:
                return False
        return True


def single_to_pair(src_path, tgt_path, pair_path):
    """Combine source and target file into a parallel one"""
    assert same_lines(src_path, tgt_path)

    src_f = io.open(src_path, encoding="utf-8")
    tgt_f = io.open(tgt_path, encoding="utf-8")
    out_f = io.open(pair_path, "w", encoding="utf-8")

    cnt = 0
    for p in zip(src_f, tgt_f):
        out_f.write(p[0].strip() + "\t" + p[1].strip() + "\n")
        cnt += 1
        if cnt % 100000 == 0:
            print(cnt)
    print(cnt)
    out_f.close()


def pair_to_single(pair_path, src_path, tgt_path):
    """Split a parallel file into source ang target file"""
    src_f = io.open(src_path, "w", encoding="utf-8")
    tgt_f = io.open(tgt_path, "w", encoding="utf-8")

    tsv_f = io.open(pair_path, encoding="utf-8")
    cnt = 0
    for line in tsv_f:
        line = line.strip()
        if len(line) == 0:
            continue
        p = line.split("\t")
        if len(p) >= 2:
            src_f.write(p[0] + "\n")
            tgt_f.write(p[1] + "\n")

        cnt += 1
        if cnt % 500000 == 0:
            print(cnt)

    print(cnt)
    src_f.close()
    tgt_f.close()


def sample(files, n):
    """"Sample sentences from bitext or source and target file"""
    in_files = [io.open(f, encoding="utf-8") for f in files]
    out_files = [io.open("{}-{}".format(f, n), "w", encoding="utf-8") for f in files]

    sampled = 0
    for p in zip(*in_files):
        prob = random.uniform(0, 1)
        if prob > 0.5:
            for i in range(len(out_files)):
                out_files[i].write(p[i].strip() + "\n")
            sampled += 1
            if sampled >= n:
                break

    for f in out_files:
        f.close()


def count_lines(fn):
    lines = 0
    with open(fn, encoding="utf-8") as f:
        for _ in f:
            lines += 1

    return lines


def split(files, num_per_file):
    """Split corpus into multiple files with the same lines"""
    in_files = [io.open(f, encoding="utf-8") for f in files]

    cnt = 0
    n_f = 0

    print("File", n_f)
    out_files = [io.open("{}-{}".format(f, n_f), "w", encoding="utf-8") for f in files]

    for p in zip(*in_files):
        cnt += 1

        for i in range(len(out_files)):
            out_files[i].write(p[i].strip() + "\n")

        if cnt % 100000 == 0:
            print(cnt)

        if cnt % num_per_file == 0:
            for f in out_files:
                f.close()
            n_f += 1

            out_files = [io.open("{}-{}".format(f, n_f), "w", encoding="utf-8") for f in files]
            print("File", n_f)

    for f in out_files:
        f.close()

    print(cnt)


def merge(data_root, out_fn):
    """Merge files in a directory into one file"""
    data_files = [os.path.join(data_root, f) for f in os.listdir(data_root)]

    out_path = os.path.join(data_root, out_fn)
    out_f = io.open(out_path, "w", encoding="utf-8")

    cnt = 0
    for f in data_files:
        in_f = io.open(f, encoding="utf-8")
        for line in in_f:
            line = line.strip()
            if len(line) > 0:
                out_f.write(line + "\n")
                cnt += 1
                if cnt % 100000 == 0:
                    print(cnt)

    print(cnt)
    out_f.close()


def hant_2_hans(hant_str: str):
    """Traditional Chinese to Simplified Chinese"""
    return zhconv.convert(hant_str, 'zh-hans')


not_letter = regex.compile(r'[^\p{L}]')


def norm(s):
    s = s.lower()
    s = regex.sub(not_letter, "", s)
    return s


def from_sgm(sgm_path, out_path):
    """Convert sgm file of WMT into plain text"""
    pattern = re.compile(r"<seg id=\"\d+\">(.+?)</seg>")

    lines = "\r".join(io.open(sgm_path, encoding="utf-8").readlines())

    out_f = io.open(out_path, "w", encoding="utf-8")

    for m in re.finditer(pattern, lines):
        print(m.group(1))
        out_f.write(m.group(1) + "\n")

    out_f.close()


def from_xml(xml_file, attr="[@translator='A']"):
    """Convert XML file of WMT into plain text"""
    output_stem = xml_file[:-4]

    pair = xml_file.split(".")[-2]
    src, tgt = pair.split("-")

    tree = ET.parse(xml_file)
    # NOTE: Assumes exactly one translation

    with open(output_stem + "." + src, "w", encoding="utf-8") as ofh:
        for seg in tree.getroot().findall(".//src//seg"):
            print(seg.text, file=ofh)

    with open(output_stem + "." + tgt, "w", encoding="utf-8") as ofh:
        for seg in tree.getroot().findall(".//ref" + attr + "//seg" ):
            print(seg.text, file=ofh)


def extract_zips(zips_dir, out_dir=None):
    """Unzip zip files in a directory into out directory"""
    if out_dir is None:
        out_dir = os.path.join(zips_dir, "unzip")

    zips = os.listdir(zips_dir)
    for zipf in zips:
        if not zipf.endswith(".zip"):
            continue

        print("Unzip " + zipf)

        zFile = zipfile.ZipFile(os.path.join(zips_dir, zipf), "r")
        for fileM in zFile.namelist():
            if fileM.rfind(".") == len(fileM)-3 or fileM.rfind(".") == len(fileM)-6:
                zFile.extract(fileM, out_dir)
        zFile.close()


def extract_gzips(zips_dir, out_dir=None):
    """Unzip gz files in a directory into out directory"""
    if out_dir is None:
        out_dir = os.path.join(zips_dir, "unzip")

    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    zips = os.listdir(zips_dir)
    for zipf in zips:
        if not zipf.endswith(".gz"):
            continue

        print("Unzip " + zipf)

        gf = gzip.GzipFile(mode="rb", filename=os.path.join(zips_dir, zipf))
        open(os.path.join(out_dir, zipf.replace(".gz", "")), "wb").write(gf.read())


def merge_moses(in_dir, source_lang=None, target_lang=None, out_dir=None):
    assert source_lang is not None or target_lang is not None

    if out_dir is None:
        out_dir = os.path.join(in_dir, "tsv")

    files = os.listdir(in_dir)
    assert len(files)%2 == 0

    files = list(sorted(files))

    if not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    for i in range(0, len(files), 2):
        f1 = files[i]
        f2 = files[i+1]
        idx = f1.rfind(".")
        bname = f1[:idx]
        outf = os.path.join(out_dir, bname + ".tsv")
        f1 = os.path.join(in_dir, f1)
        f2 = os.path.join(in_dir, f2)
        if source_lang is not None:
            if f1.endswith(source_lang):
                print(f1, f2, outf)
                single_to_pair(f1, f2, outf)
            elif f2.endswith(source_lang):
                print(f2, f1, outf)
                single_to_pair(f2, f1, outf)
        elif target_lang is not None:
            if f1.endswith(target_lang):
                print(f2, f1, outf)
                single_to_pair(f2, f1, outf)
            elif f2.endswith(target_lang):
                print(f1, f2, outf)
                single_to_pair(f1, f2, outf)
