"""
mock-jutsu — Banking Generator (BIC/SWIFT, Routing, Sort Code, BIK, Transactions)
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)
"""

import random
from datetime import datetime, timezone, timedelta

# Public BIC/SWIFT codes — published by SWIFT (swift.com) and individual banks
BIC_CODES = {
    "TR": ["TCZBTR2A", "ISCTRISM", "AKBKTRIS", "HLBKTRIS", "TVBATR2A", "DENITRIS", "TEBUTRIS", "GRNBTRIS"],
    "US": ["CHASUS33", "BOFAUS3N", "CITIUS33", "WFBIUS6S", "USBKUS44", "PNCCUS33", "SVBKUS6S"],
    "UK": ["BUKBGB22", "HBUKGB4B", "LOYDGB2L", "NWBKGB2L", "ABBYGB2L", "RBOSGB2L", "HLFXGB21"],
    "DE": ["DEUTDEDB", "COBADEFF", "HYVEDEMM", "GENODEFF", "BELADEBE", "INGDDEFF", "DRESDEFF"],
    "FR": ["BNPAFRPP", "SOGEFRPP", "AGRIFRPP", "CRLYFRPP", "CMCIFRPP", "CCFRFRPP", "BNPAFRPPPAC"],
    "RU": ["SABRRUMM", "VTBRRUMM", "ALFARUMM", "RZBSRUMM", "GAZPRUMM", "TICSRUMM", "RAIFRU8T"],
}

# Fictional bank names (locale-aware legal entity names)
BANK_NAMES = {
    "TR": ["AnadoluFinans A.Ş.", "BosphorusBank A.Ş.", "GüvenFinans A.Ş.", "Boğaz Finans A.Ş.", "MaviBank A.Ş."],
    "US": ["Pacific Trust Bank", "Liberty National Bank", "Freedom Financial", "American Commerce Bank", "Pioneer Bank"],
    "UK": ["Royal Borough Bank", "Crown Finance Trust", "London Clearing Bank", "Imperial Trust", "Commonwealth Bank plc"],
    "DE": ["Volksbank Nord GmbH", "Rheinische Sparkasse", "Berliner Finanzbank", "Saxon Trust AG", "Nord Finance GmbH"],
    "FR": ["Crédit Parisien SARL", "Banque Nationale Libre", "Loire Finance SA", "Société de Crédit SAS", "Paris Finance SA"],
    "RU": ["Народный Банк ООО", "Столичный Банк АО", "Восточный Кредит ООО", "Русфинанс АО", "МоскваБанк ПАО"],
}

# Public sort code pools (Pay.UK Vocalink published directory)
SORT_CODE_POOLS = [
    "20-00-00", "20-00-55", "20-47-00",   # Barclays
    "40-00-00", "40-14-26", "40-02-50",   # HSBC
    "30-00-00", "30-12-34", "30-80-00",   # Lloyds
    "60-00-01", "60-70-80", "60-14-73",   # NatWest
    "09-01-26", "09-01-27", "09-01-28",   # Santander UK
    "16-00-00", "16-22-33", "16-44-55",   # Yorkshire Bank
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


class BankingGenerator:
    """Banking metadata and transaction data for 6 locales."""

    @staticmethod
    def _generate_iban(locale):
        fmt = IBAN_FORMATS.get(locale, IBAN_FORMATS["TR"])
        body_len = fmt["len"] - len(fmt["prefix"]) - 2
        body = "".join([str(random.randint(0, 9)) for _ in range(body_len)])
        return f"{fmt['prefix']}{random.randint(10, 99):02d}{body}"

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
        d = [int(d_str[0]), int(d_str[1])] + [random.randint(0, 9) for _ in range(6)]
        total = 3 * (d[0] + d[3] + d[6]) + 7 * (d[1] + d[4] + d[7]) + (d[2] + d[5])
        check = (10 - total % 10) % 10
        d.append(check)
        return "".join(map(str, d))

    @staticmethod
    def generate_bik():
        return random.choice(BIK_POOL)

    @staticmethod
    def generate_transaction(locale="TR"):
        l = locale.upper()
        currency = CURRENCIES.get(l, "TRY")
        amount = round(random.uniform(5.0, 9999.99), 2)
        date_offset = random.randint(0, 7 * 24 * 3600)
        ts = (datetime.now(timezone.utc) - timedelta(seconds=date_offset)).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        ref_date = datetime.now().strftime("%Y%m%d")

        sender_iban = BankingGenerator._generate_iban(l) if l != "US" else f"RT:{BankingGenerator.generate_routing_number()}"
        receiver_iban = BankingGenerator._generate_iban(l) if l != "US" else f"RT:{BankingGenerator.generate_routing_number()}"

        return {
            "ref": f"TRN{ref_date}-{random.randint(10000, 99999)}",
            "sender_iban": sender_iban,
            "receiver_iban": receiver_iban,
            "amount": amount,
            "currency": currency,
            "description": random.choice(TRANSACTION_DESCRIPTIONS.get(l, TRANSACTION_DESCRIPTIONS["TR"])),
            "channel": random.choice(PAYMENT_CHANNELS.get(l, PAYMENT_CHANNELS["TR"])),
            "timestamp": ts,
            "status": random.choices(["COMPLETED", "PENDING", "FAILED"], weights=[80, 15, 5])[0],
        }

    def generate(self, data_type, locale="TR", **kwargs):
        l = locale.upper()
        dt = data_type.lower()

        if dt in ("swift", "bic"):
            return self.generate_swift(l)
        if dt == "sort_code":
            return self.generate_sort_code()
        if dt == "routing_number":
            return self.generate_routing_number()
        if dt == "bik_code":
            return self.generate_bik()
        if dt == "transaction":
            return self.generate_transaction(l)
        if dt == "bank_name":
            return random.choice(BANK_NAMES.get(l, BANK_NAMES["TR"]))
        return None
