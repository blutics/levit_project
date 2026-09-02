import os
import random
import signal
import subprocess
import time
import urllib.request
from pathlib import Path
from pprint import pprint

import bs4
from playwright.sync_api import sync_playwright

import coupang_functions as cf
from commons import print_platform

PROFILE_DIR = Path("/data/chrome_profile")
CDP_PORT = 9222


def cleanup_existing_chromium():
    pattern = f"chromium.*--user-data-dir={PROFILE_DIR}"

    subprocess.run(
        ["pkill", "-f", pattern],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    time.sleep(1)

    for name in (
        "SingletonLock",
        "SingletonSocket",
        "SingletonCookie",
    ):
        path = PROFILE_DIR / name

        try:
            if path.exists() or path.is_symlink():
                path.unlink()
        except Exception as e:
            print(f"LOCK REMOVE ERROR: {e}", flush=True)


def wait_for_cdp(chrome, timeout=20):
    url = f"http://127.0.0.1:{CDP_PORT}/json/version"

    started = time.monotonic()

    while time.monotonic() - started < timeout:

        # Chromium이 이미 죽었는지 먼저 확인
        if chrome.poll() is not None:
            print(
                f"Chromium exited. code={chrome.returncode}",
                flush=True,
            )

            output = chrome.stdout.read()

            if output:
                print("===== CHROMIUM LOG =====", flush=True)
                print(output, flush=True)
                print("========================", flush=True)

            raise RuntimeError("Chromium exited before CDP became ready")

        try:
            with urllib.request.urlopen(
                url,
                timeout=1,
            ) as response:
                data = response.read().decode()

            print("CDP READY", flush=True)
            print(data, flush=True)

            return

        except Exception:
            print("Waiting for CDP...", flush=True)
            time.sleep(0.5)

    raise TimeoutError(
        f"CDP was not ready after {timeout} seconds"
    )

print_platform()

print("START", flush=True)

cleanup_existing_chromium()

chrome_env = os.environ.copy()
chrome_env["DISPLAY"] = ":99"

# CHROME_PATH = "/usr/bin/chromium"
# CHROME_PATH = "/usr/bin/google-chrome"

def find_chrome():
    candidates = [
        "chromium",
        "chromium-browser",
        "google-chrome",
        "google-chrome-stable",
    ]
    import shutil
    for name in candidates:
        path = shutil.which(name)

        if path:
            return path

    raise RuntimeError("Chrome/Chromium executable not found")


CHROME_PATH = find_chrome()

chrome = subprocess.Popen(
    [
        CHROME_PATH,
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--remote-debugging-address=127.0.0.1",
        f"--remote-debugging-port={CDP_PORT}",
        f"--user-data-dir={PROFILE_DIR}",
        "--no-first-run",
        "--no-default-browser-check",
        "about:blank",
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    start_new_session=True,
    env=chrome_env,  # ★ 중요
)

print("CHROME PID:", chrome.pid, flush=True)

# ★ 고정 sleep 대신 CDP 준비 확인
wait_for_cdp(chrome)

keywords = [
    "사과",
    "크리넥스",
    "닭가슴살",
    "폴로남방",
    "물티슈",
    "드라이기",
    "오메가3",
]

f_search_url = (
    "https://www.coupang.com/np/search"
    "?component=&q={}&traceId=mtgmfdu5&channel=user&page=1"
)

try:

    with sync_playwright() as p:

        print("Connecting Playwright...", flush=True)

        browser = p.chromium.connect_over_cdp(
            f"http://127.0.0.1:{CDP_PORT}"
        )

        print("PLAYWRIGHT CONNECTED", flush=True)

        context = browser.contexts[0]

        if context.pages:
            page = context.pages[0]
        else:
            page = context.new_page()

        numbers = len(keywords)
        target_number = random.randrange(0, numbers)
        start_index = target_number
        end_index = start_index + 1

        for kd in keywords[::][start_index:end_index]:
            print(f"KEYWORD[{target_number}] : {kd}", flush=True)

            page.goto("https://www.google.com", wait_until="domcontentloaded",
                timeout=5_000,)
            page.goto(f_search_url.format(kd), wait_until="domcontentloaded",
                timeout=5_000,)
            print(page.url)

            for i in range(1, 4):
                print(f"대기중... ({i})", flush=True)
                page.wait_for_timeout(1000)

            print(page.url)
            html = page.content()
            sp = bs4.BeautifulSoup(html, "html.parser")
            html_title = sp.select_one("title")
            print(f"TITLE[{html_title.text}]", flush=True)
            # print(sp.prettify(), flush=True)

            items = cf.parse_search(html)

            print(
                f"ITEMS : {len(items)}",
                flush=True,
            )

            for n, item in enumerate(items, 1):

                print(
                    f"[{n:2}/{len(items):2}] : {item}",
                    flush=True,
                )

                target_url = item["url"]

                page.goto(
                    target_url,
                    wait_until="domcontentloaded",
                    timeout=30_000,
                )

                page.wait_for_timeout(3000)

                soup = bs4.BeautifulSoup(
                    page.content(),
                    "html.parser",
                )

                title_tag = soup.select_one("title")
                error_tags = soup.select("h3.error-img")
                if error_tags:
                    et = error_tags[0]
                    error_text = et.text
                    print(f"ERROR : {error_text}", flush=True)

                # print(soup.prettify(), flush=True)

                print(
                    "-->",
                    title_tag.get_text(strip=True)
                    if title_tag
                    else "NO TITLE",
                    flush=True,
                )

finally:

    print("Stopping Chromium...", flush=True)
    if chrome.poll() is None:
        try:
            os.killpg(
                os.getpgid(chrome.pid),
                signal.SIGTERM,
            )
            chrome.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(
                os.getpgid(chrome.pid),
                signal.SIGKILL,
            )
        except ProcessLookupError:
            pass

    print("DONE", flush=True)