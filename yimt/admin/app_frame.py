""""Frame UI for application menu"""
import os
import tkinter as tk
from tkinter import *
import tkinter.messagebox
from tkinter import ttk
from functools import partial

from yimt.admin.win_utils import ask_open_file, ask_dir
from yimt.api.translators import load_translator
from yimt.utils.bin.exec_eval import run_eval, run_infer


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
    checkboc_type['value'] = ('saved_model', 'ctranslate2', 'tflite_dynamic_range', 'tflite_float16')
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
        if checkboc_type.get() != "saved_model":
            export_cmd += " --format {}".format(checkboc_type.get())

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
    # TODO: Problem for setting command handler
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