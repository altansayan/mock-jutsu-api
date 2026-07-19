"""
mock-jutsu — Banking Generator (BIC/SWIFT, Routing, Sort Code, BIK, Transactions)
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)
"""

import random
import string
import secrets
from datetime import datetime, timezone, timedelta
from mockjutsu.algorithms import iban_check_digits, aba_routing_check_digit

# Public BIC/SWIFT codes — published by SWIFT (swift.com) and individual banks
BIC_CODES = {
    "TR": ["TCZBTR2A", "ISBKTRIS", "AKBKTRIS", "HLBKTRIS", "TVBATR2A", "DENITRIS", "TEBUTRIS", "GRNBTRIS"],
    "US": ["CHASUS33", "BOFAUS3N", "CITIUS33", "WFBIUS6S", "USBKUS44", "PNCCUS33", "SVBKUS6S"],
    "UK": ["BUKBGB22", "HBUKGB4B", "LOYDGB2L", "NWBKGB2L", "ABBYGB2L", "RBOSGB2L", "HLFXGB21"],
    "DE": ["DEUTDEDB", "COBADEFF", "HYVEDEMM", "GENODEFF", "BELADEBE", "INGDDEFF", "DRESDEFF"],
    "FR": ["BNPAFRPP", "SOGEFRPP", "AGRIFRPP", "CRLYFRPP", "CMCIFRPP", "CCFRFRPP", "BNPAFRPPPAC"],
    "RU": ["SABRRUMM", "VTBRRUMM", "ALFARUMM", "RZBSRUMM", "GAZPRUMM", "TICSRUMM", "RAIFRU8T"],
}

# Fictional bank names (locale-aware legal entity names)
BANK_NAMES = {
    "TR": ["MOCKJ Finans A.Ş.", "AnadoluFinans A.Ş.", "BosphorusBank A.Ş.", "GüvenFinans A.Ş.", "MaviBank A.Ş."],
    "US": ["MOCKJ Federal Bank", "Pacific Trust Bank", "Liberty National Bank", "Freedom Financial", "Pioneer Bank"],
    "UK": ["MOCKJ Crown Bank", "Royal Borough Bank", "Crown Finance Trust", "London Clearing Bank", "Imperial Trust"],
    "DE": ["MOCKJ Deutsche Finans", "Volksbank Nord GmbH", "Rheinische Sparkasse", "Berliner Finanzbank", "Saxon Trust AG"],
    "FR": ["MOCKJ Paris Banque", "Crédit Parisien SARL", "Banque Nationale Libre", "Loire Finance SA", "Paris Finance SA"],
    "RU": ["MOCKJ Народный Банк", "Столичный Банк АО", "Восточный Кредит ООО", "Русфинанс АО", "МоскваБанк ПАО"],
}

# Public sort code pools (Pay.UK Vocalink published directory)
SORT_CODE_POOLS = [
    "20-00-00", "20-00-55", "20-47-00",
    "40-00-00", "40-14-26", "40-02-50",
    "30-00-00", "30-12-34", "30-80-00",
    "60-00-01", "60-70-80", "60-14-73",
    "09-01-26", "09-01-27", "09-01-28",
    "16-00-00", "16-22-33", "16-44-55",
]

# Russian public BIK codes (Central Bank of Russia published directory)
BIK_POOL = [
    "044525225",  # Sberbank Moscow
    "044525187",  # VTB
    "044525593",  # Alfa-Bank
    "044525700",  # Raiffeisen
    "044525823",  # Gazprombank
    "044525999",  # Tinkoff
    "044030653",  # Sberbank St.Petersburg
    "044585326",  # Rosbank
]

