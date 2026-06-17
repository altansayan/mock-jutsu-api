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

import base64
import hashlib
import hmac
import json
import random
import secrets
import string
import time
import uuid
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

# PSD2 / Open Banking data pools
_PSD2_CURRENCY = {
    'TR': 'TRY', 'UK': 'GBP', 'US': 'USD', 'DE': 'EUR', 'FR': 'EUR', 'RU': 'RUB',
}
_PSD2_SCHEME = {
    'TR': 'TR.IBAN',
    'UK': 'UK.OBIE.SortCodeAccountNumber',
    'US': 'US.RoutingNumberAccountNumber',
    'DE': 'IBAN',
    'FR': 'IBAN',
    'RU': 'RU.IBAN',
}
_PSD2_ISSUERS = [
    'C=GB, ST=England, O=Acme Bank, OU=PISP, CN=PISP/openbanking.org.uk',
    'C=GB, ST=England, O=Fintech Ltd, OU=AISP, CN=AISP/openbanking.org.uk',
    'C=DE, ST=Bayern, O=TechBank GmbH, OU=PISP, CN=PISP/openbanking.org.uk',
    'C=TR, ST=Istanbul, O=FinKurumu AS, OU=PISP, CN=PISP/openbanking.org.uk',
]
_PSD2_CREDITOR_NAMES = [
    'Acme Inc', 'TechCorp Ltd', 'Global Trade GmbH', 'FinServ SA',
    'Nordic Pay AB', 'EastBank LLC', 'Metro Supplies Co', 'AlphaFunds Ltd',
]
_PSD2_UNSTRUCTURED = [
    'Internal ops code 5120101', 'Supplier payment Q2', 'Invoice settlement',
    'Contract payment ref 7821', 'Monthly retainer fee', 'Project milestone 3',
]

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

def _luhn_check(digits) -> int:
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
    """ABA CUSIP check digit — even 1-indexed (odd 0-indexed) positions ×2 with digit-sum."""
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
        if dt == 'psd2_consent':
            amount = kwargs.get('amount')
            return self._psd2_consent(loc, amount=float(amount) if amount else None)

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

    # ── PSD2 / Open Banking JWS ───────────────────────────────────────────────

    def _psd2_consent(self, locale: str = 'UK', amount=None) -> str:
        """UK Open Banking v3.1 Payment Consent — compact JWS (header.payload.signature).

        Header claims follow RFC 7797 (b64=false, detached) and OB Security Profile.
        Signature: HMAC-SHA256 over signing_input with ephemeral 32-byte key.
        """
        loc = locale if locale in _PSD2_CURRENCY else 'UK'
        currency = _PSD2_CURRENCY[loc]
        scheme   = _PSD2_SCHEME[loc]

        # ── JWS Header ──────────────────────────────────────────────────────
        kid    = secrets.token_hex(8).upper()
        issuer = random.choice(_PSD2_ISSUERS)
        iat    = int(time.time())

        header_dict = {
            'alg': 'PS256',  # UK OB Security Profile v3.1 §6.3 requires PS256
            'kid': kid,
            'crit': [
                'http://openbanking.org.uk/iat',
                'http://openbanking.org.uk/iss',
                'http://openbanking.org.uk/tan',
            ],
            'http://openbanking.org.uk/iat': iat,
            'http://openbanking.org.uk/iss': issuer,
            'http://openbanking.org.uk/tan': 'openbanking.org.uk',
        }
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header_dict, separators=(',', ':')).encode()
        ).rstrip(b'=').decode()

        # ── JWS Payload ─────────────────────────────────────────────────────
        consent_id   = f'MOCKJ-aac-{uuid.uuid4().hex[:12]}'
        instr_id     = secrets.token_hex(4).upper()
        e2e_id       = f'E2E-{secrets.token_hex(5).upper()}'
        amount_val   = round(amount, 2) if amount is not None else round(random.uniform(10.0, 9999.99), 2)
        creditor_name = random.choice(_PSD2_CREDITOR_NAMES)
        creditor_id   = self._creditor_id(loc)
        ref           = f'REF-{secrets.token_hex(4).upper()}'

        payload_dict = {
            'Data': {
                'ConsentId': consent_id,
                'Initiation': {
                    'InstructionIdentification': instr_id,
                    'EndToEndIdentification': e2e_id,
                    'InstructedAmount': {
                        'Amount': f'{amount_val:.2f}',
                        'Currency': currency,
                    },
                    'CreditorAccount': {
                        'SchemeName': scheme,
                        'Identification': creditor_id,
                        'Name': creditor_name,
                    },
                    'RemittanceInformation': {
                        'Reference': ref,
                        'Unstructured': random.choice(_PSD2_UNSTRUCTURED),
                    },
                },
            },
            'Risk': {},
        }
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(payload_dict, separators=(',', ':')).encode()
        ).rstrip(b'=').decode()

        # ── HMAC-SHA256 Signature ────────────────────────────────────────────
        signing_input = f'{header_b64}.{payload_b64}'.encode()
        key           = secrets.token_bytes(32)
        sig           = hmac.new(key, signing_input, hashlib.sha256).digest()
        sig_b64       = base64.urlsafe_b64encode(sig).rstrip(b'=').decode()

        return f'{header_b64}.{payload_b64}.{sig_b64}'

    @staticmethod
    def _creditor_id(locale: str) -> str:
        """Generate a locale-appropriate creditor account identifier."""
        if locale == 'UK':
            sort = f'{random.randint(10,99)}-{random.randint(10,99)}-{random.randint(10,99)}'
            acct = f'{random.randint(10000000, 99999999)}'
            return sort + acct
        if locale == 'US':
            routing = f'{random.randint(100000000, 999999999)}'
            acct    = f'{random.randint(100000000, 9999999999)}'
            return routing + acct
        # IBAN-style for TR, DE, FR, RU
        prefix = {'TR': 'TR', 'DE': 'DE', 'FR': 'FR', 'RU': 'RU'}.get(locale, 'GB')
        return prefix + f'{random.randint(10, 99)}' + ''.join(
            str(random.randint(0, 9)) for _ in range(16)
        )
