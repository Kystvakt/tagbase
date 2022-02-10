import sys

sys.path.insert(0, "/usr/lib/chromium-browser/chromedriver")

from selenium import webdriver
from selenium.webdriver.common.by import By

# chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")

import requests as req
from bs4 import BeautifulSoup

def Scraper():
    """멜론, 지니, 플로의 최신 음원 순위 페이지를 스크레이핑한 후
    데이터를 항목으로 갖는 리스트를 반환합니다.

    멜론과 지니는 BeautifulSoup를 사용하며, JavaScript를 쓰는 플로는
    Selenium Webdriver를 사용하여 스크레이핑을 진행합니다.

    Returns:
        charts (list): 각 사이트 스크레이핑 데이터 3개로 구성된 리스트
    """
    # 음원 사이트 순위 페이지 주소
    url1 = "https://www.melon.com/chart/index.htm"  # 멜론
    url2 = "https://www.genie.co.kr/chart/top200"  # 지니
    url3 = "https://www.music-flo.com/browse?chartId=1"  # 플로
    # Requests 헤더
    user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        "AppleWebKit/537.36 (KHTML, like Gecko)"
        "Chrome/86.0.4240.75 Safari/537.36"
    )
    headers = {"User-Agent": user_agent}

    # 멜론
    ## 정상적인 리스폰스가 있으면 스크레이핑
    req1 = req.get(url1, headers=headers)
    if req1.status_code == 200:
        chart1 = BeautifulSoup(req1.text, "lxml").select("tr#lst50")
    else:
        print("Melon Status:", req1.status_code)
    # 지니
    ## 정상적인 리스폰스가 있으면 스크레이핑
    req2 = req.get(url2, headers=headers)
    if req2.status_code == 200:
        chart2 = BeautifulSoup(req2.text, "lxml").select(
            "#body-content > div.newest-list > div > table > tbody > tr"
        )
    else:
        print("Genie Status:", req2.status_code)
    # 플로
    ## Selenium에는 HTTP response status code를 받는 기능이 없음
    driver = webdriver.Chrome("chromedriver", options=chrome_options)
    driver.get(url3)
    ## 처음에는 10위까지만 보여주기 때문에 '더보기' 버튼을 눌러서 100위까지 확장
    from selenium.webdriver.common.keys import Keys

    driver.find_element(
        By.CSS_SELECTOR, "#browseRank > div.chart_lst > div > button"
    ).send_keys(Keys.ENTER)
    chart3 = driver.find_elements(
        By.CSS_SELECTOR, "#browseRank > div.chart_lst > table > tbody > tr"
    )
    charts = [chart1, chart2, chart3]
    return charts


def NotationArranger(text):
    """각 음원 사이트별 표기법을 통일시키는 함수입니다.
    받아들인 스트링에서 괄호 앞과 줄임말 뒤에 공백을 넣고
    특정 용어는 대문자화합니다.

    Parameters:
        text (str): 음원 제목, 가수, 또는 앨범 제목 스트링

    Returns:
        text (str): 표기법을 통일한 스트링
    """
    text = text.replace(" (", "(").replace("(", " (")
    text = text.replace(" (Explicit Ver.)", "") # Explicit 버전도 원곡 동일 취급
    text = text.replace("Feat. ", "Feat.").replace("Feat.", "Feat. ")
    text = text.replace(" & ", ", ")
    text = text.replace("Prod. ", "Prod.").replace("Prod.", "Prod. ")
    text = text.replace("Prod. by", "Prod.")
    text = text.replace("(with", "(With")
    return text