TRANSACTION_DESCRIPTIONS = {
    "TR": ["Fatura ödemesi", "Market alışverişi", "FAST transferi", "EFT havalesi",
           "Kredi kartı ödemesi", "Kira ödemesi", "Sigorta primi", "Maaş ödemesi"],
    "US": ["Utility payment", "Online purchase", "Wire transfer", "ACH payment",
           "Rent payment", "Credit card payment", "Payroll deposit", "Insurance premium"],
    "UK": ["Utility bill payment", "Online shopping", "Faster Payment", "Standing order",
           "Direct debit", "Salary credit", "Mortgage payment", "Council tax"],
    "DE": ["Rechnung bezahlen", "Online-Einkauf", "SEPA-Überweisung", "Dauerauftrag",
           "Lastschrift", "Gehalt", "Miete", "Versicherungsprämie"],
    "FR": ["Paiement facture", "Achat en ligne", "Virement SEPA", "Prélèvement automatique",
           "Loyer", "Salaire", "Assurance", "Remboursement"],
    "RU": ["Оплата услуг ЖКХ", "Покупка в интернете", "Перевод СБП", "Оплата кредита",
           "Аренда квартиры", "Зарплата", "Страховой взнос", "Возврат средств"],
}

PAYMENT_CHANNELS = {
    "TR": ["FAST", "EFT", "Havale", "SWIFT", "Kart"],
    "US": ["ACH", "Wire", "Zelle", "SWIFT", "Check"],
    "UK": ["Faster Payments", "BACS", "CHAPS", "SWIFT"],
    "DE": ["SEPA Credit Transfer", "SEPA Direct Debit", "SWIFT", "Lastschrift"],
    "FR": ["Virement SEPA", "Prélèvement SEPA", "SWIFT", "TIP"],
    "RU": ["СБП", "Межбанк", "SWIFT", "Карточный перевод"],
}

IBAN_FORMATS = {
    "TR": {"prefix": "TR", "len": 26},
    "UK": {"prefix": "GB", "len": 22},
    "DE": {"prefix": "DE", "len": 22},
    "FR": {"prefix": "FR", "len": 27},
}

CURRENCIES = {
    "TR": "TRY", "US": "USD", "UK": "GBP", "DE": "EUR", "FR": "EUR", "RU": "RUB",
}

# SEPA reference alphanumeric charset (ISO 20022)
_SEPA_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

_ACCOUNT_TYPES = [
    'Checking', 'Savings', 'Current', 'Business Checking',
    'Money Market', 'CD', 'Investment',
]

_TRANSACTION_TYPES = [
    'CREDIT', 'DEBIT', 'TRANSFER', 'REFUND',
    'REVERSAL', 'CHARGEBACK', 'FEE', 'INTEREST',
]

_IFSC_BANK_CODES = [
    'SBIN', 'HDFC', 'ICIC', 'AXIS', 'KKBK', 'UTIB', 'PUNB',
    'CNRB', 'BARB', 'UBIN', 'IOBA', 'CBIN', 'BKID', 'VIJB',
]

_BSB_BANK_CODES = {
    '01': 'ANZ',    '03': 'Westpac',
    '06': 'CommBank', '08': 'NAB',
    '73': 'CBA',    '76': 'Bendigo',
}



def _wc(seq, weights):
    """Weighted secrets-based choice."""
    total = sum(weights)
    r = random.randrange(total)
    cumulative = 0
    for choice, weight in zip(seq, weights):
        cumulative += weight
        if r < cumulative:
            return choice
    return seq[-1]


