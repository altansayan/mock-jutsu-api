"""
mock-jutsu — Official Communication Generator (Regulatory & Combinatorial)
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)
"""

import random
import secrets

CITIES = {
    "TR": ["İstanbul", "Ankara", "İzmir", "Bursa", "Antalya", "Adana", "Konya", "Gaziantep"],
    "US": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "Dallas"],
    "UK": ["London", "Birmingham", "Manchester", "Leeds", "Glasgow", "Liverpool", "Bristol", "Sheffield"],
    "DE": ["Berlin", "Hamburg", "München", "Köln", "Frankfurt", "Stuttgart", "Düsseldorf", "Leipzig"],
    "FR": ["Paris", "Marseille", "Lyon", "Toulouse", "Nice", "Nantes", "Strasbourg", "Montpellier"],
    "RU": ["Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург", "Казань", "Нижний Новгород"],
}

STREETS = {
    "TR": ["Atatürk Caddesi", "İstiklal Caddesi", "Bağdat Caddesi", "Şair Nefi Sokak", "Nispetiye Caddesi",
           "Cumhuriyet Caddesi", "Halaskargazi Caddesi"],
    "US": ["Main Street", "Oak Avenue", "Maple Drive", "Broadway", "5th Avenue", "Park Lane",
           "Elm Street", "Cedar Road"],
    "UK": ["High Street", "Church Road", "Victoria Road", "Green Lane", "Station Road",
           "King Street", "Queen Street", "Mill Road"],
    "DE": ["Hauptstraße", "Bahnhofstraße", "Kirchenstraße", "Schillerstraße", "Goethestraße",
           "Friedrichstraße", "Wilhelmstraße"],
    "FR": ["Rue de la Paix", "Avenue des Champs-Élysées", "Boulevard Saint-Germain",
           "Rue Victor Hugo", "Rue de Rivoli", "Avenue Montaigne"],
    "RU": ["Улица Ленина", "Проспект Мира", "Улица Пушкина", "Невский проспект",
           "Тверская улица", "Арбат", "Садовая улица"],
}

PHONE_DATA = {
    "TR": {"prefix": "+90", "carriers": ["532", "533", "542", "544", "505", "506"]},
    "US": {"prefix": "+1",  "carriers": ["555", "212", "310", "415", "718", "312"]},
    # UK: 4-digit prefix → 6 trailing digits → 10 subscriber digits total after +44
    # 7700 omitted (reserved sub-ranges per Ofcom)
    "UK": {"prefix": "+44", "carriers": ["7911", "7800", "7712", "7490"]},
    "DE": {"prefix": "+49", "carriers": ["151", "160", "170", "171", "176"]},
    # FR: E.164 drops the trunk prefix 0, so "06"→"6", "07"→"7" (1 digit)
    # 1-digit prefix + 8 trailing digits = 9 subscriber digits after +33
    "FR": {"prefix": "+33", "carriers": ["6", "7"]},
    "RU": {"prefix": "+7",  "carriers": ["916", "999", "903", "917", "926"]},
}

PLATE_REGIONS = {
    "TR": [str(i).zfill(2) for i in range(1, 82)],
    "RU": ["77", "78", "99", "197", "199"],
    "DE": ["B", "M", "H", "HH", "S", "K"],
}

EMAIL_DOMAINS = {
    "TR": ["testposta.com.tr", "mock-mail.net.tr", "ornek-eposta.tr", "deneme-posta.org"],
    "US": ["testmail.us", "mockmail.net", "samplemail.org", "devtest-mail.io"],
    "UK": ["testmail.co.uk", "mockpost.org.uk", "samplemail.uk", "devmail.co.uk"],
    "DE": ["testmail.de", "mustermail.de", "beispiel-post.de", "probemail.org"],
    "FR": ["testmail.fr", "courrielfaux.fr", "exemple-mail.fr", "fakepost.org"],
    "RU": ["testmail.ru", "testovaya-pochta.ru", "primer-mail.ru", "fakepost.org"],
}

_UK_PLATE_LETTERS = "ABCEGHJKLMNOPRSTWXYZ"
_UK_PLATE_RAND    = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_RU_PLATE_CHARS   = "ABEKMHOPCTYX"
_US_PLATE_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_FR_PLATE_LETTERS = "ABCDEFGHJKLMNPQRSTUVWXYZ"
_DE_PLATE_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_TR_PLATE_LETTERS = "ABCDEFGHJKLMNPRSTUVYZ"


