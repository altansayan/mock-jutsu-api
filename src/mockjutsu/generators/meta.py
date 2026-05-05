"""
mock-jutsu — Meta Generator (Combinatorial User Agent + Security Data + Tech)
Developer: Altan Sayan (https://github.com/altansayan)
"""

import random
import uuid
import time
import hmac
import hashlib
import base64
import colorsys
import secrets
from datetime import datetime

BROWSERS = [
    {"name": "Chrome",  "engine": "Blink",   "major_range": (120, 126)},
    {"name": "Firefox", "engine": "Gecko",   "major_range": (120, 127)},
    {"name": "Safari",  "engine": "WebKit",  "major_range": (16, 18)},
    {"name": "Edge",    "engine": "Blink",   "major_range": (120, 126)},
    {"name": "Opera",   "engine": "Blink",   "major_range": (105, 110)},
]

# Real OUI prefixes (public IEEE registry — ieee.org/regauth)
OUI_PREFIXES = [
    "A4:C3:F0",  # Apple
    "3C:22:FB",  # Cisco Systems
    "B8:27:EB",  # Raspberry Pi Foundation
    "DC:2C:6E",  # MikroTik
    "00:50:56",  # VMware
    "08:00:27",  # Oracle VirtualBox
    "D8:BB:2C",  # Intel Corporate
    "28:6F:7F",  # Liteon Technology
    "F0:18:98",  # Apple
    "00:1C:42",  # Parallels
]

DOMAIN_TLDS = {
    "TR": [".com.tr", ".net.tr", ".org.tr", ".com"],
    "US": [".com", ".net", ".org", ".io", ".co"],
    "UK": [".co.uk", ".org.uk", ".me.uk", ".com"],
    "DE": [".de", ".com", ".net"],
    "FR": [".fr", ".com", ".net"],
    "RU": [".ru", ".com"],
}

URL_PATHS = [
    "/api/v1/users", "/api/v2/transactions", "/api/v1/accounts",
    "/products/list", "/orders/pending", "/invoices/2024",
    "/auth/login", "/auth/refresh", "/dashboard/overview",
    "/settings/profile", "/reports/monthly", "/webhook/events",
]

COLOR_NAMES = [
    ("Crimson",      "#DC143C", (220,  20,  60)),
    ("Dodger Blue",  "#1E90FF", ( 30, 144, 255)),
    ("Emerald",      "#50C878", ( 80, 200, 120)),
    ("Goldenrod",    "#DAA520", (218, 165,  32)),
    ("Orchid",       "#DA70D6", (218, 112, 214)),
    ("Tomato",       "#FF6347", (255,  99,  71)),
    ("Steel Blue",   "#4682B4", ( 70, 130, 180)),
    ("Coral",        "#FF7F50", (255, 127,  80)),
    ("Medium Purple","#9370DB", (147, 112, 219)),
    ("Sea Green",    "#2E8B57", ( 46, 139,  87)),
    ("Sienna",       "#A0522D", (160,  82,  45)),
    ("Slate Gray",   "#708090", (112, 128, 144)),
]


