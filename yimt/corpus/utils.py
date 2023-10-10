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

    total = count_lines(files[0])
    print(total)

    sampled = 0
    scanned = 0
    sample_prob = (1.1*n) / total
    for p in zip(*in_files):
        scanned += 1
        prob = random.uniform(0, 1)
        if prob < sample_prob:
            for i in range(len(out_files)):
                out_files[i].write(p[i].strip() + "\n")
            sampled += 1
            if sampled % 10000 == 0:
                print(scanned, sampled)
            if sampled >= n:
                break
    print(scanned, sampled)

    for f in out_files:
        f.close()


def partition(files, n):
    """"Partition a corpus with N sentences into a corpus with n sentences and a corpus with N-n sentences"""
    in_files = [io.open(f, encoding="utf-8") for f in files]
    out_files = [io.open("{}-{}".format(f, n), "w", encoding="utf-8") for f in files]
    new_files = [io.open(f+".new", "w", encoding="utf-8") for f in files]

    total = count_lines(files[0])
    print(total)

    sampled = 0
    scanned = 0
    sample_prob = (1.1*n) / total
    done = False
    for p in zip(*in_files):
        scanned += 1
        prob = random.uniform(0, 1)
        if not done and prob < sample_prob:
            for i in range(len(out_files)):
                out_files[i].write(p[i].strip() + "\n")
            sampled += 1
            if sampled % 10000 == 0:
                print(scanned, sampled)
            if sampled >= n:
                done = True
        else:
            for i in range(len(new_files)):
                new_files[i].write(p[i].strip() + "\n")
    print(scanned, sampled)

    for f in out_files:
        f.close()

    for f in new_files:
        f.close()


def count_lines(fn):
    print("Counting lines...")
    lines = 0
    interval = 500000
    with open(fn, encoding="utf-8") as f:
        for _ in f:
            lines += 1
            if lines % interval == 0:
                print(lines)

    print(lines)

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


not_letter = regex.compile(r'[^\p{L}]')


def norm(s, lower=True, remove_noletter=True):
    if lower:
        s = s.lower()

    if remove_noletter:
        s = regex.sub(not_letter, "", s)
    return s


def interset(tsv_file1, tsv_file2, out_file, creterion="SRC",
             lower=True, remove_noletter=True):
    pairs = set()
    srcs = set()
    tgts = set()
    total = 0
    print("Scanning file1...")
    with open(tsv_file1, encoding="utf-8") as bf:
        for p in bf:
            total += 1
            if total % 10000 == 0:
                print(total)
            p = p.strip()
            pp = p.split("\t")
            if len(pp) != 2:
                continue
            src = pp[0].strip()
            tgt = pp[1].strip()
            src = norm(src, lower, remove_noletter)
            hs = hash(src)
            srcs.add(hs)

            tgt = norm(tgt, lower, remove_noletter)
            ht = hash(tgt)
            tgts.add(ht)

            p = norm(p, lower, remove_noletter)
            h = hash(p)
            pairs.add(h)

    print(total)

    intersected = 0
    total = 0

    print("Scanning file2...")
    with open(tsv_file2, encoding="utf-8") as f, open(out_file, "w", encoding="utf-8") as out_f:
        for p in f:
            p = p.strip()
            total += 1
            if total % 100000 == 0:
                print("Total:", total, "Intersected:", intersected)

            if creterion == "SRC" or creterion == "TGT":
                pp = p.split("\t")
                if len(pp) != 2:
                    continue
                src = pp[0].strip()
                tgt = pp[1].strip()
                if creterion == "SRC":
                    src = norm(src, lower, remove_noletter)
                    hs = hash(src)
                    if hs in srcs:
                        out_f.write(p + "\n")
                        intersected += 1
                else:
                    tgt = norm(tgt, lower, remove_noletter)
                    ht = hash(tgt)
                    if ht in tgts:
                        out_f.write(p + "\n")
                        intersected += 1
            else:
                pn = norm(p, lower, remove_noletter)
                h = hash(pn)
                if h in pairs:
                    out_f.write(p + "\n")
                    intersected += 1

    print("Total:", total, "Intersected:", intersected)


def diff(tsv_file1, tsv_file2, out_file, creterion="SRC",
             lower=True, remove_noletter=True):
    pairs = set()
    srcs = set()
    tgts = set()
    total = 0
    print("Scanning file2...")
    with open(tsv_file2, encoding="utf-8") as bf:
        for p in bf:
            total += 1
            if total % 10000 == 0:
                print(total)
            p = p.strip()
            pp = p.split("\t")
            if len(pp) != 2:
                continue
            src = pp[0].strip()
            tgt = pp[1].strip()
            src = norm(src, lower, remove_noletter)
            hs = hash(src)
            srcs.add(hs)

            tgt = norm(tgt, lower, remove_noletter)
            ht = hash(tgt)
            tgts.add(ht)

            p = norm(p, lower, remove_noletter)
            h = hash(p)
            pairs.add(h)

    print(total)

    differed = 0
    total = 0

    print("Scanning file1...")
    with open(tsv_file1, encoding="utf-8") as f, open(out_file, "w", encoding="utf-8") as out_f:
        for p in f:
            p = p.strip()
            total += 1
            if total % 100000 == 0:
                print("Total:", total, "Differed:", differed)

            if creterion == "SRC" or creterion == "TGT":
                pp = p.split("\t")
                if len(pp) != 2:
                    continue
                src = pp[0].strip()
                tgt = pp[1].strip()
                if creterion == "SRC":
                    src = norm(src, lower, remove_noletter)
                    hs = hash(src)
                    if hs not in srcs:
                        out_f.write(p + "\n")
                        differed += 1
                else:
                    tgt = norm(tgt, lower, remove_noletter)
                    ht = hash(tgt)
                    if ht not in tgts:
                        out_f.write(p + "\n")
                        differed += 1
            else:
                pn = norm(p, lower, remove_noletter)
                h = hash(pn)
                if h not in pairs:
                    out_f.write(p + "\n")
                    differed += 1

    print("Total:", total, "Differed:", differed)
