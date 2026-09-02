import time
from idlelib.pyshell import use_subprocess
from pprint import pprint
import random

import bs4
import httpx
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import undetected_chromedriver as uc

from commons import SiteName
from session import SessionManager

ua = UserAgent()
uae = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"
mua = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "Version/18.6 Mobile/15E148 Safari/604.1"
)
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
    "User-Agent": mua,
}




def create_browser():
    options = uc.ChromeOptions()

    driver = uc.Chrome(
        options=options,
        # version_main=152,
    )

    # driver = webdriver.Chrome(options=options)
    return driver


def get_profile(reset=False):
    print("get profile")

    manager = SessionManager(
        site_name=SiteName.COUPANG,
        ttl_minutes=30,
    )

    if not reset and not manager.is_session_expired():
        return manager.get_session()

    driver = create_browser()
    session = requests.Session()

    # User-Agent 맞추기
    user_agent = driver.execute_script(
        "return navigator.userAgent"
    )

    session.headers.update({
        "User-Agent": user_agent,
    })

    driver.get("https://www.coupang.com")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    # Selenium 쿠키 -> requests.Session
    for cookie in driver.get_cookies():
        session.cookies.set(
            name=cookie["name"],
            value=cookie["value"],
            domain=cookie.get("domain"),
            path=cookie.get("path", "/"),
        )

    driver.quit()
    manager.save_session(session)
    return session


def get_items(keyword, session: requests.Session):
    for cookie in session.cookies:
        print(cookie)
    url = f"https://www.coupang.com/np/search?component=&q={keyword}&traceId=mtgmfdu5&channel=user&page=1"
    url = "https://www.coupang.com/vp/products/8966340401?itemId=28978637914&vendorItemId=75001624321&src=1042503&spec=10304025&addtag=400&ctag=8966340401&lptag=8966340401-26240258859&itime=20260831151200&pageType=PRODUCT&pageValue=8966340401&wPcid=17881382857878025270761&wRef=www.google.com&wTime=20260831151200&redirect=landing&gclid=CjwKCAjwqc_UBhBKEiwAWbl25kwBBTZahdpB65Ojt0Ak2su_sDB_lfr9XwJOzbpYD9UjQ4kIRtcyNxoC6V4QAvD_BwE&mcid=1ad4f51ec6a743108af0e47952c06252&campaignid=23544742791&adgroupid="
    items = []

    pprint(session.cookies)

    # ses.get("https://www.coupang.com")
    hdr = headers.copy()
    # hdr["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
    # res = httpx.get(
    #     url,
    #     headers=hdr,
    #
    # )
    with httpx.Client(
            http2=True,
    ) as client:
        res = client.get(
            url, headers=hdr,
        )

        print(res.http_version)
        soup = BeautifulSoup(res.text, "html.parser")
        print(soup.prettify())

def get_content():
    from playwright.sync_api import sync_playwright
    from seleniumbase import sb_cdp

    # sb = sb_cdp.Chrome(guest=True)
    sb = sb_cdp.Chrome(use_chromium=True, guest=True)
    endpoint_url = sb.get_endpoint_url()

    keyword = "오메가3"
    print(keyword)
    url = f"https://www.coupang.com/np/search?component=&q={keyword}"
    url = "https://www.coupang.com/vp/products/8966340401?itemId=28978637914&vendorItemId=75001624321&src=1042503&spec=10304025&addtag=400&ctag=8966340401&lptag=8966340401-26240258859&itime=20260831151200&pageType=PRODUCT&pageValue=8966340401&wPcid=17881382857878025270761&wRef=www.google.com&wTime=20260831151200&redirect=landing&gclid=CjwKCAjwqc_UBhBKEiwAWbl25kwBBTZahdpB65Ojt0Ak2su_sDB_lfr9XwJOzbpYD9UjQ4kIRtcyNxoC6V4QAvD_BwE&mcid=1ad4f51ec6a743108af0e47952c06252&campaignid=23544742791&adgroupid="
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(endpoint_url)
        print(endpoint_url)
        page = browser.contexts[0].pages[0]

        page.goto("https://coupang.com")
        page.wait_for_timeout(500)

        text = "오메가3"
        search_input = page.query_selector("input.headerSearchKeyword")
        for t in text:
            # search_input.fill(t)
            search_input.type(t)
            bt = random.randrange(0, 1)
            time.sleep(bt)

        button = page.query_selector("button.headerSearchBtn ")
        button.click()

        page.wait_for_timeout(500)

        time.sleep(220)

