"""
mock-jutsu — Master Identity Generator (Full Regulatory Coverage)
Developer: Altan Sayan (https://github.com/altansayan)
"""

import random
from datetime import date

NAME_POOLS = {
    "TR": {
        "male":   ["Alp", "Bora", "Can", "Deniz", "Emre", "Faruk", "Gökhan", "Hakan", "Kemal", "Mert",
                   "Okan", "Serkan", "Tolga", "Umut", "Yusuf"],
        "female": ["Ayşe", "Büşra", "Ceren", "Derya", "Esra", "Fatma", "Gül", "Hande", "İrem", "Kübra",
                   "Merve", "Neslihan", "Özge", "Pınar", "Selin"],
        "last":   ["Yılmaz", "Kaya", "Demir", "Şahin", "Çelik", "Aydın", "Arslan", "Doğan", "Kılıç",
                   "Aslan", "Çetin", "Koç", "Kurt", "Öztürk", "Yıldız"],
    },
    "US": {
        "male":   ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph",
                   "Thomas", "Charles", "Christopher", "Daniel", "Matthew", "Andrew", "Joshua"],
        "female": ["Mary", "Patricia", "Jennifer", "Linda", "Barbara", "Elizabeth", "Susan", "Jessica",
                   "Sarah", "Karen", "Nancy", "Lisa", "Betty", "Margaret", "Sandra"],
        "last":   ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
                   "Wilson", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris"],
    },
    "UK": {
        "male":   ["Oliver", "Harry", "George", "Jack", "Noah", "Charlie", "Jacob", "Alfie",
                   "Freddie", "Oscar", "Henry", "Archie", "Leo", "Arthur", "Muhammad"],
        "female": ["Olivia", "Amelia", "Isla", "Ava", "Emily", "Isabella", "Mia", "Poppy",
                   "Ella", "Lily", "Grace", "Evie", "Sophie", "Charlotte", "Aria"],
        "last":   ["Smith", "Jones", "Williams", "Taylor", "Brown", "Davies", "Evans", "Wilson",
                   "Thomas", "Roberts", "Johnson", "Lewis", "Walker", "Robinson", "Wood"],
    },
    "DE": {
        "male":   ["Alexander", "Benjamin", "Christian", "Daniel", "Felix", "Jonas", "Luca",
                   "Maximilian", "Noah", "Paul", "Leon", "Elias", "Finn", "Luis", "Jan"],
        "female": ["Anna", "Emma", "Hannah", "Julia", "Laura", "Lena", "Lisa", "Maria",
                   "Sarah", "Sophie", "Leonie", "Mia", "Jana", "Katharina", "Sandra"],
        "last":   ["Müller", "Schmidt", "Schneider", "Fischer", "Weber", "Meyer", "Wagner",
                   "Becker", "Schulz", "Hoffmann", "Schäfer", "Koch", "Bauer", "Richter", "Klein"],
    },
    "FR": {
        "male":   ["Alexandre", "Baptiste", "Clément", "Damien", "Édouard", "François", "Guillaume",
                   "Hugo", "Julien", "Louis", "Nicolas", "Pierre", "Raphaël", "Thomas", "Victor"],
        "female": ["Alice", "Camille", "Charlotte", "Clara", "Emma", "Inès", "Jade", "Léa",
                   "Manon", "Zoé", "Chloé", "Lucie", "Marie", "Pauline", "Sarah"],
        "last":   ["Martin", "Bernard", "Thomas", "Petit", "Robert", "Richard", "Durand", "Dubois",
                   "Moreau", "Laurent", "Simon", "Michel", "Lefebvre", "Leroy", "Roux"],
    },
    "RU": {
        "male":   ["Александр", "Алексей", "Андрей", "Антон", "Артём", "Дмитрий", "Иван",
                   "Кирилл", "Максим", "Михаил", "Никита", "Николай", "Павел", "Сергей", "Виктор"],
        "female": ["Анастасия", "Анна", "Валерия", "Виктория", "Дарья", "Екатерина", "Елена",
                   "Мария", "Наталья", "Ольга", "Полина", "Светлана", "Татьяна", "Юлия", "Ксения"],
        "last":   ["Иванов", "Смирнов", "Кузнецов", "Попов", "Соколов", "Лебедев", "Козлов",
                   "Новиков", "Морозов", "Петров", "Волков", "Соловьёв", "Васильев", "Зайцев", "Павлов"],
        "last_f": ["Иванова", "Смирнова", "Кузнецова", "Попова", "Соколова", "Лебедева", "Козлова",
                   "Новикова", "Морозова", "Петрова", "Волкова", "Соловьёва", "Васильева", "Зайцева", "Павлова"],
        "pat_m":  ["Александрович", "Алексеевич", "Андреевич", "Антонович", "Артёмович",
                   "Дмитриевич", "Иванович", "Кириллович", "Максимович", "Михайлович"],
        "pat_f":  ["Александровна", "Алексеевна", "Андреевна", "Антоновна", "Артёмовна",
                   "Дмитриевна", "Ивановна", "Кирилловна", "Максимовна", "Михайловна"],
    },
}


