"""
mock-jutsu — Commerce Generator (Currency, Tax Rate, Invoice, VIN, Vehicle)
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)
"""

import secrets

CURRENCIES = {
    "TR": {"code": "TRY", "symbol": "₺", "name": "Türk Lirası",       "decimals": 2},
    "US": {"code": "USD", "symbol": "$", "name": "US Dollar",          "decimals": 2},
    "UK": {"code": "GBP", "symbol": "£", "name": "British Pound",      "decimals": 2},
    "DE": {"code": "EUR", "symbol": "€", "name": "Euro",               "decimals": 2},
    "FR": {"code": "EUR", "symbol": "€", "name": "Euro",               "decimals": 2},
    "RU": {"code": "RUB", "symbol": "₽", "name": "Российский рубль",   "decimals": 2},
}

TAX_RATES = {
    "TR": {"name": "KDV",    "standard": 20, "reduced": 10,   "super_reduced": 1},
    "US": {"name": "Sales Tax", "standard": None, "note": "State-based (0%–10.25%)"},
    "UK": {"name": "VAT",    "standard": 20, "reduced": 5,    "zero": 0},
    "DE": {"name": "MwSt",   "standard": 19, "reduced": 7},
    "FR": {"name": "TVA",    "standard": 20, "reduced": 10,   "super_reduced": 5.5},
    "RU": {"name": "НДС",    "standard": 20, "reduced": 10,   "zero": 0},
}

INVOICE_PREFIXES = {
    "TR": "INV", "US": "INV", "UK": "INV", "DE": "RE", "FR": "FACT", "RU": "СФ",
}

INVOICE_FORMATS = {
    "TR": "{p}-{y}-{n:06d}",
    "US": "{p}-{y}{m:02d}{d:02d}-{n:04d}",
    "UK": "{p}/{y}/{n:06d}",
    "DE": "{p}-{y}/{n:05d}",
    "FR": "{p}-{y}-{n:06d}",
    "RU": "{p}-{y}-{n:06d}",
}

# VIN transliteration table (ISO 3779) — I, O, Q not used
VIN_TRANS = {
    'A':1,'B':2,'C':3,'D':4,'E':5,'F':6,'G':7,'H':8,
    'J':1,'K':2,'L':3,'M':4,'N':5,'P':7,'R':9,
    'S':2,'T':3,'U':4,'V':5,'W':6,'X':7,'Y':8,'Z':9,
}
VIN_WEIGHTS  = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2]
VIN_CHARS    = "0123456789ABCDEFGHJKLMNPRSTUVWXYZ"

# World Manufacturer Identifiers (WMI) — public ISO 3780 database
WMI_CODES = {
    "TR": ["NM0", "NM1", "NMT"],
    "US": ["1HG", "1G1", "4T1", "1FA", "1GC", "5YJ"],
    "UK": ["SAL", "SAJ", "SAR", "SCA"],
    "DE": ["WBA", "WDB", "WVW", "WAU", "WP0"],
    "FR": ["VF1", "VF3", "VF7", "VFA"],
    "RU": ["XTA", "XUF", "X9F", "XWB"],
}

MODEL_YEAR_CHARS = "ABCDEFGHJKLMNPRSTVWXY123456789"

