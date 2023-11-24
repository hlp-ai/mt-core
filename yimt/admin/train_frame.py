""""Frame UI for train menu"""
import os
import tkinter as tk
from tkinter import *
import tkinter.filedialog
import tkinter.messagebox
from tkinter import ttk
from functools import partial

import yaml

from yimt.admin.win_utils import ask_open_file, ask_dir
from yimt.experimental.mnmt.add_tag import add_token
from yimt.utils.bin.pre_train import get_sp_prefix, get_tok_file, get_vocab_file, pretrain_corpus
from yimt.segmentation.sp import train_spm, load_spm, tokenize_file_sp


def create_add_tag(parent):
    tk.Label(parent, text="TSV Corpus path").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_corpus = tk.Entry(parent, width=50)
    entry_corpus.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_corpus)).grid(row=0, column=2, padx=10,
                                                                                           pady=5)

    tk.Label(parent, text="Add to SRC or TGT").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_to = tk.Entry(parent)
    entry_to.grid(row=1, column=1, padx=10, pady=5, sticky="w")
    entry_to.insert(0, "tgt")

    tk.Label(parent, text="Tag").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    entry_tag = tk.Entry(parent)
    entry_tag.grid(row=2, column=1, padx=10, pady=5, sticky="w")
    entry_tag.insert(0, "<toen>")

    def go():
        corpus_file = entry_corpus.get()
        if len(corpus_file.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Corpus path empty.")
            return

        src_or_tgt = entry_to.get()

        tag = entry_tag.get()
        add_src = True if tag.lower()=="src" else False

        add_token(corpus_file, add_src, tag)

        tk.messagebox.showinfo(title="Info", message="Tag added.")

    tk.Button(parent, text="Add Tag to TSV File", command=go).grid(row=3, column=1, padx=10, pady=5)


def create_sp_train(parent):
    tk.Label(parent, text="Raw Corpus path").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_corpus = tk.Entry(parent, width=50)
    entry_corpus.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_corpus)).grid(row=0, column=2, padx=10,
                                                                                           pady=5)

    tk.Label(parent, text="Size of vocab").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_vocab_size = tk.Entry(parent)
    entry_vocab_size.grid(row=1, column=1, padx=10, pady=5, sticky="w")
    entry_vocab_size.insert(0, "4800")

    tk.Label(parent, text="SP model path").grid(row=2, column=0, sticky="e")
    entry_model = tk.Entry(parent, width=50)
    entry_model.grid(row=2, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_dir, entry_model)).grid(row=2, column=2, padx=10, pady=5)

    tk.Label(parent, text="Max num of sentences (M)").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    entry_max_sentences = tk.Entry(parent)
    entry_max_sentences.grid(row=3, column=1, padx=10, pady=5, sticky="w")
    entry_max_sentences.insert(0, "5")

    tk.Label(parent, text="Character coverage").grid(row=4, column=0, padx=10, pady=5, sticky="e")
    entry_coverage = tk.Entry(parent)
    entry_coverage.grid(row=4, column=1, padx=10, pady=5, sticky="w")
    entry_coverage.insert(0, "0.9999")

    tk.Label(parent, text="User Defined Symbols File").grid(row=5, column=0, padx=10, pady=5, sticky="e")
    entry_symbols_file = tk.Entry(parent, width=50)
    entry_symbols_file.grid(row=5, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_symbols_file)).grid(row=5, column=2,
                                                                                                 padx=10,
                                                                                                 pady=5)

    tk.Label(parent, text="remove_extra_whitespaces").grid(row=6, column=0, padx=10, pady=5, sticky="e")
    entry_extra_space = tk.Entry(parent)
    entry_extra_space.grid(row=6, column=1, padx=10, pady=5, sticky="w")
    entry_extra_space.insert(0, "true")

    tk.Label(parent, text="normalization_rule_name").grid(row=7, column=0, padx=10, pady=5, sticky="e")
    entry_norm = tk.Entry(parent)
    entry_norm.grid(row=7, column=1, padx=10, pady=5, sticky="w")
    entry_norm.insert(0, "nmt_nfkc")

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

        sp_model = os.path.join(sp_model, get_sp_prefix(corpus_file, vocab_size))

        print(corpus_file, vocab_size, sp_model)

        max_sents = int(float(entry_max_sentences.get()) * 1000000)

        symbols_file = entry_symbols_file.get()
        if len(symbols_file.strip()) == 0:
            symbols_file = None

        remove_space = entry_extra_space.get().strip().lower()
        if remove_space == "true":
            remove_space = True
        else:
            remove_space = False

        normalization = entry_norm.get().strip().lower()

        train_spm(corpus_file, sp_model, vocab_size,
                  num_sentences=max_sents,
                  coverage=entry_coverage.get(),
                  remove_extra_whitespaces=remove_space,
                  normalization_rule_name=normalization,
                  user_defined_symbols_file=symbols_file)

        tk.messagebox.showinfo(title="Info", message="SentencePiece model created.")

    tk.Button(parent, text="Train SentencePiece Model", command=go).grid(row=8, column=1, padx=10, pady=5)


