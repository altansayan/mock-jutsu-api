"""
mock-jutsu — Master Identity Generator (Full Regulatory Coverage)
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)
"""

import random
from collections import Counter
import secrets
from datetime import date

from mockjutsu.generators.name_data import NAME_POOLS

# ISO 3166-1 alpha-3 nationality codes (common pool)
_NATIONALITIES = [
    'Turkish', 'American', 'British', 'German', 'French', 'Russian',
    'Chinese', 'Indian', 'Brazilian', 'Japanese', 'Korean', 'Italian',
    'Spanish', 'Dutch', 'Polish', 'Swedish', 'Norwegian', 'Danish',
    'Finnish', 'Australian', 'Canadian', 'Mexican', 'Argentine',
    'South African', 'Egyptian', 'Nigerian', 'Saudi', 'Emirati',
    'Iranian', 'Pakistani', 'Ukrainian', 'Belgian', 'Swiss', 'Austrian',
    'Portuguese', 'Greek', 'Hungarian', 'Czech', 'Romanian', 'Bulgarian',
]


def _wc(seq, weights):
    """Weighted secrets-based choice (replaces random.choices with weights)."""
    total = sum(weights)
    r = random.randrange(total)
    cumulative = 0
    for choice, weight in zip(seq, weights):
        cumulative += weight
        if r < cumulative:
            return choice
    return seq[-1]


