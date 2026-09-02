from enum import Enum

USER_AGENT = ""

class SiteName(str, Enum):
    COUPANG = "coupang"
    NAVER = "naver"
    G_MARKET = "gmarket"
    ELEVEN_ST = "11st"