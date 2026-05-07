"""
mock-jutsu — Barcode Generator
Standards:
  GS1 General Specifications v24.0 §7.9 (EAN-13, EAN-8, UPC-A, GS1-128)
  ISO 2108:2017 (ISBN-13, ISBN-10)
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)

Entropy:
  EAN-13  : ~10^9 per country block (3-digit prefix + 9 random digits)
  EAN-8   : ~10^4 per country block (3-digit prefix + 4 random digits)
  UPC-A   : ~10^9 (1-digit system + 10 random digits)
  ISBN-13 : ~10^6-10^8 depending on registration group length
  ISBN-10 : ~10^8 (single-digit group + 8 random digits)
  GS1-128 : ~10^18 (GTIN-14 × lot serial space)
"""

import random
import secrets

# ──────────────────────────────────────────────────────────────────────────────
# GS1 Country/Region Prefixes — public list at gs1.org/standards/id-keys/prefix
# Only well-known assignments included; synthetic payload digits follow.
# ──────────────────────────────────────────────────────────────────────────────
_GS1_PREFIXES: dict[str, list[int]] = {
    "TR": [868, 869],
    "US": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
    "UK": [500, 501, 502, 503, 504, 505, 509],
    "DE": [400, 401, 410, 420, 430, 440],
    "FR": [300, 310, 320, 330, 340, 350, 360, 370],
    "RU": [460, 461, 462, 463, 464, 465, 469],
}
_GS1_PREFIXES_DEFAULT = [0, 300, 400, 500, 868, 460]

# EAN-8 uses the same country assignments but shorter payload
_EAN8_PREFIXES: dict[str, list[int]] = {
    "TR": [868, 869],
    "US": [0, 1, 2, 3],
    "UK": [500, 501, 502],
    "DE": [400, 401, 402],
    "FR": [300, 301, 302],
    "RU": [460, 461, 462],
}

# ISBN registration group codes — ISO 2108:2017, §7 (public list at isbn-international.org)
_ISBN_GROUPS = [0, 1, 2, 3, 4, 5, 7, 89, 91, 962, 968]


# ──────────────────────────────────────────────────────────────────────────────
# Check digit algorithms
# ──────────────────────────────────────────────────────────────────────────────

def _gs1_check(digits: list[int]) -> int:
    """
    GS1 MOD-10 check digit — GS1 General Specifications v24.0 §7.9.
    Weight pattern from right: pos-1 (rightmost) → 3, pos-2 → 1, alternating.
    Test vectors (all verified):
      EAN-13 payload 590123412345  → check 7
      EAN-8  payload 9638507       → check 4
      UPC-A  payload 03600029145   → check 2
    """
    total = sum(d * (3 if i % 2 == 0 else 1) for i, d in enumerate(reversed(digits)))
    return (10 - total % 10) % 10


def _isbn10_check(digits: list[int]) -> str:
    """
    ISBN-10 MOD-11 check digit — ISO 2108:2017 §5.
    Weights 10,9,8,...,2 applied to the 9 data digits.
    Returns '0'–'9' or 'X' (represents value 10).
    Test vector: data [0,3,0,6,4,0,6,1,5] → check '2' (ISBN 0-306-40615-2)
    """
    total = sum(d * (10 - i) for i, d in enumerate(digits))
    remainder = (11 - total % 11) % 11
    return "X" if remainder == 10 else str(remainder)


# ──────────────────────────────────────────────────────────────────────────────
# Generator
# ──────────────────────────────────────────────────────────────────────────────

