
from yimt.api.translator import TranslatorCT2

if __name__ == "__main__":
    enzh = TranslatorCT2(r"D:\kidden\mt\mt-exp\ko-zh\opus\run1\model\export\ct2",
                         r"D:\kidden\mt\mt-exp\ko-zh\opus\tok\opus-kozh-sf.ko-sp-32000.model",
                         "ko-zh")

    txt = ["해외 입국 전 검사에 이어 입국 후 검사도 해제돼"]
    trans = enzh.translate_list(txt)
    print(trans)
