import io
import os
import random


def is_ascii_char(s):
    """Is it an ASCII char"""
    return len(s) == 1 and '\u0000' < s[0] < '\u00ff'


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