def RankExtractor(charts):
    """음원 순위 HTML 데이터에서 제목, 아티스트, 앨범명을 추출하는 함수입니다.

    Parameters:
        charts (list): 사이트별 데이터 3개를 항목으로 갖는 리스트

    Returns:
        rank_all (list): 사이트별 TOP50 리스트 3개를 항목으로 갖는 리스트
    """
    # 검색용 태그
    tags_melon = [
        ["div", "span", "div"],
        ["ellipsis rank01", "checkEllipsis", "ellipsis rank03"],
    ]
    tags_genie = [
        ["a", "a", "a"],
        ["title ellipsis", "artist ellipsis", "albumtitle ellipsis"],
    ]
    tags_flo = ["tit__text", "artist_link_w", "album"]
    tags = [tags_melon, tags_genie, tags_flo]

    rank_all = []  # 3개 사이트의 음원 순위를 각각 담는 리스트
    for order, chart in enumerate(charts):
        rank = []  # 사이트별 랭크 순서대로 곡 정보를 담는 리스트
        if order != 2:  # 멜론, 지니
            for idx, item in enumerate(chart):
                info = []  # 제목, 아티스트, 앨범명을 담는 리스트
                for i in range(3):
                    text = item.find(tags[order][0][i], tags[order][1][i]).text
                    text = text.strip()
                    text = NotationArranger(text)
                    info.append(text)
                rank.append(info)
        else:  # 플로
            for idx, item in enumerate(chart):
                info = []
                # 플로는 기본 100개씩 보여주기 때문에
                # 멜론, 지니와 맞춰서 50개까지 자르기
                if idx < 50:
                    for i in range(3):
                        text = item.find_element(
                            By.CLASS_NAME, tags[order][i]
                        ).text.strip()
                        text = NotationArranger(text)
                        info.append(text)
                    rank.append(info)
                else:
                    break
        rank_all.append(rank)
    return rank_all


def RankIntegrator(charts):
    """각 사이트별로 정리된 음원 순위 차트를 통합하는 함수입니다.

    순위를 기반으로 점수를 부여한 뒤, 사이트 이용자 수를 기반으로 한
    가중치를 곱하여 최종 점수를 산출합니다.

    Parameters:
        charts (list): 사이트별 TOP50 리트스 3개를 항목으로 갖는 리스트

    Returns:
        data (dict): 소문자화한 제목을 키로,
                     [제목, 가수, 앨범, 점수] 리스트를 밸류로 갖는 딕셔너리
    """
    # 각 음원 사이트별 가중치
    # 사용자 수를 기준으로 함
    # 순서대로 멜론, 지니, 플로
    weight = {0: 878 / 1683, 1: 506 / 1683, 2: 299 / 1683}
    maxpoint = 50  # 1위는 50점, 2위는 49점, ... , 50위는 1점

    # 통합 차트 딕셔너리
    ## 키: 노래 제목 (소문자)
    ## 밸류: [제목, 아티스트, 앨범, 점수]
    data = dict({})
    for order, chart in enumerate(charts):
        # 멜론, 지니는 기본으로 50개씩 가져오지만
        # 플로는 기본 100개씩 가져오기 때문에 50개 초과는 자름
        for idx, info in enumerate(chart):
            # data 딕셔너리 안에 노래 정보가 이미 있으면
            if info[0].lower() in data:
                data[info[0].lower()][3] += (maxpoint - idx) * weight[order]
                # 일관성을 위해 아티스트 이름이나 앨범 제목은
                # 더 긴 쪽을 기준으로 업데이트함
                if len(data[info[0].lower()][1]) < len(info[1]):
                    data[info[0].lower()][1] = info[1]
                if len(data[info[0].lower()][2]) < len(info[2]):
                    data[info[0].lower()][2] = info[2]
            else:  # 처음 나오는 노래 제목이면
                data[info[0].lower()] = [
                    info[0],
                    info[1],
                    info[2],
                    (maxpoint - idx) * weight[order],
                ]
    return data


def DataFrameMaker(data):
    """완전히 정리된 데이터를 받아 Pandas DataFrame으로 만드는 함수입니다.
    점수를 기준으로 내림차순으로 정리합니다.

    Parameters:
        data (dict): 소문자화한 제목을 키로,
                     [제목, 가수, 앨범, 점수] 리스트를 밸류로 갖는 딕셔너리
    Returns:
        df (pandas.DataFrame): 점수를 기준으로 내림차순으로 정리된 DataFrame
    """
    import pandas as pd

    IDs = sorted(data, key=lambda x: data[x][3], reverse=True)
    titles = [data[id][0] for id in IDs]
    artists = [data[id][1] for id in IDs]
    albums = [data[id][2] for id in IDs]
    # points = [data[id][3] for id in IDs]

    df = pd.DataFrame({"제목": titles, "가수": artists, "앨범": albums})
    df.rename_axis("순위", inplace=True)
    df.index += 1
    return df
