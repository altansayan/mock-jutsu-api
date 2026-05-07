"""
mock-jutsu — E-Commerce Generator
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)

Standards / Algorithms:
  USPS tracking — Luhn MOD-10 (USPS Publication 97, Appendix F)
  UPS tracking  — weighted check digit (alternating ×1/×2, mod 10)
  FedEx tracking — Mod-11 with weights [3,1,7,3,1,7,3,1,7,3,1]
  SKU           — GS1-inspired alphanumeric format (no proprietary constraint)
  Order ID      — ORD- prefix + CSPRNG alphanumeric suffix
"""

import secrets
import string

# ── Data ─────────────────────────────────────────────────────────────────────

_PRODUCT_NAMES = [
    "Wireless Headphones", "Mechanical Keyboard", "USB-C Hub", "LED Desk Lamp",
    "Ergonomic Mouse", "Laptop Stand", "Webcam HD", "Portable SSD",
    "Smart Watch", "Bluetooth Speaker", "Phone Case", "Screen Protector",
    "Gaming Chair", "Monitor Arm", "Cable Management Kit", "Power Bank",
    "Noise Cancelling Earbuds", "Graphic Tablet", "Drawing Pad", "Ring Light",
    "Action Camera", "Drone Mini", "VR Headset", "Smart Plug",
    "Robot Vacuum", "Air Purifier", "Coffee Maker", "Electric Kettle",
    "Standing Desk", "Mesh Wi-Fi System", "NAS Drive", "Raspberry Pi Kit",
]

_CATEGORIES = [
    "Electronics", "Computers & Accessories", "Audio & Video", "Photography",
    "Gaming", "Office Supplies", "Home & Kitchen", "Health & Beauty",
    "Sports & Outdoors", "Books & Media", "Clothing", "Automotive",
    "Toys & Games", "Tools & Hardware", "Garden & Outdoor", "Pet Supplies",
]

_USPS_PREFIXES = ['92', '94', '70', '93', '95']
_UPS_SERVICE   = ['01', '02', '03', '12', '13']
_ALPHA_UPPER   = string.ascii_uppercase + string.digits


# ── Checksum helpers ──────────────────────────────────────────────────────────

def _luhn_check_digit(digits: list[int]) -> int:
    """Standard Luhn check digit for a payload list (rightmost is position 1)."""
    total = 0
    for i, d in enumerate(reversed(digits)):
        n = d * 2 if i % 2 == 0 else d
        if n > 9:
            n -= 9
        total += n
    return (10 - total % 10) % 10


def _ups_check_digit(payload: str) -> int:
    """UPS check digit: letters A=10..Z=35, alternate ×1/×2, digit-sum, mod 10."""
    total = 0
    for i, c in enumerate(payload):
        v = int(c) if c.isdigit() else ord(c) - 55
        if i % 2 == 1:
            v *= 2
        if v > 9:
            v -= 9
        total += v
    return (10 - total % 10) % 10


def _fedex_check_digit(payload: str) -> int:
    """FedEx Express 12-digit: Mod-11 with weights [3,1,7,3,1,7,3,1,7,3,1]."""
    weights = [3, 1, 7, 3, 1, 7, 3, 1, 7, 3, 1]
    total = sum(int(d) * w for d, w in zip(payload, weights))
    check = total % 11
    return 0 if check == 10 else check


# ── Generator ─────────────────────────────────────────────────────────────────

