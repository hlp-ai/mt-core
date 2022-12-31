import os
import tkinter as tk
import tkinter.filedialog
from tkinter import ttk
from tkinter import *
from functools import partial

from yimt.admin.compare import main
from yimt.admin.win_utils import ask_open_file


def create_trans(parent):
    def selectPath():
        path_ = tkinter.filedialog.askopenfilename()
        # replace函数替换绝对文件地址中的/来使文件可被程序读取
        # \\转义，便于传参
        path_ = path_.replace("/", "\\\\")
        # path设置path_的值
        path.set(path_)

    # 选择放入的路径
    def selecttPath():
        path_t = tkinter.filedialog.askdirectory()
        path_t = path_t.replace("/", "\\\\")
        patht.set(path_t)

    # 窗口内容
    path = tk.StringVar()
    patht = tk.StringVar()
    sl_choose = tk.StringVar()
    tl_choose = tk.StringVar()
    # 选择文件
    laber_choose = tk.Label(parent, text="你选择的文件是:", font=('微软雅黑', 10), anchor="nw")
    laber_choose.grid(pady=10, row=0, column=0)
    entry_choose = tk.Entry(parent, textvariable=path, width=50).grid(row=0, column=1, padx=10, pady=5, sticky="w")
    Button_choose = tk.Button(parent, text="...", command=selectPath, font=('微软雅黑', 10)).grid(row=0, column=2, padx=10,
                                                                                              pady=5)
    # 选择路径
    laber_target = tk.Label(parent, text="你输出的路径是:", font=('微软雅黑', 10), anchor="nw")
    laber_target.grid(pady=10, row=1, column=0)
    entry_choose_target = tk.Entry(parent, textvariable=patht, width=50).grid(row=1, column=1, padx=10, pady=5,
                                                                              sticky="w")
    Button_choose_target = tk.Button(parent, text="...", command=selecttPath, font=('微软雅黑', 10)).grid(row=1, column=2,
                                                                                                      padx=10, pady=5)
    # 选择源语言
    laber_choose_slanguage = tk.Label(parent, text="翻译源语言:", font=('微软雅黑', 10), anchor="nw")
    laber_choose_slanguage.grid(pady=10, row=2, column=0)
    choose_slanguage = ttk.Combobox(parent, textvariable=sl_choose)
    choose_slanguage.grid(row=2, column=1, padx=10, pady=5, sticky='w')
    choose_slanguage["value"] = ("中文", "英文", "韩文", "日文", "越南语", "俄语", "德语")
    choose_slanguage.current(0)

    # 选择目标语言
    laber_choose_tlanguage = tk.Label(parent, text="翻译目标语言:", font=('微软雅黑', 10), anchor="nw")
    laber_choose_tlanguage.grid(pady=10, row=3, column=0)
    choose_tlanguage = ttk.Combobox(parent, textvariable=tl_choose)
    choose_tlanguage.grid(row=3, column=1, padx=10, pady=5, sticky='w')
    choose_tlanguage["value"] = ("中文", "英文", "韩文", "日文", "越南语", "俄语", "德语")

    # 选择翻译api
    laber_choose_api = tk.Label(parent, text="翻译来源:", font=('微软雅黑', 10), anchor="nw")
    laber_choose_api.grid(row=4, column=0, padx=10, pady=5)
    v1 = IntVar()
    c1 = Checkbutton(parent, text="百度", variable=v1)
    c1.grid(row=4, column=1, sticky='w')
    v2 = IntVar()
    c2 = Checkbutton(parent, text="有道", variable=v2)
    c2.grid(row=5, column=1, sticky='w')
    v3 = IntVar()
    c3 = Checkbutton(parent, text="腾讯", variable=v3)
    c3.grid(row=6, column=1, sticky='w')
    v4 = IntVar()
    c4 = Checkbutton(parent, text="微软", variable=v4)
    c4.grid(row=7, column=1, sticky='w')

    # 选择语言下拉选项响应事件
    def sFunc(event):
        if (str(sl_choose.get()) == '中文'):
            choose_tlanguage["value"] = ("中文", "英文", "韩文", "日文", "越南语", "俄语", "德语")
        elif (str(sl_choose.get()) == '英文'):
            choose_tlanguage["value"] = ("中文")
        elif (str(sl_choose.get()) == '日文'):
            choose_tlanguage["value"] = ("中文")
        elif (str(sl_choose.get()) == '韩文'):
            choose_tlanguage["value"] = ("中文")
        elif (str(sl_choose.get()) == '越南语'):
            choose_tlanguage["value"] = ("中文")
        elif (str(sl_choose.get()) == '俄语'):
            choose_tlanguage["value"] = ("中文")
        elif (str(sl_choose.get()) == '德语'):
            choose_tlanguage["value"] = ("中文")

    def tFunc(event):
        if (str(tl_choose.get()) == '中文'):
            choose_slanguage["value"] = ("中文", "英文", "韩文", "日文", "越南语", "俄语", "德语")
        elif (str(tl_choose.get()) == '英文'):
            choose_slanguage["value"] = ("中文")
        elif (str(tl_choose.get()) == '日文'):
            choose_slanguage["value"] = ("中文")
        elif (str(tl_choose.get()) == '韩文'):
            choose_slanguage["value"] = ("中文")
        elif (str(tl_choose.get()) == '越南语'):
            choose_slanguage["value"] = ("中文")
        elif (str(tl_choose.get()) == '德语'):
            choose_slanguage["value"] = ("中文")
        elif (str(tl_choose.get()) == '俄语'):
            choose_slanguage["value"] = ("中文")

    # 选择api响应事件
    choose_slanguage.bind("<<ComboboxSelected>>", sFunc)
    choose_tlanguage.bind("<<ComboboxSelected>>", tFunc)

    def go():
        main(str(path.get()), str(patht.get()), str(sl_choose.get()), str(tl_choose.get()), v1.get(), v2.get(),
             v3.get(), v4.get())
        tk.messagebox.showinfo(title="Info", message="翻译完成！")

    # 基本框架
    button_start = tk.Button(parent, text="开始翻译", command=go)
    button_start.grid(row=10, column=1, padx=10, pady=5)


