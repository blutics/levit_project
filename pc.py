import io

import pycurl

mua = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "Version/18.6 Mobile/15E148 Safari/604.1"
)

headers = {
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,image/apng,*/*;q=0.8,"
        "application/signed-exchange;v=b3;q=0.7"
    ),
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": (
        "ko-KR,ko;q=0.9,zh-MO;q=0.8,zh;q=0.7,"
        "en-US;q=0.6,en;q=0.5"
    ),
    "Priority": "u=0, i",
    "Sec-Ch-Ua": (
        '"Not=A?Brand";v="99", '
        '"Google Chrome";v="151", '
        '"Chromium";v="151"'
    ),
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": mua,
}


def get_html(url: str) -> str:
    buffer = io.BytesIO()

    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.WRITEDATA, buffer)
    curl.setopt(pycurl.FOLLOWLOCATION, True)
    curl.setopt(pycurl.TIMEOUT, 10)

    curl.setopt(
        pycurl.HTTPHEADER,
        [
            f"{key}: {value}"
            for key, value in headers.items()
            if key.lower() != "accept-encoding"
        ],
    )

    curl.setopt(
        pycurl.ACCEPT_ENCODING,
        ""
    )

    try:
        curl.perform()

        status_code = curl.getinfo(pycurl.RESPONSE_CODE)

        print("status:", status_code)

    finally:
        curl.close()

    return buffer.getvalue().decode(
        "utf-8",
        errors="replace",
    )

keyword = "통닭"
# url = "https://www.coupang.com/vp/products/8966340401?itemId=28978637914&vendorItemId=75001624321&src=1042503&spec=10304025&addtag=400&ctag=8966340401&lptag=8966340401-26240258859&itime=20260831151200&pageType=PRODUCT&pageValue=8966340401&wPcid=17881382857878025270761&wRef=www.google.com&wTime=20260831151200&redirect=landing&gclid=CjwKCAjwqc_UBhBKEiwAWbl25kwBBTZahdpB65Ojt0Ak2su_sDB_lfr9XwJOzbpYD9UjQ4kIRtcyNxoC6V4QAvD_BwE&mcid=1ad4f51ec6a743108af0e47952c06252&campaignid=23544742791&adgroupid="
url = f"https://www.coupang.com/np/search?component=&q={keyword}&traceId=mtgmfdu5&channel=user&page=1"
url = "https://www.coupang.com/np/search?component=&q=%EC%88%98%EB%B0%95&traceId=mtgzeljx&channel=user"
html = get_html(url)

print(html[:1000])