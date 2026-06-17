"""
mock-jutsu — Card Physics Generator (ISO 8583, EMV Cryptograms, ATM/POS)
Standards: ISO 8583-1:1993 v1987, ISO 9564-1:2011, EMV v4.3
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)
"""

import json
import random
import secrets
from datetime import datetime

from .financial import FinancialGenerator


# ISO 4217 currency: (DE049 numeric n3, alphabetic name) keyed by mock-jutsu locale
# DE049 is n3 per ISO 8583 — 3 digits, no leading zero prefix.
# NOTE: EMV chip tag 5F2A uses 2-byte BCD (e.g. 0x09 0x49 for TRY) — that lives in hardware.py.
_CURRENCY = {
    'TR': ('949', 'TRY'),
    'DE': ('978', 'EUR'),
    'FR': ('978', 'EUR'),
    'UK': ('826', 'GBP'),
    'US': ('840', 'USD'),
    'RU': ('643', 'RUB'),
}

# EMV AID pool (Visa, MC, JCB, Amex) — public application identifiers
_AID_POOL = [
    'A0000000031010',  # Visa Credit
    'A0000000041010',  # Mastercard Credit
    'A0000000651010',  # JCB
    'A0000000251010',  # Amex
]

_MCC_POOL = ['5411', '5999', '4111', '5912', '5691', '7011', '5812', '6011']
_ENTRY_MODES = ['051', '071', '002']   # Chip/Contact, Chip/Contactless, Magnetic
_RESPONSE_CODES = ['00', '05', '12', '14', '51', '54', '57', '91']
_RECEIPT_WIDTH = 40


def _make_bitmap(*des: int) -> str:
    """Compute ISO 8583 primary bitmap from DE numbers (1-indexed).
    Formula: bit (64-N) is set for each present Data Element N.
    """
    bits = 0
    for de in des:
        bits |= (1 << (64 - de))
    return f"{bits:016X}"


# Pre-computed bitmaps for each message type
_BITMAP_AUTH_REQ  = _make_bitmap(2, 3, 4, 7, 11, 12, 13, 14, 18, 22, 25, 37, 41, 42, 49)
_BITMAP_AUTH_RESP = _make_bitmap(2, 3, 4, 7, 11, 12, 13, 38, 39, 41, 42)
_BITMAP_REVERSAL  = _make_bitmap(2, 3, 4, 7, 11, 12, 13, 37, 41, 42, 49, 56)