def create_sp_tokenize(parent):
    tk.Label(parent, text="Raw Corpus path").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_corpus = tk.Entry(parent, width=50)
    entry_corpus.grid(row=0, column=1, padx=10, pady=5)

    tk.Button(parent, text="...", command=partial(ask_open_file, entry_corpus)).grid(row=0, column=2, padx=10, pady=5)

    tk.Label(parent, text="SP model path").grid(row=1, column=0, sticky="e")
    entry_model = tk.Entry(parent, width=50)
    entry_model.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry_model)).grid(row=1, column=2, padx=10, pady=5)

    tk.Label(parent, text="Output path").grid(row=2, column=0, sticky="e")
    entry_output = tk.Entry(parent, width=50)
    entry_output.grid(row=2, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_dir, entry_output)).grid(row=2, column=2, padx=10, pady=5)


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

        tok_output = os.path.join(tok_output, get_tok_file(corpus_file))

        print(corpus_file, sp_model, tok_output)

        sp = load_spm(sp_model)
        tokenize_file_sp(sp, corpus_file, tok_output)

        tk.messagebox.showinfo(title="Info", message="Raw corpus tokenized.")

    tk.Button(parent, text="Tokenize Corpus with SP", command=go).grid(row=3, column=1, padx=10, pady=5)