class BarcodeGenerator:
    """GS1 / ISO 2108 compliant barcode generators for 6 locales."""

    @staticmethod
    def generate_ean13(locale: str = "TR") -> str:
        """EAN-13: 3-digit GS1 prefix + 9 random digits + MOD-10 check."""
        prefixes = _GS1_PREFIXES.get(locale.upper(), _GS1_PREFIXES_DEFAULT)
        prefix_str = f"{random.choice(prefixes):03d}"
        payload_str = prefix_str + "".join(str(random.randrange(10)) for _ in range(9))
        return payload_str + str(_gs1_check([int(c) for c in payload_str]))

    @staticmethod
    def generate_ean8(locale: str = "TR") -> str:
        """EAN-8: 3-digit GS1 prefix + 4 random digits + MOD-10 check."""
        prefixes = _EAN8_PREFIXES.get(locale.upper(), [0, 300, 400, 500, 868, 460])
        prefix_str = f"{random.choice(prefixes):03d}"
        payload_str = prefix_str + "".join(str(random.randrange(10)) for _ in range(4))
        return payload_str + str(_gs1_check([int(c) for c in payload_str]))

    @staticmethod
    def generate_upca() -> str:
        """UPC-A (US/Canada): 1-digit system code + 10 random digits + MOD-10 check."""
        # System digits: 0=general, 1=weight, 3=NDC, 6-8=general (most common)
        system = random.choice([0, 0, 0, 0, 1, 3, 6, 7, 8])
        payload_str = str(system) + "".join(str(random.randrange(10)) for _ in range(10))
        return payload_str + str(_gs1_check([int(c) for c in payload_str]))

    @staticmethod
    def generate_isbn13() -> str:
        """ISBN-13 (Bookland EAN): 978/979 prefix + registration group + publisher + MOD-10 check."""
        prefix = random.choice([978, 979])
        group = random.choice(_ISBN_GROUPS)
        group_str = str(group)
        pub_title = "".join(str(random.randrange(10)) for _ in range(9 - len(group_str)))
        payload_str = str(prefix) + group_str + pub_title
        return payload_str + str(_gs1_check([int(c) for c in payload_str]))

    @staticmethod
    def generate_isbn10() -> str:
        """ISBN-10: 1-digit group + 8 random digits + MOD-11 check (ISO 2108:2017)."""
        group = random.choice([0, 1, 2, 3, 4, 5, 7])
        payload_str = str(group) + "".join(str(random.randrange(10)) for _ in range(8))
        return payload_str + _isbn10_check([int(c) for c in payload_str])

    @staticmethod
    def generate_gs1_128() -> str:
        """
        GS1-128 barcode content — GS1 General Specifications v24.0 §5.4.
        Encodes: AI(01) GTIN-14, AI(17) expiry YYMMDD, AI(10) lot number.
        Combination space: ~10^18.
        """
        # AI(01): GTIN-14 = indicator(1) + GS1-company-prefix(7) + item-ref(5) + check(1)
        indicator = random.randrange(9)
        company   = "".join(str(random.randrange(10)) for _ in range(7))
        item_ref  = "".join(str(random.randrange(10)) for _ in range(5))
        gtin13_payload = [indicator] + [int(c) for c in company + item_ref]
        gtin14 = f"{indicator}{company}{item_ref}{_gs1_check(gtin13_payload)}"

        # AI(17): synthetic expiry within 0-730 days from today
        from datetime import date, timedelta
        expiry = (date.today() + timedelta(days=random.randrange(730))).strftime("%y%m%d")

        # AI(10): 6-character alphanumeric lot number
        lot_chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        lot = "".join(random.choice(lot_chars) for _ in range(6))

        return f"(01){gtin14}(17){expiry}(10){lot}"

    def generate(self, data_type: str, locale: str = "TR", **_) -> str | None:
        dt = data_type.lower().replace("_", "").replace("-", "")
        if dt == "ean13":
            return self.generate_ean13(locale)
        if dt == "ean8":
            return self.generate_ean8(locale)
        if dt == "upca":
            return self.generate_upca()
        if dt == "isbn13":
            return self.generate_isbn13()
        if dt == "isbn10":
            return self.generate_isbn10()
        if dt == "gs1128":
            return self.generate_gs1_128()
        return None
