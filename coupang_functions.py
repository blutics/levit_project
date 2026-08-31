import time
from pprint import pprint

from bs4 import BeautifulSoup
from fake_useragent import UserAgent

import requests
from selenium import webdriver

ses = requests.Session()
ua = UserAgent()
uae = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "ko-KR,ko;q=0.9,zh-MO;q=0.8,zh;q=0.7,en-US;q=0.6,en;q=0.5",
    "Priority": "u=0, i",
    "Sec-Ch-Ua": '"Not=A?Brand";v="99", "Google Chrome";v="151", "Chromium";v="151"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": uae,
}
ses.headers.update(headers)

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import undetected_chromedriver as uc

def create_browser():
    options = Options()
    options.add_argument("--start-maximized")

    driver = uc.Chrome()
    # driver = webdriver.Chrome(options=options)
    return driver


def get_profile():
    print("get profile")
    driver = create_browser()
    session = requests.Session()

    # User-Agent 맞추기
    user_agent = driver.execute_script(
        "return navigator.userAgent"
    )

    session.headers.update({
        "User-Agent": user_agent,
    })

    driver.get("https://www.coupang.com/")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    # Selenium 쿠키 -> requests.Session
    for cookie in driver.get_cookies():
        print(cookie)
        session.cookies.set(
            name=cookie["name"],
            value=cookie["value"],
            domain=cookie.get("domain"),
            path=cookie.get("path", "/"),
        )

    return session


def get_items(keyword, session):
    url = f"https://www.coupang.com/np/search?component=&q={keyword}&traceId=mtgmfdu5&channel=user&page=1"

    items = []

    pprint(session.cookies)

    # ses.get("https://www.coupang.com")
    hdr = headers.copy()
    # hdr["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
    res = session.get(
        url,
        headers=hdr,
    )
    soup = BeautifulSoup(res.text, "html.parser")
    print(soup.prettify())
