"""
mock-jutsu — Financial Markets Generator
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)

Standards:
  ISIN       — ISO 6166:2021  (Luhn MOD-10 on numeric expansion)
  CUSIP      — ABA CUSIP System (odd-position ×2, digit-sum)
  SEDOL      — London Stock Exchange (weights [1,3,1,7,3,9], no vowels)
  LEI        — ISO 17442 / ISO 7064 MOD 97-10
  FIX 4.4   — FIX Trading Community (fixtradingcommunity.org)
               BodyLength = bytes from tag-35 to SOH before tag-10
               CheckSum   = sum of all bytes before tag-10 field, mod 256
"""

import random
import secrets
import string
from datetime import datetime, timezone

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

# FIX 4.4 data pools
_FIX_SOH = chr(1)

_FIX_SENDER_IDS = [
    'ALGOCLIENT', 'TRADEWORKS', 'HEDGE_FUND', 'MM_CORP', 'PROP_DESK',
    'QUANT_ALPHA', 'ARB_CAPITAL', 'HFT_ENGINE', 'STAT_ARB', 'MKTMKR01',
]
_FIX_TARGET_IDS = [
    'EXCHANGE', 'BROKER_NYC', 'PRIME_BRKR', 'DARK_POOL', 'ECN_VENUE',
    'NYSE_ARCA', 'NASDAQ_OMX', 'BATS_EXCH', 'IEX_VENUE', 'CBOE_EXCH',
]
_FIX_SYMBOLS = [
    'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META', 'TSLA', 'NVDA', 'JPM',
    'GS', 'BAC', 'IBM', 'ORCL', 'INTC', 'AMD', 'NFLX', 'SPY', 'QQQ',
    'IWM', 'DIA', 'VXX', 'BRKB', 'V', 'MA', 'UNH', 'WMT',
]


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
    """ISIN, CUSIP, SEDOL, LEI, FIX 4.4 — algorithmic check digits, standards-compliant."""

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
        if dt == 'fix_message':
            return self._fix_message()

        return f"ERROR: Unknown DataType '{dt}'"

    # ── ISIN ─────────────────────────────────────────────────────────────────

    def _isin(self, locale: str) -> str:
        """ISO 6166:2021 — CC + 9-char NSIN + Luhn check digit."""
        cc = _ISIN_COUNTRY.get(locale, 'US')

        # Build 9-char NSIN: mostly digits, occasional alpha for realism
        nsin_chars = []
        for i in range(9):
            if i == 0 and random.randrange(4) == 0:
                nsin_chars.append(random.choice(_ISIN_NSIN_ALPHA))
            else:
                nsin_chars.append(random.choice(_ISIN_NSIN_DIGIT))
        nsin = ''.join(nsin_chars)

        payload = cc + nsin
        check = _isin_luhn_check(payload)
        return payload + str(check)

    # ── CUSIP ─────────────────────────────────────────────────────────────────

    def _cusip(self) -> str:
        """ABA CUSIP — 6-char issuer + 2-char issue + 1 check digit."""
        # Issuer: 6 alphanumeric chars (mostly digits for US equities)
        issuer = ''.join(
            random.choice(string.digits + 'ABCDEFGHJKLMNPQRSTUVWXYZ')
            for _ in range(6)
        )
        # Issue number: 2 alphanumeric chars
        issue = ''.join(
            random.choice(string.digits + string.ascii_uppercase)
            for _ in range(2)
        )
        payload = issuer + issue
        check = _cusip_check(payload)
        return payload + str(check)

    # ── SEDOL ─────────────────────────────────────────────────────────────────

    def _sedol(self) -> str:
        """LSE SEDOL — 6 consonant/digit chars + 1 weighted check digit."""
        # Mix of old-style (digits) and new-style (consonant prefix) SEDOLs
        if random.randrange(2) == 0:
            # New-style: first char is consonant (B-Z, no vowels), rest mixed
            first = random.choice('BCDFGHJKLMNPQRSTVWXYZ')
            rest = ''.join(random.choice(_SEDOL_CHARS) for _ in range(5))
            payload = first + rest
        else:
            # Old-style: all digits
            payload = ''.join(random.choice(string.digits) for _ in range(6))
        check = _sedol_check(payload)
        return payload + str(check)

    # ── LEI ───────────────────────────────────────────────────────────────────

    def _lei(self) -> str:
        """ISO 17442 — 4-char LOU + 14-char entity + 2 MOD 97-10 check digits."""
        # 4-char LOU prefix (uppercase letters only, real LOU codes)
        lou = random.choice(_LOU_PREFIXES)[:4]

        # 14-char entity-specific part: alphanumeric, uppercase
        entity = ''.join(
            random.choice(string.digits + string.ascii_uppercase)
            for _ in range(14)
        )
        prefix18 = lou + entity
        check = _lei_check(prefix18)
        return prefix18 + check

    # ── FIX Protocol 4.4 ─────────────────────────────────────────────────────

    def _fix_message(self) -> str:
        """FIX 4.4 New Order Single (MsgType=D).

        BodyLength: byte count from first byte of tag-35 to SOH after last body tag.
        CheckSum:   sum of all byte values before the '10=' field, mod 256, zero-padded to 3 digits.
        """
        SOH = _FIX_SOH

        sender  = random.choice(_FIX_SENDER_IDS)
        target  = random.choice(_FIX_TARGET_IDS)
        seq_num = random.randint(1, 9_999_999)
        cl_ord_id = secrets.token_hex(8).upper()
        symbol  = random.choice(_FIX_SYMBOLS)
        side    = random.choice(['1', '2'])          # 1=Buy, 2=Sell
        qty     = random.randint(1, 1000) * 100      # round lots: 100–100000
        ord_type = random.choice(['1', '2', '3'])    # 1=Market, 2=Limit, 3=Stop

        now = datetime.now(timezone.utc)
        ts  = now.strftime('%Y%m%d-%H:%M:%S.') + f'{now.microsecond // 1000:03d}'

        body_fields = [
            f'35=D',
            f'49={sender}',
            f'56={target}',
            f'34={seq_num}',
            f'52={ts}',
            f'11={cl_ord_id}',
            f'55={symbol}',
            f'54={side}',
            f'38={qty}',
            f'40={ord_type}',
            f'60={ts}',
        ]

        if ord_type in ('2', '3'):
            price = round(random.uniform(1.0, 9999.99), 2)
            body_fields.append(f'44={price:.2f}')

        body     = SOH.join(body_fields) + SOH
        body_len = len(body)

        header               = f'8=FIX.4.4{SOH}9={body_len}{SOH}'
        before_checksum      = header + body
        checksum             = sum(ord(c) for c in before_checksum) % 256

        return before_checksum + f'10={checksum:03d}{SOH}'
