import os
import random
import signal
import subprocess
import time
import urllib.request
from pathlib import Path

import bs4
from playwright.sync_api import sync_playwright

import coupang_functions as cf


PROFILE_DIR = Path("/tmp/chrome-cdp-test")
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


print("START", flush=True)

cleanup_existing_chromium()

chrome_env = os.environ.copy()
chrome_env["DISPLAY"] = ":99"

chrome = subprocess.Popen(
    [
        "/usr/bin/chromium",
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

        for kd in keywords[::][2:3]:

            print(f"KEYWORD : {kd}", flush=True)

            page.goto("https://www.coupang.com")
            page.wait_for_timeout(5000)

            search_input = page.query_selector("input.headerSearchKeyword")
            for k in kd:
                print(f"TYPE : {k}", flush=True)
                search_input.type(k)
                t = random.uniform(0.2, 0.6)
                time.sleep(t)
            # page.keyboard.press("Enter")

            btn = page.query_selector("form#wa-search-form-tablet button.headerSearchBtn")
            btn.click()
            for i in range(10):
                print(f"대기중... ({i})", flush=True)
                page.wait_for_timeout(1000)

            html = page.content()
            sp = bs4.BeautifulSoup(html, "html.parser")
            print(sp.prettify(), flush=True)

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