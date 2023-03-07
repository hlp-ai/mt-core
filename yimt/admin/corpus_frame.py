import os
import tkinter as tk
from tkinter import *
import tkinter.messagebox
from functools import partial

from yimt.admin.win_utils import ask_open_file, ask_dir, ask_save_file
from yimt.corpus.dedup import dedup
from yimt.corpus.tokenize_file import tokenize_single, detok_zh
from yimt.corpus.utils import pair_to_single, single_to_pair, merge, sample, split, merge_moses, extract_zips, \
    extract_gzips
import yimt.corpus.bin.normalize as norm
import yimt.corpus.bin.filter as filt


def create_tsv2mono_corpus(parent):
    tk.Label(parent, text="path of parallel file").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_corpus_pair = tk.Entry(parent, width=50)
    entry_corpus_pair.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_corpus_pair)).grid(row=0, column=2,
                                                                                                padx=10, pady=5)

    tk.Label(parent, text="path of source file").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_corpus_src = tk.Entry(parent, width=50)
    entry_corpus_src.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_save_file, entry=entry_corpus_src)).grid(row=1, column=2, padx=10,
                                                                                               pady=5)

    tk.Label(parent, text="path of target file").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    entry_corpus_tgt = tk.Entry(parent, width=50)
    entry_corpus_tgt.grid(row=2, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_save_file, entry=entry_corpus_tgt)).grid(row=2, column=2, padx=10,
                                                                                               pady=5)

    def go():
        corpus_pair = entry_corpus_pair.get().strip()
        corpus_src = entry_corpus_src.get().strip()
        corpus_tgt = entry_corpus_tgt.get().strip()

        if len(corpus_pair) == 0 or len(corpus_src) == 0 or len(corpus_tgt) == 0:
            tk.messagebox.showinfo(title="Info", message="Some parameter empty.")
            return

        pair_to_single(corpus_pair, corpus_src, corpus_tgt)

        tk.messagebox.showinfo(title="Info", message="done")

    tk.Button(parent, text="Split a parallel file into source ang target file", command=go).grid(row=5, column=1,
                                                                                                 padx=10, pady=5)


def create_mono2tsv_corpus(parent):
    tk.Label(parent, text="path of source file").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_corpus_src = tk.Entry(parent, width=50)
    entry_corpus_src.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_corpus_src)).grid(row=0, column=2,
                                                                                               padx=10, pady=5)

    tk.Label(parent, text="path of target file").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_corpus_tgt = tk.Entry(parent, width=50)
    entry_corpus_tgt.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_corpus_tgt)).grid(row=1, column=2, padx=10,
                                                                                               pady=5)

    tk.Label(parent, text="path of parallel file").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    entry_corpus_pair = tk.Entry(parent, width=50)
    entry_corpus_pair.grid(row=2, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_save_file, entry=entry_corpus_pair)).grid(row=2, column=2,
                                                                                                padx=10,
                                                                                                pady=5)

    def go():
        corpus_pair = entry_corpus_pair.get().strip()
        corpus_src = entry_corpus_src.get().strip()
        corpus_tgt = entry_corpus_tgt.get().strip()

        if len(corpus_pair) == 0 or len(corpus_src) == 0 or len(corpus_tgt) == 0:
            tk.messagebox.showinfo(title="Info", message="Some parameter empty.")
            return
        single_to_pair(corpus_src, corpus_tgt, corpus_pair)
        tk.messagebox.showinfo(title="Info", message="done")

    tk.Button(parent, text="Combine source and target file into a parallel one", command=go).grid(row=5, column=1,
                                                                                                  padx=10, pady=5)


