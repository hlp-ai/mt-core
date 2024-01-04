import sys

import requests, json
import base64
import os

END_POINT = "http://127.0.0.1:5555"  # for edit
token = "api_key"  # api_key
source_lang = sys.argv[2]
target_lang = sys.argv[3]

img_file = sys.argv[1]


with open(img_file, "rb") as image_file:    # 设置本地图片路径
    encoded_image = base64.b64encode(image_file.read())

# print(encoded_image) # for test
headers1 = {"Content-Type": "application/json"}
json1 = {"base64": encoded_image.decode('utf-8'),
         "token": token,
         "source": source_lang,
         "target": target_lang}
try:
    response1 = requests.post(url=END_POINT+"/translate_image2text", headers=headers1, json=json1)
    print(response1.text)  # 客户端输出固定返回文本（服务器端保存解码图片decoded_image.png到本地）
except requests.exceptions.RequestException as e:
    print(f"test1请求失败,错误信息：{e}")