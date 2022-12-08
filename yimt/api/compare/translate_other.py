import http.client
import hashlib
import urllib
import random
import json
import requests
import uuid
import time
from tqdm import *
from tencentcloud.common import credential#这里需要安装腾讯翻译sdk pip install tencentcloud-sdk-python
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tmt.v20180321 import tmt_client, models

def main(sf,tf,sl,tl,ifbaidu,ifyoudao,iftencent,ifWin):
    fo = open(sf, "r", encoding='utf-8')  # 编码必须是utf-8
    if (ifbaidu):
        f1= open(tf+"\\"+"baiduresult.txt", mode="w",encoding='utf-8')
        f1.truncate()
    if (ifyoudao):
        f2= open(tf+"\\"+"youdaoresult.txt", mode="w",encoding='utf-8')
        f2.truncate()
    if (iftencent):
        f3= open(tf+"\\"+"tencentresult.txt", mode="w",encoding='utf-8')
        f3.truncate()
    if(ifWin):
        f4= open(tf+"\\"+"WinAzureresult.txt", mode="w",encoding='utf-8')
        f4.truncate()

    for line in tqdm(fo):               #循环读取与读入
        line = line.strip('\n')#读取不带换行符号，避免最后一行出问题
        if(ifbaidu):
            f1.write(line+'\t')
            f1.write(baidutrans(line, sl, tl) + '\n')
        if (ifyoudao):
            f2.write(line + '\t')
            f2.write(youdaotrans(line,sl,tl) + '\n')
        if (iftencent):
            f3.write(line + '\t')
            f3.write(tencenttrans(line,sl,tl)+ '\n')
        if(ifWin):
            f4.write(line + '\t')
            f4.write(WinAzuretrans(line, sl, tl) + '\n')
        time.sleep(1)#避免产生api过频调用
    print('翻译结束！')

def WinAzuretrans(str4,slanguage,tlanguage):
    if (slanguage == '中文'): slanguage = 'zh-Hans'
    if (slanguage == '英文'): slanguage = 'en'
    if (slanguage == '日文'): slanguage = 'ja'
    if (slanguage == '韩文'): slanguage = 'ko'
    if (tlanguage == '中文'): tlanguage = 'zh-Hans'
    if (tlanguage == '英文'): tlanguage = 'en'
    if (tlanguage == '日文'): tlanguage = 'ja'
    if (tlanguage == '韩文'): tlanguage = 'ko'
    key = "e29ce19c977b45b9b29051e6c4577ae7"
    endpoint = "https://api.cognitive.microsofttranslator.com/"

    # location, also known as region.
    # required if you're using a multi-service or regional (not global) resource. It can be found in the Azure portal on the Keys and Endpoint page.
    location = "eastasia"

    path = '/translate'
    constructed_url = endpoint + path

    params = {
        'api-version': '3.0',
        'from': slanguage,
        'to': [tlanguage]
    }

    headers = {
        'Ocp-Apim-Subscription-Key': key,
        # location required if you're using a multi-service or regional (not global) resource.
        'Ocp-Apim-Subscription-Region': location,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    # You can pass more than one object in body.
    body = [{
        'text': str4
    }]

    request = requests.post(constructed_url, params=params, headers=headers, json=body)
    response = request.json()

    data=json.dumps(response, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ': '))
    result=json.loads(data)
    return result[0]['translations'][0]['text']

def baidutrans(str1,slanguage,tlanguage):
    appid = '20220808001298811'  # 填写你的appid
    secretKey = 'BlvcEoyjf41q7TrJJfeQ'  # 填写你的密钥

    httpClient = None
    myurl = '/api/trans/vip/translate'  # 通用翻译API HTTP地址
    if(slanguage=='中文'):slanguage='zh'
    if(slanguage=='英文'):slanguage='en'
    if(slanguage=='日文'): slanguage = 'jp'
    if(slanguage=='韩文'): slanguage = 'kor'
    if(tlanguage=='中文'):tlanguage='zh'
    if(tlanguage=='英文'):tlanguage='en'
    if(tlanguage=='日文'): tlanguage = 'jp'
    if(tlanguage=='韩文'): tlanguage = 'kor'
    fromLang = slanguage  # 原文语种，中zh 英en 日 韩
    toLang = tlanguage  # 译文语种
    salt = random.randint(32768, 65536)
    # 手动录入翻译内容，q存放
    q = str1
    sign = appid + q + str(salt) + secretKey
    sign = hashlib.md5(sign.encode()).hexdigest()
    myurl = myurl + '?appid=' + appid + '&q=' + urllib.parse.quote(q) + '&from=' + fromLang + \
            '&to=' + toLang + '&salt=' + str(salt) + '&sign=' + sign
    # 建立会话，返回结果
    try:
        httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('GET', myurl)
        # response是HTTPResponse对象
        response = httpClient.getresponse()
        result_all = response.read().decode("utf-8")
        result = json.loads(result_all)

    except Exception as e:
        print(e)
    finally:
        if httpClient:
            httpClient.close()
    return result['trans_result'][0]['dst']

