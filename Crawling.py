#!/usr/bin/env python
# coding: utf-8

# # Import Modules

import requests
from pprint import pprint
from urllib import request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, UnexpectedAlertPresentException, WebDriverException
from selenium.webdriver.common.keys import Keys
from time import sleep
import time
import pandas as pd
import numpy as np
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')


def get_bands():  # 밴드목록
    url = f'https://openapi.band.us/v2.1/bands?access_token={token}'
    req = request.Request(url)
    res = request.urlopen(req)
    decoded = res.read().decode("utf8")
    json_dict = json.loads(decoded)
    return json_dict


# Selenium
def login():
    options = Options()
    options.headless = False
    driver = webdriver.Chrome('C:/Users/yuins/Hanyang_22_2nd/k99/chromedriver.exe', options=options)
    driver.implicitly_wait(3)
    driver.get("https://auth.band.us/login_page")
    time.sleep(1)
    return driver


def load(driver, num):
    """
    특정 번호의 게시물로 로딩
    """
    url = f'https://band.us/band/86069680/post/{num}'
    driver.get(url)


def getCreatedAt(driver):
    """
    글 작성 시간을 datetime 형식으로 불러옴
    """
    time = driver.find_element_by_xpath('//*[@id="content"]/div/section/div/div/div[3]/div[1]/div/div/a/time').text
    time_date = datetime.strptime(time, '%b %d, %Y, %H:%M %p')
    return time_date


def getAuthorName(driver, cust_info):
    """
    글 작성자의 닉네임을 불러옴

    cust_info : df
    """
    authorName = driver.find_element_by_xpath(
        '//*[@id="content"]/div/section/div/div/div[3]/div[1]/div/span/strong').text
    try:
        kid = cust_info[cust_info['닉네임'] == authorName]['id']
        kname = cust_info[cust_info['닉네임'] == authorName]['이름']
    except:
        kid = None
        kname = None
    return authorName, kid, kname


def getText(driver):
    """
    글의 원문을 불러옴
    """
    string = ""
    text = driver.find_elements_by_class_name('dPostTextView')
    for t in text:
        string += t.text
    return string


def getTag(driver):
    """
    태그 (실전사례 등) 을 가져옴
    """
    try:
        tag = driver.find_element_by_xpath('//*[@id="content"]/div/section/div/div/div[3]/div[6]/a').text
    except NoSuchElementException as e:
        tag = None
    return tag


def getVideoPhotoUrls(driver):
    """
    사진과 동영상의 url을 가져옴
    """
    vps = driver.find_elements_by_class_name('uCollage')
    l = []
    for vp in vps:
        try:
            tmp = vp.find_element_by_tag_name('video')
            l.append(tmp.get_attribute('src'))
        except NoSuchElementException as e:
            l.append(vp.find_element_by_tag_name('img').get_attribute('src'))
    return l


def main(log, driver=None):
    if not log:
        driver = login()
        return driver, None
    else:
        df = pd.DataFrame(columns=['postkey', 'createdat', '닉네임', 'authorkid', 'authorkname', 'text', 'tag', 'pvurl'])
        cust_info = pd.read_csv("../data/customer_update.csv", encoding='utf-8')
        for num in range(1, 2210):  # ~2210
            try:
                load(driver, num)
                time.sleep(2)
                createdat = getCreatedAt(driver)
                author, kid, kname = getAuthorName(driver, cust_info)
                text = getText(driver)
                tag = getTag(driver)
                vp_urls = getVideoPhotoUrls(driver)
                df = df.append({'postkey': num,
                                'createdat': createdat,
                                '닉네임': author,
                                'authorkid': kid,
                                'authorkname': kname,
                                'text': text,
                                'tag': tag,
                                'pvurl': vp_urls}, ignore_index=True)
            #                 print(createdat, author, text, tag, vp_urls)
            except UnexpectedAlertPresentException as e:
                # 삭제된 게시물의 경우 다음거로
                continue
            except Exception as e:
                print("게시물 번호 : ", num)
                print(e)
                continue
        return driver, df.reset_index(drop=True)


# Main
if __name__ == "__main__":

    ################# PARAMETER #################
    # access_token과 bandkey 입력.
    token = "ACCESS TOKEN HERE"  # 유출 금지
    bandkey = "BAND KEY HERE"  # 유출 금지
    LOGIN = False  # 처음에 로그인되어있지 않을 때, False인 상태에서 시작
    #############################################
    if not LOGIN:
        driver = None
    driver, df = main(log=LOGIN, driver=driver)
    df.to_csv("posts.csv", encoding='utf-8')

# In[ ]:




