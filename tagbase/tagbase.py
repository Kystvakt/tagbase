# tagbase.py

import sys

sys.path.insert(0, "/usr/lib/chromium-browser/chromedriver")

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

import requests
from bs4 import BeautifulSoup
from random import shuffle
import numpy as np


# Current Popular Tags and Recommendations

def genie_postprocess(tags):
    exception = ["#오늘의선곡", "#TV속음악", "#시대별음악", "#레이블추천", "#스타플레이리스트", "#브랜드DJ"]
    tags_genie = [x for x in tags if x not in exception and " " not in x]
    temp = dict({})
    for tag in tags_genie:
        if tag in temp:
            temp[tag] += 1
        else:
            temp[tag] = 1
    tags_genie = sorted(temp, key=lambda x: temp[x], reverse=True)
    return tags_genie


def popular_tags(index):
    genie_popular_url = "https://www.genie.co.kr/playlist/popular"
    genie_selector = "div.tag"

    melon_popular_url = "https://www.melon.com/dj/today/djtoday_list.htm"
    melon_selector = "div.tag_list.type02"

    user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        "AppleWebKit/537.36 (KHTML, like Gecko)"
        "Chrome/86.0.4240.75 Safari/537.36"
    )
    headers = {"User-Agent": user_agent}

    if index == 0:
        url = melon_popular_url
        selector = melon_selector
    else:
        url = genie_popular_url
        selector = genie_selector

    req = requests.get(url, headers=headers)
    response = req.status_code
    if response != 200:
        raise Exception(f"Status code: {response}")
    else:
        html = BeautifulSoup(req.text, "lxml")
        data = html.select(selector)

        tags = []
        for line in data:
            line = line.text.split("\n")
            for tag in line:
                if tag:
                    tags.append(tag)
    return tags


# Searching tags

def tagsearch(tag, index):

    query_melon = "https://www.melon.com/search/dj/index.htm?q="
    end_melon = "&section=&searchGnbYn=Y&kkoSpl=N&kkoDpType="
    selector_melon = "#pageList > div > ul > li:nth-child(1) > div.dj_collection_info > div > dl > dt > a"

    query_genie = "https://www.genie.co.kr/search/searchPlaylist?query="
    end_genie = "&Coll="
    selector_genie = "div.music-list-wrap > table > tbody"

    query_flo = "https://www.music-flo.com/search/theme?keyword="
    end_flo = "&sortType=ACCURACY"
    selector_flo = "#main > div > div.section_content_wrap > ul > li:nth-child(1) > div > div > a"

    query = {
        0: [query_melon, end_melon, selector_melon],
        1: [query_genie, end_genie, selector_genie],
        2: [query_flo, end_flo, selector_flo],
    }

    if index in (0, 1):
        url = query[index][0] + str(tag) + query[index][1]

        selector = query[index][2]
        driver = webdriver.Chrome(r"C:\projects\tagbase\chromedriver.exe", options=chrome_options)
        driver.get(url)
        # driver.maximize_window()
        wait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector))).send_keys(Keys.ENTER)
        #driver.find_element(By.CSS_SELECTOR, selector).send_keys(Keys.ENTER)
        list_url = driver.current_url
        return list_url

    elif index in (2,):
        url = query[index][0] + str(tag) + query[index][1]

        selector = query[index][2]
        driver = webdriver.Chrome(r"C:\projects\tagbase\chromedriver.exe", options=chrome_options)
        driver.get(url)
        driver.maximize_window()
        driver.find_element(By.CSS_SELECTOR, selector).send_keys(Keys.ENTER)
        ActionChains(driver).move_to_element(WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))).click().perform()
        list_url = driver.current_url
        return list_url

    else:
        raise ValueError("0, 1, 2 가운데 하나를 입력")


def notation(text):
    text = text.replace("TITLE", "").strip()
    text = text.replace(" (", "(").replace("(", " (")
    text = text.replace(" (Explicit Ver.)", "") # Explicit 버전도 원곡 동일 취급
    text = text.replace("Feat. ", "Feat.").replace("Feat.", "Feat. ")
    text = text.replace(" & ", ", ")
    text = text.replace("Prod. ", "Prod.").replace("Prod.", "Prod. ")
    text = text.replace("Prod. by", "Prod.")
    text = text.replace("(with", "(With")
    return text


def extract(index, tag=None):
    # Requests 헤더
    user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        "AppleWebKit/537.36 (KHTML, like Gecko)"
        "Chrome/86.0.4240.75 Safari/537.36"
    )
    headers = {"User-Agent": user_agent}


    topchart = [
        "https://www.melon.com/chart/index.htm",
        "https://www.genie.co.kr/chart/top200",
        "https://www.music-flo.com/browse?chartId=1"
    ]
    if tag == None:
        list_url = topchart[index]
    else:
        list_url = tagsearch(tag, index)

    selector_melon = "#frm > div > table > tbody"
    classes_melon = ["ellipsis rank01", "checkEllipsis", "ellipsis rank03"]

    selector_genie = "div.music-list-wrap > table > tbody"
    classes_genie = ["title ellipsis", "artist ellipsis", "albumtitle ellipsis"]


    selector_flo = "div.chart_lst > table > tbody"
    classes_flo = ["tit__text", "artist", "album"]

    selector_all = [selector_melon, selector_genie, selector_flo]
    classes_all = [classes_melon, classes_genie, classes_flo]

    selector = selector_all[index]
    classes = classes_all[index]

    ## 정상적인 리스폰스가 있으면 스크레이핑
    r = requests.get(list_url, headers=headers)
    if r.status_code != 200:
        raise Exception(f"Status code: {r.status_code}")
    else:
        info = []
        if index != 2:
            data = BeautifulSoup(r.text, "lxml").select(selector)

            for item in data:
                for class_ in classes:
                    temp = []
                    for idx, line in enumerate(item.find_all(class_=class_)):
                        if idx > 49:
                            break
                        text = line.text.strip()
                        text = notation(text)
                        temp.append(text)
                    info.append(temp)
        else:
            try:
                driver = webdriver.Chrome(r"C:\projects\tagbase\chromedriver.exe", options=chrome_options)
                driver.get(list_url)
            except TimeoutException:
                print("페이지가 응답하지 않습니다.")

            if tag == None:
                driver.find_element(By.CSS_SELECTOR, "#browseRank > div.chart_lst > div > button").send_keys(Keys.ENTER)
            data = driver.find_elements(By.CSS_SELECTOR, selector)
            for item in data:
                for class_ in classes:
                    temp = []
                    for idx, line in enumerate(item.find_elements(By.CLASS_NAME, class_)):
                        if idx > 49:
                            break
                        text = line.text.strip()
                        text = notation(text)
                        temp.append(text)
                    info.append(temp)

        if len(info) != 0:
            chart = dict({})
            pts = 50
            for idx, title in enumerate(info[0]):
                chart[title.lower()] = [
                    info[0][idx],
                    info[1][idx],
                    info[2][idx],
                    pts - idx
                ]
            return chart
        else:
            print("무언가 잘못됐습니다.")


def integrate(*charts):
    weight = {0: 878 / 1683, 1: 506 / 1683, 2: 299 / 1683}
    point = 50
    data = dict({})
    for order, chart in enumerate(charts):
        for id in chart:
            if id not in data:
                data[id] = [
                    chart[id][0],
                    chart[id][1],
                    chart[id][2],
                    chart[id][3] * weight[order]
                ]
            else:
                data[id][3] += chart[id][3] * weight[order]
    return data


def randomize(chart):
    length = len(chart)
    pouch = list(np.arange(1, length+1, 1, dtype=int))
    shuffle(pouch)
    for idx, item in enumerate(chart):
        chart[item][3] = pouch[idx]
    return chart
