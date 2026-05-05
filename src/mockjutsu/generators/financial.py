"""
mock-jutsu — Advanced Financial Generator (Global Formats)
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)
"""

import random

CARD_NETWORKS = {
    "visa":     {"prefixes": [["4"]], "length": 16},
    "mc":       {"prefixes": [["5","1"],["5","2"],["5","3"],["5","4"],["5","5"]], "length": 16},
    "amex":     {"prefixes": [["3","4"],["3","7"]], "length": 15},
    "troy":     {"prefixes": [["9","7","9","2"]], "length": 16},
    "jcb":      {"prefixes": [["3","5","2"],["3","5","8"]], "length": 16},
    "discover": {"prefixes": [["6","0","1","1"],["6","5"]], "length": 16},
    "unionpay": {"prefixes": [["6","2"]], "length": 16},
    "mir":      {"prefixes": [["2","2","0","0"],["2","2","0","1"],["2","2","0","2"]], "length": 16},
    "maestro":  {"prefixes": [["6","3","0","4"],["6","7","5","9"]], "length": 16},
}

ISSUERS = {
    "TR": ["Türkbank A.Ş.", "AnadoluFinans", "BosphorusBank", "GüvenFinans", "KırmızıBanka", "Boğaz Finans"],
    "US": ["First National Bank", "Pacific Trust", "American Commerce", "Liberty Bank", "Freedom Financial"],
    "UK": ["Royal Borough Bank", "Crown Finance Trust", "London Clearing Bank", "Imperial Trust", "Commonwealth Bank"],
    "DE": ["Volksbank Nord", "Hamburger Sparkasse", "Berliner Bank", "Rhine Finance", "Saxon Trust"],
    "FR": ["Crédit Parisien", "Banque Nationale", "Société de Crédit", "Paris Finance", "Loire Bank"],
    "RU": ["Народный Банк", "Столичный Банк", "Восточный Кредит", "Русфинанс", "МоскваБанк"],
}

BANK_FORMATS = {
    "TR": {"type": "IBAN", "prefix": "TR", "len": 26},
    "UK": {"type": "IBAN", "prefix": "GB", "len": 22},
    "DE": {"type": "IBAN", "prefix": "DE", "len": 22},
    "FR": {"type": "IBAN", "prefix": "FR", "len": 27},
    "US": {"type": "ROUTING", "len": 9},
    "RU": {"type": "BIK", "len": 9},
}


class FinancialGenerator:
    """Financial data with global banking format awareness."""

    @staticmethod
    def _luhn_complete(prefix_digits, total_length):
        """Build a Luhn-valid card number from a prefix."""
        partial = prefix_digits + [random.randint(0, 9) for _ in range(total_length - len(prefix_digits) - 1)]
        total = 0
        for i, d in enumerate(reversed(partial)):
            # check digit is at position 1 from right; partial[-1] is at position 2
            pos = i + 2
            n = d * 2 if pos % 2 == 0 else d
            if n > 9:
                n -= 9
            total += n
        partial.append((10 - total % 10) % 10)
        return "".join(map(str, partial))

    def generate_card_number(self, network="visa"):
        cfg = CARD_NETWORKS.get(network.lower(), CARD_NETWORKS["visa"])
        prefix = [int(d) for d in random.choice(cfg["prefixes"])]
        return self._luhn_complete(prefix, cfg["length"])

    def generate_bank_account(self, locale="TR"):
        l = locale.upper()
        fmt = BANK_FORMATS.get(l, BANK_FORMATS["TR"])
        if fmt["type"] == "IBAN":
            # prefix (2) + check digits (2) + body = total length
            body_len = fmt["len"] - len(fmt["prefix"]) - 2
            body = "".join([str(random.randint(0, 9)) for _ in range(body_len)])
            return f"{fmt['prefix']}{random.randint(10, 99):02d}{body}"
        if fmt["type"] == "ROUTING":
            r = "".join([str(random.randint(0, 9)) for _ in range(9)])
            a = "".join([str(random.randint(0, 9)) for _ in range(12)])
            return f"RT:{r} ACC:{a}"
        if fmt["type"] == "BIK":
            bik = "04" + "".join([str(random.randint(0, 9)) for _ in range(7)])
            acc = "40817" + "".join([str(random.randint(0, 9)) for _ in range(15)])
            return f"BIK:{bik} ACC:{acc}"
        return "ACC-123456789"

    def generate(self, data_type, locale="TR", **kwargs):
        l = locale.upper()
        dt = data_type.lower()
        network = str(kwargs.get('network', 'visa')).lower()

        if dt == 'cardnum':
            return self.generate_card_number(network)

        if dt == 'cardnetwork':
            return random.choice(list(CARD_NETWORKS.keys())).upper()

        if dt == 'cardtype':
            return random.choice(['Credit', 'Debit'])

        if dt == 'cardstatus':
            return random.choice(['Active', 'Blocked', 'Expired'])

        if dt == 'cardcategory':
            return random.choice(['Classic', 'Gold', 'Platinum', 'Business'])

        if dt == 'cvv3':
            return f"{random.randint(100, 999)}"

        if dt == 'cvv4':
            return f"{random.randint(1000, 9999)}"

        if dt == 'pin':
            return f"{random.randint(1000, 9999)}"

        if dt == 'expirymonth':
            return f"{random.randint(1, 12):02d}"

        if dt == 'expiryyear':
            return f"{random.randint(25, 30)}"

        if dt == 'expiry':
            return f"{random.randint(1, 12):02d}/{random.randint(25, 30)}"

        if dt == 'issuer':
            return random.choice(ISSUERS.get(l, ISSUERS['TR']))

        if dt == 'balance':
            mn = float(kwargs.get('min', 10))
            mx = float(kwargs.get('max', 50000))
            return round(random.uniform(mn, mx), 2)

        if dt in ('iban', 'bankaccount'):
            return self.generate_bank_account(locale)

        return "FINANCIAL_DATA"
