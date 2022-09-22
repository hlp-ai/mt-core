import tkinter as tk
from tkinter import *

from yimt.admin.app_frame import create_average, create_export, create_eval, create_infer, create_translate
from yimt.admin.train_frame import create_sp_train, create_sp_tokenize, create_build_vocab, create_edit_config, \
    create_train


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
