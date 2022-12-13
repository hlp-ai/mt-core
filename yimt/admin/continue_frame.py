import os
import tkinter as tk
from tkinter import *
import tkinter.messagebox
from functools import partial

from yimt.admin.win_utils import ask_open_file, ask_dir


def create_ft(parent):
    tk.Label(parent, text="Raw fine-tuning Corpus path").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_corpus_train = tk.Entry(parent, width=50)
    entry_corpus_train.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_corpus_train)).grid(row=0, column=2, padx=10, pady=5)

    tk.Label(parent, text="Source SP model path").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_sp_src = tk.Entry(parent, width=50)
    entry_sp_src.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_sp_src)).grid(row=1, column=2, padx=10, pady=5)

    tk.Label(parent, text="Target SP model path").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    entry_sp_tgt = tk.Entry(parent, width=50)
    entry_sp_tgt.grid(row=2, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_sp_tgt)).grid(row=2, column=2, padx=10,
                                                                                           pady=5)

    tk.Label(parent, text="Source vocabulary").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    entry_vocab_src = tk.Entry(parent, width=50)
    entry_vocab_src.grid(row=3, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_vocab_src)).grid(row=3, column=2, padx=10,
                                                                                           pady=5)

    tk.Label(parent, text="Target vocabulary").grid(row=4, column=0, padx=10, pady=5, sticky="e")
    entry_vocab_tgt = tk.Entry(parent, width=50)
    entry_vocab_tgt.grid(row=4, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_vocab_tgt)).grid(row=4, column=2, padx=10,
                                                                                           pady=5)

    tk.Label(parent, text="Checkpoint dir to be fine-tuned").grid(row=5, column=0, padx=10, pady=5, sticky="e")
    entry_chkpt_ft = tk.Entry(parent, width=50)
    entry_chkpt_ft.grid(row=5, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_dir, entry_chkpt_ft)).grid(row=5, column=2, padx=10, pady=5)

    tk.Label(parent, text="Output dir").grid(row=6, column=0, padx=10, pady=5, sticky="e")
    entry_output = tk.Entry(parent, width=50)
    entry_output.grid(row=6, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_dir, entry_output)).grid(row=6, column=2, padx=10, pady=5)

    tk.Label(parent, text="Steps for fine-tuning").grid(row=7, column=0, padx=10, pady=5, sticky="e")
    entry_steps = tk.Entry(parent)
    entry_steps.grid(row=7, column=1, padx=10, pady=5, sticky="w")
    entry_steps.insert(0, "1")

    tk.Label(parent, text="Additional config file").grid(row=8, column=0, padx=10, pady=5, sticky="e")
    entry_ex_config = tk.Entry(parent, width=50)
    entry_ex_config.grid(row=8, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_ex_config)).grid(row=8, column=2, padx=10,
                                                                                              pady=5)

    var_con_ckpt = IntVar()
    check_con_ckpt = Checkbutton(parent, text="Continue form checkpoint", variable=var_con_ckpt, onvalue=1, offvalue=0)
    check_con_ckpt.grid(row=9, column=1, padx=10, pady=5)

    def go():
        corpus_train = entry_corpus_train.get().strip()
        sp_src = entry_sp_src.get().strip()
        sp_tgt = entry_sp_tgt.get().strip()
        vocab_src = entry_vocab_src.get().strip()
        vocab_tgt = entry_vocab_tgt.get().strip()
        chkpt_dir = entry_chkpt_ft.get().strip()
        output_path = entry_output.get().strip()
        steps = entry_steps.get().strip()
        ex_config = entry_ex_config.get().strip()

        if len(corpus_train) == 0 or len(sp_src) == 0 or len(sp_tgt) == 0 \
                or len(vocab_src) == 0 or len(vocab_tgt) == 0 or len(chkpt_dir)==0 \
                or len(output_path)==0:
            tk.messagebox.showinfo(title="Info", message="Some parameter empty.")
            return

        pretrain_cmd = "python ../core/ex/fine_tune.py --corpus_fn {} --src_sp_model {} --tgt_sp_model {} --src_vocab {} --tgt_vocab {} --ckpt_dir {} --output_dir {} --steps {}"
        cmd_str = pretrain_cmd.format(corpus_train, sp_src, sp_tgt, vocab_src, vocab_tgt, chkpt_dir, output_path, steps)
        if len(ex_config) > 0:
            cmd_str += " --config " + ex_config

        if var_con_ckpt.get() == 1:
            cmd_str += " --continue_from_checkpoint"

        os.popen(cmd_str).readlines()

        tk.messagebox.showinfo(title="Info", message="Fine-tuning Done.")

    tk.Button(parent, text="Fine-tune Model", command=go).grid(row=10, column=1, padx=10, pady=5)