VEHICLES = {
    "TR": {
        "makes": ["Renault", "Fiat", "Ford", "Volkswagen", "Toyota", "Hyundai", "Honda", "Peugeot"],
        "models": {
            "Renault": ["Clio", "Megane", "Symbol", "Kadjar", "Captur"],
            "Fiat": ["Egea", "Doblò", "Fiorino"],
            "Ford": ["Focus", "Fiesta", "Kuga", "Puma"],
            "Volkswagen": ["Passat", "Golf", "Polo", "Tiguan"],
            "Toyota": ["Corolla", "Yaris", "RAV4", "C-HR"],
            "Hyundai": ["i20", "Tucson", "i10", "Kona"],
            "Honda": ["Civic", "CR-V", "Jazz"],
            "Peugeot": ["208", "2008", "308", "3008"],
        },
        "colors": ["Beyaz", "Siyah", "Gri", "Gümüş", "Kırmızı", "Mavi", "Lacivert", "Bej"],
        "fuel": ["Benzin", "Dizel", "Hibrit", "Elektrik", "LPG"],
    },
    "US": {
        "makes": ["Ford", "Chevrolet", "Toyota", "Honda", "Tesla", "GMC", "Ram", "Dodge"],
        "models": {
            "Ford": ["F-150", "Explorer", "Mustang", "Escape"],
            "Chevrolet": ["Silverado", "Equinox", "Malibu", "Tahoe"],
            "Toyota": ["Camry", "RAV4", "Corolla", "Highlander"],
            "Honda": ["Accord", "Civic", "CR-V", "Pilot"],
            "Tesla": ["Model 3", "Model Y", "Model S", "Model X"],
            "GMC": ["Sierra", "Terrain", "Acadia"],
            "Ram": ["1500", "2500", "ProMaster"],
            "Dodge": ["Charger", "Challenger", "Durango"],
        },
        "colors": ["White", "Black", "Silver", "Gray", "Red", "Blue", "Navy", "Pearl"],
        "fuel": ["Gasoline", "Diesel", "Hybrid", "Electric", "Flex Fuel"],
    },
    "UK": {
        "makes": ["Vauxhall", "Ford", "Volkswagen", "BMW", "Audi", "Land Rover", "Jaguar", "Mini"],
        "models": {
            "Vauxhall": ["Corsa", "Astra", "Mokka", "Insignia"],
            "Ford": ["Fiesta", "Focus", "Kuga", "Puma"],
            "BMW": ["3 Series", "5 Series", "X3", "X5"],
            "Audi": ["A3", "A4", "Q3", "Q5"],
            "Land Rover": ["Defender", "Discovery", "Range Rover", "Freelander"],
            "Volkswagen": ["Polo", "Golf", "Tiguan", "Passat"],
            "Jaguar": ["XE", "XF", "E-Pace", "F-Pace"],
            "Mini": ["Hatch", "Countryman", "Clubman"],
        },
        "colors": ["White", "Black", "Silver", "Grey", "Red", "Blue", "Green", "Bronze"],
        "fuel": ["Petrol", "Diesel", "Hybrid", "Electric", "Mild Hybrid"],
    },
    "DE": {
        "makes": ["Volkswagen", "BMW", "Mercedes-Benz", "Audi", "Opel", "Ford", "Porsche", "Skoda"],
        "models": {
            "Volkswagen": ["Golf", "Polo", "Passat", "Tiguan", "T-Roc"],
            "BMW": ["3er", "5er", "X3", "1er", "X5"],
            "Mercedes-Benz": ["C-Klasse", "E-Klasse", "GLC", "A-Klasse", "GLE"],
            "Audi": ["A4", "A3", "Q5", "Q3", "A6"],
            "Opel": ["Corsa", "Astra", "Mokka", "Insignia"],
            "Ford": ["Focus", "Fiesta", "Kuga", "Puma"],
            "Porsche": ["911", "Cayenne", "Macan", "Panamera"],
            "Skoda": ["Octavia", "Fabia", "Kodiaq", "Karoq"],
        },
        "colors": ["Weiß", "Schwarz", "Silber", "Grau", "Rot", "Blau", "Beige", "Grün"],
        "fuel": ["Benzin", "Diesel", "Hybrid", "Elektro", "Erdgas"],
    },
    "FR": {
        "makes": ["Renault", "Peugeot", "Citroën", "Volkswagen", "Toyota", "Ford", "BMW", "Dacia"],
        "models": {
            "Renault": ["Clio", "Mégane", "Kadjar", "Captur", "Zoé"],
            "Peugeot": ["208", "2008", "308", "3008", "5008"],
            "Citroën": ["C3", "C4", "C5 Aircross", "Berlingo"],
            "Volkswagen": ["Golf", "Polo", "Tiguan", "Passat"],
            "Toyota": ["Yaris", "Corolla", "RAV4", "C-HR"],
            "BMW": ["Série 3", "Série 5", "X3", "X1"],
            "Dacia": ["Sandero", "Duster", "Logan", "Spring"],
            "Ford": ["Fiesta", "Focus", "Puma", "Kuga"],
        },
        "colors": ["Blanc", "Noir", "Gris", "Argent", "Rouge", "Bleu", "Marine", "Beige"],
        "fuel": ["Essence", "Diesel", "Hybride", "Électrique", "GPL"],
    },
    "RU": {
        "makes": ["АвтоВАЗ", "Toyota", "Hyundai", "Kia", "Volkswagen", "УАЗ", "GAZ", "Skoda"],
        "models": {
            "АвтоВАЗ": ["Гранта", "Веста", "XRAY", "Нива Тревел"],
            "Toyota": ["Camry", "RAV4", "Land Cruiser", "Corolla"],
            "Hyundai": ["Solaris", "Creta", "Tucson", "Sonata"],
            "Kia": ["Rio", "Sportage", "Ceed", "K5"],
            "Volkswagen": ["Polo", "Tiguan", "Passat", "Golf"],
            "УАЗ": ["Патриот", "Hunter", "Буханка"],
            "GAZ": ["Газель Next", "Газель Бизнес"],
            "Skoda": ["Octavia", "Rapid", "Kodiaq", "Karoq"],
        },
        "colors": ["Белый", "Чёрный", "Серебристый", "Серый", "Красный", "Синий", "Золотой", "Зелёный"],
        "fuel": ["Бензин", "Дизель", "Гибрид", "Электро", "Газ"],
    },
}


