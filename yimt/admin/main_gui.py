import os
import tkinter as tk
from tkinter import *
import tkinter.filedialog
import tkinter.messagebox
from tkinter import ttk
from functools import partial

import yaml

from yimt.core.ex.exec_eval import run_eval, run_infer
from yimt.core.ex.sp import train_spm, load_spm, tokenize_file
from yimt.api.translator import load_translator


def ask_open_file(entry):
    filename = tk.filedialog.askopenfilename()
    if filename != '':
        entry.delete(0, tk.END)
        entry.insert(0, filename)


def ask_save_file(entry):
    filename = tk.filedialog.asksaveasfilename()
    if filename != '':
        entry.delete(0, tk.END)
        entry.insert(0, filename)


def ask_dir(entry):
    filename = tk.filedialog.askdirectory()
    if filename != '':
        entry.delete(0, tk.END)
        entry.insert(0, filename)


def create_sp_train(parent):
    tk.Label(parent, text="Corpus path").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_corpus = tk.Entry(parent, width=50)
    entry_corpus.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_corpus)).grid(row=0, column=2, padx=10, pady=5)

    tk.Label(parent, text="Size of vocab").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_vocab_size = tk.Entry(parent)
    entry_vocab_size.grid(row=1, column=1, padx=10, pady=5, sticky="w")
    entry_vocab_size.insert(0, "4800")

    tk.Label(parent, text="SP model path").grid(row=2, column=0, sticky="e")
    entry_model = tk.Entry(parent, width=50)
    entry_model.grid(row=2, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_save_file, entry_model)).grid(row=2, column=2, padx=10, pady=5)

    tk.Label(parent, text="Max num of sentences").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    entry_max_sentences = tk.Entry(parent)
    entry_max_sentences.grid(row=3, column=1, padx=10, pady=5, sticky="w")
    entry_max_sentences.insert(0, "5000000")

    tk.Label(parent, text="Character coverage").grid(row=4, column=0, padx=10, pady=5, sticky="e")
    entry_coverage = tk.Entry(parent)
    entry_coverage.grid(row=4, column=1, padx=10, pady=5, sticky="w")
    entry_coverage.insert(0, "0.9999")

    def go():
        corpus_file = entry_corpus.get()
        if len(corpus_file.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Corpus path empty.")
            return

        vocab_size = entry_vocab_size.get()
        if len(vocab_size.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Vocab size empty.")
            return

        sp_model = entry_model.get()
        if len(sp_model.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Model path empty.")
            return

        print(corpus_file, vocab_size, sp_model)

        train_spm(corpus_file, sp_model, vocab_size,
                  num_sentences=entry_max_sentences.get(),
                  coverage=entry_coverage.get())

        tk.messagebox.showinfo(title="Info", message="SentencePiece model created.")

    tk.Button(parent, text="Train SentencePiece Model", command=go).grid(row=5, column=1, padx=10, pady=5)


def create_sp_tokenize(parent):
    tk.Label(parent, text="Corpus path").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_corpus = tk.Entry(parent, width=50)
    entry_corpus.grid(row=0, column=1, padx=10, pady=5)

    tk.Button(parent, text="...", command=partial(ask_open_file, entry_corpus)).grid(row=0, column=2, padx=10, pady=5)

    tk.Label(parent, text="SP model path").grid(row=1, column=0, sticky="e")
    entry_model = tk.Entry(parent, width=50)
    entry_model.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry_model)).grid(row=1, column=2, padx=10, pady=5)

    tk.Label(parent, text="Output file").grid(row=2, column=0, sticky="e")
    entry_output = tk.Entry(parent, width=50)
    entry_output.grid(row=2, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_save_file, entry_output)).grid(row=2, column=2, padx=10, pady=5)


    def go():
        corpus_file = entry_corpus.get()
        if len(corpus_file.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Corpus path empty.")
            return

        sp_model = entry_model.get()
        if len(sp_model.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="SP model empty.")
            return

        tok_output = entry_output.get()
        if len(tok_output.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Output path empty.")
            return

        print(corpus_file, sp_model, tok_output)

        sp = load_spm(sp_model)
        tokenize_file(sp, corpus_file, tok_output)

        tk.messagebox.showinfo(title="Info", message="Raw corpus tokenized.")

    tk.Button(parent, text="Tokenize Corpus with SP", command=go).grid(row=3, column=1, padx=10, pady=5)


def create_build_vocab(parent):
    tk.Label(parent, text="Corpus path").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_corpus = tk.Entry(parent, width=50)
    entry_corpus.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_corpus)).grid(row=0, column=2, padx=10, pady=5)

    tk.Label(parent, text="Size of vocab").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_vocab_size = tk.Entry(parent)
    entry_vocab_size.grid(row=1, column=1, padx=10, pady=5, sticky="w")
    entry_vocab_size.insert(0, "4800")

    tk.Label(parent, text="Vocab path").grid(row=2, column=0, sticky="e")
    entry_vocab = tk.Entry(parent, width=50)
    entry_vocab.grid(row=2, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_save_file, entry_vocab)).grid(row=2, column=2, padx=10, pady=5)

    def go():
        corpus_file = entry_corpus.get()
        if len(corpus_file.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Corpus path empty.")
            return

        vocab_size = entry_vocab_size.get()
        if len(vocab_size.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Vocab size empty.")
            return

        vocab_path = entry_vocab.get()
        if len(vocab_path.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Vocab path empty.")
            return

        print(corpus_file, vocab_size, vocab_path)

        build_vocab_cmd = "python ../core/bin/build_vocab.py --size {} --save_vocab {} {}"

        os.popen(build_vocab_cmd.format(vocab_size, vocab_path, corpus_file)).readlines()

        tk.messagebox.showinfo(title="Info", message="Vocab created.")

    tk.Button(parent, text="Build Vocab", command=go).grid(row=3, column=1, padx=10, pady=5)


def create_edit_config(parent):
    tk.Label(parent, text="Model Dir").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_model_dir = tk.Entry(parent, width=50)
    entry_model_dir.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_dir, entry=entry_model_dir)).grid(row=0, column=2, padx=10, pady=5)

    tk.Label(parent, text="Source File for Training").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_src_train = tk.Entry(parent, width=50)
    entry_src_train.grid(row=1, column=1, padx=10, pady=5, sticky="w")
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_src_train)).grid(row=1, column=2, padx=10,
                                                                                              pady=5)

    tk.Label(parent, text="Target File for Traning").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    entry_tgt_train = tk.Entry(parent, width=50)
    entry_tgt_train.grid(row=2, column=1, padx=10, pady=5, sticky="w")
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_tgt_train)).grid(row=2, column=2, padx=10,
                                                                                              pady=5)

    tk.Label(parent, text="Source File for Eval").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    entry_src_eval = tk.Entry(parent, width=50)
    entry_src_eval.grid(row=3, column=1, padx=10, pady=5, sticky="w")
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_src_eval)).grid(row=3, column=2, padx=10,
                                                                                              pady=5)

    tk.Label(parent, text="Target File for Eval").grid(row=4, column=0, padx=10, pady=5, sticky="e")
    entry_tgt_eval = tk.Entry(parent, width=50)
    entry_tgt_eval.grid(row=4, column=1, padx=10, pady=5, sticky="w")
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_tgt_eval)).grid(row=4, column=2, padx=10,
                                                                                              pady=5)

    tk.Label(parent, text="Source Vocab").grid(row=5, column=0, padx=10, pady=5, sticky="e")
    entry_src_vocab = tk.Entry(parent, width=50)
    entry_src_vocab.grid(row=5, column=1, padx=10, pady=5, sticky="w")
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_src_vocab)).grid(row=5, column=2, padx=10,
                                                                                             pady=5)

    tk.Label(parent, text="Target Vocab").grid(row=6, column=0, padx=10, pady=5, sticky="e")
    entry_tgt_vocab = tk.Entry(parent, width=50)
    entry_tgt_vocab.grid(row=6, column=1, padx=10, pady=5, sticky="w")
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_tgt_vocab)).grid(row=6, column=2, padx=10,
                                                                                             pady=5)

    tk.Label(parent, text="Train Batch Type").grid(row=7, column=0, padx=10, pady=5, sticky="e")
    cbox_batch_type = ttk.Combobox(parent)
    cbox_batch_type.grid(row=7, column=1, padx=10, pady=5, sticky="w")
    cbox_batch_type['value'] = ('tokens', 'examples')
    cbox_batch_type.current(0)

    tk.Label(parent, text="Train Batch Size").grid(row=8, column=0, padx=10, pady=5, sticky="e")
    entry_batch_size = tk.Entry(parent)
    entry_batch_size.grid(row=8, column=1, padx=10, pady=5, sticky="w")
    entry_batch_size.insert(0, "4096")

    tk.Label(parent, text="Train Max Step").grid(row=9, column=0, padx=10, pady=5, sticky="e")
    entry_max_step = tk.Entry(parent)
    entry_max_step.grid(row=9, column=1, padx=10, pady=5, sticky="w")
    entry_max_step.insert(0, "30000")

    tk.Label(parent, text="Checkpoint Step").grid(row=10, column=0, padx=10, pady=5, sticky="e")
    entry_ckpt_step = tk.Entry(parent)
    entry_ckpt_step.grid(row=10, column=1, padx=10, pady=5, sticky="w")
    entry_ckpt_step.insert(0, 200)

    tk.Label(parent, text="Max Checkpoints").grid(row=11, column=0, padx=10, pady=5, sticky="e")
    entry_ckpt_max = tk.Entry(parent)
    entry_ckpt_max.grid(row=11, column=1, padx=10, pady=5, sticky="w")
    entry_ckpt_max.insert(0, 5)

    tk.Label(parent, text="Summary Step").grid(row=12, column=0, padx=10, pady=5, sticky="e")
    entry_summary_step = tk.Entry(parent)
    entry_summary_step.grid(row=12, column=1, padx=10, pady=5, sticky="w")
    entry_summary_step.insert(0, 100)

    tk.Label(parent, text="Evaluation Step").grid(row=13, column=0, padx=10, pady=5, sticky="e")
    entry_eval_step = tk.Entry(parent)
    entry_eval_step.grid(row=13, column=1, padx=10, pady=5, sticky="w")
    entry_eval_step.insert(0, 800)

    tk.Label(parent, text="Evaluation Scorer").grid(row=14, column=0, padx=10, pady=5, sticky="e")
    entry_eval_scorer = tk.Entry(parent)
    entry_eval_scorer.grid(row=14, column=1, padx=10, pady=5, sticky="w")
    entry_eval_scorer.insert(0, "bleu")

    tk.Label(parent, text="EarlyStopping Metric").grid(row=15, column=0, padx=10, pady=5, sticky="e")
    cbox_stop_metric = ttk.Combobox(parent)
    cbox_stop_metric.grid(row=15, column=1, padx=10, pady=5, sticky="w")
    cbox_stop_metric['value'] = ('bleu', 'loss')
    cbox_stop_metric.current(0)

    tk.Label(parent, text="EarlyStopping Min Improve.").grid(row=16, column=0, padx=10, pady=5, sticky="e")
    entry_stop_min = tk.Entry(parent)
    entry_stop_min.grid(row=16, column=1, padx=10, pady=5, sticky="w")
    entry_stop_min.insert(0, "0.01")

    tk.Label(parent, text="EarlyStopping Patience").grid(row=17, column=0, padx=10, pady=5, sticky="e")
    entry_stop_step = tk.Entry(parent)
    entry_stop_step.grid(row=17, column=1, padx=10, pady=5, sticky="w")
    entry_stop_step.insert(0, 4)

    def save():
        config = {}

        model_dir = entry_model_dir.get()
        if len(model_dir.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Model dir empty.")
            return
        config["model_dir"] = model_dir

        config["data"] = {}

        src_train = entry_src_train.get()
        if len(src_train.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Source file for training empty.")
            return
        config["data"]["train_features_file"] = src_train

        tgt_train = entry_tgt_train.get()
        if len(tgt_train.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Target file for training empty.")
            return
        config["data"]["train_labels_file"] = tgt_train

        src_eval = entry_src_eval.get()
        if len(src_eval.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Source file for eval empty.")
            return
        config["data"]["eval_features_file"] = src_eval

        tgt_eval = entry_tgt_eval.get()
        if len(tgt_eval.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Target file for eval empty.")
            return
        config["data"]["eval_labels_file"] = tgt_eval

        src_vocab = entry_src_vocab.get()
        if len(src_vocab.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Source vocab empty.")
            return
        config["data"]["source_vocabulary"] = src_vocab

        tgt_vocab = entry_tgt_vocab.get()
        if len(tgt_vocab.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Target vocab empty.")
            return
        config["data"]["target_vocabulary"] = tgt_vocab

        config["train"] = {}
        config["train"]["batch_type"] = cbox_batch_type.get()
        config["train"]["batch_size"] = int(entry_batch_size.get())
        config["train"]["max_step"] = int(entry_max_step.get())
        config["train"]["save_checkpoints_steps"] = int(entry_ckpt_step.get())
        config["train"]["keep_checkpoint_max"] = int(entry_ckpt_max.get())
        config["train"]["keep_checkpoint_max"] = int(entry_ckpt_max.get())
        config["train"]["average_last_checkpoints"] = int(entry_summary_step.get())

        config["eval"] = {}
        config["eval"]["steps"] = int(entry_eval_step.get())
        config["eval"]["scorers"] = entry_eval_scorer.get()
        config["eval"]["early_stopping"] = {}
        config["eval"]["early_stopping"]["metric"] = cbox_stop_metric.get()
        config["eval"]["early_stopping"]["min_improvement"] = float(entry_stop_min.get())
        config["eval"]["early_stopping"]["steps"] = int(entry_stop_step.get())

        filename = tk.filedialog.asksaveasfilename()
        if filename != '':
            with open(filename, "w",  encoding='utf-8') as f:
                f.write(yaml.dump(config))
        else:
            tk.messagebox.showinfo(message="Not file chosen.")
            return

        tk.messagebox.showinfo(title="Info", message="Config saved.")

    def get_conf(conf, *keys):
        for k in keys:
            if k not in conf:
                return ""
            conf = conf[k]
        return conf

    def load():
        conf_fn = tk.filedialog.askopenfilename()
        if conf_fn != "":
            with open(conf_fn, encoding="utf-8") as f:
                conf = yaml.load(f, Loader=yaml.FullLoader)
                entry_model_dir.delete(0, tk.END)
                entry_model_dir.insert(0, conf["model_dir"])

                entry_src_train.delete(0, tk.END)
                entry_src_train.insert(0, conf["data"]["train_features_file"])

                entry_tgt_train.delete(0, tk.END)
                entry_tgt_train.insert(0, conf["data"]["train_labels_file"])

                entry_src_eval.delete(0, tk.END)
                entry_src_eval.insert(0, get_conf(conf, "data", "eval_features_file"))

                entry_tgt_eval.delete(0, tk.END)
                entry_tgt_eval.insert(0, get_conf(conf, "data", "eval_labels_file"))

                entry_src_vocab.delete(0, tk.END)
                entry_src_vocab.insert(0, conf["data"]["source_vocabulary"])

                entry_tgt_vocab.delete(0, tk.END)
                entry_tgt_vocab.insert(0, conf["data"]["target_vocabulary"])

                entry_batch_size.delete(0, tk.END)
                entry_batch_size.insert(0, conf["train"]["batch_size"])

                entry_max_step.delete(0, tk.END)
                entry_max_step.insert(0, conf["train"]["max_step"])

                entry_ckpt_step.delete(0, tk.END)
                entry_ckpt_step.insert(0, get_conf(conf, "train", "save_checkpoints_steps"))

                entry_ckpt_max.delete(0, tk.END)
                entry_ckpt_max.insert(0, get_conf(conf, "train", "keep_checkpoint_max"))

                entry_summary_step.delete(0, tk.END)
                entry_summary_step.insert(0, get_conf(conf, "train", "save_summary_steps"))
        else:
            tk.messagebox.showinfo(message="Not file chosen.")
            return

    tk.Button(parent, text="Load Config", command=load).grid(row=18, column=0, padx=10, pady=5)
    tk.Button(parent, text="Save Config", command=save).grid(row=18, column=1, padx=10, pady=5)


def create_train(parent):
    tk.Label(parent, text="Config File").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_config = tk.Entry(parent, width=50)
    entry_config.grid(row=0, column=1, padx=10, pady=5, sticky="w")
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_config)).grid(row=0, column=2, padx=10,
                                                                                              pady=5)

    tk.Label(parent, text="Model Type").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    cbox = ttk.Combobox(parent)
    cbox.grid(row=1, column=1, padx=10, pady=5, sticky="w")
    cbox['value'] = ('Transformer', 'TransformerBig')
    cbox.current(0)

    var_eval = IntVar()
    check_eval = Checkbutton(parent, text="Train with Evaluation", variable=var_eval, onvalue=1, offvalue=0)
    check_eval.grid(row=2, column=0, padx=10, pady=5)

    var_mxp = IntVar()
    check_mxp = Checkbutton(parent, text="Train with Mixed Precision", variable=var_mxp, onvalue=1, offvalue=0)
    check_mxp.grid(row=2, column=1, padx=10, pady=5)
    check_mxp.select()

    def go():
        conf = entry_config.get()
        if len(conf.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Config file empty.")
            return

        model_type = cbox.get()

        train_cmd_str = "python ../core/bin/main.py --model_type {} --config {} --auto_config"
        train_cmd = train_cmd_str.format(model_type, conf)
        if var_mxp.get() == 1:
            train_cmd += " --mixed_precision"
        train_cmd += " train"
        if var_eval.get() == 1:
            train_cmd += " --with_eval"
        print(train_cmd)
        os.popen(train_cmd).readlines()

        tk.messagebox.showinfo(title="Info", message="Training Done.")

    tk.Button(parent, text="Start Training", command=go).grid(row=3, column=1, padx=10, pady=5)


def create_average(parent):
    tk.Label(parent, text="Config File").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_config = tk.Entry(parent, width=50)
    entry_config.grid(row=0, column=1, padx=10, pady=5, sticky="w")
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_config)).grid(row=0, column=2, padx=10,
                                                                                              pady=5)
    tk.Label(parent, text="Output Directory").grid(row=1, column=0, sticky="e")
    entry_output = tk.Entry(parent, width=50)
    entry_output.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_dir, entry_output)).grid(row=1, column=2, padx=10, pady=5)

    def go():
        conf = entry_config.get()
        if len(conf.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Config file empty.")
            return

        out = entry_output.get()
        if len(out.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Output dir empty.")
            return

        average_pattern = "python ../core/bin/main.py --config {} --auto_config average_checkpoints --output_dir {}"
        average_cmd = average_pattern.format(conf, out)
        print(average_cmd)
        os.popen(average_cmd).readlines()

        tk.messagebox.showinfo(title="Info", message="Average Done.")

    tk.Button(parent, text="Average Checkpoints", command=go).grid(row=2, column=1, padx=10, pady=5)


def create_export(parent):
    tk.Label(parent, text="Config File").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_config = tk.Entry(parent, width=50)
    entry_config.grid(row=0, column=1, padx=10, pady=5, sticky="w")
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_config)).grid(row=0, column=2, padx=10,
                                                                                              pady=5)
    tk.Label(parent, text="Output Directory").grid(row=1, column=0, sticky="e")
    entry_output = tk.Entry(parent, width=50)
    entry_output.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_dir, entry_output)).grid(row=1, column=2, padx=10, pady=5)

    tk.Label(parent, text="Export Type").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    checkboc_type = ttk.Combobox(parent)
    checkboc_type.grid(row=2, column=1, padx=10, pady=5, sticky="w")
    checkboc_type['value'] = ('SavedModel', 'ctranslate2')
    checkboc_type.current(0)

    def go():
        conf = entry_config.get()
        if len(conf.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Config file empty.")
            return

        out = entry_output.get()
        if len(out.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Output dir empty.")
            return

        export_pattern = "python ../core/bin/main.py --config {} --auto_config export --output_dir {}"
        export_cmd = export_pattern.format(conf, out)
        if checkboc_type.get() == "ctranslate2":
            export_cmd += " --format ctranslate2"

        print(export_cmd)
        os.popen(export_cmd).readlines()

        tk.messagebox.showinfo(title="Info", message="Export Done.")

    tk.Button(parent, text="Export Checkpoints", command=go).grid(row=3, column=1, padx=10, pady=5)


def create_infer(parent):
    tk.Label(parent, text="Config File").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_config = tk.Entry(parent, width=50)
    entry_config.grid(row=0, column=1, padx=10, pady=5, sticky="w")
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_config)).grid(row=0, column=2, padx=10,
                                                                                           pady=5)

    tk.Label(parent, text="Raw Source File").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_src = tk.Entry(parent, width=50)
    entry_src.grid(row=1, column=1, padx=10, pady=5, sticky="w")
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_src)).grid(row=1, column=2, padx=10,
                                                                                              pady=5)

    tk.Label(parent, text="Source SP Model").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    entry_src_sp = tk.Entry(parent, width=50)
    entry_src_sp.grid(row=2, column=1, padx=10, pady=5, sticky="w")
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_src_sp)).grid(row=2, column=2, padx=10,
                                                                                              pady=5)

    tk.Label(parent, text="Target SP Model").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    entry_tgt_sp = tk.Entry(parent, width=50)
    entry_tgt_sp.grid(row=3, column=1, padx=10, pady=5, sticky="w")
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_tgt_sp)).grid(row=3, column=2, padx=10,
                                                                                              pady=5)

    def go():
        config_fn = entry_config.get()
        if len(config_fn.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Config file empty.")
            return

        src = entry_src.get()
        if len(src.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Source file empty.")
            return

        src_sp = entry_src_sp.get()
        if len(src_sp.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Source SP model empty.")
            return

        tgt_sp = entry_tgt_sp.get()
        if len(tgt_sp.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Target SP model empty.")
            return

        out = run_infer(config_fn, src, src_sp, tgt_sp)
        os.startfile(out)

        tk.messagebox.showinfo(title="Info", message="Eval Done.")

    tk.Button(parent, text="Translate", command=go).grid(row=6, column=1, padx=10, pady=5)


def create_eval(parent):
    tk.Label(parent, text="Config File").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_config = tk.Entry(parent, width=50)
    entry_config.grid(row=0, column=1, padx=10, pady=5, sticky="w")
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_config)).grid(row=0, column=2, padx=10,
                                                                                           pady=5)

    tk.Label(parent, text="Source File").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_src = tk.Entry(parent, width=50)
    entry_src.grid(row=1, column=1, padx=10, pady=5, sticky="w")
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_src)).grid(row=1, column=2, padx=10,
                                                                                              pady=5)

    tk.Label(parent, text="Reference File").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    entry_ref = tk.Entry(parent, width=50)
    entry_ref.grid(row=2, column=1, padx=10, pady=5, sticky="w")
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_ref)).grid(row=2, column=2, padx=10,
                                                                                              pady=5)

    tk.Label(parent, text="Source SP Model").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    entry_src_sp = tk.Entry(parent, width=50)
    entry_src_sp.grid(row=3, column=1, padx=10, pady=5, sticky="w")
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_src_sp)).grid(row=3, column=2, padx=10,
                                                                                              pady=5)

    tk.Label(parent, text="Target SP Model").grid(row=4, column=0, padx=10, pady=5, sticky="e")
    entry_tgt_sp = tk.Entry(parent, width=50)
    entry_tgt_sp.grid(row=4, column=1, padx=10, pady=5, sticky="w")
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_tgt_sp)).grid(row=4, column=2, padx=10,
                                                                                              pady=5)

    tk.Label(parent, text="Language Pair").grid(row=5, column=0, padx=10, pady=5, sticky="e")
    entry_lang = tk.Entry(parent)
    entry_lang.grid(row=5, column=1, padx=10, pady=5, sticky="w")
    entry_lang.insert(0, "en-zh")

    def go():
        config_fn = entry_config.get()
        if len(config_fn.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Config file empty.")
            return

        src = entry_src.get()
        if len(src.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Source file empty.")
            return

        ref = entry_ref.get()
        if len(ref.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Reference file empty.")
            return

        src_sp = entry_src_sp.get()
        if len(src_sp.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Source SP model empty.")
            return

        tgt_sp = entry_tgt_sp.get()
        if len(tgt_sp.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Target SP model empty.")
            return

        run_eval(config_fn, src, ref, src_sp, tgt_sp, entry_lang.get())

        tk.messagebox.showinfo(title="Info", message="Eval Done.")

    tk.Button(parent, text="Evaluate", command=go).grid(row=6, column=1, padx=10, pady=5)


def create_translate(parent):
    tk.Label(parent, text="Model Format").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    checkboc_format = ttk.Combobox(parent)
    checkboc_format.grid(row=0, column=1, padx=10, pady=5, sticky="w")
    checkboc_format['value'] = ('Checkpoint', 'SavedModel', 'ctranslate2')
    checkboc_format.current(0)

    tk.Label(parent, text="Config File or Model Dir").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_config = tk.Entry(parent, width=50)
    entry_config.grid(row=1, column=1, padx=10, pady=5, sticky="w")
    if checkboc_format.get() == "Checkpoint":
        cmd = partial(ask_open_file, entry=entry_config)
    else:
        cmd = partial(ask_dir, entry=entry_config)
    tk.Button(parent, text="...", command=cmd).grid(row=1, column=2, padx=10, pady=5)

    tk.Label(parent, text="Source SP Model").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    entry_src_sp = tk.Entry(parent, width=50)
    entry_src_sp.grid(row=2, column=1, padx=10, pady=5, sticky="w")
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_src_sp)).grid(row=2, column=2, padx=10,
                                                                                              pady=5)

    tk.Label(parent, text="Source Text").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    text_src = Text(parent, width=50, height=15, undo=True, autoseparators=False)
    text_src.grid(row=3, column=1, padx=10, pady=5)

    translator = None
    conf_or_dir = ""

    def go():
        nonlocal conf_or_dir
        conf = entry_config.get()
        if len(conf.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Config file or model dir empty.")
            return

        src_sp = entry_src_sp.get()
        if len(src_sp.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Source SP empty.")
            return

        src = text_src.get("1.0", "end")
        if len(src.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Source text empty.")
            return

        nonlocal translator
        if translator is None or conf_or_dir != conf:
            translator = load_translator(conf, src_sp)
            conf_or_dir = conf
        translation = translator.translate_paragraph(src)
        text_out.delete("1.0", "end")
        text_out.insert(INSERT, translation)
        print(src)

    tk.Button(parent, text="Translate", command=go).grid(row=4, column=1, padx=10, pady=5)

    tk.Label(parent, text="Translation").grid(row=5, column=0, padx=10, pady=5, sticky="e")
    text_out = Text(parent, width=50, height=15, undo=True, autoseparators=False)
    text_out.grid(row=5, column=1, padx=10, pady=5)


def create_menu(win):
    def train_sp():
        sp_train_frame.pack()
        sp_tokenize_frame.pack_forget()
        build_vocab_frame.pack_forget()
        edit_config_frame.pack_forget()
        train_frame.pack_forget()
        infer_frame.pack_forget()
        average_frame.pack_forget()
        export_frame.pack_forget()
        translate_frame.pack_forget()

    def tokenize_sp():
        sp_tokenize_frame.pack()
        sp_train_frame.pack_forget()
        build_vocab_frame.pack_forget()
        edit_config_frame.pack_forget()
        train_frame.pack_forget()
        eval_frame.pack_forget()
        infer_frame.pack_forget()
        average_frame.pack_forget()
        export_frame.pack_forget()
        translate_frame.pack_forget()

    def build_vocab():
        build_vocab_frame.pack()
        sp_tokenize_frame.pack_forget()
        sp_train_frame.pack_forget()
        edit_config_frame.pack_forget()
        train_frame.pack_forget()
        eval_frame.pack_forget()
        infer_frame.pack_forget()
        average_frame.pack_forget()
        export_frame.pack_forget()
        translate_frame.pack_forget()

    def edit_config():
        edit_config_frame.pack()
        build_vocab_frame.pack_forget()
        sp_tokenize_frame.pack_forget()
        sp_train_frame.pack_forget()
        train_frame.pack_forget()
        eval_frame.pack_forget()
        infer_frame.pack_forget()
        average_frame.pack_forget()
        export_frame.pack_forget()
        translate_frame.pack_forget()

    def train():
        edit_config_frame.pack_forget()
        build_vocab_frame.pack_forget()
        sp_tokenize_frame.pack_forget()
        sp_train_frame.pack_forget()
        eval_frame.pack_forget()
        infer_frame.pack_forget()
        train_frame.pack()
        average_frame.pack_forget()
        export_frame.pack_forget()
        translate_frame.pack_forget()

    def average():
        edit_config_frame.pack_forget()
        build_vocab_frame.pack_forget()
        sp_tokenize_frame.pack_forget()
        sp_train_frame.pack_forget()
        train_frame.pack_forget()
        infer_frame.pack_forget()
        eval_frame.pack_forget()
        average_frame.pack()
        export_frame.pack_forget()
        translate_frame.pack_forget()

    def export():
        edit_config_frame.pack_forget()
        build_vocab_frame.pack_forget()
        sp_tokenize_frame.pack_forget()
        sp_train_frame.pack_forget()
        train_frame.pack_forget()
        infer_frame.pack_forget()
        eval_frame.pack_forget()
        average_frame.pack_forget()
        export_frame.pack()
        translate_frame.pack_forget()

    def infer():
        edit_config_frame.pack_forget()
        build_vocab_frame.pack_forget()
        sp_tokenize_frame.pack_forget()
        sp_train_frame.pack_forget()
        train_frame.pack_forget()
        eval_frame.pack_forget()
        infer_frame.pack()
        average_frame.pack_forget()
        export_frame.pack_forget()
        translate_frame.pack_forget()

    def eval_bleu():
        edit_config_frame.pack_forget()
        build_vocab_frame.pack_forget()
        sp_tokenize_frame.pack_forget()
        sp_train_frame.pack_forget()
        train_frame.pack_forget()
        infer_frame.pack_forget()
        eval_frame.pack()
        average_frame.pack_forget()
        export_frame.pack_forget()
        translate_frame.pack_forget()

    def translate():
        translate_frame.pack()
        edit_config_frame.pack_forget()
        build_vocab_frame.pack_forget()
        sp_tokenize_frame.pack_forget()
        sp_train_frame.pack_forget()
        train_frame.pack_forget()
        infer_frame.pack_forget()
        eval_frame.pack_forget()
        average_frame.pack_forget()
        export_frame.pack_forget()

    mainmenu = Menu(win)
    train_menu = Menu(mainmenu, tearoff=False)
    train_menu.add_command(label="Train SP", command=train_sp)
    train_menu.add_command(label="Tokenize with SP", command=tokenize_sp)
    train_menu.add_command(label="Build Vocab", command=build_vocab)
    train_menu.add_command(label="Edit Config", command=edit_config)
    train_menu.add_separator()
    train_menu.add_command(label="Train MT", command=train)
    train_menu.add_separator()
    train_menu.add_command(label="Exit", command=win.quit)

    mainmenu.add_cascade(label="Train", menu=train_menu)

    app_menu = Menu(mainmenu, tearoff=False)
    app_menu.add_command(label="Average Checkpoints", command=average)
    app_menu.add_command(label="Export Checkpoint", command=export)
    app_menu.add_separator()
    app_menu.add_command(label="Inference", command=infer)
    app_menu.add_command(label="Evaluation", command=eval_bleu)
    app_menu.add_separator()
    app_menu.add_command(label="Translate", command=translate)

    mainmenu.add_cascade(label="Application", menu=app_menu)

    win.config(menu=mainmenu)


win_main = tk.Tk()
win_main.title("MT Pipeline")
win_main.geometry("800x700")

sp_train_frame = tk.Frame(win_main)
sp_train_frame.pack()
create_sp_train(sp_train_frame)

sp_tokenize_frame = tk.Frame(win_main)
sp_tokenize_frame.pack()
create_sp_tokenize(sp_tokenize_frame)

build_vocab_frame = tk.Frame(win_main)
build_vocab_frame.pack()
create_build_vocab(build_vocab_frame)

edit_config_frame = tk.Frame(win_main)
edit_config_frame.pack()
create_edit_config(edit_config_frame)

train_frame = tk.Frame(win_main)
train_frame.pack()
create_train(train_frame)

average_frame = tk.Frame(win_main)
average_frame.pack()
create_average(average_frame)

export_frame = tk.Frame(win_main)
export_frame.pack()
create_export(export_frame)

eval_frame = tk.Frame(win_main)
eval_frame.pack()
create_eval(eval_frame)

infer_frame = tk.Frame(win_main)
infer_frame.pack()
create_infer(infer_frame)

translate_frame = tk.Frame()
translate_frame.pack()
create_translate(translate_frame)

create_menu(win_main)

# hide all frames
sp_train_frame.pack_forget()
sp_tokenize_frame.pack_forget()
build_vocab_frame.pack_forget()
edit_config_frame.pack_forget()
train_frame.pack_forget()

average_frame.pack_forget()
export_frame.pack_forget()
eval_frame.pack_forget()
infer_frame.pack_forget()
translate_frame.pack_forget()

win_main.mainloop()
