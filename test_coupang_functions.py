from unittest import TestCase

import requests

import coupang_functions as cf

class Test(TestCase):
    def test_get_items(self):
        session = cf.get_profile(reset=False)
        ses = requests.Session()

        cf.get_items("사과", ses)

    def test_get_profile(self):
        session = cf.get_profile()


    def test_get_content(self):
        cf.get_content_3()

    def test_remote_playwright(self):
        keyword = "오메가3"
        print(keyword)
        url = "https://www.coupang.com"
        url = "https://www.coupang.com/vp/products/8966340401?itemId=28978637914&vendorItemId=75001624321&src=1042503&spec=10304025&addtag=400&ctag=8966340401&lptag=8966340401-26240258859&itime=20260831151200&pageType=PRODUCT&pageValue=8966340401&wPcid=17881382857878025270761&wRef=www.google.com&wTime=20260831151200&redirect=landing&gclid=CjwKCAjwqc_UBhBKEiwAWbl25kwBBTZahdpB65Ojt0Ak2su_sDB_lfr9XwJOzbpYD9UjQ4kIRtcyNxoC6V4QAvD_BwE&mcid=1ad4f51ec6a743108af0e47952c06252&campaignid=23544742791&adgroupid="
        url = f"https://www.coupang.com/np/search?component=&q={keyword}"
        browser_client = BrowserClient(CDP_URL)

        browser_client.connect()
        page = browser_client.get_page()
        page.goto(url)
        page.wait_for_timeout(500)
        print(page.title())

    def test_remote_driver(self):
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        options = Options()
        driver = webdriver.Remote(
            command_executor="http://127.0.0.1:4444",
            options=options,
        )
        keyword = "오메가3"
        print(keyword)
        url = "https://www.coupang.com/vp/products/8966340401?itemId=28978637914&vendorItemId=75001624321&src=1042503&spec=10304025&addtag=400&ctag=8966340401&lptag=8966340401-26240258859&itime=20260831151200&pageType=PRODUCT&pageValue=8966340401&wPcid=17881382857878025270761&wRef=www.google.com&wTime=20260831151200&redirect=landing&gclid=CjwKCAjwqc_UBhBKEiwAWbl25kwBBTZahdpB65Ojt0Ak2su_sDB_lfr9XwJOzbpYD9UjQ4kIRtcyNxoC6V4QAvD_BwE&mcid=1ad4f51ec6a743108af0e47952c06252&campaignid=23544742791&adgroupid="
        url = f"https://www.coupang.com/np/search?component=&q={keyword}"
        url = "https://www.coupang.com"
        driver.get(url)

        print(driver.page_source)

        driver.quit()