class BankingGenerator:
    """Banking metadata and transaction data for 6 locales."""

    @staticmethod
    def _generate_iban(locale):
        fmt = IBAN_FORMATS.get(locale, IBAN_FORMATS["TR"])
        body_len = fmt["len"] - len(fmt["prefix"]) - 2
        body = "".join(str(random.randrange(10)) for _ in range(body_len))
        check = iban_check_digits(fmt["prefix"], body)
        return f"{fmt['prefix']}{check}{body}"

    @staticmethod
    def generate_swift(locale="TR"):
        return random.choice(BIC_CODES.get(locale.upper(), BIC_CODES["TR"]))

    @staticmethod
    def generate_sort_code():
        return random.choice(SORT_CODE_POOLS)

    @staticmethod
    def generate_routing_number():
        """ABA routing number — MOD-10 checksum: 3*(d0+d3+d6) + 7*(d1+d4+d7) + (d2+d5+d8) ≡ 0 (mod 10)."""
        districts = [
            "01","02","03","04","05","06","07","08","09","10","11","12",
            "21","22","23","24","25","26","27","28","29","30","31","32",
            "61","62","63","64","65","66","67","68","69","70","71","72","80",
        ]
        d_str = random.choice(districts)
        d = [int(d_str[0]), int(d_str[1])] + [random.randrange(10) for _ in range(6)]
        d.append(aba_routing_check_digit(d))
        return "".join(map(str, d))

    @staticmethod
    def generate_bik():
        return random.choice(BIK_POOL)

    @staticmethod
    def generate_sepa_ref():
        """SEPA end-to-end reference — ISO 20022, max 35 uppercase alphanumeric chars."""
        length = random.randrange(10) + 10  # 10–20 chars
        return f"MOCKJ-E2E-{''.join(random.choice(_SEPA_CHARS) for _ in range(length))}"

    @staticmethod
    def generate_creditor_ref():
        """ISO 11649 Creditor Reference — RF + 2-digit MOD-97 check + 3-21 alphanumeric chars."""
        length = random.randrange(10) + 5
        # Prefix the body with MOCKJ to label the data clearly
        body = f"MOCKJ{''.join(random.choice(_SEPA_CHARS) for _ in range(length))}"
        rearranged = body + "RF00"
        numeric = "".join(str(ord(c) - 55) if c.isalpha() else c for c in rearranged)
        check = 98 - int(numeric) % 97
        return f"RF{check:02d}{body}"

    @staticmethod
    def generate_transaction(locale="TR"):
        l = locale.upper()
        currency = CURRENCIES.get(l, "TRY")

        # Three-tier amount distribution: micro / normal / large
        tier = random.randrange(10)
        if tier == 0:
            amount = round(0.01 + random.randrange(100) / 100, 2)       # micro: 0.01–1.00
        elif tier <= 8:
            amount = round(5.0 + random.randrange(10 ** 8) / 10 ** 8 * 9994.99, 2)  # normal: 5.00–9999.99
        else:
            amount = float(100000 + random.randrange(900000))             # large: 100k–999k

        date_offset = random.randrange(7 * 24 * 3600)
        ts = (datetime.now(timezone.utc) - timedelta(seconds=date_offset)).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        ref_date = datetime.now().strftime("%Y%m%d")

        if l != "US":
            sender_iban   = BankingGenerator._generate_iban(l)
            receiver_iban = BankingGenerator._generate_iban(l)
        else:
            sender_iban   = f"RT:{BankingGenerator.generate_routing_number()}"
            receiver_iban = f"RT:{BankingGenerator.generate_routing_number()}"

        return {
            "ref":           f"MOCKJ-TRN{ref_date}-{random.randrange(90000) + 10000}",
            "sender_iban":   sender_iban,
            "receiver_iban": receiver_iban,
            "amount":        amount,
            "currency":      currency,
            "description":   random.choice(TRANSACTION_DESCRIPTIONS.get(l, TRANSACTION_DESCRIPTIONS["TR"])),
            "channel":       random.choice(PAYMENT_CHANNELS.get(l, PAYMENT_CHANNELS["TR"])),
            "timestamp":     ts,
            "status":        _wc(["COMPLETED", "PENDING", "FAILED"], [80, 15, 5]),
        }

    @staticmethod
    def generate_ifsc_code() -> str:
        bank = random.choice(_IFSC_BANK_CODES)
        branch = ''.join(random.choice(string.digits + string.ascii_uppercase) for _ in range(6))
        return f"{bank}0{branch}"

    @staticmethod
    def generate_bsb_code() -> str:
        bank_prefix = random.choice(list(_BSB_BANK_CODES.keys()))
        branch = random.randint(0, 999)
        return f"{bank_prefix}{random.randint(0, 9)}-{branch:03d}"

    @staticmethod
    def generate_check_number() -> str:
        return f"{random.randint(1, 9999):04d}"

    @staticmethod
    def generate_micr_line() -> str:
        routing = BankingGenerator.generate_routing_number()
        acct = ''.join(str(random.randint(0, 9)) for _ in range(random.randint(8, 12)))
        check = BankingGenerator.generate_check_number()
        return f"|{routing}| |{acct}| {check}"

    @staticmethod
    def generate_payment_reference() -> str:
        date_part = datetime.now().strftime('%Y%m%d')
        seq = random.randint(10000, 99999)
        return f"PAYREF-{date_part}-{seq}"

    @staticmethod
    def generate_account_number() -> str:
        length = random.randint(8, 12)
        return ''.join(str(random.randint(0, 9)) for _ in range(length))

    @staticmethod
    def generate_account_number_masked() -> str:
        """PCI-DSS v4.0 §3.3: only last 4 digits of account number may be displayed."""
        last4 = ''.join(str(random.randint(0, 9)) for _ in range(4))
        return f"****{last4}"

    @staticmethod
    def generate_micr_line_masked() -> str:
        """PCI-DSS §3.3: routing number is public (ABA directory), account segment masked."""
        routing = BankingGenerator.generate_routing_number()
        check = BankingGenerator.generate_check_number()
        return f"|{routing}| |****| {check}"

    @staticmethod
    def generate_transaction_description_masked(locale: str = "TR") -> str:
        """GDPR Art. 5(1)(c) data minimisation: truncate free-text description to 10 chars."""
        desc = random.choice(TRANSACTION_DESCRIPTIONS.get(locale.upper(), TRANSACTION_DESCRIPTIONS["TR"]))
        if len(desc) > 10:
            return desc[:10] + "***"
        return desc + "***"

    @staticmethod
    def generate_check_number_masked() -> str:
        """Mask check sequence number — last 2 digits visible (internal identifier, not PAN)."""
        n = random.randint(1, 9999)
        last2 = f"{n:04d}"[-2:]
        return f"**{last2}"

    @staticmethod
    def generate_payment_reference_masked() -> str:
        """Mask payment reference sequence; date segment not sensitive (GLBA best practice)."""
        date_part = datetime.now().strftime('%Y%m%d')
        return f"PAYREF-{date_part}-*****"

    def generate(self, data_type, locale="TR", **kwargs):
        l = locale.upper()
        dt = data_type.lower()

        if dt in ("swift", "bic"):
            return self.generate_swift(l)
        if dt == "sort_code":
            return self.generate_sort_code()
        if dt in ("routing_number", "wire_routing_number"):
            return self.generate_routing_number()
        if dt == "bik_code":
            return self.generate_bik()
        if dt == "transaction":
            return self.generate_transaction(l)
        if dt == "bank_name":
            return random.choice(BANK_NAMES.get(l, BANK_NAMES["TR"]))
        if dt == "sepa_ref":
            return self.generate_sepa_ref()
        if dt == "creditor_ref":
            return self.generate_creditor_ref()
        if dt == "account_type":
            return random.choice(_ACCOUNT_TYPES)
        if dt == "transaction_type":
            return random.choice(_TRANSACTION_TYPES)
        if dt == "transaction_description":
            return random.choice(TRANSACTION_DESCRIPTIONS.get(l, TRANSACTION_DESCRIPTIONS["TR"]))
        if dt == "ifsc_code":
            return self.generate_ifsc_code()
        if dt == "bsb_code":
            return self.generate_bsb_code()
        if dt == "check_number":
            return self.generate_check_number()
        if dt == "micr_line":
            return self.generate_micr_line()
        if dt == "payment_reference":
            return self.generate_payment_reference()
        if dt == "account_number":
            return self.generate_account_number()
        if dt == "account_number_masked":
            return self.generate_account_number_masked()
        if dt == "micr_line_masked":
            return self.generate_micr_line_masked()
        if dt == "transaction_description_masked":
            return self.generate_transaction_description_masked(l)
        if dt == "check_number_masked":
            return self.generate_check_number_masked()
        if dt == "payment_reference_masked":
            return self.generate_payment_reference_masked()
        return None
