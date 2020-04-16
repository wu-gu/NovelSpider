#!/usr/bin/python3
# coding:utf-8

from bs4 import BeautifulSoup
import requests
import re
import os
import time

# 基本信息,从开发者工具的Netword可以获取
headers = {
    'Host': 'qiushubang.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
    'Connection': 'closed'
}
# 看网站的meta标签的charset是什么
websiteEncoding = "gbk"

host = "https://qiushubang.com"
bookId = "135346"
firstChapterId = "57931970"

# 获取书信息
bookPageUrl = f'{host}/{bookId}/'
bookPageResponse = requests.get(bookPageUrl, headers=headers)
bookPageResponse.encoding = websiteEncoding
# print(bookPageResponse.text)

soup = BeautifulSoup(bookPageResponse.text, 'html.parser')

bookName = soup.head.select('meta[property="og:title"]')[0]['content']
bookAuthor = soup.head.select('meta[property="og:novel:author"]')[0]['content']
bookIntroduction = soup.select('div.intro_info')[0].text

# 创建目录，open函数不会自动创建新目录
dirPath = os.path.join(os.getcwd(), 'books')
if not os.path.exists(dirPath):
    os.makedirs(dirPath)
filePath = os.path.join(dirPath, bookName + '.txt')
# 此处设置字符集为utf-8，有时候gbk会有些字符不识别
file = open(filePath, mode='w+', encoding='utf-8')
# 写入基本信息
file.write(f'书名: {bookName}\n')
file.write(f'作者: {bookAuthor}\n')
file.write(f'简介: {bookIntroduction}\n')
file.write('\n')

firstChapterUrl = f'{host}/{bookId}/{firstChapterId}.html'
currChapterUrl = firstChapterUrl
chapterCount = 1

# 设置重连次数
requests.adapters.DEFAULT_RETRIES = 5

# 此处采用从第一章开始，获取内容后，捕获下一章按钮的链接，然后跳转到第二章循环往复，结束条件根据网站而变，此处为判断是否有下一章按钮
while 1:
    try:
        chapterResponse = requests.get(currChapterUrl, headers=headers)
        chapterResponse.encoding = websiteEncoding
    #except requests.exceptions.ConnectionError:
    # 防止请求速度过快或连接数过多，同时最好在headers里面设置Connections为closed
    except:
        print("ZZzzzz...")
        time.sleep(5)
        continue

    chapterSoup = BeautifulSoup(chapterResponse.text, 'html.parser')

    chapterTitle = chapterSoup.body.select('#nr_title')[0].text.strip()
    rawContent = chapterSoup.body.select('#nr1')[0].text.strip()
    ''' 
    关于换行：
    br标签通常是单独使用，但Beautifulsoup只能抓取成对的标签，所以碰到br时返回None。
    在rawContent中，网页的<br>不会存在，所以要识别换行:
    一种方法是将response的text中的<br>替换成为\n，然后再转换成BeautifulSoup，最后将&nbsp去除；
    另一种方法是识别网页中的空格符&nbsp(毕竟每一段开头一般会空两个中文字符的位置)，将其替换为\n
    '''
    # 去除空格 &nbsp，也就是unicode的\xa0
    content = re.sub('\xa0{4}', '\n', rawContent)

    file.write(f'第{chapterCount}章 {chapterTitle}\n')
    file.write(content)
    file.write('\n\n')
    print(f'第{chapterCount}章 {chapterTitle} 爬取完毕')
    chapterCount += 1

    # 是否最后一章
    nextPageSelection = chapterSoup.body.select('#pb_next')
    if len(nextPageSelection) == 0:
        break
    else:
        nextChapterUrlSuffix = nextPageSelection[0]['href']
        currChapterUrl = host + nextChapterUrlSuffix
        # 是否设置爬取间隔，避免过于频繁，ip被封
        # time.sleep(0.5)

file.close()
print('整本书爬取完毕')






