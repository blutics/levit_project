from seleniumbase import sb_cdp

import coupang_functions as cf

print("!!!!")
sb = sb_cdp.Chrome(
    host="127.0.0.1",
    port=9223,
)

try:
    print(sb.get_current_url())

    sb.goto("https://example.com")

    print(sb.get_title())

finally:
    sb.quit()