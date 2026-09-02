import os
import platform
import sys
from enum import Enum

USER_AGENT = ""

class SiteName(str, Enum):
    COUPANG = "coupang"
    NAVER = "naver"
    G_MARKET = "gmarket"
    ELEVEN_ST = "11st"


def print_platform():
    print("=== SYSTEM INFO ===")
    from pathlib import Path
    os_release = Path("/etc/os-release")

    if os_release.exists():
        info = {}

        for line in os_release.read_text().splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                info[key] = value.strip('"')

        print("DISTRO:", info.get("NAME"))
        print("VERSION:", info.get("VERSION"))
        print("ID:", info.get("ID"))
        print("VERSION_ID:", info.get("VERSION_ID"))
        print()

    print("OS:", platform.system())
    print("OS Release:", platform.release())
    print("OS Version:", platform.version())
    print("Platform:", platform.platform())
    print("Machine:", platform.machine())
    print("Processor:", platform.processor())
    print("Python:", sys.version)
    print("Python Executable:", sys.executable)
    print("Hostname:", platform.node())
    print("DISPLAY:", os.environ.get("DISPLAY"))
    print("===================")