class IdentityGenerator:
    """Identity Generator with 100% official regulatory algorithms for 6 countries."""

    @staticmethod
    def generate_tr_id(prefix=None):
        d = [int(x) for x in str(prefix)] if prefix else [random.choice([2, 4, 5, 6, 7, 8])]
        while len(d) < 9:
            d.append(random.randrange(10))
        d.append(((sum(d[0::2]) * 7) - sum(d[1::2])) % 10)
        d.append(sum(d) % 10)
        return "".join(map(str, d))

    @staticmethod
    def generate_ykn():
        """YKN: 11 digits, starts with 99, MOD-10 (Luhn) checksum."""
        base = [9, 9] + [random.randrange(10) for _ in range(8)]
        total = 0
        for i, d in enumerate(reversed(base)):
            n = d * 2 if i % 2 == 0 else d
            if n > 9:
                n -= 9
            total += n
        base.append((10 - total % 10) % 10)
        return "".join(map(str, base))

    @staticmethod
    def generate_ru_inn_corporate():
        """Russian Corporate Tax ID (INN) — 10 digits, 1 check digit."""
        base = [random.randrange(10) for _ in range(9)]
        weights = [2, 4, 10, 3, 5, 9, 4, 6, 8]
        control = sum(a * b for a, b in zip(base, weights)) % 11 % 10
        base.append(control)
        return "".join(map(str, base))

    @staticmethod
    def generate_ru_inn_individual():
        """Russian Individual Tax ID (INN) — 12 digits, 2 check digits.

        check1 weights (positions 0-9): [7,2,4,10,3,5,9,4,6,8]
        check2 weights (positions 0-10): [3,7,2,4,10,3,5,9,4,6,8]
        check = (sum % 11) % 10
        """
        base = [random.randrange(10) for _ in range(10)]
        w1 = [7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
        w2 = [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
        c1 = sum(base[i] * w1[i] for i in range(10)) % 11 % 10
        base.append(c1)
        c2 = sum(base[i] * w2[i] for i in range(11)) % 11 % 10
        base.append(c2)
        return "".join(map(str, base))

    # Alias kept for backwards compatibility
    @staticmethod
    def generate_ru_inn():
        return IdentityGenerator.generate_ru_inn_corporate()

    @staticmethod
    def generate_de_steuer_id():
        """German Steuerliche Identifikationsnummer — 11 digits, ISO 7064 MOD 11,10 checksum.
        BZSt rule: among first 10 digits, exactly one digit must appear 2 or 3 times;
        all other digits appear at most once (per stdnum.de.idnr specification).
        """
        while True:
            base = [random.randrange(9) + 1] + [random.randrange(10) for _ in range(9)]
            counts = [c for c in Counter(base).values() if c > 1]
            if len(counts) != 1 or counts[0] not in (2, 3):
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
        allowed_first  = [c for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' if c not in FORBIDDEN_FIRST]
        allowed_second = [c for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' if c not in FORBIDDEN_SECOND]
        while True:
            c1 = random.choice(allowed_first)
            c2 = random.choice(allowed_second)
            if c1 + c2 not in FORBIDDEN_PREFIX:
                break
        digits = f"{random.randrange(10)}{random.randrange(10)} {random.randrange(10)}{random.randrange(10)} {random.randrange(10)}{random.randrange(10)}"
        return f"{c1}{c2} {digits} {random.choice('ABCD')}"

    @staticmethod
    def generate_ru_snils():
        """Russian Insurance ID (SNILS) — 11 digits with checksum."""
        base = [random.randrange(10) for _ in range(9)]
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
        d = [random.randrange(9) + 1] + [random.randrange(10) for _ in range(8)]
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
        """Turkish SGK Employer Registration Number — il-sequence-unit.branch-sub.
        Format: XX-XXXXXXX-X.XX-XX (province-sequence-unit.branch-subbranch).
        This is the *employer* registration number, not the individual health ID.
        For individual insurance ID use insurance_id[TR] which returns TCKN-format.
        """
        il   = random.randrange(81) + 1
        seq  = random.randrange(9999999) + 1
        unit = random.randrange(9) + 1
        sub  = random.randrange(99) + 1
        sube = random.randrange(99) + 1
        return f"{il:02d}-{seq:07d}-{unit}.{sub:02d}-{sube:02d}"

    @staticmethod
    def _generate_tr_individual_insurance():
        """Turkish individual social/health insurance ID.
        Turkey uses TC Kimlik No (TCKN) as the primary SGK/health insurance identifier.
        Format: 11-digit, first digit 1-9, MOD-11 checksum (same algorithm as TCKN).
        """
        d = [random.randrange(9) + 1] + [random.randrange(10) for _ in range(8)]
        d9 = ((7 * (d[0] + d[2] + d[4] + d[6] + d[8])) -
              (d[1] + d[3] + d[5] + d[7])) % 10
        d10 = (d[0] + d[1] + d[2] + d[3] + d[4] +
               d[5] + d[6] + d[7] + d[8] + d9) % 10
        return "".join(map(str, d + [d9, d10]))

    @staticmethod
    def _generate_uk_nhs_number():
        """UK NHS Number — 10 digits, weighted Mod-11 checksum (weights 10→2).
        Format: XXX XXX XXXX (displayed with spaces).
        """
        while True:
            base = [random.randrange(10) for _ in range(9)]
            weights = [10, 9, 8, 7, 6, 5, 4, 3, 2]
            total = sum(d * w for d, w in zip(base, weights))
            remainder = total % 11
            if remainder == 1:
                continue
            check = 0 if remainder == 0 else 11 - remainder
            if check == 10:
                continue
            digits = "".join(map(str, base)) + str(check)
            return f"{digits[:3]} {digits[3:6]} {digits[6:]}"

    @staticmethod
    def generate_tr_mersis():
        """Turkish MERSİS company registration — 16 digits (VKN-based)."""
        vkn    = IdentityGenerator.generate_tr_vkn()
        suffix = f"{random.randrange(100000):05d}"
        return f"{vkn}0{suffix}"

    # ── US ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def generate_us_ssn():
        """US Social Security Number — area 001-899 excluding 000 and 666, group 01-99, serial 0001-9999."""
        area = random.randrange(898) + 1   # 1-898; shift >=666 to skip 666
        if area >= 666:
            area += 1                       # maps 1-665 → 1-665, 666-898 → 667-899
        group  = random.randrange(99) + 1   # 01-99 (00 invalid per SSA)
        serial = random.randrange(9999) + 1 # 0001-9999 (0000 invalid per SSA)
        return f"{area:03d}-{group:02d}-{serial:04d}"

    # IRS campus-assigned EIN prefixes (invalid ones excluded per stdnum.us.ein numdb)
    _VALID_EIN_PREFIXES = [
        10, 11, 12, 13, 14, 15, 16, 20, 21, 22, 23, 24, 25, 26, 27,
        30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48,
        50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68,
        71, 72, 73, 74, 75, 76, 77, 80, 81, 82, 83, 84, 85, 86, 87, 88,
        90, 91, 92, 93, 94, 95, 98, 99,
    ]

    @staticmethod
    def generate_us_ein():
        """US Employer Identification Number — XX-XXXXXXX, IRS campus prefix only."""
        prefix = random.choice(IdentityGenerator._VALID_EIN_PREFIXES)
        return f"{prefix:02d}-{random.randrange(9000000) + 1000000}"

    # ── UK ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def generate_uk_utr():
        """UK Unique Taxpayer Reference — 10 digits, weighted check as first digit."""
        # weights and check map from stdnum.gb.utr
        _weights = (6, 7, 8, 9, 10, 5, 4, 3, 2)
        _check_map = '21987654321'
        digits = [random.randrange(10) for _ in range(9)]
        check = _check_map[sum(d * w for d, w in zip(digits, _weights)) % 11]
        return check + ''.join(map(str, digits))

    @staticmethod
    def generate_gb_vat():
        """UK VAT registration number — GB + 9 digits, mod-97 weighted checksum."""
        _weights = (8, 7, 6, 5, 4, 3, 2)
        # First digit ≥ 1 so 3-digit prefix ≥ 100, which allows checksum in {0, 42, 55}
        d = [random.randrange(1, 10)] + [random.randrange(10) for _ in range(6)]
        partial = sum(w * di for w, di in zip(_weights, d))
        # Solve last 2 digits for target checksum 0 (deterministic, target always ≤ 96)
        target = (-partial) % 97  # in [0, 96]
        d7, d8 = target // 10, target % 10
        return f"GB{''.join(map(str, d))}{d7}{d8}"

    @staticmethod
    def generate_uk_crn():
        """UK Company Registration Number — 8 digits (E&W) or SC/NI + 6 digits."""
        variant = _wc(['EW', 'SC', 'NI'], [8, 1, 1])
        if variant == 'EW':
            return f"{random.randrange(90000000) + 10000000}"
        prefix = 'SC' if variant == 'SC' else 'NI'
        return f"{prefix}{random.randrange(900000) + 100000}"

    @staticmethod
    def generate_uk_paye():
        """UK PAYE Employer Reference — XXX/XXXXXX."""
        office = random.randrange(900) + 100
        ref    = "".join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for _ in range(6))
        return f"{office}/{ref}"

    # ── DE ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def generate_de_ust_id():
        """German VAT ID (Umsatzsteuer-IdNr) — DE + 9 digits, ISO 7064 MOD 11,10."""
        while True:
            base = [random.randrange(9) + 1] + [random.randrange(10) for _ in range(7)]
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
        return f"{random.choice(['HRB', 'HRA'])} {random.randrange(999999) + 1}"

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
        day    = random.randrange(28) + 1
        month  = random.randrange(12) + 1
        year   = random.randrange(60) + 40
        letter = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        serial = random.randrange(999) + 1

        base = f"{area:02d}{day:02d}{month:02d}{year:02d}{letter}{serial:03d}"

        expanded = ""
        for c in base:
            expanded += c if c.isdigit() else f"{ord(c) - ord('A') + 1:02d}"

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
        base = [random.randrange(9) + 1] + [random.randrange(10) for _ in range(7)]
        return "".join(map(str, base + [IdentityGenerator._luhn_check(base)]))

    @staticmethod
    def generate_fr_siret():
        """French SIRET — Luhn-valid SIREN (9) + NIC (4) + Luhn check (1) = 14 digits."""
        siren = [int(c) for c in IdentityGenerator.generate_fr_siren()]
        nic   = [random.randrange(10) for _ in range(4)]
        base  = siren + nic
        return "".join(map(str, base + [IdentityGenerator._luhn_check(base)]))

    @staticmethod
    def generate_fr_tva():
        """French TVA (VAT) — FR + 2-digit mod-97 key + SIREN."""
        siren = IdentityGenerator.generate_fr_siren()
        key   = (12 + 3 * (int(siren) % 97)) % 97
        return f"FR{key:02d}{siren}"

    # EU VIES VAT key charset for FR: A-Z excluding I and O, plus digits 0-9
    _FR_VAT_KEY_CHARS = 'ABCDEFGHJKLMNPQRSTUVWXYZ0123456789'

    @staticmethod
    def generate_vat_number(locale: str) -> str:
        """EU/Global VAT number with country prefix — VIES-compatible format.

        TR: TR + 10-digit VKN  |  DE: DE + 9 digits (ISO 7064 MOD 11,10)
        FR: FR + mod-97 key + SIREN  |  GB/UK: GB + 9 digits (mod-97 weighted checksum)
        US: US + EIN-style XX-XXXXXXX  |  RU: RU + 10-digit INN
        """
        l = locale.upper()
        if l == 'TR':
            return f"TR{IdentityGenerator.generate_tr_vkn()}"
        if l == 'DE':
            return IdentityGenerator.generate_de_ust_id()
        if l == 'FR':
            return IdentityGenerator.generate_fr_tva()
        if l in ('UK', 'GB'):
            return IdentityGenerator.generate_gb_vat()
        if l == 'US':
            prefix = random.randrange(10, 100)
            suffix = random.randrange(1000000, 10000000)
            return f"US{prefix:02d}-{suffix:07d}"
        if l == 'RU':
            return f"RU{IdentityGenerator.generate_ru_inn_corporate()}"
        # fallback → TR format
        return f"TR{IdentityGenerator.generate_tr_vkn()}"

    # ── RU ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def generate_ru_ogrn():
        """Russian OGRN (Primary State Registration) — 13 digits, checksum mod 11."""
        year   = random.randrange(23) + 2
        region = random.randrange(79) + 1
        seq    = random.randrange(9999999) + 1
        base   = f"1{year:02d}{region:02d}{seq:07d}"
        check  = (int(base) % 11) % 10
        return base + str(check)

    @staticmethod
    def generate_ru_kpp():
        """Russian KPP (Tax Registration Reason Code) — 9 digits."""
        region = random.randrange(92) + 1
        ifns   = random.randrange(99) + 1
        reason = random.randrange(50) + 1
        seq    = random.randrange(999) + 1
        return f"{region:02d}{ifns:02d}{reason:02d}{seq:03d}"

    # ── Passport ──────────────────────────────────────────────────────────────

    _TR_PASSPORT_LETTERS = "ABCDEFGHJKLMNPRSTUVYZ"   # Turkish uppercase, I/Q excluded
    _DE_PASSPORT_LETTERS = "CFGHJKLMNPRTVWXYZ"        # German Reisepass series letters
    _FR_PASSPORT_ALPHA   = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    @staticmethod
    def _generate_passport(locale: str) -> str:
        """Locale-aware passport number.

        TR: 1 letter + 8 digits (e.g. U12345678)  — ICAO MRTD, 9 chars
        US: 1 letter + 8 digits (e.g. A12345678)  — US NPPD format, 9 chars
        UK: 9 digits (no letter prefix, post-2006) — HMPO, 9 chars
        DE: 1 letter (German series) + 8 alphanumeric — Bundesdruckerei, 9 chars
        FR: 2 digits + 2 uppercase letters + 5 digits — ANTS format, 9 chars
        RU: 2-digit series + 7-digit number — zagranpassport, 9 chars
        """
        l = locale.upper()
        if l == 'TR':
            letter = random.choice(IdentityGenerator._TR_PASSPORT_LETTERS)
            return letter + "".join(str(random.randrange(10)) for _ in range(8))
        if l == 'US':
            letter = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            return letter + "".join(str(random.randrange(10)) for _ in range(8))
        if l == 'UK':
            return "".join(str(random.randrange(10)) for _ in range(9))
        if l == 'DE':
            letter = random.choice(IdentityGenerator._DE_PASSPORT_LETTERS)
            alnum = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
            return letter + "".join(random.choice(alnum) for _ in range(8))
        if l == 'FR':
            d1 = f"{random.randrange(99) + 1:02d}"
            letters = "".join(random.choice(IdentityGenerator._FR_PASSPORT_ALPHA) for _ in range(2))
            digits = f"{random.randrange(99999) + 1:05d}"
            return f"{d1}{letters}{digits}"
        if l == 'RU':
            series = f"{random.randrange(90) + 10:02d}"
            number = f"{random.randrange(9000000) + 1000000:07d}"
            return f"{series}{number}"
        # fallback → TR format
        letter = random.choice(IdentityGenerator._TR_PASSPORT_LETTERS)
        return letter + "".join(str(random.randrange(10)) for _ in range(8))

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
                return f"{random.randrange(9000) + 1000} {random.randrange(900000) + 100000}"
            if l == 'US':
                return self.generate_us_ssn()
            if l == 'UK':
                return self.generate_uk_ni()
            if l == 'FR':
                month = random.randint(1, 12)
                base = (f"{random.randrange(2) + 1}{random.randrange(60) + 40:02d}{month:02d}"
                        f"{random.randrange(95) + 1:02d}{random.randrange(999) + 1:03d}{random.randrange(999) + 1:03d}")
                return f"{base}{97 - (int(base) % 97):02d}"
            if l == 'DE':
                return self.generate_de_steuer_id()
            return self.generate_tr_id()

        if dt == 'ssn':
            return self.generate_us_ssn()

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
            if l == 'RU': return self.generate_ru_inn_corporate()
            return self.generate_tr_vkn()

        if dt == 'vat_number':
            return self.generate_vat_number(l)

        if dt == 'inn':
            return self.generate_ru_inn_corporate()

        if dt == 'inn_individual':
            return self.generate_ru_inn_individual()

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
            # TR: Individual social/health insurance ID = TCKN-style 11-digit number
            #     (Turkey uses TC Kimlik No as the primary SGK/health insurance identifier)
            # US: SSN is the standard health/social insurance identifier (Medicare, Medicaid)
            # UK: NHS Number (10-digit, weighted checksum) — the individual health ID
            # DE: Rentenversicherungsnummer — the statutory social insurance number
            # FR: Numéro de sécurité sociale (NIR) — French social insurance number
            # RU: SNILS — Russian individual insurance account number
            if l == 'TR': return self._generate_tr_individual_insurance()
            if l == 'US': return self.generate_us_ssn()
            if l == 'UK': return self._generate_uk_nhs_number()
            if l == 'DE': return self.generate_de_rvn()
            if l == 'FR':
                month = random.randint(1, 12)
                base = (f"{random.randrange(2) + 1}{random.randrange(60) + 40:02d}{month:02d}"
                        f"{random.randrange(95) + 1:02d}{random.randrange(999) + 1:03d}{random.randrange(999) + 1:03d}")
                return f"{base}{97 - (int(base) % 97):02d}"
            if l == 'RU': return self.generate_ru_snils()
            return self.generate_tr_sgk()

        # --- Documents ---
        if dt == 'passport':
            return self._generate_passport(l)

        if dt == 'license':
            return f"{random.randrange(900000) + 100000}"

        # --- Demographics ---
        if dt == 'age':
            mn = int(kwargs.get('min', 18))
            mx = int(kwargs.get('max', 80))
            if mn >= mx: mx = mn + 1
            return random.randint(mn, mx)

        if dt == 'gender':
            return random.choice(['Male', 'Female'])

        if dt == 'birthdate':
            age = random.randrange(63) + 18
            year = date.today().year - age
            return date(year, random.randrange(12) + 1, random.randrange(28) + 1).strftime('%Y-%m-%d')

        # --- Masked Types ---
        if dt == 'tckn_masked':
            mid = "".join(str(random.randrange(10)) for _ in range(6))
            return f"***{mid}**"

        if dt == 'ssn_masked':
            last4 = "".join(str(random.randrange(10)) for _ in range(4))
            return f"***-**-{last4}"

        if dt == 'nationality':
            return random.choice(_NATIONALITIES)

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