class EcommerceGenerator:
    """Product, SKU, Order ID, Tracking Numbers, Category, Rating."""

    def generate(self, data_type: str, **kwargs):
        dt = data_type.lower().strip()
        carrier = str(kwargs.get('carrier', 'usps')).lower()

        if dt == 'product_name':
            return secrets.choice(_PRODUCT_NAMES)
        if dt == 'sku':
            return self._sku()
        if dt == 'order_id':
            return self._order_id()
        if dt == 'tracking_number':
            return self._tracking(carrier)
        if dt == 'category':
            return secrets.choice(_CATEGORIES)
        if dt == 'rating':
            return self._rating()
        if dt == 'dhl_tracking':
            return self._tracking_dhl()

        return f"ERROR: Unknown DataType '{dt}'"

    # ── SKU ───────────────────────────────────────────────────────────────────

    def _sku(self) -> str:
        """GS1-inspired format: 2-4 uppercase letters + dash + 4-8 digits."""
        prefix = ''.join(secrets.choice(string.ascii_uppercase)
                         for _ in range(secrets.randbelow(3) + 2))
        number = ''.join(secrets.choice(string.digits)
                         for _ in range(secrets.randbelow(5) + 4))
        return f"{prefix}-{number}"

    # ── Order ID ──────────────────────────────────────────────────────────────

    def _order_id(self) -> str:
        """ORD- + 8-12 uppercase alphanumeric characters (CSPRNG)."""
        length = secrets.randbelow(5) + 8
        suffix = ''.join(secrets.choice(_ALPHA_UPPER) for _ in range(length))
        return f"ORD-{suffix}"

    # ── Tracking Numbers ─────────────────────────────────────────────────────

    def _tracking(self, carrier: str) -> str:
        if carrier == 'ups':
            return self._tracking_ups()
        if carrier == 'fedex':
            return self._tracking_fedex()
        return self._tracking_usps()  # default

    def _tracking_usps(self) -> str:
        """USPS IMpb 22-digit: prefix(2) + 19 random digits + Luhn check digit.
        Prefixes: 92=Priority, 94=First Class, 70=Certified, 93/95=other.
        Reference: USPS Publication 97, Appendix F.
        """
        prefix = secrets.choice(_USPS_PREFIXES)
        body = [secrets.randbelow(10) for _ in range(19)]
        payload = [int(d) for d in prefix] + body
        check = _luhn_check_digit(payload)
        return prefix + ''.join(map(str, body)) + str(check)

    def _tracking_ups(self) -> str:
        """UPS 18-char: 1Z + 6-char shipper + 2-digit service + 8 alphanum + check.
        Reference: public UPS technical documentation (weighted mod-10).
        """
        shipper = ''.join(secrets.choice(_ALPHA_UPPER) for _ in range(6))
        service = secrets.choice(_UPS_SERVICE)
        package = ''.join(secrets.choice(_ALPHA_UPPER) for _ in range(7))
        payload = shipper + service + package
        check = _ups_check_digit(payload)
        return f"1Z{payload}{check}"

    def _tracking_fedex(self) -> str:
        """FedEx Express 12-digit: 11 random digits + Mod-11 check digit.
        Reference: FedEx Developer Guide — tracking number formats.
        """
        body = ''.join(str(secrets.randbelow(10)) for _ in range(11))
        check = _fedex_check_digit(body)
        return body + str(check)

    # ── DHL Tracking ─────────────────────────────────────────────────────────

    def _tracking_dhl(self) -> str:
        """DHL JD-series tracking: 'JD' + 8 random digits + 1 Luhn check digit.
        Reference: DHL Express developer guide — JD waybill format.
        """
        body = [secrets.randbelow(10) for _ in range(8)]
        check = _luhn_check_digit(body)
        return "JD" + ''.join(map(str, body)) + str(check)

    # ── Rating ────────────────────────────────────────────────────────────────

    def _rating(self) -> str:
        """Product rating: 1.0–5.0 with one decimal place."""
        choices = ['1.0','1.5','2.0','2.5','3.0','3.5','4.0','4.5','5.0']
        weights = [1, 2, 3, 4, 8, 12, 20, 25, 25]
        r = secrets.randbelow(sum(weights))
        cumulative = 0
        for val, w in zip(choices, weights):
            cumulative += w
            if r < cumulative:
                return val
        return '5.0'
