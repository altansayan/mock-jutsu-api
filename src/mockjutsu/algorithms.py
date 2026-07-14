"""
Mock Jutsu — Shared Checksum Algorithms
========================================
Single source of truth for all checksum / validation algorithms.

Generation helpers  → used by generators/* to build valid values
Validation helpers  → used by validators.py to verify real-world input
"""

import re

# ── Verhoeff tables (Aadhaar) ─────────────────────────────────────────────────

_V_D = [
    [0,1,2,3,4,5,6,7,8,9],[1,2,3,4,0,6,7,8,9,5],[2,3,4,0,1,7,8,9,5,6],
    [3,4,0,1,2,8,9,5,6,7],[4,0,1,2,3,9,5,6,7,8],[5,9,8,7,6,0,4,3,2,1],
    [6,5,9,8,7,1,0,4,3,2],[7,6,5,9,8,2,1,0,4,3],[8,7,6,5,9,3,2,1,0,4],
    [9,8,7,6,5,4,3,2,1,0],
]
_V_P = [
    [0,1,2,3,4,5,6,7,8,9],[1,5,7,6,2,8,3,0,9,4],[5,8,0,3,7,9,6,1,4,2],
    [8,9,1,6,0,4,3,5,2,7],[9,4,5,3,1,2,6,8,7,0],[4,2,8,6,5,7,3,9,0,1],
    [2,7,9,3,8,0,6,4,1,5],[7,0,4,6,9,1,3,2,5,8],
]


# ══════════════════════════════════════════════════════════════════════════════
# GENERATION HELPERS  (return check digit, used by generators)
# ══════════════════════════════════════════════════════════════════════════════

def luhn_check_digit(digits: list[int]) -> int:
    """Standard Luhn check digit for a payload digit list (rightmost payload = position 2).

    ISO/IEC 7812-1.  Test vector: [4,9,0,1,5,4,2,0,3,2,3,7,5,1] → 8
    """
    total = 0
    for i, d in enumerate(reversed(digits)):
        n = d * 2 if i % 2 == 0 else d
        if n > 9:
            n -= 9
        total += n
    return (10 - total % 10) % 10


def iban_check_digits(prefix: str, body: str) -> str:
    """ISO 13616 MOD-97 check digits (2-digit string) for IBAN generation.

    Single source — previously duplicated in financial.py and banking.py.
    """
    rearranged = body + prefix + "00"
    numeric = "".join(str(ord(c) - 55) if c.isalpha() else c for c in rearranged)
    check = 98 - int(numeric) % 97
    return f"{check:02d}"


def isin_luhn_check(payload: str) -> int:
    """Luhn check digit for ISIN: expand letters (A=10…Z=35), then standard Luhn."""
    numeric = "".join(str(ord(c) - 55) if c.isalpha() else c for c in payload)
    return luhn_check_digit([int(d) for d in numeric])


def cusip_check(payload: str) -> int:
    """ABA CUSIP check digit — even 1-indexed positions ×2 with digit-sum."""
    total = 0
    for i, c in enumerate(payload):
        v = int(c) if c.isdigit() else ord(c) - 55
        if i % 2 == 1:
            v *= 2
        total += v // 10 + v % 10
    return (10 - total % 10) % 10


def iso7064_mod11_10_check(digits: list[int]) -> int:
    """ISO 7064 MOD 11,10 check digit — used for HR OIB, DE Steuer-IdNr."""
    product = 10
    for d in digits:
        s = (product + d) % 10
        if s == 0:
            s = 10
        product = (s * 2) % 11
    return (11 - product) % 10


def verhoeff_check(base_digits: list[int]) -> int:
    """Verhoeff check digit — used for Aadhaar (IN)."""
    for check in range(10):
        c = 0
        for i, d in enumerate(reversed(base_digits + [check])):
            c = _V_D[c][_V_P[i % 8][d]]
        if c == 0:
            return check
    return 0


def ee_lt_check(digits_10: list[int]) -> int:
    """EE/LT personal code check digit (two-pass weighted MOD-11)."""
    weights1 = [(i % 9) + 1 for i in range(10)]
    s = sum(w * d for w, d in zip(weights1, digits_10)) % 11
    if s == 10:
        weights2 = [((i + 2) % 9) + 1 for i in range(10)]
        s = sum(w * d for w, d in zip(weights2, digits_10)) % 11
    return s % 10


# ══════════════════════════════════════════════════════════════════════════════
# VALIDATION HELPERS  (return bool, used by validators.py)
# ══════════════════════════════════════════════════════════════════════════════