def create_sarcebleu_trans(parent):
    tk.Label(parent, text="Reference File").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_ref = tk.Entry(parent, width=50)
    entry_ref.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_ref)).grid(row=0, column=2,
                                                                                          padx=10, pady=5)

    tk.Label(parent, text="Hyp File").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_sys = tk.Entry(parent, width=50)
    entry_sys.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(parent, text="...", command=partial(ask_open_file, entry=entry_sys)).grid(row=1, column=2, padx=10,
                                                                                          pady=5)

    tk.Label(parent, text="Language Pair").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    entry_lang = tk.Entry(parent, width=50)
    entry_lang.grid(row=2, column=1, padx=10, pady=5)
    entry_lang.insert(0, "en-zh")

    tk.Label(parent, text="Additional Metrics").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    var_ter = IntVar()
    check_ter = Checkbutton(parent, text="TER", variable=var_ter, onvalue=1, offvalue=0)
    check_ter.grid(row=3, column=1, padx=10, pady=5)

    var_chrf = IntVar()
    check_chrf = Checkbutton(parent, text="ChrF", variable=var_chrf, onvalue=1, offvalue=0)
    check_chrf.grid(row=4, column=1, padx=10, pady=5)

    def go():
        ref_path = entry_ref.get().strip()
        sys_path = entry_sys.get().strip()

        if len(ref_path) == 0 or len(sys_path) == 0:
            tk.messagebox.showwarning(title="Info", message="Some parameter empty.")
            return

        cal_cmd = "sacrebleu {} -i {} -l {} -f text"
        if var_ter.get() == 1 or var_chrf.get() == 1:
            cal_cmd += " -m bleu"
            if var_ter.get() == 1:
                cal_cmd += " ter"
            if var_chrf.get() == 1:
                cal_cmd += " chrf"
        cf = os.popen(cal_cmd.format(ref_path, sys_path, entry_lang.get().strip()))
        lines = cf.readlines()
        for line in lines:
            print(line.strip())

        tk.messagebox.showinfo(title="Info", message="done")

    button_start = tk.Button(parent, text="Calculate Metric", command=go)
    button_start.grid(padx=5, pady=10, row=5, column=1)
