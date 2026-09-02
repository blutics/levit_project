import os

print("DISPLAY =", os.environ.get("DISPLAY"), flush=True)

print("================================", flush=True)
print("sb_example.py STARTED", flush=True)
print("================================", flush=True)

import asyncio
import random
import time
from pathlib import Path

import bs4
from playwright.sync_api import sync_playwright
from seleniumbase import sb_cdp

import coupang_functions as cf
from commons import SiteName
from session import SessionManager

from curl_cffi import requests as curl_requests

print("SB_EXAMPLE starts")
PROFILE_DIR = Path("./chrome_profile").resolve()

print(PROFILE_DIR)
sb = sb_cdp.Chrome(
    user_data_dir=str(PROFILE_DIR),
    # guest=True,  # 제거 권장
)

endpoint_url = sb.get_endpoint_url()

keywords = [
    "사과", "크리넥스", "닭가슴살", "폴로남방", "물티슈", "드라이기", "오메가3",
]
keyword = "오메가3"
url = "https://www.coupang.com/vp/products/8966340401?itemId=28978637914&vendorItemId=75001624321&src=1042503&spec=10304025&addtag=400&ctag=8966340401&lptag=8966340401-26240258859&itime=20260831151200&pageType=PRODUCT&pageValue=8966340401&wPcid=17881382857878025270761&wRef=www.google.com&wTime=20260831151200&redirect=landing&gclid=CjwKCAjwqc_UBhBKEiwAWbl25kwBBTZahdpB65Ojt0Ak2su_sDB_lfr9XwJOzbpYD9UjQ4kIRtcyNxoC6V4QAvD_BwE&mcid=1ad4f51ec6a743108af0e47952c06252&campaignid=23544742791&adgroupid="
url = f"https://www.coupang.com/np/search?component=&q={keyword}&traceId=mtgmfdu5&channel=user&page=1"
f_search_url = "https://www.coupang.com/np/search?component=&q={}&traceId=mtgmfdu5&channel=user&page=1"

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(endpoint_url)

    context = browser.contexts[0]

    if context.pages:
        page = context.pages[0]
    else:
        page = context.new_page()

    # time.sleep(555)
    for kd in keywords[::][:]:
        # page.goto(f_search_url.format(kd))

        page.goto("https://www.coupang.com")
        page.wait_for_timeout(5000)

        search_input = page.query_selector("input.headerSearchKeyword")
        for k in kd:
            search_input.type(k)
            t = random.uniform(0.2, 0.6)
            time.sleep(t)
        # page.keyboard.press("Enter")
        btn = page.query_selector("form button.headerSearchBtn")
        btn.click()

        page.wait_for_timeout(5000)

        html = page.content()
        items = cf.parse_search(html)

        # time.sleep(1111)
        for n, item in enumerate(items, 1):
            print(f"[{n:2}/{len(items):2}] : {item}")
            target_url = item['url']
            page.goto(target_url)
            page.wait_for_timeout(3000)

            soup = bs4.BeautifulSoup(page.content(), "html.parser")
            title_tag = soup.select_one("title")
            print("-->", title_tag.text)

        page.wait_for_timeout(5000)
        time.sleep(3)


    cookies = context.cookies()
    manager = SessionManager(SiteName.COUPANG)
    manager.get_session()
    manager.save_session(cookies)

    session = curl_requests.Session(
        impersonate="chrome"
    )
    manager.apply_to_cffi_session(session)


    # for i, it in enumerate(items[:]):
    #     result = session.get(it['url'])
    #     soup = bs4.BeautifulSoup(result.text, "html.parser")
    #     title_tag = soup.select_one("title")
    #     print(i, title_tag.text)
    #     time.sleep(2)

    browser.close() # 는 상황에 따라 주의