class CardPhysicsGenerator:
    """ISO 8583 authorization messages, EMV cryptograms, ATM sessions, POS receipts."""

    def __init__(self):
        self._fin = FinancialGenerator()

    # ── EMV Cryptograms ─────────────────────────────────────────────────────

    def emv_arqc(self) -> str:
        """Application Request Cryptogram (EMV tag 9F26) — 8 bytes / 16 hex."""
        return secrets.token_hex(8).upper()

    def emv_atc(self) -> str:
        """Application Transaction Counter (EMV tag 9F36) — 2 bytes / 4 hex."""
        return f"{random.randint(1, 9999):04X}"

    def emv_iad(self) -> str:
        """Issuer Application Data (EMV tag 9F10) — 11 bytes / 22 hex.
        Layout: 0A(len) | DKI(1B) | CVN(1B) | CVR(2B) | ADD(4B) | PAD(2B)
        CVN values: 0x10=CVN10 (Visa legacy), 0x1A=CVN17, 0x22=CVN18
        """
        dki = random.randint(1, 3)
        cvn = random.choice([0x10, 0x1A, 0x22])
        cvr = random.randint(0, 0xFFFF)
        add = random.randint(0, 0xFFFFFFFF)
        pad = random.randint(0, 0xFFFF)
        return f"0A{dki:02X}{cvn:02X}{cvr:04X}{add:08X}{pad:04X}"

    # ── ISO 8583 Messages ───────────────────────────────────────────────────

    def iso8583_auth_request(self, locale: str = 'TR') -> str:
        """ISO 8583 v1987 Authorization Request (MTI 0100).
        DEs: 2,3,4,7,11,12,13,14,18,22,25,37,41,42,49
        """
        pan      = self._fin.generate_card_number('visa')
        curr_yy  = datetime.now().year % 100
        exp      = f"{random.randint(curr_yy + 1, curr_yy + 5):02d}{random.randint(1, 12):02d}"
        now      = datetime.now()
        trace    = f"{random.randint(1, 999999):06d}"
        rrn      = f"MOCKJ{secrets.token_hex(4)[:7].upper()}"   # 12 chars
        tid      = f"MOCKJT{random.randint(10, 99)}"             # 8 chars
        mid      = f"MOCKJM{random.randint(100000000, 999999999)}"  # 15 chars
        curr_code, _ = _CURRENCY.get(locale, _CURRENCY['TR'])
        amount   = random.randint(100, 9999999)

        return "\n".join([
            "MTI:0100",
            f"BITMAP:{_BITMAP_AUTH_REQ}",
            f"DE002:{pan}",
            "DE003:000000",
            f"DE004:{amount:012d}",
            f"DE007:{now.strftime('%m%d%H%M%S')}",
            f"DE011:{trace}",
            f"DE012:{now.strftime('%H%M%S')}",
            f"DE013:{now.strftime('%m%d')}",
            f"DE014:{exp}",
            f"DE018:{random.choice(_MCC_POOL)}",
            f"DE022:{random.choice(_ENTRY_MODES)}",
            "DE025:00",
            f"DE037:{rrn}",
            f"DE041:{tid}",
            f"DE042:{mid}",
            f"DE049:{curr_code}",
        ])

    def iso8583_auth_response(self, locale: str = 'TR') -> str:
        """ISO 8583 v1987 Authorization Response (MTI 0110).
        DEs: 2,3,4,7,11,12,13,38,39,41,42
        """
        pan       = self._fin.generate_card_number('visa')
        now       = datetime.now()
        trace     = f"{random.randint(1, 999999):06d}"
        auth_code = f"MOCKJ{random.randint(1, 9)}"   # 6 chars
        resp_code = random.choice(_RESPONSE_CODES)
        tid       = f"MOCKJT{random.randint(10, 99)}"
        mid       = f"MOCKJM{random.randint(100000000, 999999999)}"
        amount    = random.randint(100, 9999999)

        return "\n".join([
            "MTI:0110",
            f"BITMAP:{_BITMAP_AUTH_RESP}",
            f"DE002:{pan}",
            "DE003:000000",
            f"DE004:{amount:012d}",
            f"DE007:{now.strftime('%m%d%H%M%S')}",
            f"DE011:{trace}",
            f"DE012:{now.strftime('%H%M%S')}",
            f"DE013:{now.strftime('%m%d')}",
            f"DE038:{auth_code}",
            f"DE039:{resp_code}",
            f"DE041:{tid}",
            f"DE042:{mid}",
        ])

    def iso8583_reversal(self, locale: str = 'TR') -> str:
        """ISO 8583 v1987 Reversal Request (MTI 0400).
        DEs: 2,3,4,7,11,12,13,37,41,42,49,56
        DE056 = orig MTI(4) + orig STAN(6) + orig datetime(10) + acq ID(11)
        """
        pan        = self._fin.generate_card_number('visa')
        now        = datetime.now()
        trace      = f"{random.randint(1, 999999):06d}"
        rrn        = f"MOCKJ{secrets.token_hex(4)[:7].upper()}"
        tid        = f"MOCKJT{random.randint(10, 99)}"
        mid        = f"MOCKJM{random.randint(100000000, 999999999)}"
        curr_code, _ = _CURRENCY.get(locale, _CURRENCY['TR'])
        amount     = random.randint(100, 9999999)
        orig_trace = f"{random.randint(1, 999999):06d}"
        acq_id     = f"MOCKJ{random.randint(100000, 999999):06d}"  # 11 chars
        de056      = f"0100{orig_trace}{now.strftime('%m%d%H%M%S')}{acq_id}"

        return "\n".join([
            "MTI:0400",
            f"BITMAP:{_BITMAP_REVERSAL}",
            f"DE002:{pan}",
            "DE003:000000",
            f"DE004:{amount:012d}",
            f"DE007:{now.strftime('%m%d%H%M%S')}",
            f"DE011:{trace}",
            f"DE012:{now.strftime('%H%M%S')}",
            f"DE013:{now.strftime('%m%d')}",
            f"DE037:{rrn}",
            f"DE041:{tid}",
            f"DE042:{mid}",
            f"DE049:{curr_code}",
            f"DE056:{de056}",
        ])

    # ── ATM / POS ───────────────────────────────────────────────────────────

    def atm_session(self, locale: str = 'TR') -> str:
        """ATM session data record (ISO 8583-compatible fields) as JSON string."""
        curr_code, curr_name = _CURRENCY.get(locale, _CURRENCY['TR'])
        pan        = self._fin.generate_card_number('visa')
        masked_pan = f"{pan[:4]} **** **** {pan[-4:]}"
        curr_yy    = datetime.now().year % 100
        exp_yy     = curr_yy + random.randint(1, 5)
        exp_mm     = random.randint(1, 12)
        amount     = random.randint(2000, 1000000) / 100  # 20.00 – 10000.00
        trace      = f"{random.randint(1, 999999):06d}"
        session_id = f"MOCKJ-ATM-{secrets.token_hex(4).upper()}"
        tid        = f"MOCKJT{random.randint(10, 99)}"
        auth_code  = f"MOCKJ{random.randint(1, 9)}"

        data = {
            "session_id":        session_id,
            "terminal_id":       tid,
            "terminal_location": f"MOCKJ Bank Branch {random.randint(1, 99)}",
            "card_scheme":       "VISA",
            "masked_pan":        masked_pan,
            "expiry":            f"{exp_mm:02d}/{exp_yy:02d}",
            "transaction_type":  random.choice(["CASH_WITHDRAWAL", "BALANCE_INQUIRY", "MINI_STATEMENT"]),
            "amount":            f"{amount:.2f}",
            "currency":          curr_name,
            "response_code":     "00",
            "response_message":  "APPROVED",
            "auth_code":         auth_code,
            "atc":               self.emv_atc(),
            "arqc":              self.emv_arqc(),
            "stan":              trace,
            "timestamp":         datetime.now().isoformat(timespec='seconds'),
        }
        return json.dumps(data)

    def pos_receipt(self, locale: str = 'TR') -> str:
        """POS receipt formatted text (40-char wide)."""
        _, curr_name = _CURRENCY.get(locale, _CURRENCY['TR'])
        pan        = self._fin.generate_card_number('visa')
        masked_pan = f"**** **** **** {pan[-4:]}"
        curr_yy    = datetime.now().year % 100
        exp_yy     = curr_yy + random.randint(1, 5)
        exp_mm     = random.randint(1, 12)
        amount     = random.randint(100, 99999) / 100
        now        = datetime.now()
        tid        = f"MOCKJT{random.randint(10, 99)}"
        mid        = f"MOCKJM{random.randint(100000000, 999999999)}"
        auth_code  = f"MOCKJ{random.randint(1, 9)}"
        aid        = random.choice(_AID_POOL)
        entry_map  = {'051': 'CHIP/CONTACT', '071': 'CHIP/CONTACTLESS', '002': 'MAGNETIC'}
        entry      = entry_map[random.choice(list(entry_map))]

        w   = _RECEIPT_WIDTH
        sep = "=" * w
        dsh = "-" * w

        lines = [
            sep,
            "MOCKJ MERCHANT SERVICES".center(w),
            sep,
            f"Date: {now.strftime('%Y-%m-%d')}  Time: {now.strftime('%H:%M:%S')}",
            f"MID : {mid}",
            f"TID : {tid}",
            dsh,
            "SALE",
            f"Card  : {masked_pan}",
            f"Expiry: {exp_yy:02d}/{exp_mm:02d}",
            f"Mode  : {entry}",
            f"AID   : {aid}",
            dsh,
            f"Amount: {curr_name} {amount:>10.2f}",
            dsh,
            f"Auth  : {auth_code}",
            "Result: APPROVED",
            dsh,
            "*** TEST TRANSACTION ***".center(w),
            "*** MOCKJ TEST DATA ***".center(w),
            sep,
        ]
        return "\n".join(lines)

    # ── Dispatch ────────────────────────────────────────────────────────────

    def generate(self, data_type: str, **kwargs) -> str:
        dt     = data_type.lower().strip()
        locale = str(kwargs.get('locale', 'TR')).upper()

        if dt == 'emv_arqc':              return self.emv_arqc()
        if dt == 'emv_atc':               return self.emv_atc()
        if dt == 'emv_iad':               return self.emv_iad()
        if dt == 'iso8583_auth_request':  return self.iso8583_auth_request(locale)
        if dt == 'iso8583_auth_response': return self.iso8583_auth_response(locale)
        if dt == 'iso8583_reversal':      return self.iso8583_reversal(locale)
        if dt == 'atm_session':           return self.atm_session(locale)
        if dt == 'pos_receipt':           return self.pos_receipt(locale)
        return None