def create_unzip_corpus(parent):
    tk.Label(parent, text="Path of data").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_corpus_datapath = tk.Entry(parent, width=50)
    entry_corpus_datapath.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_dir, entry=entry_corpus_datapath)).grid(row=0, column=2,
                                                                                              padx=10, pady=5)

    tk.Label(parent, text="Output Directory (Optional)").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_corpus_output = tk.Entry(parent, width=50)
    entry_corpus_output.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_save_file, entry=entry_corpus_output)).grid(row=1, column=2, padx=10,
                                                                                               pady=5)

    tk.Label(parent, text="Compression Format").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    entry_format = tk.Entry(parent, width=50)
    entry_format.grid(row=2, column=1, padx=10, pady=5)
    entry_format.insert(0, "zip")

    def go():
        corpus_datapath = entry_corpus_datapath.get().strip()
        unzip_dir = entry_corpus_output.get().strip()
        format = entry_format.get().strip()
        if len(unzip_dir) == 0:
            unzip_dir = None

        if len(corpus_datapath) == 0:
            tk.messagebox.showinfo(title="Info", message="Corpus directory empty.")
            return

        if format == "zip":
            extract_zips(corpus_datapath, unzip_dir)
        elif format == "gz":
            extract_gzips(corpus_datapath, unzip_dir)

        tk.messagebox.showinfo(title="Info", message="done")

    tk.Button(parent, text="Unzip files", command=go).grid(row=3, column=1, padx=10, pady=5)


def create_merge_corpus(parent):
    tk.Label(parent, text="Path of data").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_corpus_datapath = tk.Entry(parent, width=50)
    entry_corpus_datapath.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_dir, entry=entry_corpus_datapath)).grid(row=0, column=2,
                                                                                              padx=10, pady=5)

    tk.Label(parent, text="Output file").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_corpus_tgt = tk.Entry(parent, width=50)
    entry_corpus_tgt.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_save_file, entry=entry_corpus_tgt)).grid(row=1, column=2, padx=10,
                                                                                               pady=5)

    def go():
        corpus_datapath = entry_corpus_datapath.get().strip()
        corpus_tgt = entry_corpus_tgt.get().strip()

        if len(corpus_datapath) == 0 or len(corpus_tgt) == 0:
            tk.messagebox.showinfo(title="Info", message="Some parameter empty.")
            return

        merge(corpus_datapath, corpus_tgt)
        tk.messagebox.showinfo(title="Info", message="done")

    tk.Button(parent, text="Merge files in a directory into one file", command=go).grid(row=5, column=1,
                                                                                        padx=10, pady=5)


def create_merge_moses_corpus(parent):
    tk.Label(parent, text="Input directory").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_mergemoses_datapath = tk.Entry(parent, width=50)
    entry_mergemoses_datapath.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_dir, entry=entry_mergemoses_datapath)).grid(row=0, column=2,
                                                                                                  padx=10, pady=5)

    tk.Label(parent, text="Output directory(Optional)").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_mergemoses_outpath = tk.Entry(parent, width=50)
    entry_mergemoses_outpath.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_dir, entry=entry_mergemoses_outpath)).grid(row=1, column=2, padx=10,
                                                                                             pady=5)

    tk.Label(parent, text="Source language").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    entry_mergemoses_sl = tk.Entry(parent, width=50)
    entry_mergemoses_sl.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(parent, text="Target language").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    entry_mergemoses_tl = tk.Entry(parent, width=50)
    entry_mergemoses_tl.grid(row=3, column=1, padx=10, pady=5)

    def go():
        corpus_mergemoses_datapath = entry_mergemoses_datapath.get().strip()
        corpus_output_path = entry_mergemoses_outpath.get().strip()
        if len(corpus_output_path) == 0:
            corpus_output_path = None
        corpus_mergemoses_sl = entry_mergemoses_sl.get().strip()
        if len(corpus_mergemoses_sl) == 0:
            corpus_mergemoses_sl = None
        corpus_mergemoses_tl = entry_mergemoses_tl.get().strip()
        if len(corpus_mergemoses_tl) == 0:
            corpus_mergemoses_tl = None

        merge_moses(corpus_mergemoses_datapath, corpus_mergemoses_sl, corpus_mergemoses_tl, corpus_output_path)
        tk.messagebox.showinfo(title="Info", message="done")

    tk.Button(parent, text="Merge", command=go).grid(row=5, column=1, padx=10, pady=5)


