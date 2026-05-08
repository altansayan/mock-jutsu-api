"""
mock-jutsu — Advanced Financial Generator (Global Formats)
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)
"""

import random
import secrets
from mockjutsu.generators.name_data import NAME_POOLS

def _crc16_emvco(data: str) -> str:
    crc = 0xFFFF
    for char in data:
        crc ^= ord(char) << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc = crc << 1
            crc &= 0xFFFF
    return f"{crc:04X}"

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


def _iban_check_digits(prefix: str, body: str) -> str:
    """Compute ISO 13616 MOD-97 check digits (2-digit string)."""
    rearranged = body + prefix + "00"
    numeric = ''.join(str(ord(c) - 55) if c.isalpha() else c for c in rearranged)
    check = 98 - int(numeric) % 97
    return f"{check:02d}"


class FinancialGenerator:
    """Financial data with global banking format awareness."""

    @staticmethod
    def _luhn_complete(prefix_digits, total_length):
        """Build a Luhn-valid card number from a prefix."""
        partial = prefix_digits + [random.randrange(10) for _ in range(total_length - len(prefix_digits) - 1)]
        total = 0
        for i, d in enumerate(reversed(partial)):
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
            body_len = fmt["len"] - len(fmt["prefix"]) - 2
            body = "".join(str(random.randrange(10)) for _ in range(body_len))
            check = _iban_check_digits(fmt["prefix"], body)
            return f"{fmt['prefix']}{check}{body}"
        if fmt["type"] == "ROUTING":
            r = _generate_aba_routing()
            a = "".join(str(random.randrange(10)) for _ in range(12))
            return f"RT:{r} ACC:{a}"
        if fmt["type"] == "BIK":
            bik = "04" + "".join(str(random.randrange(10)) for _ in range(7))
            acc = "40817" + "".join(str(random.randrange(10)) for _ in range(15))
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
            return f"{random.randrange(900) + 100}"

        if dt == 'cvv4':
            return f"{random.randrange(9000) + 1000}"

        if dt == 'pin':
            return f"{random.randrange(9000) + 1000}"

        if dt == 'expirymonth':
            return f"{random.randrange(12) + 1:02d}"

        if dt == 'expiryyear':
            return f"{random.randrange(6) + 25}"

        if dt == 'expiry':
            return f"{random.randrange(12) + 1:02d}/{random.randrange(6) + 25}"

        if dt == 'issuer':
            return random.choice(ISSUERS.get(l, ISSUERS['TR']))

        if dt == 'balance':
            mn = float(kwargs.get('min', 10))
            mx = float(kwargs.get('max', 50000))
            return round(mn + (mx - mn) * random.randrange(10 ** 8) / 10 ** 8, 2)

        if dt == 'credit_score':
            return random.randrange(551) + 300  # FICO: 300–850

        if dt in ('iban', 'bankaccount'):
            return self.generate_bank_account(locale)

        if dt == 'sepa_qr':
            return self._generate_sepa_qr(locale)
            
        if dt == 'tr_karekod':
            return self._generate_tr_karekod()

        return "FINANCIAL_DATA"

    def _generate_sepa_qr(self, locale: str) -> str:
        loc = locale if locale in NAME_POOLS else 'DE'
        names = NAME_POOLS[loc]
        first_name = random.choice(names[random.choice(['male', 'female'])])
        name = f"{first_name} {random.choice(names['last'])}"
        
        iban = self.generate_bank_account(loc)
        bic = f"{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') * 4}{loc}22"
        amount = f"{random.randrange(10, 1000)}.{random.choice(['00', '50'])}"
        reference = f"INV-2025-{random.randrange(1000,9999)}"
        
        return f"BCD\n002\n1\nSCT\n{bic}\n{name}\n{iban}\nEUR{amount}\n\n{reference}\n\n"

    def _generate_tr_karekod(self) -> str:
        names = NAME_POOLS['TR']
        first_name = random.choice(names[random.choice(['male', 'female'])])
        name = f"{first_name} {random.choice(names['last'])}"
        iban = self.generate_bank_account('TR')
        amount = f"{random.randrange(10, 5000)}.{random.choice(['00', '50'])}"
        
        p00 = "000201"
        p01 = "010211"
        p53 = "5303949"
        p54 = f"54{len(amount):02d}{amount}"
        p58 = "5802TR"
        p59 = f"59{len(name):02d}{name}"
        
        merch_info = f"01{len(iban):02d}{iban}"
        p26 = f"26{len(merch_info):02d}{merch_info}"
        
        payload = f"{p00}{p01}{p26}{p53}{p54}{p58}{p59}6304"
        crc = _crc16_emvco(payload)
        
        return payload + crc


def _generate_aba_routing():
    """ABA routing number — MOD-10 checksum: 3*(d0+d3+d6) + 7*(d1+d4+d7) + (d2+d5+d8) ≡ 0 (mod 10)."""
    districts = [
        "01","02","03","04","05","06","07","08","09","10","11","12",
        "21","22","23","24","25","26","27","28","29","30","31","32",
        "61","62","63","64","65","66","67","68","69","70","71","72","80",
    ]
    d_str = random.choice(districts)
    d = [int(d_str[0]), int(d_str[1])] + [random.randrange(10) for _ in range(6)]
    total = 3 * (d[0] + d[3] + d[6]) + 7 * (d[1] + d[4] + d[7]) + (d[2] + d[5])
    check = (10 - total % 10) % 10
    d.append(check)
    return "".join(map(str, d))
