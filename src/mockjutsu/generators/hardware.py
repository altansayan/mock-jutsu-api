"""
mock-jutsu — Hardware & Telemetry Generator
Standards: ISO/IEC 7813 (Magnetic Stripe), ISO 9564-1:2011 (PIN Block), EMV v4.3
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)
"""

import random
from datetime import datetime

from .financial import FinancialGenerator

# ISO 4217 BCD encoding for EMV tag 5F2A (Transaction Currency Code)
# Value = 2-byte BCD of ISO 4217 numeric code, e.g. TRY 949 → '0949'
_CURRENCY_TLV = {
    'TR': '5F2A020949',  # TRY 949
    'DE': '5F2A020978',  # EUR 978
    'FR': '5F2A020978',  # EUR 978
    'UK': '5F2A020826',  # GBP 826
    'US': '5F2A020840',  # USD 840
    'RU': '5F2A020643',  # RUB 643
}

_TRACK1_LASTNAMES  = ["MOCKJDOE", "MOCKJROE", "MOCKJKIM", "MOCKJLEE", "MOCKJRAY"]
_TRACK1_FIRSTNAMES = ["MOCKJJOHN", "MOCKJJANE", "MOCKJBOB", "MOCKJANN", "MOCKJMAX"]


class HardwareGenerator:
    """Hardware level data (Magnetic Stripe, Sensors, Telemetry)."""

    def __init__(self):
        self.financial = FinancialGenerator()

    def generate_track1_data(self) -> str:
        """ISO/IEC 7813 Track 1 Magnetic Stripe Data.
        Format: %B{PAN}^{LAST/FIRST}^{YYMM}{SC}{DD}?
        Max length: 79 chars total.
        MOCKJ marker placed in cardholder name field.
        """
        pan = self.financial.generate_card_number('visa')
        current_yy = datetime.now().year % 100
        yy = random.randint(current_yy + 1, current_yy + 5)
        mm = random.randint(1, 12)
        sc1 = random.choice(['1', '2'])
        sc3 = random.choice(['1', '6'])
        service_code = f"{sc1}0{sc3}"
        discretionary = "".join(str(random.randint(0, 9)) for _ in range(3))
        last  = random.choice(_TRACK1_LASTNAMES)
        first = random.choice(_TRACK1_FIRSTNAMES)
        name  = f"{last}/{first}"
        return f"%B{pan}^{name}^{yy:02d}{mm:02d}{service_code}{discretionary}?"

    def generate_track2_data(self) -> str:
        """ISO/IEC 7813 Track 2 Magnetic Stripe Data.
        Format: ;PAN=YYMMServiceCodeDiscretionaryData?
        """
        pan = self.financial.generate_card_number('visa')
        current_yy = datetime.now().year % 100
        yy = random.randint(current_yy + 1, current_yy + 10)
        mm = random.randint(1, 12)
        expiry = f"{yy:02d}{mm:02d}"
        sc1 = random.choice(['1', '2'])
        sc3 = random.choice(['1', '6'])
        service_code = f"{sc1}0{sc3}"
        discretionary_len = random.randint(3, 5)
        discretionary_data = "".join(str(random.randint(0, 9)) for _ in range(discretionary_len))
        return f";{pan}={expiry}{service_code}{discretionary_data}?"

    def generate_chip_data(self, locale: str = 'TR') -> str:
        """Simulated EMV chip (ICC) TLV data (Tag-Length-Value).
        Currency (5F2A) is locale-aware; ISO 4217 BCD encoding.
        """
        currency_tlv = _CURRENCY_TLV.get(locale, _CURRENCY_TLV['TR'])
        tags = [
            f"9F0206{random.randrange(100000000000):012d}",  # Amount (authorised)
            f"9F0306{random.randrange(100000000000):012d}",  # Amount (other)
            f"9505{random.randrange(10**10):010X}",          # Terminal Verification Results
            currency_tlv,                                    # Transaction Currency Code
            f"9A03{datetime.now().strftime('%y%m%d')}",     # Transaction Date YYMMDD
            "9C0100",                                        # Transaction Type (purchase)
        ]
        return "".join(tags)

    def generate_pin_block(self) -> str:
        """ISO 9564-1 Format 0 PIN block — 16 hex nibbles.
        Structure: [0][L][P1..PL][F..F] where L=PIN len, P=digit, F=0xF fill.
        """
        pin_len = random.randint(4, 6)
        pin_digits = [random.randint(0, 9) for _ in range(pin_len)]
        fill_count = 14 - pin_len  # 16 total - 1 format - 1 length - pin_len
        nibbles = [0, pin_len] + pin_digits + [0xF] * fill_count
        return "".join(f"{n:X}" for n in nibbles)

    def generate_pin_block_fmt3(self) -> str:
        """ISO 9564-1 Format 3 PIN block — 16 hex nibbles.
        Same as Format 0 but format nibble = 3 and fill = random decimal digits 0-9.
        """
        pin_len = random.randint(4, 6)
        pin_digits = [random.randint(0, 9) for _ in range(pin_len)]
        fill_count = 14 - pin_len
        fill_digits = [random.randint(0, 9) for _ in range(fill_count)]
        nibbles = [3, pin_len] + pin_digits + fill_digits
        return "".join(f"{n:X}" for n in nibbles)

    def generate(self, data_type: str, **kwargs) -> str:
        dt = data_type.lower().strip()
        locale = str(kwargs.get('locale', 'TR')).upper()

        if dt == 'track1_data':    return self.generate_track1_data()
        if dt == 'track2_data':    return self.generate_track2_data()
        if dt == 'chip_data':      return self.generate_chip_data(locale)
        if dt == 'pin_block':      return self.generate_pin_block()
        if dt == 'pin_block_fmt3': return self.generate_pin_block_fmt3()

        return "HARDWARE_DATA"