def create_normalize_corpus(parent):
    tk.Label(parent, text="Input TSV file").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_normalize_in = tk.Entry(parent, width=50)
    entry_normalize_in.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_normalize_in)).grid(row=0, column=2,
                                                                                                 padx=10, pady=5)

    tk.Label(parent, text="Output file (Optional)").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_normalize_out = tk.Entry(parent, width=50)
    entry_normalize_out.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_save_file, entry=entry_normalize_out)).grid(row=1, column=2,
                                                                                                  padx=10,
                                                                                                  pady=5)

    tk.Label(parent, text="About Chinese").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    entry_zh = tk.Entry(parent, width=50)
    entry_zh.grid(row=2, column=1, padx=10, pady=5)
    entry_zh.insert(0, "tozh")

    def go():
        corpus_normalize_in = entry_normalize_in.get().strip()
        corpus_normalize_out = entry_normalize_out.get().strip()
        if len(corpus_normalize_out) == 0:
            corpus_normalize_out = corpus_normalize_in + ".norm"

        zh = entry_zh.get().strip()

        if len(corpus_normalize_in) == 0:
            tk.messagebox.showinfo(title="Info", message="Input parameter empty.")
            return

        norm.main(corpus_normalize_in, corpus_normalize_out, zh)

        tk.messagebox.showinfo(title="Info", message="done")

    tk.Button(parent, text="Normalize bitext", command=go).grid(row=5, column=1, padx=10, pady=5)


def create_filter_corpus(parent):
    tk.Label(parent, text="Input TSV file").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_filter_in = tk.Entry(parent, width=50)
    entry_filter_in.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_filter_in)).grid(row=0, column=2,
                                                                                              padx=10, pady=5)

    tk.Label(parent, text="Output file").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_filter_out = tk.Entry(parent, width=50)
    entry_filter_out.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_save_file, entry=entry_filter_out)).grid(row=1, column=2,
                                                                                               padx=10, pady=5)

    tk.Label(parent, text="Language Pair").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    entry_filter_langpair = tk.Entry(parent, width=50)
    entry_filter_langpair.grid(row=2, column=1, padx=10, pady=5)
    entry_filter_langpair.insert(0, "en-zh")

    def go():
        corpus_filter_in = entry_filter_in.get().strip()
        corpus_filter_out = entry_filter_out.get().strip()
        corpus_filter_langpair = entry_filter_langpair.get().strip()

        if len(corpus_filter_in) == 0 or len(corpus_filter_out) == 0:
            tk.messagebox.showinfo(title="Info", message="Some parameter empty.")
            return

        filt.main(corpus_filter_in, corpus_filter_out, corpus_filter_langpair)

        tk.messagebox.showinfo(title="Info", message="done")

    tk.Button(parent, text="Filter", command=go).grid(row=5, column=1, padx=10, pady=5)


def create_dedup_corpus(parent):
    tk.Label(parent, text="Input TSV file").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_dedup_in = tk.Entry(parent, width=50)
    entry_dedup_in.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_dedup_in)).grid(row=0, column=2,
                                                                                             padx=10, pady=5)

    tk.Label(parent, text="Output file (Optional)").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_dedup_out = tk.Entry(parent, width=50)
    entry_dedup_out.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_save_file, entry=entry_dedup_out)).grid(row=1, column=2,
                                                                                              padx=10, pady=5)

    tk.Label(parent, text="Dedup condition").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    var_srctgt = IntVar()
    check_srctgt = Checkbutton(parent, text="Source and Target", variable=var_srctgt, onvalue=1, offvalue=0)
    check_srctgt.grid(row=2, column=1, padx=10, pady=5)
    check_srctgt.select()

    var_src = IntVar()
    check_src = Checkbutton(parent, text="Source", variable=var_src, onvalue=1, offvalue=0)
    check_src.grid(row=3, column=1, padx=10, pady=5)

    var_tgt = IntVar()
    check_tgt = Checkbutton(parent, text="Target", variable=var_tgt, onvalue=1, offvalue=0)
    check_tgt.grid(row=4, column=1, padx=10, pady=5)

    def go():
        corpus_dedup_in = entry_dedup_in.get().strip()
        corpus_dedup_out = entry_dedup_out.get().strip()

        if len(corpus_dedup_out) == 0:
            corpus_dedup_out = corpus_dedup_in + ".dedup"

        if len(corpus_dedup_in) == 0:
            tk.messagebox.showinfo(title="Info", message="Input parameter empty.")
            return

        dedup_srctgt = True if var_srctgt.get() == 1 else False
        dedup_src = True if var_src.get() == 1 else False
        dedup_tgt = True if var_tgt.get() == 1 else False

        dedup(corpus_dedup_in, corpus_dedup_out, dedup_srctgt, dedup_src, dedup_tgt)

        tk.messagebox.showinfo(title="Info", message="done")

    tk.Button(parent, text="Write unique inputs", command=go).grid(row=5, column=1, padx=10, pady=5)