class CommerceGenerator:
    """E-commerce and commerce data for 6 locales."""

    @staticmethod
    def generate_currency(locale="TR"):
        return CURRENCIES.get(locale.upper(), CURRENCIES["TR"])

    @staticmethod
    def generate_tax_rate(locale="TR"):
        return TAX_RATES.get(locale.upper(), TAX_RATES["TR"])

    @staticmethod
    def generate_invoice_number(locale="TR"):
        from datetime import date
        l = locale.upper()
        today = date.today()
        prefix = INVOICE_PREFIXES.get(l, "INV")
        fmt = INVOICE_FORMATS.get(l, "{p}-{y}-{n:06d}")
        return fmt.format(
            p=prefix, y=today.year, m=today.month,
            d=today.day, n=secrets.randbelow(999999) + 1
        )

    @staticmethod
    def generate_vin(locale="TR"):
        """ISO 3779 VIN — 17 chars with check digit at position 9."""
        l = locale.upper()
        wmi = secrets.choice(WMI_CODES.get(l, WMI_CODES["TR"]))
        vds_4_8 = "".join(secrets.choice(VIN_CHARS) for _ in range(5))
        model_year = secrets.choice(MODEL_YEAR_CHARS)
        plant = secrets.choice(VIN_CHARS)
        seq = f"{secrets.randbelow(900000) + 100000}"

        # Build without check (position 9 = index 8, set to '0')
        partial = list(wmi + vds_4_8 + "0" + model_year + plant + seq)

        total = 0
        for i, c in enumerate(partial):
            val = int(c) if c.isdigit() else VIN_TRANS.get(c, 0)
            total += val * VIN_WEIGHTS[i]

        check = total % 11
        partial[8] = "X" if check == 10 else str(check)
        return "".join(partial)

    @staticmethod
    def generate_vehicle(locale="TR"):
        l = locale.upper()
        data = VEHICLES.get(l, VEHICLES["TR"])
        make = secrets.choice(data["makes"])
        model = secrets.choice(data["models"].get(make, [make]))
        year = secrets.randbelow(27) + 2000  # 2000–2026
        return {
            "make":  make,
            "model": model,
            "year":  year,
            "vin":   CommerceGenerator.generate_vin(l),
            "color": secrets.choice(data["colors"]),
            "fuel":  secrets.choice(data["fuel"]),
        }

    def generate(self, data_type, locale="TR", **kwargs):
        l  = locale.upper()
        dt = data_type.lower().replace("_", "")

        if dt == "currency":
            return self.generate_currency(l)
        if dt == "taxrate":
            return self.generate_tax_rate(l)
        if dt == "invoicenumber":
            return self.generate_invoice_number(l)
        if dt == "vin":
            return self.generate_vin(l)
        if dt == "vehicle":
            return self.generate_vehicle(l)
        return None