def luhn_valid(number_str: str) -> bool:
    """Validate a full number (including check digit) with the Luhn algorithm.

    Strips spaces and dashes before checking.
    ISO/IEC 7812-1.  Test vector: "4901542032375108" → True
    """
    digits = [int(c) for c in re.sub(r"[\s\-]", "", str(number_str)) if c.isdigit()]
    if len(digits) < 2:
        return False
    total = 0
    for i, d in enumerate(reversed(digits)):
        if i % 2 == 1:
            n = d * 2
            total += n - 9 if n > 9 else n
        else:
            total += d
    return total % 10 == 0


def iban_valid(iban_str: str) -> bool:
    """Validate an IBAN string (ISO 13616, MOD-97).

    Accepts spaces and lowercase.  Returns True only if MOD-97 remainder = 1.
    """
    s = re.sub(r"\s", "", iban_str).upper()
    if len(s) < 5 or not s[:2].isalpha() or not s[2:4].isdigit():
        return False
    rearranged = s[4:] + s[:4]
    numeric = "".join(str(ord(c) - 55) if c.isalpha() else c for c in rearranged)
    if not numeric.isdigit():
        return False
    return int(numeric) % 97 == 1


def tckn_valid(tckn_str: str) -> bool:
    """Validate a Turkish Republic ID (TC Kimlik Numarası).

    Rules (Nüfus Müdürlüğü):
      • 11 digits, first digit 1-9
      • d[9]  = (sum(d[0:9:2]) * 7 - sum(d[1:9:2])) % 10
      • d[10] = sum(d[0:10]) % 10
    """
    s = re.sub(r"\s", "", tckn_str)
    if not s.isdigit() or len(s) != 11 or s[0] == "0":
        return False
    d = [int(x) for x in s]
    if ((sum(d[0:9:2]) * 7 - sum(d[1:9:2])) % 10) != d[9]:
        return False
    return sum(d[0:10]) % 10 == d[10]


def vkn_valid(vkn_str: str) -> bool:
    """Validate a Turkish Tax ID (Vergi Kimlik Numarası).

    10 digits.  Proprietary GİB checksum algorithm.
    """
    s = re.sub(r"\s", "", vkn_str)
    if not s.isdigit() or len(s) != 10:
        return False
    d = [int(x) for x in s]
    total = 0
    for i in range(9):
        v = (d[i] + (9 - i)) % 10
        if v != 0:
            c = (v * (2 ** (9 - i))) % 9
            if c == 0:
                c = 9
        else:
            c = 0
        total += c
    return (10 - total % 10) % 10 == d[9]


def ssn_valid(ssn_str: str) -> bool:
    """Validate a US Social Security Number (format + SSA area/group/serial rules).

    Format: AAA-GG-SSSS
    Rules (SSA): area 001-899 excl. 000 and 666; group 01-99; serial 0001-9999.
    """
    m = re.fullmatch(r"(\d{3})-(\d{2})-(\d{4})", ssn_str.strip())
    if not m:
        return False
    area, group, serial = int(m.group(1)), int(m.group(2)), int(m.group(3))
    return area not in (0, 666) and area <= 899 and group != 0 and serial != 0


def nin_valid(nin_str: str) -> bool:
    """Validate a UK National Insurance Number (HMRC format rules).

    Format: XX 99 99 99 X  (spaces optional)
    Forbidden first chars:  D F I Q U V
    Forbidden second chars: D F I O Q U V
    Forbidden prefixes:     BG GB KN NK NT TN ZZ
    """
    s = re.sub(r"\s", "", nin_str).upper()
    if not re.fullmatch(r"[A-Z]{2}\d{6}[A-D]", s):
        return False
    forbidden_first  = set("DFIQUV")
    forbidden_second = set("DFIOQUV")
    forbidden_prefix = {"BG", "GB", "KN", "NK", "NT", "TN", "ZZ"}
    return (
        s[0] not in forbidden_first
        and s[1] not in forbidden_second
        and s[:2] not in forbidden_prefix
    )


def ykn_valid(ykn_str: str) -> bool:
    """Validate a Turkish Foreigner ID (Yabancı Kimlik Numarası).

    11 digits, must start with "99", Luhn check on full number.
    """
    s = re.sub(r"\s", "", ykn_str)
    if not s.isdigit() or len(s) != 11 or not s.startswith("99"):
        return False
    return luhn_valid(s)


def bic_valid(bic_str: str) -> bool:
    """Validate a BIC/SWIFT code (ISO 9362).

    Format: 4-letter bank + 2-letter country + 2-char location + optional 3-char branch.
    Length: 8 or 11 characters.
    """
    s = bic_str.strip().upper()
    return bool(re.fullmatch(r"[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?", s))
