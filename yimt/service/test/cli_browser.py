import requests, json

END_POINT = "http://127.0.0.1:5555"  # for edit
token = "api_key"  # api_key
source_lang = "en"
target_lang = "zh"


headers1 = {"Content-Type": "application/json"}
json1 = {"q": ['This is a test.', '<a href="">this is a link.</a>'],
         "token": token,
         "source": source_lang,
         "target": target_lang}
try:
    response1 = requests.post(url=END_POINT+"/translate", headers=headers1, json=json1)
    print(response1.text)
    jstr = json.loads(response1.text)
    print(jstr["translatedText"])
    ts = jstr["translatedText"]
    for t in ts:
        print(t)
except requests.exceptions.RequestException as e:
    print(f"请求失败, 错误信息：{e}")