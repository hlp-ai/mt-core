import requests, json
import base64
import os

END_POINT = "http://127.0.0.1:5555"  # for edit
token = "api_key"  # api_key
source_lang = "zh"
target_lang = "en"

# test1: image to text
with open("image.png", "rb") as image_file:    # 设置本地图片路径
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


# test2: audio to text
audio_file_path = "dida.wav"
audio_64_string = base64.b64encode(open(audio_file_path, "rb").read())
# print(audio_64_string) # for test
suffix = audio_file_path.split(".")[-1]
if suffix == "wav" or suffix == "pcm" or suffix == "m4a" or suffix == "amr":
    audio_format = suffix  # 语音文件格式，不区分大小写，pcm/wav/amr/m4a
else:
    print("不支持该格式音频文件，请重新上传")
rate = 8000  # 采样率，8000/16000
channel = 1  # 声道数，固定为1
len = os.path.getsize(audio_file_path)  # 本地音频文件字节数4419498
# print(len) # for test
headers2 = {"Content-Type": "application/json"}
json2 = {"base64": audio_64_string.decode('utf-8'),
         "format": audio_format,
         "rate": rate,
         "channel": channel,
         "token": token,
         "len": len,
         "source": source_lang,
         "target": target_lang
         }
try:
    response_2 = requests.post(url=END_POINT+"/translate_audio2text", headers=headers2, json=json2)
    print(response_2.text)  # 客户端输出固定返回文本（服务器端保存解码音频decoded_audio.wav到本地）
except requests.exceptions.RequestException as e:
    print(f"test2请求失败,错误信息：{e}")


# test3: text to audio
headers3 = {"Content-Type": "application/json"}
json3 = {"text": "test text for 'text to audio' ",
         "source": source_lang,
         "target": target_lang
         }
try:
    response_3 = requests.post(url=END_POINT+"/translate_text2audio", headers=headers3, json=json3)
    # print(response_3.json()) # for test
    audio_data = base64.b64decode(json.loads(response_3.text).get('base64'))
    type3 = json.loads(response_3.text).get('type')
    # print(type3) # for test
    with open("text2audio." + type3, "wb") as text2audio_file:
        text2audio_file.write(audio_data)
        # 客户端保存解码音频text2audio.type到本地（服务器端打印固定接收文本）
except requests.exceptions.RequestException as e:
    print(f"test3请求失败,错误信息：{e}")