def create_han2hans_corpus(parent):
    tk.Label(parent, text="input").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_han2hans_in = tk.Entry(parent, width=50)
    entry_han2hans_in.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_han2hans_in)).grid(row=0, column=2,
                                                                                                padx=10, pady=5)

    tk.Label(parent, text="output").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_han2hans_out = tk.Entry(parent, width=50)
    entry_han2hans_out.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_save_file, entry=entry_han2hans_out)).grid(row=1, column=2,
                                                                                                 padx=10, pady=5)

    def go():
        corpus_han2hans_in = entry_han2hans_in.get().strip()
        corpus_han2hans_out = entry_han2hans_out.get().strip()
        if len(corpus_han2hans_in) == 0 or len(corpus_han2hans_out) == 0:
            tk.messagebox.showinfo(title="Info", message="Some parameter empty.")
            return

        convert_cmd = "python ../corpus/bin/hant2hans.py {} {}"
        os.popen(convert_cmd.format(corpus_han2hans_in, corpus_han2hans_out)).readlines()

        tk.messagebox.showinfo(title="Info", message="done")

    tk.Button(parent, text="Convert file in traditional Chinese into file in simplified Chinese", \
              command=go).grid(row=5, column=1, padx=10, pady=5)


def create_sample_corpus(parent):
    tk.Label(parent, text="file1").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_sample_in1 = tk.Entry(parent, width=50)
    entry_sample_in1.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_sample_in1)).grid(row=0, column=2,
                                                                                               padx=10, pady=5)

    tk.Label(parent, text="file2").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_sample_in2 = tk.Entry(parent, width=50)
    entry_sample_in2.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_sample_in2)).grid(row=1, column=2,
                                                                                               padx=10, pady=5)

    tk.Label(parent, text="number of samples").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    entry_sample_number = tk.Entry(parent, width=50)
    entry_sample_number.grid(row=2, column=1, padx=10, pady=5)

    def go():
        corpus_sample_in1 = entry_sample_in1.get().strip()
        corpus_sample_in2 = entry_sample_in2.get().strip()
        corpus_sample_number = entry_sample_number.get().strip()
        if len(corpus_sample_in1) != 0 and len(corpus_sample_in2) != 0:
            files = [corpus_sample_in1, corpus_sample_in2]
        elif len(corpus_sample_in1) != 0 and len(corpus_sample_in2) == 0:
            files = [corpus_sample_in1]
        elif len(corpus_sample_in1) == 0 and len(corpus_sample_in2) != 0:
            files = [corpus_sample_in2]
        else:
            tk.messagebox.showinfo(title="Info", message="Some parameter empty.")
            return
        if len(corpus_sample_number) == 0:
            tk.messagebox.showinfo(title="Info", message="Some parameter empty.")
            return
        sample(files, int(corpus_sample_number))
        tk.messagebox.showinfo(title="Info", message="done")

    tk.Button(parent, text="Sample sentences from bitext or source and target file", command=go).grid( \
        row=5, column=1, padx=10, pady=5)


