"""
mock-jutsu — Official Communication Generator (Regulatory & Combinatorial)
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)
"""

import random

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
    "UK": {"prefix": "+44", "carriers": ["7911", "7700", "7800", "7712", "7490"]},
    "DE": {"prefix": "+49", "carriers": ["151", "160", "170", "171", "176"]},
    "FR": {"prefix": "+33", "carriers": ["06", "07"]},
    "RU": {"prefix": "+7",  "carriers": ["916", "999", "903", "917", "926"]},
}

PLATE_REGIONS = {
    "TR": [str(i).zfill(2) for i in range(1, 82)],
    "RU": ["77", "78", "99", "197", "199"],
    "DE": ["B", "M", "H", "HH", "S", "K"],
}

EMAIL_DOMAINS = {
    "TR": ["gmail.com", "hotmail.com", "yahoo.com", "outlook.com", "mynet.com"],
    "US": ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com"],
    "UK": ["gmail.com", "hotmail.co.uk", "yahoo.co.uk", "outlook.com", "btinternet.com"],
    "DE": ["gmail.com", "web.de", "gmx.de", "t-online.de", "outlook.de"],
    "FR": ["gmail.com", "laposte.net", "orange.fr", "free.fr", "outlook.fr"],
    "RU": ["gmail.com", "mail.ru", "yandex.ru", "rambler.ru", "inbox.ru"],
}


class CommunicationGenerator:
    """Regulatory-compliant Communication data for 6 locales."""

    def generate_plate(self, locale="TR"):
        l = locale.upper()
        if l == "TR":
            city = random.choice(PLATE_REGIONS["TR"])
            letters = "".join(random.choices("ABCDEFGHJKLMNPRSTUVYZ", k=random.randint(1, 3)))
            return f"{city} {letters} {random.randint(10, 9999)}"
        if l == "UK":
            region = random.choice("ABCEGHJKLMNOPRSTWXYZ") + random.choice("ABCDEFGHJKLMNOPRSTWXYZ")
            age = random.choice(["23", "73", "24", "74"])
            rand = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=3))
            return f"{region}{age} {rand}"
        if l == "DE":
            city = random.choice(PLATE_REGIONS["DE"])
            letters = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=random.randint(1, 2)))
            return f"{city}-{letters} {random.randint(1, 9999)}"
        if l == "FR":
            l1 = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ", k=2))
            l2 = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ", k=2))
            return f"{l1}-{random.randint(100, 999)}-{l2}"
        if l == "RU":
            chars = "ABEKMHOPCTYX"
            region = random.choice(PLATE_REGIONS["RU"])
            return f"{random.choice(chars)}{random.randint(100,999)}{''.join(random.choices(chars,k=2))} {region}"
        if l == "US":
            return f"{random.randint(1,9)}{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ',k=3))}{random.randint(100,999)}"
        return "PLATE-123"

    def generate_phone(self, locale="TR", atomic=None):
        l = locale.upper()
        data = PHONE_DATA.get(l, PHONE_DATA["TR"])
        prefix = data["prefix"]
        carrier = random.choice(data["carriers"])
        local_len = 8 if l == "FR" else 7
        local = "".join([str(random.randint(0, 9)) for _ in range(local_len)])

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
            return f"{prefix}{random.randint(100, 999)}"
        if l == "US":
            return f"{random.randint(10000, 99999)}"
        if l == "UK":
            area = random.choice(["SW", "EC", "WC", "SE", "E", "N", "NW", "W", "EC"])
            letters = "".join(random.choices("ABCDEFGHJKLMNPRSTUVWXY", k=2))
            return f"{area}{random.randint(1,9)} {random.randint(1,9)}{letters}"
        if l == "DE":
            return f"{random.randint(10000, 99999)}"
        if l == "FR":
            return f"{random.randint(75000, 97680):05d}"
        if l == "RU":
            return f"{random.randint(100000, 999999)}"
        return f"{random.randint(10000, 99999)}"

    def generate_address(self, locale="TR", atomic=None):
        l = locale.upper()
        city = random.choice(CITIES.get(l, CITIES["TR"]))
        street = random.choice(STREETS.get(l, STREETS["TR"]))
        no = random.randint(1, 200)

        if atomic == 'city':
            return city
        if atomic == 'street':
            return street
        if atomic == 'district':
            return city
        if atomic == 'neighborhood':
            return f"{city} {random.randint(1, 20)}. Mahalle"
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
            l = locale.upper()
            domain = random.choice(EMAIL_DOMAINS.get(l, EMAIL_DOMAINS["TR"]))
            prefixes = ["user", "test", "mock", "dev", "demo", "sandbox", "ninja"]
            return f"{random.choice(prefixes)}{random.randint(100, 9999)}@{domain}"

        return None