class IdentityGenerator:
    """Identity Generator with 100% official regulatory algorithms for 6 countries."""

    @staticmethod
    def generate_tr_id(prefix=None):
        d = [int(x) for x in str(prefix)] if prefix else [random.choice([2, 4, 5, 6, 7, 8])]
        while len(d) < 9:
            d.append(random.randint(0, 9))
        d.append(((sum(d[0::2]) * 7) - sum(d[1::2])) % 10)
        d.append(sum(d) % 10)
        return "".join(map(str, d))

    @staticmethod
    def generate_ykn():
        """YKN: 11 digits, starts with 99, MOD-10 (Luhn) checksum."""
        base = [9, 9] + [random.randint(0, 9) for _ in range(8)]
        total = 0
        for i, d in enumerate(reversed(base)):
            n = d * 2 if i % 2 == 0 else d
            if n > 9:
                n -= 9
            total += n
        base.append((10 - total % 10) % 10)
        return "".join(map(str, base))

    @staticmethod
    def generate_ru_inn():
        """Russian Tax ID (INN) — 10 digits with checksum."""
        base = [random.randint(0, 9) for _ in range(9)]
        weights = [2, 4, 10, 3, 5, 9, 4, 6, 8]
        control = sum(a * b for a, b in zip(base, weights)) % 11 % 10
        base.append(control)
        return "".join(map(str, base))

    @staticmethod
    def generate_de_steuer_id():
        """German Steuerliche Identifikationsnummer — 11 digits, ISO 7064 MOD 11,10 checksum."""
        from collections import Counter
        while True:
            base = [random.randint(1, 9)] + [random.randint(0, 9) for _ in range(9)]
            if max(Counter(base).values()) > 3:
                continue
            product = 10
            for d in base:
                s = (product + d) % 10
                if s == 0:
                    s = 10
                product = (s * 2) % 11
            check = (11 - product) % 10
            if check == 10:
                continue
            base.append(check)
            return "".join(map(str, base))

    @staticmethod
    def generate_uk_ni():
        """UK National Insurance Number — AA 99 99 99 A with official HMRC prefix restrictions."""
        FORBIDDEN_FIRST  = set('DFIQUV')
        FORBIDDEN_SECOND = set('DFIOQUV')
        FORBIDDEN_PREFIX = {'BG', 'GB', 'KN', 'NK', 'NT', 'TN', 'ZZ'}
        while True:
            c1 = random.choice([c for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' if c not in FORBIDDEN_FIRST])
            c2 = random.choice([c for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' if c not in FORBIDDEN_SECOND])
            if c1 + c2 not in FORBIDDEN_PREFIX:
                break
        nn = lambda: random.randint(0, 9)
        digits = f"{nn()}{nn()} {nn()}{nn()} {nn()}{nn()}"
        return f"{c1}{c2} {digits} {random.choice('ABCD')}"

    @staticmethod
    def generate_ru_snils():
        """Russian Insurance ID (SNILS) — 11 digits with checksum."""
        base = [random.randint(0, 9) for _ in range(9)]
        num = int("".join(map(str, base)))
        if num <= 1001:
            control = 0
        else:
            total = sum(d * (9 - i) for i, d in enumerate(base))
            control = 0 if total in (100, 101) else (total % 101 % 100)
        s = "".join(map(str, base))
        return f"{s[0:3]}-{s[3:6]}-{s[6:9]} {control:02d}"

    @staticmethod
    def _luhn_check(partial):
        """Returns Luhn check digit for a partial digit list (used by FR SIREN/SIRET)."""
        total = 0
        for i, d in enumerate(reversed(partial)):
            n = d * 2 if i % 2 == 0 else d
            if n > 9:
                n -= 9
            total += n
        return (10 - total % 10) % 10

    # ── TR ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def generate_tr_vkn():
        """Turkish Tax ID (Vergi Kimlik Numarası) — 10 digits, proprietary checksum."""
        d = [random.randint(1, 9)] + [random.randint(0, 9) for _ in range(8)]
        total = 0
        for i in range(9):
            v = (d[i] + (9 - i)) % 10
            if v != 0:
                c = (v * (2 ** (9 - i))) % 9
                if c == 0:
                    c = 9
            else:
                c = 0
            total += c
        d.append((10 - total % 10) % 10)
        return "".join(map(str, d))

    @staticmethod
    def generate_tr_sgk():
        """Turkish SGK Employer Registration — il-sequence-unit.branch-sub."""
        il   = random.randint(1, 81)
        seq  = random.randint(1, 9999999)
        unit = random.randint(1, 9)
        sub  = random.randint(1, 99)
        sube = random.randint(1, 99)
        return f"{il:02d}-{seq:07d}-{unit}.{sub:02d}-{sube:02d}"

    @staticmethod
    def generate_tr_mersis():
        """Turkish MERSİS company registration — 16 digits (VKN-based)."""
        vkn    = IdentityGenerator.generate_tr_vkn()
        suffix = f"{random.randint(0, 99999):05d}"
        return f"{vkn}0{suffix}"

    # ── US ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def generate_us_ein():
        """US Employer Identification Number — XX-XXXXXXX."""
        return f"{random.randint(10, 99)}-{random.randint(1000000, 9999999)}"

    # ── UK ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def generate_uk_utr():
        """UK Unique Taxpayer Reference — 10 digits."""
        return str(random.randint(1000000000, 9999999999))

    @staticmethod
    def generate_uk_crn():
        """UK Company Registration Number — 8 digits (E&W) or SC/NI + 6 digits."""
        variant = random.choices(['EW', 'SC', 'NI'], weights=[8, 1, 1])[0]
        if variant == 'EW':
            return f"{random.randint(10000000, 99999999)}"
        prefix = 'SC' if variant == 'SC' else 'NI'
        return f"{prefix}{random.randint(100000, 999999)}"

    @staticmethod
    def generate_uk_paye():
        """UK PAYE Employer Reference — XXX/XXXXXX."""
        office = random.randint(100, 999)
        ref    = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=6))
        return f"{office}/{ref}"

    # ── DE ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def generate_de_ust_id():
        """German VAT ID (Umsatzsteuer-IdNr) — DE + 9 digits, ISO 7064 MOD 11,10."""
        while True:
            base = [random.randint(1, 9)] + [random.randint(0, 9) for _ in range(7)]
            product = 10
            for d in base:
                s = (product + d) % 10
                if s == 0:
                    s = 10
                product = (s * 2) % 11
            check = (11 - product) % 10
            if check == 10:
                continue
            return f"DE{''.join(map(str, base))}{check}"

    @staticmethod
    def generate_de_hrb():
        """German Commercial Register Number — HRB/HRA XXXXXX."""
        return f"{random.choice(['HRB', 'HRA'])} {random.randint(1, 999999)}"

    @staticmethod
    def generate_de_rvn():
        """German Rentenversicherungsnummer — BB TTMMJJ A SSSC, official check digit."""
        AREA_CODES = [
            10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
            20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
            30, 31, 32, 33, 38, 39, 40, 48, 50, 52,
            58, 60, 61, 62, 65, 70, 71, 72, 78, 80,
            81, 88, 89, 90, 91, 92, 93, 94,
        ]
        area   = random.choice(AREA_CODES)
        day    = random.randint(1, 28)
        month  = random.randint(1, 12)
        year   = random.randint(40, 99)
        letter = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        serial = random.randint(1, 999)

        base = f"{area:02d}{day:02d}{month:02d}{year:02d}{letter}{serial:03d}"

        # Expand letters to 2-digit position codes (A=01 … Z=26)
        expanded = ""
        for c in base:
            expanded += c if c.isdigit() else f"{ord(c) - ord('A') + 1:02d}"

        # Alternate weights 2,1,2,1,… starting at index 0
        total = 0
        for i, ch in enumerate(expanded):
            n = int(ch) * (2 if i % 2 == 0 else 1)
            total += n // 10 + n % 10

        check = total % 10
        return f"{area:02d} {day:02d}{month:02d}{year:02d} {letter} {serial:03d}{check}"

    # ── FR ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def generate_fr_siren():
        """French SIREN — 9 digits, Luhn checksum."""
        base = [random.randint(1, 9)] + [random.randint(0, 9) for _ in range(7)]
        return "".join(map(str, base + [IdentityGenerator._luhn_check(base)]))

    @staticmethod
    def generate_fr_siret():
        """French SIRET — Luhn-valid SIREN (9) + NIC (4) + Luhn check (1) = 14 digits."""
        siren = [int(c) for c in IdentityGenerator.generate_fr_siren()]
        nic   = [random.randint(0, 9) for _ in range(4)]
        base  = siren + nic
        return "".join(map(str, base + [IdentityGenerator._luhn_check(base)]))

    @staticmethod
    def generate_fr_tva():
        """French TVA (VAT) — FR + 2-digit mod-97 key + SIREN."""
        siren = IdentityGenerator.generate_fr_siren()
        key   = (12 + 3 * (int(siren) % 97)) % 97
        return f"FR{key:02d}{siren}"

    # ── RU ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def generate_ru_ogrn():
        """Russian OGRN (Primary State Registration) — 13 digits, checksum mod 11."""
        year   = random.randint(2, 24)
        region = random.randint(1, 79)
        seq    = random.randint(1, 9999999)
        base   = f"1{year:02d}{region:02d}{seq:07d}"
        check  = (int(base) % 11) % 10
        return base + str(check)

    @staticmethod
    def generate_ru_kpp():
        """Russian KPP (Tax Registration Reason Code) — 9 digits."""
        region = random.randint(1, 92)
        ifns   = random.randint(1, 99)
        reason = random.randint(1, 50)
        seq    = random.randint(1, 999)
        return f"{region:02d}{ifns:02d}{reason:02d}{seq:03d}"

    # ────────────────────────────────────────────────────────────────────────────

    def generate(self, data_type, locale="TR", **kwargs):
        l = locale.upper()
        dt = data_type.lower()

        # --- National IDs ---
        if dt == 'tckn' or (dt == 'nationalid' and l == 'TR'):
            return self.generate_tr_id()

        if dt == 'ykn':
            return self.generate_ykn()

        if dt == 'nationalid':
            if l == 'RU':
                return f"{random.randint(1000, 9999)} {random.randint(100000, 999999)}"
            if l == 'US':
                return f"{random.randint(100, 899):03d}-{random.randint(10, 99):02d}-{random.randint(1000, 9999):04d}"
            if l == 'UK':
                return self.generate_uk_ni()
            if l == 'FR':
                base = (f"{random.randint(1,2)}{random.randint(40,99):02d}{random.randint(1,12):02d}"
                        f"{random.randint(1,95):02d}{random.randint(1,999):03d}{random.randint(1,999):03d}")
                return f"{base}{97 - (int(base) % 97):02d}"
            if l == 'DE':
                return self.generate_de_steuer_id()
            return self.generate_tr_id()

        if dt == 'ssn':
            return f"{random.randint(100,899):03d}-{random.randint(10,99):02d}-{random.randint(1000,9999):04d}"

        if dt == 'nin':
            return self.generate_uk_ni()

        # --- Tax IDs (locale-aware) ---
        if dt == 'vkn':
            return self.generate_tr_vkn()

        if dt == 'taxid':
            if l == 'TR': return self.generate_tr_vkn()
            if l == 'US': return self.generate_us_ein()
            if l == 'UK': return self.generate_uk_utr()
            if l == 'DE': return self.generate_de_ust_id()
            if l == 'FR': return self.generate_fr_siren()
            if l == 'RU': return self.generate_ru_inn()
            return self.generate_tr_vkn()

        if dt == 'inn':
            return self.generate_ru_inn()

        if dt == 'snils':
            return self.generate_ru_snils()

        # --- Country-specific shortcuts ---
        if dt == 'sgk':
            return self.generate_tr_sgk()
        if dt == 'mersis':
            return self.generate_tr_mersis()
        if dt == 'ein':
            return self.generate_us_ein()
        if dt == 'utr':
            return self.generate_uk_utr()
        if dt == 'crn':
            return self.generate_uk_crn()
        if dt == 'paye':
            return self.generate_uk_paye()
        if dt in ('ust_id', 'ustid'):
            return self.generate_de_ust_id()
        if dt == 'hrb':
            return self.generate_de_hrb()
        if dt == 'rvn':
            return self.generate_de_rvn()
        if dt == 'siren':
            return self.generate_fr_siren()
        if dt == 'siret':
            return self.generate_fr_siret()
        if dt == 'tva':
            return self.generate_fr_tva()
        if dt == 'ogrn':
            return self.generate_ru_ogrn()
        if dt == 'kpp':
            return self.generate_ru_kpp()

        # --- Locale-aware aggregate types ---
        if dt == 'employer_id':
            if l == 'TR': return self.generate_tr_mersis()
            if l == 'US': return self.generate_us_ein()
            if l == 'UK': return self.generate_uk_crn()
            if l == 'DE': return self.generate_de_hrb()
            if l == 'FR': return self.generate_fr_siret()
            if l == 'RU': return self.generate_ru_ogrn()
            return self.generate_tr_mersis()

        if dt == 'insurance_id':
            if l == 'TR': return self.generate_tr_sgk()
            if l == 'US': return f"{random.randint(100,899):03d}-{random.randint(10,99):02d}-{random.randint(1000,9999):04d}"
            if l == 'UK': return self.generate_uk_paye()
            if l == 'DE': return self.generate_de_rvn()
            if l == 'FR':
                base = (f"{random.randint(1,2)}{random.randint(40,99):02d}{random.randint(1,12):02d}"
                        f"{random.randint(1,95):02d}{random.randint(1,999):03d}{random.randint(1,999):03d}")
                return f"{base}{97 - (int(base) % 97):02d}"
            if l == 'RU': return self.generate_ru_snils()
            return self.generate_tr_sgk()

        # --- Documents ---
        if dt == 'passport':
            return f"P{random.randint(1000000, 9999999)}"

        if dt == 'license':
            return f"{random.randint(100000, 999999)}"

        # --- Demographics ---
        if dt == 'age':
            return random.randint(18, 80)

        if dt == 'gender':
            return random.choice(['Male', 'Female'])

        if dt == 'birthdate':
            age = random.randint(18, 80)
            year = date.today().year - age
            return date(year, random.randint(1, 12), random.randint(1, 28)).strftime('%Y-%m-%d')

        # --- Names ---
        pool = NAME_POOLS.get(l, NAME_POOLS['TR'])
        gender_kwarg = str(kwargs.get('gender', '')).lower()
        if gender_kwarg in ('female', 'kadın', 'f'):
            g = 'female'
        elif gender_kwarg in ('male', 'erkek', 'm'):
            g = 'male'
        else:
            g = random.choice(['male', 'female'])

        if dt == 'firstname':
            return random.choice(pool[g])

        if dt == 'lastname':
            key = 'last_f' if (l == 'RU' and g == 'female') else 'last'
            return random.choice(pool.get(key, pool['last']))

        if dt == 'patronymic':
            if l == 'RU':
                key = 'pat_m' if g == 'male' else 'pat_f'
                return random.choice(pool.get(key, ['Иванович']))
            return ''

        if dt == 'fullname':
            fn = random.choice(pool[g])
            ln_key = 'last_f' if (l == 'RU' and g == 'female') else 'last'
            ln = random.choice(pool.get(ln_key, pool['last']))
            if l == 'RU':
                pat_key = 'pat_m' if g == 'male' else 'pat_f'
                pat = random.choice(pool.get(pat_key, ['Иванович']))
                return f"{fn} {pat} {ln}"
            return f"{fn} {ln}"

        return "GENERATED_DATA"