def get_content_2():
    from playwright.sync_api import sync_playwright
    from seleniumbase import sb_cdp

    sb = sb_cdp.Chrome(use_subprocess=True)
    # sb = sb_cdp.Chrome(use_chromium=True)
    endpoint_url = sb.get_endpoint_url()

    keyword = "오메가3"
    print(keyword)
    url = "https://www.coupang.com/vp/products/8966340401?itemId=28978637914&vendorItemId=75001624321&src=1042503&spec=10304025&addtag=400&ctag=8966340401&lptag=8966340401-26240258859&itime=20260831151200&pageType=PRODUCT&pageValue=8966340401&wPcid=17881382857878025270761&wRef=www.google.com&wTime=20260831151200&redirect=landing&gclid=CjwKCAjwqc_UBhBKEiwAWbl25kwBBTZahdpB65Ojt0Ak2su_sDB_lfr9XwJOzbpYD9UjQ4kIRtcyNxoC6V4QAvD_BwE&mcid=1ad4f51ec6a743108af0e47952c06252&campaignid=23544742791&adgroupid="
    url = f"https://www.coupang.com/np/search?component=&q={keyword}"
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(endpoint_url)
        print(endpoint_url)
        page = browser.contexts[0].pages[0]

        page.goto(url)
        page.wait_for_timeout(500)

        time.sleep(220)

def get_content_3():
    from scrapling.fetchers import Fetcher, AsyncFetcher, StealthyFetcher, DynamicFetcher
    StealthyFetcher.adaptive = True
    keyword = "오메가3"
    print(keyword)
    url = f"https://www.coupang.com/np/search?component=&q={keyword}"
    url = "https://www.coupang.com/vp/products/8966340401?itemId=28978637914&vendorItemId=75001624321&src=1042503&spec=10304025&addtag=400&ctag=8966340401&lptag=8966340401-26240258859&itime=20260831151200&pageType=PRODUCT&pageValue=8966340401&wPcid=17881382857878025270761&wRef=www.google.com&wTime=20260831151200&redirect=landing&gclid=CjwKCAjwqc_UBhBKEiwAWbl25kwBBTZahdpB65Ojt0Ak2su_sDB_lfr9XwJOzbpYD9UjQ4kIRtcyNxoC6V4QAvD_BwE&mcid=1ad4f51ec6a743108af0e47952c06252&campaignid=23544742791&adgroupid="
    url = "https://www.coupang.com"
    p = StealthyFetcher.fetch(url, headless=False, network_idle=True)  # Fetch website under the radar!

    time.sleep(220)

def get_content_4():
    import asyncio
    import nodriver as uc
    keyword = "오메가3"
    print(keyword)
    url = "https://www.coupang.com/vp/products/8966340401?itemId=28978637914&vendorItemId=75001624321&src=1042503&spec=10304025&addtag=400&ctag=8966340401&lptag=8966340401-26240258859&itime=20260831151200&pageType=PRODUCT&pageValue=8966340401&wPcid=17881382857878025270761&wRef=www.google.com&wTime=20260831151200&redirect=landing&gclid=CjwKCAjwqc_UBhBKEiwAWbl25kwBBTZahdpB65Ojt0Ak2su_sDB_lfr9XwJOzbpYD9UjQ4kIRtcyNxoC6V4QAvD_BwE&mcid=1ad4f51ec6a743108af0e47952c06252&campaignid=23544742791&adgroupid="
    url = f"https://www.coupang.com/np/search?component=&q={keyword}"
    async def main():
        browser = await uc.start()

        page = await browser.get(url)

        print(await page.get_content())
        time.sleep(1200)
        await browser.stop()

    asyncio.run(main())


def parse_search(html):
    soup = BeautifulSoup(html, "html.parser")

    item_selector = "ul#product-list > li"
    items = soup.select(item_selector)
    result = []
    for item in items:
        title_tag = item.select_one("div[class*='productName']")
        title = title_tag.text
        a_tag = item.select_one("a")
        path = a_tag.get("href")
        i = {
            'title': title,
            'url': f"https://www.coupang.com{path}",
        }
        result.append(i)
    return result