def create_split_corpus(parent):
    tk.Label(parent, text="Input File 1").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_split_in1 = tk.Entry(parent, width=50)
    entry_split_in1.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_split_in1)).grid(row=0, column=2,
                                                                                              padx=10, pady=5)

    tk.Label(parent, text="Input File2 (Optional)").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_split_in2 = tk.Entry(parent, width=50)
    entry_split_in2.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_split_in2)).grid(row=1, column=2,
                                                                                              padx=10, pady=5)

    tk.Label(parent, text="Number of Samples in each File").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    entry_split_number = tk.Entry(parent, width=50)
    entry_split_number.grid(row=2, column=1, padx=10, pady=5)

    def go():
        corpus_split_in1 = entry_split_in1.get().strip()
        corpus_split_in2 = entry_split_in2.get().strip()
        corpus_split_number = entry_split_number.get().strip()
        if len(corpus_split_in1) != 0 and len(corpus_split_in2) != 0:
            files = [corpus_split_in1, corpus_split_in2]
        elif len(corpus_split_in1) != 0 and len(corpus_split_in2) == 0:
            files = [corpus_split_in1]
        elif len(corpus_split_in1) == 0 and len(corpus_split_in2) != 0:
            files = [corpus_split_in2]
        else:
            tk.messagebox.showinfo(title="Info", message="Some parameter empty.")
            return
        if len(corpus_split_number) == 0:
            tk.messagebox.showinfo(title="Info", message="Some parameter empty.")
            return
        split(files, int(corpus_split_number))
        tk.messagebox.showinfo(title="Info", message="done")

    tk.Button(parent, text="Split corpus into multiple files with the same lines", command=go).grid( \
        row=5, column=1, padx=10, pady=5)


def create_tok_mono(parent):
    tk.Label(parent, text="Input File").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_in = tk.Entry(parent, width=50)
    entry_in.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_in)).grid(row=0, column=2,
                                                                                                padx=10, pady=5)

    tk.Label(parent, text="Output File (Optional)").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_out = tk.Entry(parent, width=50)
    entry_out.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_save_file, entry=entry_out)).grid(row=1, column=2,
                                                                                                 padx=10, pady=5)

    tk.Label(parent, text="Input Language").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    entry_lang = tk.Entry(parent, width=50)
    entry_lang.grid(row=2, column=1, padx=10, pady=5)
    entry_lang.insert(0, "zh")

    def go():
        corpus_in = entry_in.get().strip()
        corpus_out = entry_out.get().strip()
        if len(corpus_in) == 0:
            tk.messagebox.showinfo(title="Info", message="Some parameter empty.")
            return

        if len(corpus_out) == 0:
            corpus_out = None

        lang = entry_lang.get().strip()
        tokenize_single(corpus_in, lang, corpus_out)

        tk.messagebox.showinfo(title="Info", message="done")

    tk.Button(parent, text="Tokenize File", command=go).grid(row=3, column=1, padx=10, pady=5)


def create_detok_zh(parent):
    tk.Label(parent, text="Input File").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_in = tk.Entry(parent, width=50)
    entry_in.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_in)).grid(row=0, column=2,
                                                                                                padx=10, pady=5)

    tk.Label(parent, text="Output File (Optional)").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_out = tk.Entry(parent, width=50)
    entry_out.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_save_file, entry=entry_out)).grid(row=1, column=2,
                                                                                                 padx=10, pady=5)

    def go():
        corpus_in = entry_in.get().strip()
        corpus_out = entry_out.get().strip()
        if len(corpus_in) == 0:
            tk.messagebox.showinfo(title="Info", message="Some parameter empty.")
            return

        if len(corpus_out) == 0:
            corpus_out = None

        detok_zh(corpus_in, corpus_out)

        tk.messagebox.showinfo(title="Info", message="done")

    tk.Button(parent, text="Detokenize Chinese Text", command=go).grid(row=2, column=1, padx=10, pady=5)