class CommunicationGenerator:
    """Regulatory-compliant Communication data for 6 locales."""

    def generate_plate(self, locale="TR"):
        l = locale.upper()
        if l == "TR":
            city    = random.choice(PLATE_REGIONS["TR"])
            letters = "".join(random.choice(_TR_PLATE_LETTERS) for _ in range(random.randrange(3) + 1))
            return f"{city} {letters} {random.randrange(9990) + 10}"
        if l == "UK":
            region = random.choice(_UK_PLATE_LETTERS) + random.choice(_UK_PLATE_LETTERS)
            age    = random.choice(["23", "73", "24", "74"])
            rand   = "".join(random.choice(_UK_PLATE_RAND) for _ in range(3))
            return f"{region}{age} {rand}"
        if l == "DE":
            city    = random.choice(PLATE_REGIONS["DE"])
            letters = "".join(random.choice(_DE_PLATE_LETTERS) for _ in range(random.randrange(2) + 1))
            return f"{city}-{letters} {random.randrange(9999) + 1}"
        if l == "FR":
            l1 = "".join(random.choice(_FR_PLATE_LETTERS) for _ in range(2))
            l2 = "".join(random.choice(_FR_PLATE_LETTERS) for _ in range(2))
            return f"{l1}-{random.randrange(900) + 100}-{l2}"
        if l == "RU":
            region = random.choice(PLATE_REGIONS["RU"])
            return f"{random.choice(_RU_PLATE_CHARS)}{random.randrange(900) + 100}{''.join(random.choice(_RU_PLATE_CHARS) for _ in range(2))} {region}"
        if l == "US":
            return f"{random.randrange(9) + 1}{''.join(random.choice(_US_PLATE_LETTERS) for _ in range(3))}{random.randrange(900) + 100}"
        return "PLATE-123"

    def generate_phone(self, locale="TR", atomic=None):
        l = locale.upper()
        data = PHONE_DATA.get(l, PHONE_DATA["TR"])
        prefix  = data["prefix"]
        carrier = random.choice(data["carriers"])
        # Trailing digit count per locale so that total subscriber digits are E.164-correct:
        # UK: 4-digit carrier + 6 = 10 | FR: 1-digit carrier + 8 = 9 | others: 3-digit + 7 = 10
        _local_len = {"UK": 6, "FR": 8}
        local_len = _local_len.get(l, 7)
        local   = "".join(str(random.randrange(10)) for _ in range(local_len))

        if atomic in ('country', 'country_code'):
            return prefix
        if atomic in ('area', 'area_code'):
            return carrier
        if atomic in ('local', 'local_number'):
            return local
        return f"{prefix}{carrier}{local}"

    def generate_postalcode(self, locale="TR"):
        l = locale.upper()
        if l == "TR":
            prefix = random.choice(["06", "16", "34", "35", "41", "42"])
            return f"{prefix}{random.randrange(900) + 100}"
        if l == "US":
            return f"{random.randrange(90000) + 10000}"
        if l == "UK":
            area    = random.choice(["SW", "EC", "WC", "SE", "E", "N", "NW", "W", "EC"])
            letters = "".join(random.choice("ABCDEFGHJKLMNPRSTUVWXY") for _ in range(2))
            return f"{area}{random.randrange(9) + 1} {random.randrange(9) + 1}{letters}"
        if l == "DE":
            return f"{random.randrange(90000) + 10000}"
        if l == "FR":
            # Valid FR range: 01000–97999
            return f"{random.randrange(97000) + 1000:05d}"
        if l == "RU":
            return f"{random.randrange(900000) + 100000}"
        return f"{random.randrange(90000) + 10000}"

    def generate_address(self, locale="TR", atomic=None):
        l = locale.upper()
        city   = random.choice(CITIES.get(l, CITIES["TR"]))
        street = random.choice(STREETS.get(l, STREETS["TR"]))
        no     = random.randrange(200) + 1

        if atomic == 'city':
            return city
        if atomic == 'street':
            return street
        if atomic == 'district':
            return city
        if atomic == 'neighborhood':
            return f"{city} {random.randrange(20) + 1}. Mahalle"
        return f"{city}, {street} No:{no}"

    def generate(self, data_type, locale="TR", **kwargs):
        dt = data_type.lower()

        if dt == 'plate':
            return self.generate_plate(locale)
        if dt == 'phone':
            return self.generate_phone(locale)
        if dt.startswith('phone_'):
            return self.generate_phone(locale, dt.replace('phone_', ''))
        if dt == 'postalcode':
            return self.generate_postalcode(locale)
        if dt == 'address_full':
            return self.generate_address(locale)
        if dt.startswith('address_'):
            return self.generate_address(locale, dt.replace('address_', ''))
        if dt == 'email':
            l      = locale.upper()
            domain = random.choice(EMAIL_DOMAINS.get(l, EMAIL_DOMAINS["TR"]))
            prefixes = ["user", "test", "mock", "dev", "demo", "sandbox", "ninja"]
            return f"{random.choice(prefixes)}{random.randrange(9900) + 100}@{domain}"

        return None
