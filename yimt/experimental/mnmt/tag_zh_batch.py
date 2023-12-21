import argparse
import os


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", required=True, help="file dir")
    args = parser.parse_args()

    input = args.dir

    files = os.listdir(input)
    for f in files:
        i = f.index("-")
        lang = f[:i]
        token = "<to" + lang + ">"
        f = os.path.join(input, f)
        print(f, token)
        with open(f, encoding="utf-8") as zh_f, open(f+".tag", "w", encoding="utf-8") as out:
            for line in zh_f:
                line = token + " " + line.strip()
                out.write(line + "\n")