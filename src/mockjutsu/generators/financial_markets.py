"""
mock-jutsu — Financial Markets Generator
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)

Standards:
  ISIN  — ISO 6166:2021  (Luhn MOD-10 on numeric expansion)
  CUSIP — ABA CUSIP System (odd-position ×2, digit-sum)
  SEDOL — London Stock Exchange (weights [1,3,1,7,3,9], no vowels)
  LEI   — ISO 17442 / ISO 7064 MOD 97-10
"""

import secrets
import string

# ── Constants ────────────────────────────────────────────────────────────────

_SEDOL_CHARS = '0123456789BCDFGHJKLMNPQRSTVWXYZ'  # digits + consonants, no vowels

_LOU_PREFIXES = [
    '5299000', '2138000', '7LTWFH', '3H2OSJ', 'XKZZ2J',
    'HWUPKR', 'UWJKHY', '6SHGI4', '9695005', 'EVKOSJ',
    'BF90RS', 'F3716T', 'XTIQ1S', 'YZ83GR', 'QEKMOT',
]

_ISIN_COUNTRY = {
    'TR': 'TR', 'US': 'US', 'UK': 'GB', 'DE': 'DE', 'FR': 'FR', 'RU': 'RU',
}

# NSIN character pool per locale (exchange-appropriate, no vowels in non-digit parts)
_ISIN_NSIN_ALPHA = 'BCDFGHJKLMNPQRSTVWXYZ'
_ISIN_NSIN_DIGIT = string.digits


# ── Checksum helpers ─────────────────────────────────────────────────────────

def _luhn_check(digits: list[int]) -> int:
    """Standard Luhn check digit for a payload (rightmost payload digit at position 1)."""
    total = 0
    for i, d in enumerate(reversed(digits)):
        n = d * 2 if i % 2 == 0 else d  # payload's rightmost is at pos 1 in full number
        if n > 9:
            n -= 9
        total += n
    return (10 - total % 10) % 10


def _isin_luhn_check(payload: str) -> int:
    """Luhn check digit for ISIN: expand letters (A=10…Z=35), then standard Luhn."""
    numeric = ''.join(str(ord(c) - 55) if c.isalpha() else c for c in payload)
    return _luhn_check([int(d) for d in numeric])


def _cusip_check(payload: str) -> int:
    """ABA CUSIP check digit — odd positions (0-indexed) ×2 with digit-sum."""
    total = 0
    for i, c in enumerate(payload):
        v = int(c) if c.isdigit() else ord(c) - 55
        if i % 2 == 1:
            v *= 2
        total += v // 10 + v % 10
    return (10 - total % 10) % 10


def _sedol_check(payload: str) -> int:
    """LSE SEDOL check digit — weighted sum with [1,3,1,7,3,9]."""
    weights = [1, 3, 1, 7, 3, 9]
    total = sum(
        (int(c) if c.isdigit() else ord(c) - 55) * w
        for c, w in zip(payload, weights)
    )
    return (10 - total % 10) % 10


def _lei_check(prefix18: str) -> str:
    """ISO 7064 MOD 97-10 check digits for LEI prefix (18 chars)."""
    numeric = ''.join(str(ord(c) - 55) if c.isalpha() else c for c in prefix18 + '00')
    remainder = int(numeric) % 97
    return f'{98 - remainder:02d}'


# ── Generator ────────────────────────────────────────────────────────────────

class FinancialMarketsGenerator:
    """ISIN, CUSIP, SEDOL, LEI — algorithmic check digits, standards-compliant."""

    def generate(self, data_type: str, locale: str = 'US', **kwargs):
        dt = data_type.lower().strip()
        loc = locale.upper()

        if dt == 'isin':
            return self._isin(loc)
        if dt == 'cusip':
            return self._cusip()
        if dt == 'sedol':
            return self._sedol()
        if dt == 'lei':
            return self._lei()

        return f"ERROR: Unknown DataType '{dt}'"

    # ── ISIN ─────────────────────────────────────────────────────────────────

    def _isin(self, locale: str) -> str:
        """ISO 6166:2021 — CC + 9-char NSIN + Luhn check digit."""
        cc = _ISIN_COUNTRY.get(locale, 'US')

        # Build 9-char NSIN: mostly digits, occasional alpha for realism
        nsin_chars = []
        for i in range(9):
            if i == 0 and secrets.randbelow(4) == 0:
                nsin_chars.append(secrets.choice(_ISIN_NSIN_ALPHA))
            else:
                nsin_chars.append(secrets.choice(_ISIN_NSIN_DIGIT))
        nsin = ''.join(nsin_chars)

        payload = cc + nsin
        check = _isin_luhn_check(payload)
        return payload + str(check)

    # ── CUSIP ─────────────────────────────────────────────────────────────────

    def _cusip(self) -> str:
        """ABA CUSIP — 6-char issuer + 2-char issue + 1 check digit."""
        # Issuer: 6 alphanumeric chars (mostly digits for US equities)
        issuer = ''.join(
            secrets.choice(string.digits + 'ABCDEFGHJKLMNPQRSTUVWXYZ')
            for _ in range(6)
        )
        # Issue number: 2 alphanumeric chars
        issue = ''.join(
            secrets.choice(string.digits + string.ascii_uppercase)
            for _ in range(2)
        )
        payload = issuer + issue
        check = _cusip_check(payload)
        return payload + str(check)

    # ── SEDOL ─────────────────────────────────────────────────────────────────

    def _sedol(self) -> str:
        """LSE SEDOL — 6 consonant/digit chars + 1 weighted check digit."""
        # Mix of old-style (digits) and new-style (consonant prefix) SEDOLs
        if secrets.randbelow(2) == 0:
            # New-style: first char is consonant (B-Z, no vowels), rest mixed
            first = secrets.choice('BCDFGHJKLMNPQRSTVWXYZ')
            rest = ''.join(secrets.choice(_SEDOL_CHARS) for _ in range(5))
            payload = first + rest
        else:
            # Old-style: all digits
            payload = ''.join(secrets.choice(string.digits) for _ in range(6))
        check = _sedol_check(payload)
        return payload + str(check)

    # ── LEI ───────────────────────────────────────────────────────────────────

    def _lei(self) -> str:
        """ISO 17442 — 4-char LOU + 14-char entity + 2 MOD 97-10 check digits."""
        # 4-char LOU prefix (uppercase letters only, real LOU codes)
        lou = secrets.choice(_LOU_PREFIXES)[:4]

        # 14-char entity-specific part: alphanumeric, uppercase
        entity = ''.join(
            secrets.choice(string.digits + string.ascii_uppercase)
            for _ in range(14)
        )
        prefix18 = lou + entity
        check = _lei_check(prefix18)
        return prefix18 + check
