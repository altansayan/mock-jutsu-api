"""
mock-jutsu — Meta Generator (Combinatorial User Agent + Security Data + Tech)
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)
"""

import uuid
import time
import hmac
import zlib
import hashlib
import base64
import colorsys
import random
import secrets
import string
from datetime import datetime


def _crc16_ccitt(data: bytes) -> int:
    """CRC-16/CCITT-FALSE — poly 0x1021, init 0xFFFF."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) if crc & 0x8000 else crc << 1
            crc &= 0xFFFF
    return crc

BROWSERS = [
    {"name": "Chrome",  "engine": "Blink",   "major_range": (120, 126)},
    {"name": "Firefox", "engine": "Gecko",   "major_range": (120, 127)},
    {"name": "Safari",  "engine": "WebKit",  "major_range": (16, 18)},
    {"name": "Edge",    "engine": "Blink",   "major_range": (120, 126)},
    {"name": "Opera",   "engine": "Blink",   "major_range": (105, 110)},
]

# Expanded OUI prefixes (public IEEE registry — ieee.org/regauth)
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
    "00:23:AE",  # Cisco Meraki
    "AC:BC:32",  # Apple
    "F4:5C:89",  # Samsung Electronics
    "70:F0:96",  # Samsung Electronics
    "CC:46:D6",  # Cisco
    "00:0C:29",  # VMware
    "44:38:39",  # Cumulus Networks
    "2C:F0:5D",  # Cisco
    "B0:BE:83",  # Dell
    "00:25:90",  # Super Micro Computer
    "3C:D9:2B",  # Hewlett Packard
    "78:E3:B5",  # Cisco
    "00:1A:11",  # Google
    "54:EE:75",  # Apple
    "00:17:88",  # Philips Hue
    "18:B4:30",  # Nest Labs
    "70:85:C2",  # Ubiquiti Networks
    "00:27:22",  # Mimosa Networks
    "44:D9:E7",  # Murata Manufacturing
    "A8:40:41",  # Espressif Inc.
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

_API_KEY_CHARS = string.ascii_letters + string.digits

# Reserved IPv4 ranges to exclude from public IPs
_RESERVED_FIRST_OCTETS = {
    0,    # 0.0.0.0/8
    10,   # RFC 1918
    127,  # loopback
    169,  # link-local
    172,  # RFC 1918 (172.16-31.x)
    192,  # RFC 1918 (192.168.x)
    198,  # IETF protocol assignments
    203,  # IETF protocol assignments
    224,  # multicast
    225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239,
    240,  # reserved
    241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255,
}


def _is_public_ipv4(a, b, c, d) -> bool:
    """Return True if the given IPv4 octets form a globally routable address."""
    if a in _RESERVED_FIRST_OCTETS:
        return False
    if a == 172 and 16 <= b <= 31:
        return False
    if a == 192 and b == 168:
        return False
    return True


def _gen_public_ipv4() -> str:
    """Generate a globally routable (public) IPv4 address."""
    while True:
        a = random.randrange(256)
        b = random.randrange(256)
        c = random.randrange(256)
        d = random.randrange(256)
        if _is_public_ipv4(a, b, c, d):
            return f"{a}.{b}.{c}.{d}"


def _gen_private_ipv4() -> str:
    """Generate an RFC 1918 private IPv4 address."""
    tier = random.randrange(3)
    if tier == 0:
        return f"10.{random.randrange(256)}.{random.randrange(256)}.{random.randrange(256)}"
    if tier == 1:
        return f"172.{random.randrange(16) + 16}.{random.randrange(256)}.{random.randrange(256)}"
    return f"192.168.{random.randrange(256)}.{random.randrange(256)}"


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
        chrome_v = f"{random.randrange(7) + 120}.0.{random.randrange(9000) + 1000}.{random.randrange(90) + 10}"
        safari_v = f"{random.randrange(71) + 530}.{random.randrange(40) + 1}"

        plat = random.choice(platforms)
        arch = random.choice(archs) if ("Windows" in plat or "Linux" in plat) else ""

        ua  = f"Mozilla/5.0 ({plat}{'; ' + arch if arch else ''}) "
        ua += f"AppleWebKit/{safari_v} (KHTML, like Gecko) "
        ua += f"Chrome/{chrome_v} Safari/{safari_v}"
        return ua

    def generate_app_password(self):
        """6-digit PIN with no consecutive repeats and no sequential runs of 3+."""
        while True:
            digits = [random.randrange(10) for _ in range(6)]
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
                major = random.randrange(hi - lo + 1) + lo
                return f"{major}.0.{random.randrange(9000) + 1000}.{random.randrange(90) + 10}"
        return f"{random.randrange(21) + 100}.0"

    def _bearer_token(self):
        header  = base64.urlsafe_b64encode(b'{"alg":"HS256","typ":"JWT"}').decode().rstrip('=')
        payload_str = f'{{"sub":"{uuid.uuid4()}","iat":{int(time.time())}}}'
        payload = base64.urlsafe_b64encode(payload_str.encode()).decode().rstrip('=')
        sig_bytes = secrets.token_bytes(32)
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
            return _gen_public_ipv4()

        if dt == 'public_ip':
            return _gen_public_ipv4()

        if dt == 'private_ip':
            return _gen_private_ipv4()

        if dt == 'ipv6':
            return ":".join(f"{random.randrange(65536):04x}" for _ in range(8))

        if dt == 'timestamp_iso':
            return datetime.now().isoformat()

        if dt == 'timestamp':
            return str(int(time.time()))

        if dt == 'clientversion':
            return f"{random.randrange(4) + 1}.{random.randrange(10)}.{random.randrange(10)}"

        if dt == 'jwt':
            return self._bearer_token().replace("Bearer ", "", 1)

        if dt == 'hash':
            algorithm = str(kwargs.get('algorithm', 'sha256')).lower()
            data = secrets.token_bytes(64)

            # Standard hashlib algorithms
            _HL = {
                'md5':      hashlib.md5,
                'sha1':     hashlib.sha1,
                'sha224':   hashlib.sha224,
                'sha256':   hashlib.sha256,
                'sha384':   hashlib.sha384,
                'sha512':   hashlib.sha512,
                'sha3-224': hashlib.sha3_224,
                'sha3-256': hashlib.sha3_256,
                'sha3-384': hashlib.sha3_384,
                'sha3-512': hashlib.sha3_512,
            }
            if algorithm in _HL:
                return _HL[algorithm](data).hexdigest()

            # CRC32 — zlib, unsigned 32-bit → 8 hex chars
            if algorithm == 'crc32':
                return f"{zlib.crc32(data) & 0xFFFFFFFF:08x}"

            # Adler-32 — zlib, unsigned 32-bit → 8 hex chars
            if algorithm == 'adler32':
                return f"{zlib.adler32(data) & 0xFFFFFFFF:08x}"

            # CRC-16/CCITT-FALSE — pure Python, 16-bit → 4 hex chars
            if algorithm == 'crc16':
                return f"{_crc16_ccitt(data):04x}"

            # Fallback: sha256
            return hashlib.sha256(data).hexdigest()

        if dt == 'mac_address':
            oui    = random.choice(OUI_PREFIXES)
            suffix = ":".join(f"{random.randrange(256):02X}" for _ in range(3))
            return f"{oui}:{suffix}"

        if dt == 'domain':
            locale = str(kwargs.get('locale', 'TR')).upper()
            tld    = random.choice(DOMAIN_TLDS.get(locale, DOMAIN_TLDS["TR"]))
            words  = ["api", "data", "test", "mock", "demo", "dev", "sample", "sandbox", "lab", "platform"]
            return f"{random.choice(words)}-{random.randrange(90) + 10}{tld}"

        if dt == 'url':
            locale = str(kwargs.get('locale', 'TR')).upper()
            tld    = random.choice(DOMAIN_TLDS.get(locale, DOMAIN_TLDS["TR"]))
            host   = f"mockapi-{random.randrange(900) + 100}{tld}"
            path   = random.choice(URL_PATHS)
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

        # ── Security / API types ─────────────────────────────────────────────

        if dt == 'api_key':
            suffix = "".join(random.choice(_API_KEY_CHARS) for _ in range(48))
            return f"sk-{suffix}"

        if dt == 'totp_code':
            return f"{random.randrange(1000000):06d}"

        if dt == 'webhook_signature':
            payload_bytes = secrets.token_bytes(32)
            sig = hashlib.sha256(payload_bytes).hexdigest()
            return f"sha256={sig}"

        if dt == 'transaction_id':
            return f"TXN{secrets.token_hex(8).upper()}"

        return None
