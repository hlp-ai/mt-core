"""Admin GUI entry"""
import tkinter as tk
from functools import partial
from tkinter import *

from yimt.admin.app_frame import create_average, create_export, create_eval, create_infer, create_translate
from yimt.admin.continue_frame import create_ft, create_mix_ft
from yimt.admin.train_frame import create_sp_train, create_sp_tokenize, create_build_vocab, create_edit_config, \
    create_train, create_pretrain
from yimt.admin.corpus_frame import create_tsv2mono_corpus, create_mono2tsv_corpus, create_merge_corpus, \
    create_normalize_corpus, create_filter_corpus, create_dedup_corpus, create_han2hans_corpus, create_sample_corpus, \
    create_split_corpus, create_merge_moses_corpus, create_tok_mono, create_detok_zh
from yimt.admin.compare_frame import create_trans,create_sarcebleu_trans


def on_menu(frame):
    for f in frames:
        if f == frame:
            f.pack()
        else:
            f.pack_forget()


if __name__ == "__main__":
    win_main = tk.Tk()
    win_main.title("MT Pipeline")
    win_main.geometry("800x700")

    ##########################################################

    frames = []

    tsv2mono_frame=tk.Frame(win_main)
    tsv2mono_frame.pack()
    create_tsv2mono_corpus(tsv2mono_frame)
    frames.append(tsv2mono_frame)

    mono2tsv_frame = tk.Frame(win_main)
    mono2tsv_frame.pack()
    create_mono2tsv_corpus(mono2tsv_frame)
    frames.append(mono2tsv_frame)

    merge_frame = tk.Frame(win_main)
    merge_frame.pack()
    create_merge_corpus(merge_frame)
    frames.append(merge_frame)

    merge_moses_frame = tk.Frame(win_main)
    merge_moses_frame.pack()
    create_merge_moses_corpus(merge_moses_frame)
    frames.append(merge_moses_frame)

    normalize_frame = tk.Frame(win_main)
    normalize_frame.pack()
    create_normalize_corpus(normalize_frame)
    frames.append(normalize_frame)

    filter_frame=tk.Frame(win_main)
    filter_frame.pack()
    create_filter_corpus(filter_frame)
    frames.append(filter_frame)

    dedup_frame = tk.Frame(win_main)
    dedup_frame.pack()
    create_dedup_corpus(dedup_frame)
    frames.append(dedup_frame)

    han2Hans_frame = tk.Frame(win_main)
    han2Hans_frame.pack()
    create_han2hans_corpus(han2Hans_frame)
    frames.append(han2Hans_frame)

    sample_frame = tk.Frame(win_main)
    sample_frame.pack()
    create_sample_corpus(sample_frame)
    frames.append(sample_frame)

    split_frame = tk.Frame(win_main)
    split_frame.pack()
    create_split_corpus(split_frame)
    frames.append(split_frame)

    tokenize_frame = tk.Frame(win_main)
    tokenize_frame.pack()
    create_tok_mono(tokenize_frame)
    frames.append(tokenize_frame)

    detokenize_frame = tk.Frame(win_main)
    detokenize_frame.pack()
    create_detok_zh(detokenize_frame)
    frames.append(detokenize_frame)

    sp_train_frame = tk.Frame(win_main)
    sp_train_frame.pack()
    create_sp_train(sp_train_frame)
    frames.append(sp_train_frame)

    sp_tokenize_frame = tk.Frame(win_main)
    sp_tokenize_frame.pack()
    create_sp_tokenize(sp_tokenize_frame)
    frames.append(sp_tokenize_frame)

    build_vocab_frame = tk.Frame(win_main)
    build_vocab_frame.pack()
    create_build_vocab(build_vocab_frame)
    frames.append(build_vocab_frame)

    pretrain_frame = tk.Frame(win_main)
    pretrain_frame.pack()
    create_pretrain(pretrain_frame)
    frames.append(pretrain_frame)

    edit_config_frame = tk.Frame(win_main)
    edit_config_frame.pack()
    create_edit_config(edit_config_frame)
    frames.append(edit_config_frame)

    train_frame = tk.Frame(win_main)
    train_frame.pack()
    create_train(train_frame)
    frames.append(train_frame)

    ft_frame = tk.Frame(win_main)
    ft_frame.pack()
    create_ft(ft_frame)
    frames.append(ft_frame)

    mix_ft_frame = tk.Frame(win_main)
    mix_ft_frame.pack()
    create_mix_ft(mix_ft_frame)
    frames.append(mix_ft_frame)

    average_frame = tk.Frame(win_main)
    average_frame.pack()
    create_average(average_frame)
    frames.append(average_frame)

    export_frame = tk.Frame(win_main)
    export_frame.pack()
    create_export(export_frame)
    frames.append(export_frame)

    eval_frame = tk.Frame(win_main)
    eval_frame.pack()
    create_eval(eval_frame)
    frames.append(eval_frame)

    infer_frame = tk.Frame(win_main)
    infer_frame.pack()
    create_infer(infer_frame)
    frames.append(infer_frame)

    translate_frame = tk.Frame()
    translate_frame.pack()
    create_translate(translate_frame)
    frames.append(translate_frame)

    translation_frame = tk.Frame(win_main)
    translation_frame.pack()
    create_trans(translation_frame)
    frames.append(translation_frame)

    bleu_frame = tk.Frame(win_main)
    bleu_frame.pack()
    create_sarcebleu_trans(bleu_frame)
    frames.append(bleu_frame)

    ####################################################################

    mainmenu = Menu(win_main)

    corpus_menu = Menu(mainmenu, tearoff=False)
    corpus_menu.add_command(label="TSV2Mono",command=partial(on_menu, tsv2mono_frame))
    corpus_menu.add_command(label="Mono2TSV",command=partial(on_menu,mono2tsv_frame))
    corpus_menu.add_separator()
    corpus_menu.add_command(label="Merge Moses Files", command=partial(on_menu, merge_moses_frame))
    corpus_menu.add_command(label="Merge Files", command=partial(on_menu, merge_frame))
    corpus_menu.add_command(label="Normalize",command=partial(on_menu,normalize_frame))
    corpus_menu.add_command(label="Dedup", command=partial(on_menu, dedup_frame))
    corpus_menu.add_command(label="Filter",command=partial(on_menu,filter_frame))
    corpus_menu.add_command(label="Split", command=partial(on_menu, split_frame))
    corpus_menu.add_separator()
    corpus_menu.add_command(label="Hant2Hans", command=partial(on_menu, han2Hans_frame))
    corpus_menu.add_command(label="Sample", command=partial(on_menu, sample_frame))
    corpus_menu.add_separator()
    corpus_menu.add_command(label="Tokenize File", command=partial(on_menu, tokenize_frame))
    corpus_menu.add_command(label="DeTokenize Chinese Text", command=partial(on_menu, detokenize_frame))
    corpus_menu.add_separator()
    corpus_menu.add_command(label="Exit", command=win_main.quit)



    mainmenu.add_cascade(label="Corpus", menu=corpus_menu)

    train_menu = Menu(mainmenu, tearoff=False)
    train_menu.add_command(label="Train SP", command=partial(on_menu, sp_train_frame))
    train_menu.add_command(label="Tokenize with SP", command=partial(on_menu, sp_tokenize_frame))
    train_menu.add_command(label="Build Vocab", command=partial(on_menu, build_vocab_frame))
    train_menu.add_separator()
    train_menu.add_command(label="One-Step PreTrain", command=partial(on_menu, pretrain_frame))
    train_menu.add_command(label="Edit Config", command=partial(on_menu, edit_config_frame))
    train_menu.add_separator()
    train_menu.add_command(label="Train MT", command=partial(on_menu, train_frame))
    train_menu.add_command(label="Fine-tune", command=partial(on_menu, ft_frame))
    train_menu.add_command(label="Mixed Fine-tune", command=partial(on_menu, mix_ft_frame))

    mainmenu.add_cascade(label="Train", menu=train_menu)

    app_menu = Menu(mainmenu, tearoff=False)
    app_menu.add_command(label="Average Checkpoints", command=partial(on_menu, average_frame))
    app_menu.add_command(label="Export Checkpoint", command=partial(on_menu, export_frame))
    app_menu.add_separator()
    app_menu.add_command(label="Inference", command=partial(on_menu, infer_frame))
    app_menu.add_command(label="Evaluate", command=partial(on_menu, eval_frame))
    app_menu.add_separator()
    app_menu.add_command(label="Translate interactively", command=partial(on_menu, translate_frame))

    mainmenu.add_cascade(label="Application", menu=app_menu)

    Trans_menu = Menu(mainmenu, tearoff=False)
    Trans_menu.add_command(label="Other APIs", command=partial(on_menu, translation_frame))
    Trans_menu.add_command(label="Calculate Bleu", command=partial(on_menu, bleu_frame))

    mainmenu.add_cascade(label="Compare", menu=Trans_menu)

    win_main.config(menu=mainmenu)

    ######################################################################

    for f in frames:
        f.pack_forget()

    win_main.mainloop()
