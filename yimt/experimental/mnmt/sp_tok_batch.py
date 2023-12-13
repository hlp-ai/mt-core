import argparse
import os

from yimt.segmentation.sp import load_spm, tokenize_file_sp

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--sp_model", required=True, help="SentencePiece model path")
    argparser.add_argument("--root", required=True, help="directory")
    args = argparser.parse_args()

    root = args.root
    files = os.listdir(root)
    files = [os.path.join(root, f) for f in files]

    sp = load_spm(args.sp_model)

    for f in files:
        print(f)
        tokenize_file_sp(sp, f, f+".tok")