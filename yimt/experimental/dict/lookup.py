import json
import os


if __name__ == "__main__":
    json_fn = r"D:\kidden\mt\mt-exp\dict\zhen-dict.json"

    dict_json = {}
    if os.path.exists(json_fn):
        with open(json_fn, encoding="utf-8") as f:
            dict_json = json.loads(f.read())

    print(len(dict_json))

    while True:
        w = input("Input word or phrase: ")
        if w in dict_json:
            print(dict_json[w])
        else:
            print("Not exist")