class MetaGenerator:
    """Security and system data with combinatorial logic."""

    def generate_ua(self):
        """Builds a User Agent from separate building blocks."""
        platforms = [
            "Windows NT 10.0", "Windows NT 11.0",
            "Macintosh; Intel Mac OS X 10_15_7",
            "X11; Linux x86_64",
            "iPhone; CPU iPhone OS 17_5 like Mac OS X",
        ]
        archs = ["Win64; x64", "WOW64", "ARM64", "x86_64"]
        chrome_v = f"{random.randint(120, 126)}.0.{random.randint(1000, 9999)}.{random.randint(10, 99)}"
        safari_v = f"{random.randint(530, 600)}.{random.randint(1, 40)}"

        plat = random.choice(platforms)
        arch = random.choice(archs) if ("Windows" in plat or "Linux" in plat) else ""

        ua = f"Mozilla/5.0 ({plat}{'; ' + arch if arch else ''}) "
        ua += f"AppleWebKit/{safari_v} (KHTML, like Gecko) "
        ua += f"Chrome/{chrome_v} Safari/{safari_v}"
        return ua

    def generate_app_password(self):
        """6-digit PIN with no consecutive repeats and no sequential runs of 3+."""
        while True:
            digits = [random.randint(0, 9) for _ in range(6)]
            has_repeat = any(digits[i] == digits[i + 1] for i in range(5))
            has_seq = any(
                (digits[i + 1] - digits[i] == 1 and digits[i + 2] - digits[i + 1] == 1) or
                (digits[i] - digits[i + 1] == 1 and digits[i + 1] - digits[i + 2] == 1)
                for i in range(4)
            )
            if not has_repeat and not has_seq:
                return "".join(map(str, digits))

    def _browser_version(self, name):
        for b in BROWSERS:
            if b["name"] == name:
                lo, hi = b["major_range"]
                major = random.randint(lo, hi)
                return f"{major}.0.{random.randint(1000, 9999)}.{random.randint(10, 99)}"
        return f"{random.randint(100, 120)}.0"

    def _bearer_token(self):
        header = base64.urlsafe_b64encode(b'{"alg":"HS256","typ":"JWT"}').decode().rstrip('=')
        payload_str = f'{{"sub":"{uuid.uuid4()}","iat":{int(time.time())}}}'
        payload = base64.urlsafe_b64encode(payload_str.encode()).decode().rstrip('=')
        sig_bytes = bytes([random.randint(0, 255) for _ in range(32)])
        signature = base64.urlsafe_b64encode(sig_bytes).decode().rstrip('=')
        return f"Bearer {header}.{payload}.{signature}"

    def generate(self, data_type, **kwargs):
        dt = data_type.lower()

        if dt == 'useragent':
            return self.generate_ua()

        if dt == 'apppassword':
            return self.generate_app_password()

        if dt == 'bearertoken':
            return self._bearer_token()

        if dt == 'browser_name':
            return random.choice(BROWSERS)["name"]

        if dt == 'browser_engine':
            return random.choice(BROWSERS)["engine"]

        if dt == 'browser_version':
            b = random.choice(BROWSERS)
            return self._browser_version(b["name"])

        if dt in ('uuid', 'requestid', 'correlationid', 'sessionid', 'idempotencykey'):
            return str(uuid.uuid4())

        if dt == 'signature':
            key = str(kwargs.get('secret', 'ninja')).encode()
            msg = str(kwargs.get('payload', 'mock')).encode()
            return hmac.new(key, msg, hashlib.sha256).hexdigest()

        if dt == 'deviceid':
            return str(uuid.uuid4()).upper()

        if dt == 'ipv4':
            return ".".join([str(random.randint(0, 255)) for _ in range(4)])

        if dt == 'ipv6':
            return ":".join([hex(random.randint(0, 65535))[2:].zfill(4) for _ in range(8)])

        if dt == 'timestamp_iso':
            return datetime.now().isoformat()

        if dt == 'timestamp':
            return str(int(time.time()))

        if dt == 'clientversion':
            return f"{random.randint(1, 4)}.{random.randint(0, 9)}.{random.randint(0, 9)}"

        if dt == 'jwt':
            return self._bearer_token().replace("Bearer ", "", 1)

        if dt == 'hash':
            algorithm = str(kwargs.get('algorithm', 'sha256')).lower()
            data = secrets.token_bytes(64)
            algos = {
                'md5':    hashlib.md5,
                'sha1':   hashlib.sha1,
                'sha256': hashlib.sha256,
                'sha512': hashlib.sha512,
            }
            return algos.get(algorithm, hashlib.sha256)(data).hexdigest()

        if dt == 'mac_address':
            oui = random.choice(OUI_PREFIXES)
            suffix = ":".join(f"{random.randint(0, 255):02X}" for _ in range(3))
            return f"{oui}:{suffix}"

        if dt == 'domain':
            locale = str(kwargs.get('locale', 'TR')).upper()
            tld = random.choice(DOMAIN_TLDS.get(locale, DOMAIN_TLDS["TR"]))
            words = ["api", "data", "test", "mock", "demo", "dev", "sample", "sandbox", "lab", "platform"]
            return f"{random.choice(words)}-{random.randint(10, 99)}{tld}"

        if dt == 'url':
            locale = str(kwargs.get('locale', 'TR')).upper()
            tld = random.choice(DOMAIN_TLDS.get(locale, DOMAIN_TLDS["TR"]))
            host = f"mockapi-{random.randint(100, 999)}{tld}"
            path = random.choice(URL_PATHS)
            return f"https://{host}{path}"

        if dt == 'color':
            fmt = str(kwargs.get('format', 'hex')).lower()
            name, hex_val, (r, g, b) = random.choice(COLOR_NAMES)
            if fmt == 'hex':
                return hex_val
            if fmt == 'rgb':
                return f"rgb({r}, {g}, {b})"
            if fmt == 'hsl':
                h, l_val, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
                return f"hsl({int(h * 360)}, {int(s * 100)}%, {int(l_val * 100)}%)"
            if fmt == 'name':
                return name
            return hex_val

        return None
