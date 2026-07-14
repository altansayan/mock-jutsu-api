"""
mock-jutsu — Advanced Financial Generator (Global Formats)
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)
"""

import random
import secrets
from datetime import datetime
from mockjutsu.generators.name_data import NAME_POOLS
from mockjutsu.algorithms import iban_check_digits

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

_CREDIT_SCORE_MODELS = ['FICO', 'VantageScore', 'TransUnion', 'Equifax', 'Experian']
_CREDIT_SCORE_TIERS  = ['Exceptional', 'Very Good', 'Good', 'Fair', 'Poor']
_LOAN_TYPES          = ['Personal', 'Mortgage', 'Auto', 'Student', 'Business', 'Home Equity', 'Payday']
_CLAIM_STATUSES      = ['Submitted', 'Under Review', 'Approved', 'Denied', 'Paid', 'Closed', 'Appealed']
_MORTGAGE_TERMS      = [10, 15, 20, 25, 30]

# bban_fmt: list of ('alpha'|'digit'|'alnum', length) segments (BBAN without check digits)
BANK_FORMATS = {
    "TR": {"type": "IBAN", "prefix": "TR", "len": 26, "bban_fmt": [("digit", 22)]},
    # UK/GB: 4-letter bank code + 6-digit sort code + 8-digit account = 18 chars
    "UK": {"type": "IBAN", "prefix": "GB", "len": 22, "bban_fmt": [("alpha", 4), ("digit", 14)]},
    "DE": {"type": "IBAN", "prefix": "DE", "len": 22, "bban_fmt": [("digit", 18)]},
    # FR: 5-digit bank + 5-digit branch + 11-alnum account + 2-digit RIB key = 23 chars
    "FR": {"type": "IBAN", "prefix": "FR", "len": 27, "bban_fmt": [("digit", 10), ("alnum", 11), ("digit", 2)]},
    "US": {"type": "ROUTING", "len": 9},
    "RU": {"type": "BIK", "len": 9},
}



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

    _IBAN_ALNUM = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    def generate_bank_account(self, locale="TR"):
        l = locale.upper()
        fmt = BANK_FORMATS.get(l, BANK_FORMATS["TR"])
        if fmt["type"] == "IBAN":
            body_parts = []
            for kind, length in fmt.get("bban_fmt", [("digit", fmt["len"] - len(fmt["prefix"]) - 2)]):
                if kind == "digit":
                    body_parts.append("".join(str(random.randrange(10)) for _ in range(length)))
                elif kind == "alpha":
                    body_parts.append("".join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(length)))
                else:
                    body_parts.append("".join(random.choice(self._IBAN_ALNUM) for _ in range(length)))
            body  = "".join(body_parts)
            check = iban_check_digits(fmt["prefix"], body)
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
            yy = datetime.now().year % 100
            return f"{random.randrange(6) + yy}"

        if dt == 'expiry':
            yy = datetime.now().year % 100
            return f"{random.randrange(12) + 1:02d}/{random.randrange(6) + yy}"

        if dt == 'issuer':
            return random.choice(ISSUERS.get(l, ISSUERS['TR']))

        if dt == 'balance':
            mn = float(kwargs.get('min', 10))
            mx = float(kwargs.get('max', 50000))
            return f"{mn + (mx - mn) * random.randrange(10 ** 8) / 10 ** 8:.2f}"

        if dt == 'credit_score':
            return random.randrange(551) + 300  # FICO: 300–850

        if dt in ('iban', 'bankaccount'):
            return self.generate_bank_account(locale)

        if dt == 'sepa_qr':
            return self._generate_sepa_qr(locale)
            
        if dt == 'emv_qr_p2p':
            return self._generate_emv_qr_p2p(locale)
            
        if dt == 'emv_qr_atm':
            return self._generate_emv_qr_atm(locale)
            
        if dt == 'emv_qr_pos':
            return self._generate_emv_qr_pos(locale)

        if dt == '3ds_cavv':
            return self.generate_3ds_cavv()

        if dt == '3ds_eci':
            return self.generate_3ds_eci(network)

        if dt == 'credit_score_model':
            return random.choice(_CREDIT_SCORE_MODELS)

        if dt == 'credit_score_tier':
            return random.choice(_CREDIT_SCORE_TIERS)

        if dt == 'credit_limit':
            # Tier distribution: low 500–5k, normal 5k–30k, high 30k–100k
            tier = random.randrange(10)
            if tier <= 3:
                v = 500 + random.randrange(4501)
            elif tier <= 8:
                v = 5000 + random.randrange(25001)
            else:
                v = 30000 + random.randrange(70001)
            return f"{v:.2f}"

        if dt == 'credit_utilization':
            # Weighted toward realistic 0–80% range
            v = round(random.randrange(10001) / 100, 2)  # 0.00–100.00
            return f"{v:.2f}"

        if dt == 'credit_card_issuer_name':
            return random.choice(ISSUERS.get(l, ISSUERS['TR']))

        if dt == 'apr':
            # Realistic APR: 3.99–29.99% for consumer credit
            v = round(3.99 + random.randrange(2601) / 100, 2)
            return f"{v:.2f}"

        if dt == 'loan_type':
            return random.choice(_LOAN_TYPES)

        if dt == 'mortgage_rate':
            # Realistic mortgage rate: 1.50–12.00%
            v = round(1.50 + random.randrange(1051) / 100, 2)
            return f"{v:.2f}"

        if dt == 'mortgage_term':
            return str(random.choice(_MORTGAGE_TERMS))

        if dt == 'premium_amount':
            # Monthly insurance premium: $25–$2,500
            v = round(25 + random.randrange(247601) / 100, 2)
            return f"{v:.2f}"

        if dt == 'deductible':
            # Insurance deductible: $100–$10,000 in round steps
            steps = [100, 250, 500, 750, 1000, 1500, 2000, 2500, 3000, 5000, 7500, 10000]
            v = random.choice(steps)
            return f"{v:.2f}"

        if dt == 'coverage_limit':
            # Coverage limits: $10k–$5M in realistic tiers
            tiers = [10000, 25000, 50000, 100000, 250000, 500000, 1000000, 2000000, 5000000]
            v = random.choice(tiers)
            return f"{v:.2f}"

        if dt == 'claim_status':
            return random.choice(_CLAIM_STATUSES)

        if dt == 'credit_limit_masked':
            # GLBA §501: exact credit limit is NPI — show order of magnitude only
            return '$**,***'

        if dt == 'mortgage_rate_masked':
            # GLBA §501: exact mortgage rate is NPI — mask both integer and decimal parts
            return '**.**%'

        if dt == 'premium_amount_masked':
            # GLBA §501: exact premium is NPI — show currency symbol only
            return '$*,***'

        return "FINANCIAL_DATA"

    def generate_3ds_cavv(self):
        # MOCK LIMITATION: random 20 bytes encoded as base64. A real CAVV is a
        # cryptogram generated by the ACS (Access Control Server) using issuer keys
        # and the transaction's authentication data. Will NOT pass 3DS ARQC/CAVV
        # verification in any real payment authorization flow.
        import secrets
        import base64
        raw = secrets.token_bytes(20)
        return base64.b64encode(raw).decode('utf-8')

    def generate_3ds_eci(self, network="visa"):
        net = network.lower()
        if 'visa' in net or 'amex' in net or 'jcb' in net:
            return random.choice(['05', '06', '07'])
        if 'mc' in net or 'mastercard' in net:
            return random.choice(['02', '01', '00'])
        return random.choice(['05', '02', '06', '01'])

    _CURRENCY_CODES = {
        'TR': '949',
        'DE': '978',
        'FR': '978',
        'US': '840',
        'UK': '826',
        'RU': '643'
    }

    # ISO 3166-1 alpha-2 mapping for EMVCo country code field
    _EMV_COUNTRY_CODE = {
        'TR': 'TR', 'DE': 'DE', 'FR': 'FR', 'US': 'US', 'UK': 'GB', 'RU': 'RU',
    }
    # SEPA-zone locales only (EPC QR code is SEPA-specific)
    _SEPA_LOCALE_FALLBACK = {
        'DE': 'DE', 'FR': 'FR', 'UK': 'UK',
        'TR': 'DE', 'US': 'DE', 'RU': 'FR',  # non-SEPA → fallback to SEPA locale
    }

    def _get_emv_locale_data(self, locale: str):
        loc = locale if locale in self._CURRENCY_CODES else 'TR'
        currency = self._CURRENCY_CODES[loc]
        country_code = self._EMV_COUNTRY_CODE.get(loc, loc)
        return loc, currency, country_code

    def _generate_sepa_qr(self, locale: str) -> str:
        # SEPA QR (EPC QR Code Guideline v2.1) only valid for SEPA-zone IBANs
        sepa_loc = self._SEPA_LOCALE_FALLBACK.get(locale, 'DE')
        names = NAME_POOLS.get(sepa_loc, NAME_POOLS['DE'])
        first_name = random.choice(names[random.choice(['male', 'female'])])
        name = f"{first_name} {random.choice(names['last'])}"

        iban = self.generate_bank_account(sepa_loc)
        bic_cc = {'DE': 'DE', 'FR': 'FR', 'UK': 'GB'}.get(sepa_loc, 'DE')
        bic = f"{''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(4))}{bic_cc}2X"
        amount = f"{random.randrange(10, 1000)}.{random.choice(['00', '50'])}"
        reference = f"INV-{datetime.now().year}-{random.randrange(1000,9999)}"

        return f"BCD\n002\n1\nSCT\n{bic}\n{name}\n{iban}\nEUR{amount}\n\n{reference}\n\n"

    def _generate_emv_qr_p2p(self, locale: str) -> str:
        loc, currency, country_code = self._get_emv_locale_data(locale)
        names = NAME_POOLS.get(loc, NAME_POOLS['TR'])
        first_name = random.choice(names[random.choice(['male', 'female'])])
        name = f"{first_name} {random.choice(names['last'])}"
        iban = self.generate_bank_account(loc)
        amount = f"{random.randrange(10, 5000)}.{random.choice(['00', '50'])}"

        p00 = "000201"
        p01 = "010211"
        p53 = f"5303{currency}"
        p54 = f"54{len(amount):02d}{amount}"
        p58 = f"5802{country_code}"
        p59 = f"59{len(name):02d}{name}"
        
        merch_info = f"01{len(iban):02d}{iban}"
        p26 = f"26{len(merch_info):02d}{merch_info}"
        
        payload = f"{p00}{p01}{p26}{p53}{p54}{p58}{p59}6304"
        crc = _crc16_emvco(payload)
        
        return payload + crc

    def _generate_emv_qr_atm(self, locale: str) -> str:
        loc, currency, country_code = self._get_emv_locale_data(locale)

        p00 = "000201"
        p01 = "010212"
        p53 = f"5303{currency}"
        p58 = f"5802{country_code}"
        
        atm_name = f"ATM {loc}-{random.randrange(1000, 9999)}"
        p59 = f"59{len(atm_name):02d}{atm_name}"
        
        # Terminal ID and Session Token in Tag 62
        tid = f"T{random.randrange(1000000, 9999999)}"
        token = f"TOK{random.randrange(10000000, 99999999)}"
        
        tag62_07 = f"07{len(tid):02d}{tid}"
        tag62_08 = f"08{len(token):02d}{token}"
        tag62_val = f"{tag62_07}{tag62_08}"
        p62 = f"62{len(tag62_val):02d}{tag62_val}"
        
        payload = f"{p00}{p01}{p53}{p58}{p59}{p62}6304"
        crc = _crc16_emvco(payload)
        
        return payload + crc

    def _generate_emv_qr_pos(self, locale: str) -> str:
        loc, currency, country_code = self._get_emv_locale_data(locale)

        p00 = "000201"
        p01 = "010211"

        mcc = f"{random.randrange(5000, 5999)}"
        p52 = f"5204{mcc}"

        p53 = f"5303{currency}"

        amount = f"{random.randrange(10, 1000)}.{random.choice(['00', '25', '50', '75'])}"
        p54 = f"54{len(amount):02d}{amount}"

        p58 = f"5802{country_code}"
        
        names = NAME_POOLS.get(loc, NAME_POOLS['TR'])
        company_suffix = "A.S." if loc == 'TR' else ("GmbH" if loc == 'DE' else ("LLC" if loc == 'US' else "LTD"))
        merch_name = f"{random.choice(names['last']).upper()} {company_suffix}"
        p59 = f"59{len(merch_name):02d}{merch_name}"
        
        cities = {'TR': 'ISTANBUL', 'DE': 'BERLIN', 'FR': 'PARIS', 'US': 'NEW YORK', 'UK': 'LONDON', 'RU': 'MOSCOW'}
        city = cities.get(loc, 'CAPITAL')
        p60 = f"60{len(city):02d}{city}"
        
        # tag 26 merchant identifier
        merch_id = f"{random.randrange(1000000000, 9999999999)}"
        tag26_01 = f"01{len(merch_id):02d}{merch_id}"
        p26 = f"26{len(tag26_01):02d}{tag26_01}"
        
        payload = f"{p00}{p01}{p26}{p52}{p53}{p54}{p58}{p59}{p60}6304"
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
