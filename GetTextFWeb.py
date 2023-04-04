import requests
from bs4 import BeautifulSoup
#import langid 备用库
from langdetect import detect#pip install langdetect

def GetHtmlText(url):
    if __name__ == '__main__':
        req = requests.get(url)
        req.encoding='utf-8'
        html = req.text
        bes = BeautifulSoup(html,'html.parser')
        texts = bes.get_text()
        texts_list = texts.split("\n")
        texts_list = [x.strip() for x in texts_list if x.strip() != '']
        with open("D:/nove.txt", "w",encoding='utf-8') as file:  ##打开读写文件，逐行将列表读入文件内
            for line in texts_list:
                file.write(line+"\n")
                #print(detect(line))
                with open("D:/"+detect(line)+".txt", encoding="utf-8", mode="a") as f:
                    f.write(line+"\n")
                f.close()

    #detect 可以用langid中的langid.classify()代替