def create_mix_ft(parent):
    tk.Label(parent, text="Raw fine-tuning Corpus path").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_corpus_train = tk.Entry(parent, width=50)
    entry_corpus_train.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_corpus_train)).grid(row=0, column=2, padx=10, pady=5)

    tk.Label(parent, text="Source SP model path").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_sp_src = tk.Entry(parent, width=50)
    entry_sp_src.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_sp_src)).grid(row=1, column=2, padx=10, pady=5)

    tk.Label(parent, text="Target SP model path").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    entry_sp_tgt = tk.Entry(parent, width=50)
    entry_sp_tgt.grid(row=2, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_sp_tgt)).grid(row=2, column=2, padx=10,
                                                                                           pady=5)

    tk.Label(parent, text="Source vocabulary").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    entry_vocab_src = tk.Entry(parent, width=50)
    entry_vocab_src.grid(row=3, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_vocab_src)).grid(row=3, column=2, padx=10,
                                                                                           pady=5)

    tk.Label(parent, text="Target vocabulary").grid(row=4, column=0, padx=10, pady=5, sticky="e")
    entry_vocab_tgt = tk.Entry(parent, width=50)
    entry_vocab_tgt.grid(row=4, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_vocab_tgt)).grid(row=4, column=2, padx=10,
                                                                                           pady=5)

    tk.Label(parent, text="Checkpoint dir to be fine-tuned").grid(row=5, column=0, padx=10, pady=5, sticky="e")
    entry_chkpt_ft = tk.Entry(parent, width=50)
    entry_chkpt_ft.grid(row=5, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_dir, entry_chkpt_ft)).grid(row=5, column=2, padx=10, pady=5)

    tk.Label(parent, text="Output dir").grid(row=6, column=0, padx=10, pady=5, sticky="e")
    entry_output = tk.Entry(parent, width=50)
    entry_output.grid(row=6, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_dir, entry_output)).grid(row=6, column=2, padx=10, pady=5)

    tk.Label(parent, text="Steps for fine-tuning").grid(row=7, column=0, padx=10, pady=5, sticky="e")
    entry_steps = tk.Entry(parent)
    entry_steps.grid(row=7, column=1, padx=10, pady=5, sticky="w")
    entry_steps.insert(0, "1")

    tk.Label(parent, text="Additional config file").grid(row=8, column=0, padx=10, pady=5, sticky="e")
    entry_ex_config = tk.Entry(parent, width=50)
    entry_ex_config.grid(row=8, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_ex_config)).grid(row=8, column=2, padx=10,
                                                                                              pady=5)

    var_con_ckpt = IntVar()
    check_con_ckpt = Checkbutton(parent, text="Continue form checkpoint", variable=var_con_ckpt, onvalue=1, offvalue=0)
    check_con_ckpt.grid(row=9, column=1, padx=10, pady=5)

    def go():
        corpus_train = entry_corpus_train.get().strip()
        sp_src = entry_sp_src.get().strip()
        sp_tgt = entry_sp_tgt.get().strip()
        vocab_src = entry_vocab_src.get().strip()
        vocab_tgt = entry_vocab_tgt.get().strip()
        chkpt_dir = entry_chkpt_ft.get().strip()
        output_path = entry_output.get().strip()
        steps = entry_steps.get().strip()
        ex_config = entry_ex_config.get().strip()

        if len(corpus_train) == 0 or len(sp_src) == 0 or len(sp_tgt) == 0 \
                or len(vocab_src) == 0 or len(vocab_tgt) == 0 or len(chkpt_dir)==0 \
                or len(output_path)==0:
            tk.messagebox.showinfo(title="Info", message="Some parameter empty.")
            return

        pretrain_cmd = "python ../core/ex/fine_tune.py --corpus_fn {} --src_sp_model {} --tgt_sp_model {} --src_vocab {} --tgt_vocab {} --ckpt_dir {} --output_dir {} --steps {}"
        cmd_str = pretrain_cmd.format(corpus_train, sp_src, sp_tgt, vocab_src, vocab_tgt, chkpt_dir, output_path, steps)
        if len(ex_config) > 0:
            cmd_str += " --config " + ex_config

        if var_con_ckpt.get() == 1:
            cmd_str += " --continue_from_checkpoint"

        os.popen(cmd_str).readlines()

        tk.messagebox.showinfo(title="Info", message="Fine-tuning Done.")

    tk.Button(parent, text="Fine-tune Model", command=go).grid(row=10, column=1, padx=10, pady=5)