def create_build_vocab(parent):
    tk.Label(parent, text="Tokenized Corpus path").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_corpus = tk.Entry(parent, width=50)
    entry_corpus.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_corpus)).grid(row=0, column=2, padx=10, pady=5)

    tk.Label(parent, text="Size of vocab").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_vocab_size = tk.Entry(parent)
    entry_vocab_size.grid(row=1, column=1, padx=10, pady=5, sticky="w")

    tk.Label(parent, text="Vocab path").grid(row=2, column=0, sticky="e")
    entry_vocab = tk.Entry(parent, width=50)
    entry_vocab.grid(row=2, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_dir, entry_vocab)).grid(row=2, column=2, padx=10, pady=5)

    tk.Label(parent, text="User Defined Symbols File").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    entry_symbols_file = tk.Entry(parent, width=50)
    entry_symbols_file.grid(row=3, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_symbols_file)).grid(row=3, column=2,
                                                                                                 padx=10,
                                                                                                 pady=5)

    tk.Label(parent, text="SentencePiece Vocab File").grid(row=4, column=0, padx=10, pady=5, sticky="e")
    entry_sp_vocab = tk.Entry(parent, width=50)
    entry_sp_vocab.grid(row=4, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_sp_vocab)).grid(row=4, column=2, padx=10,
                                                                                           pady=5)

    def go():
        corpus_file = entry_corpus.get()
        sp_vocab = entry_sp_vocab.get()
        if len(corpus_file.strip()) == 0 and len(sp_vocab.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Corpus path or sp vocab empty.")
            return

        vocab_size = entry_vocab_size.get()
        if len(corpus_file.strip()) > 0 and len(vocab_size.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Vocab size empty.")
            return

        vocab_path = entry_vocab.get()
        if len(vocab_path.strip()) == 0:
            tk.messagebox.showinfo(title="Info", message="Vocab path empty.")
            return

        symbols_file = entry_symbols_file.get().strip()
        cmd_ex = ""
        if len(symbols_file) > 0:
            cmd_ex = " --custom_symbol_file {}".format(symbols_file)

        if len(corpus_file.strip()) > 0:
            vocab_path = os.path.join(vocab_path, get_vocab_file(corpus_file))
            build_vocab_cmd = "python ../core/bin/build_vocab.py --size {} --save_vocab {} {}" + cmd_ex
            os.popen(build_vocab_cmd.format(vocab_size, vocab_path, corpus_file)).readlines()
        elif len(sp_vocab.strip()) > 0:
            vocab_path = os.path.join(vocab_path, get_vocab_file(sp_vocab))
            build_vocab_cmd = "python ../core/bin/build_vocab.py --from_vocab {} --save_vocab {}" + cmd_ex
            os.popen(build_vocab_cmd.format(sp_vocab, vocab_path)).readlines()

        tk.messagebox.showinfo(title="Info", message="Vocab created.")

    tk.Button(parent, text="Build Vocab", command=go).grid(row=5, column=1, padx=10, pady=5)


def create_pretrain(parent):
    tk.Label(parent, text="Raw Training Corpus").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_corpus_raw_train = tk.Entry(parent, width=50)
    entry_corpus_raw_train.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_corpus_raw_train)).grid(row=0, column=2, padx=10, pady=5)

    tk.Label(parent, text="PreTokenize Language").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_pretok_lang = tk.Entry(parent)
    entry_pretok_lang.grid(row=1, column=1, padx=10, pady=5, sticky="w")

    tk.Label(parent, text="Size of vocab").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    entry_vocab_size = tk.Entry(parent)
    entry_vocab_size.grid(row=2, column=1, padx=10, pady=5, sticky="w")
    entry_vocab_size.insert(0, "32000")

    tk.Label(parent, text="Raw Eval Corpus (Optional)").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    entry_corpus_raw_eval = tk.Entry(parent, width=50)
    entry_corpus_raw_eval.grid(row=3, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_corpus_raw_eval)).grid(row=3, column=2, padx=10,
                                                                                           pady=5)

    tk.Label(parent, text="Max num of sentences").grid(row=4, column=0, padx=10, pady=5, sticky="e")
    entry_max_sentences = tk.Entry(parent)
    entry_max_sentences.grid(row=4, column=1, padx=10, pady=5, sticky="w")
    entry_max_sentences.insert(0, "10000000")

    tk.Label(parent, text="Character coverage").grid(row=5, column=0, padx=10, pady=5, sticky="e")
    entry_coverage = tk.Entry(parent)
    entry_coverage.grid(row=5, column=1, padx=10, pady=5, sticky="w")
    entry_coverage.insert(0, "0.9999")

    tk.Label(parent, text="Output path (Optional)").grid(row=6, column=0, sticky="e")
    entry_output = tk.Entry(parent, width=50)
    entry_output.grid(row=6, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_dir, entry_output)).grid(row=6, column=2, padx=10, pady=5)


    def go():
        corpus_raw_train = entry_corpus_raw_train.get().strip()
        corpus_raw_eval = entry_corpus_raw_eval.get().strip()
        vocab_size = entry_vocab_size.get().strip()
        output_path = entry_output.get().strip()

        if len(corpus_raw_train) == 0:
            tk.messagebox.showinfo(title="Info", message="Training Corpus path empty.")
            return

        if len(vocab_size) == 0:
            tk.messagebox.showinfo(title="Info", message="Vocab size empty.")
            return

        pretok_lang = entry_pretok_lang.get().strip()
        if len(pretok_lang) == 0:
            pretok_lang = None

        if len(output_path) == 0:
            output_path = None

        pretrain_corpus(corpus_raw_train, corpus_raw_eval, pretok_lang,
                        vocab_size, output_path,
                        entry_max_sentences.get(), entry_coverage.get())

        tk.messagebox.showinfo(title="Info", message="One-Step PreTrain Done.")

    tk.Button(parent, text="One-Step PreTrain", command=go).grid(row=9, column=1, padx=10, pady=5)


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

    tk.Label(parent, text="Target File for Training").grid(row=2, column=0, padx=10, pady=5, sticky="e")
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
    entry_batch_size.insert(0, "3200")

    tk.Label(parent, text="Effective Train Batch Size").grid(row=9, column=0, padx=10, pady=5, sticky="e")
    entry_effective_batch_size = tk.Entry(parent)
    entry_effective_batch_size.grid(row=9, column=1, padx=10, pady=5, sticky="w")
    entry_effective_batch_size.insert(0, "25600")

    tk.Label(parent, text="Train Max Step").grid(row=10, column=0, padx=10, pady=5, sticky="e")
    entry_max_step = tk.Entry(parent)
    entry_max_step.grid(row=10, column=1, padx=10, pady=5, sticky="w")
    entry_max_step.insert(0, "30000")

    tk.Label(parent, text="Checkpoint Step").grid(row=11, column=0, padx=10, pady=5, sticky="e")
    entry_ckpt_step = tk.Entry(parent)
    entry_ckpt_step.grid(row=11, column=1, padx=10, pady=5, sticky="w")
    entry_ckpt_step.insert(0, 1000)

    tk.Label(parent, text="Max Checkpoints").grid(row=12, column=0, padx=10, pady=5, sticky="e")
    entry_ckpt_max = tk.Entry(parent)
    entry_ckpt_max.grid(row=12, column=1, padx=10, pady=5, sticky="w")
    entry_ckpt_max.insert(0, '5')

    tk.Label(parent, text="Summary Step").grid(row=13, column=0, padx=10, pady=5, sticky="e")
    entry_summary_step = tk.Entry(parent)
    entry_summary_step.grid(row=13, column=1, padx=10, pady=5, sticky="w")
    entry_summary_step.insert(0, 100)

    tk.Label(parent, text="Evaluation Step").grid(row=14, column=0, padx=10, pady=5, sticky="e")
    entry_eval_step = tk.Entry(parent)
    entry_eval_step.grid(row=14, column=1, padx=10, pady=5, sticky="w")
    entry_eval_step.insert(0, 1000)

    tk.Label(parent, text="Evaluation Scorer").grid(row=15, column=0, padx=10, pady=5, sticky="e")
    entry_eval_scorer = tk.Entry(parent)
    entry_eval_scorer.grid(row=15, column=1, padx=10, pady=5, sticky="w")
    entry_eval_scorer.insert(0, "bleu")

    tk.Label(parent, text="Beam Width").grid(row=16, column=0, padx=10, pady=5, sticky="e")
    entry_params_beam = tk.Entry(parent)
    entry_params_beam.grid(row=16, column=1, padx=10, pady=5, sticky="w")
    entry_params_beam.insert(0, "5")

    tk.Label(parent, text="Sample Buffer Size").grid(row=17, column=0, padx=10, pady=5, sticky="e")
    entry_train_buf_size = tk.Entry(parent)
    entry_train_buf_size.grid(row=17, column=1, padx=10, pady=5, sticky="w")
    entry_train_buf_size.insert(0, "-1")

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
        if len(src_eval.strip()) > 0:
            config["data"]["eval_features_file"] = src_eval.strip()

        tgt_eval = entry_tgt_eval.get()
        if len(tgt_eval.strip()) > 0:
            config["data"]["eval_labels_file"] = tgt_eval.strip()

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
        config["train"]["effective_batch_size"] = int(entry_effective_batch_size.get())
        config["train"]["max_step"] = int(entry_max_step.get())
        config["train"]["save_checkpoints_steps"] = int(entry_ckpt_step.get())
        config["train"]["keep_checkpoint_max"] = int(entry_ckpt_max.get())
        config["train"]["average_last_checkpoints"] = int(entry_ckpt_max.get())
        config["train"]["save_summary_steps"] = int(entry_summary_step.get())
        config["train"]["sample_buffer_size"] = int(entry_train_buf_size.get())

        config["eval"] = {}
        config["eval"]["steps"] = int(entry_eval_step.get())
        config["eval"]["scorers"] = entry_eval_scorer.get()

        config["params"] = {}
        config["params"]["beam_width"] = int(entry_params_beam.get())

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
