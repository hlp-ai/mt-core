import os
import tkinter as tk
from tkinter import *
import tkinter.messagebox
from functools import partial

from yimt.admin.win_utils import ask_open_file, ask_dir,ask_save_file
from yimt.corpus.utils import pair_to_single,single_to_pair,merge
import yimt.corpus.bin.normalize as norm
import yimt.corpus.bin.filter as filt

def create_tsv2mono_corpus(parent):
    tk.Label(parent, text="path of parallel file").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_corpus_pair = tk.Entry(parent, width=50)
    entry_corpus_pair.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_corpus_pair)).grid(row=0, column=2, padx=10, pady=5)

    tk.Label(parent, text="path of source file").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_corpus_src = tk.Entry(parent, width=50)
    entry_corpus_src.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_save_file, entry=entry_corpus_src)).grid(row=1, column=2, padx=10, pady=5)

    tk.Label(parent, text="path of target file").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    entry_corpus_tgt = tk.Entry(parent, width=50)
    entry_corpus_tgt.grid(row=2, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_save_file, entry=entry_corpus_tgt)).grid(row=2, column=2, padx=10,
                                                                                           pady=5)


    def go():
        corpus_pair = entry_corpus_pair.get().strip()
        corpus_src = entry_corpus_src.get().strip()
        corpus_tgt = entry_corpus_tgt.get().strip()

        if len(corpus_pair) == 0 or len(corpus_src) == 0 or len(corpus_tgt) == 0 :
            tk.messagebox.showinfo(title="Info", message="Some parameter empty.")
            return

        pair_to_single(corpus_pair, corpus_src, corpus_tgt)

        tk.messagebox.showinfo(title="Info", message="done")

    tk.Button(parent, text="Split a parallel file into source ang target file", command=go).grid(row=5, column=1, padx=10, pady=5)


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
    tk.Button(parent, text="...", command=partial(ask_save_file, entry=entry_corpus_pair)).grid(row=2, column=2, padx=10,
                                                                                               pady=5)

    def go():
        corpus_pair = entry_corpus_pair.get().strip()
        corpus_src = entry_corpus_src.get().strip()
        corpus_tgt = entry_corpus_tgt.get().strip()

        if len(corpus_pair) == 0 or len(corpus_src) == 0 or len(corpus_tgt) == 0:
            tk.messagebox.showinfo(title="Info", message="Some parameter empty.")
            return
        single_to_pair(corpus_src,corpus_tgt,corpus_pair)
        tk.messagebox.showinfo(title="Info", message="done")
    tk.Button(parent, text="Combine source and target file into a parallel one", command=go).grid(row=5, column=1,
                                                                                                 padx=10, pady=5)

def create_merge_corpus(parent):
    tk.Label(parent, text="path of data").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_corpus_datapath = tk.Entry(parent, width=50)
    entry_corpus_datapath.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_dir, entry=entry_corpus_datapath)).grid(row=0, column=2,
                                                                                               padx=10, pady=5)

    tk.Label(parent, text="path of target file").grid(row=1, column=0, padx=10, pady=5, sticky="e")
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

def create_normalize_corpus(parent):
    tk.Label(parent, text="in_fn").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_normalize_in = tk.Entry(parent, width=50)
    entry_normalize_in.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_normalize_in)).grid(row=0, column=2,
                                                                                              padx=10, pady=5)

    tk.Label(parent, text="out_fn").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_normalize_out = tk.Entry(parent, width=50)
    entry_normalize_out.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_save_file, entry=entry_normalize_out)).grid(row=1, column=2, padx=10,
                                                                                            pady=5)

    def go():
        corpus_normalize_in = entry_normalize_in.get().strip()
        corpus_normalize_out = entry_normalize_out.get().strip()

        if len(corpus_normalize_in) == 0 or len(corpus_normalize_out) == 0:
            tk.messagebox.showinfo(title="Info", message="Some parameter empty.")
            return

        norm.main(corpus_normalize_in,corpus_normalize_out)

        tk.messagebox.showinfo(title="Info", message="done")

    tk.Button(parent, text="Normalize bitext",command=go).grid(row=5, column=1, padx=10, pady=5)

def create_filter_corpus(parent):
    tk.Label(parent, text="in_fn").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_filter_in = tk.Entry(parent, width=50)
    entry_filter_in.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_filter_in)).grid(row=0, column=2,
                                                                                                 padx=10, pady=5)

    tk.Label(parent, text="out_fn").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_filter_out = tk.Entry(parent, width=50)
    entry_filter_out.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_save_file, entry=entry_filter_out)).grid(row=1, column=2,
                                                                                                  padx=10,pady=5)

    tk.Label(parent, text="from_lang").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    entry_filter_fromlang=tk.Entry(parent, width=50)
    entry_filter_fromlang.grid(row=2, column=1, padx=10, pady=5)
    entry_filter_fromlang.insert(0, "latin")

    def go():
        corpus_filter_in = entry_filter_in.get().strip()
        corpus_filter_out = entry_filter_out.get().strip()
        corpus_filter_fromlang=entry_filter_fromlang.get().strip()

        if len(corpus_filter_in) == 0 or len(corpus_filter_out) == 0:
            tk.messagebox.showinfo(title="Info", message="Some parameter empty.")
            return

        filt.main(corpus_filter_in,corpus_filter_out,corpus_filter_fromlang)

        tk.messagebox.showinfo(title="Info", message="done")

    tk.Button(parent, text="Filter",command=go).grid(row=5, column=1, padx=10, pady=5)