def youdaotrans(str2,slanguage,tlanguage):
    youdao_url = 'https://openapi.youdao.com/api'  # 有道api地址
    # 需要翻译的文本'
    translate_text = str2
    # 翻译文本生成sign前进行的处理
    input_text = ""

    # 当文本长度小于等于20时，取文本
    if (len(translate_text) <= 20):
        input_text = translate_text
    # 当文本长度大于20时，进行特殊处理
    elif (len(translate_text) > 20):
        input_text = translate_text[:10] + str(len(translate_text)) + translate_text[-10:]

    time_curtime = int(time.time())  # 秒级时间戳获取
    app_id = '4ea30230142fb070'  # 应用id
    uu_id = uuid.uuid1()  # 随机生成的uuid数，为了每次都生成一个不重复的数。
    salt = str(uu_id)
    app_key = 'le6A4etmjineVBDegcbGAYxclqeDvAlE'  # 应用密钥

    sign = hashlib.sha256((app_id + input_text + salt + str(time_curtime) + app_key).encode('utf-8')).hexdigest()  # sign生成
    if (slanguage == '中文'): slanguage = 'zh-CHS'
    if (slanguage == '英文'): slanguage = 'en'
    if (slanguage == '日文'): slanguage = 'ja'
    if (slanguage == '韩文'): slanguage = 'ko'
    if (tlanguage == '中文'): tlanguage = 'zh-CHS'
    if (tlanguage == '英文'): tlanguage = 'en'
    if (tlanguage == '日文'): tlanguage = 'ja'
    if (tlanguage == '韩文'): tlanguage = 'ko'
    data = {
        'q': translate_text,  # 翻译文本
        'from': slanguage,  # 源语言参数
        'to': tlanguage,  # 翻译语言参数
        'appKey': app_id,  # 应用id
        'salt': salt,  # 随机生产的uuid码
        'sign': sign,  # 签名
        'signType': "v3",  # 签名类型，固定值
        'curtime': time_curtime,  # 秒级时间戳
    }

    r = requests.get(youdao_url, params=data).json()  # 获取返回的json()内容
    return r["translation"][0]  # 获取翻译内容

def tencenttrans(str3,slanguage,tlanguage):
    try:
        cred = credential.Credential("AKIDeCZiJfmdEZeS0HI5cdOvBALfojQyMUO6", "XopcAUZR7bpqmaClAMNAi04uhFafV4NP")
        httpProfile = HttpProfile()
        httpProfile.endpoint = "tmt.tencentcloudapi.com"
        if (slanguage == "中文"): slanguage = 'zh'
        if (slanguage == '英文'): slanguage = 'en'
        if (slanguage == '日文'): slanguage = 'ja'
        if (slanguage == '韩文'): slanguage = 'ko'
        if (tlanguage == '中文'): tlanguage = 'zh'
        if (tlanguage == '英文'): tlanguage = 'en'
        if (tlanguage == '日文'): tlanguage = 'ja'
        if (tlanguage == '韩文'): tlanguage = 'ko'
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = tmt_client.TmtClient(cred, "ap-beijing", clientProfile)

        req = models.TextTranslateRequest()
        req.SourceText = str3
        req.Source =slanguage
        req.Target =tlanguage
        req.ProjectId = 0

        resp = client.TextTranslate(req)
        data=json.loads(resp.to_json_string())
        return data['TargetText']


    except TencentCloudSDKException as err:
        print(err)
