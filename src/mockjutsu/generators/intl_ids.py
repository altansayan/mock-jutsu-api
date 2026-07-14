"""
mock-jutsu — International National ID & Tax Number Generator
48 country-specific identity, tax, and business numbers with correct checksums.
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)
"""
import random
from collections import Counter
from mockjutsu.algorithms import luhn_check_digit, iso7064_mod11_10_check, verhoeff_check, ee_lt_check


# ── Spanish MOD-23 table ──────────────────────────────────────────────────────
_ES_DNI_LETTERS = "TRWAGMYFPDXBNJZSQVHLCKE"

# ── Italian Codice Fiscale tables ─────────────────────────────────────────────
# Even-position values: digits 0-9→0-9, letters A-Z→0-25 (stdnum compatible)
_CF_EVEN = {}
for _i, _c in enumerate('0123456789'):
    _CF_EVEN[_c] = _i
for _i, _c in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    _CF_EVEN[_c] = _i

_CF_ODD_VALS = [1, 0, 5, 7, 9, 13, 15, 17, 19, 21, 2, 4, 18, 20, 11, 3, 6, 8, 12, 14, 16, 10, 22, 25, 24, 23]
_CF_ODD = {}
for _i, _c in enumerate('0123456789'):
    _CF_ODD[_c] = _CF_ODD_VALS[_i]
for _i, _c in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    _CF_ODD[_c] = _CF_ODD_VALS[_i]
_CF_MONTHS = 'ABCDEHLMPRST'
_CF_MUNICIPALITIES = [
    'A001', 'B619', 'C351', 'D612', 'E625', 'F205', 'G273',
    'H501', 'I452', 'L219', 'M163', 'N678', 'A944', 'B354',
    'C129', 'D086', 'E456', 'F839', 'G911', 'H724', 'I158',
]

# ── MY NRIC valid birth place codes ──────────────────────────────────────────
_MY_BP_CODES = [
    '01','02','03','04','05','06','07','08','09','10',
    '11','12','13','14','15','16','21','22','23','24',
    '25','26','27','28','29','30','31','32','33','34',
    '35','36','37','38','39','40','41','42','43','44',
    '45','46','47','48','49','50','51','52','53','54',
    '55','56','57','58','59','60','61','62','63','64',
    '65','66','67','68','71','72','74','75','76','77',
    '78','79','82','83','84','85','86','87','88','89',
    '90','91','92','93','98','99',
]

# ── SG UEN check chars ────────────────────────────────────────────────────────
_SG_BIZ_CHECKS    = 'XMKECAWLJDB'   # 8-digit business (ROB) format
_SG_LOCAL_CHECKS  = 'ZKCMDNERGWH'   # local company format


class IntlIdsGenerator:
    """International National ID & Tax Number Generator (48 types)."""

    # ── Brazil ───────────────────────────────────────────────────────────────

    @staticmethod
    def gen_br_cpf():
        """Brazilian CPF — 11 digits, MOD-11 two check digits."""
        d = [random.randint(0, 9) for _ in range(9)]
        s1 = sum(d[i] * (10 - i) for i in range(9)) % 11
        d.append(0 if s1 < 2 else 11 - s1)
        s2 = sum(d[i] * (11 - i) for i in range(10)) % 11
        d.append(0 if s2 < 2 else 11 - s2)
        n = ''.join(map(str, d))
        return f"{n[:3]}.{n[3:6]}.{n[6:9]}-{n[9:]}"

    @staticmethod
    def gen_br_cnpj():
        """Brazilian CNPJ — 14 digits, MOD-11 two check digits."""
        base = [random.randint(0, 9) for _ in range(8)] + [0, 0, 0, 1]
        w1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        r1 = sum(a * b for a, b in zip(base, w1)) % 11
        base.append(0 if r1 < 2 else 11 - r1)
        w2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        r2 = sum(a * b for a, b in zip(base, w2)) % 11
        base.append(0 if r2 < 2 else 11 - r2)
        n = ''.join(map(str, base))
        return f"{n[:2]}.{n[2:5]}.{n[5:8]}/{n[8:12]}-{n[12:]}"

    # ── India ────────────────────────────────────────────────────────────────

    @staticmethod
    def gen_in_pan():
        """Indian PAN — AAATZNNNNA format (5 letters + 4 digits + 1 letter)."""
        p1 = ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(3))
        p2 = random.choice('PCFHBLJGTA')
        p3 = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        p4 = ''.join(str(random.randint(0, 9)) for _ in range(4))
        p5 = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        return f"{p1}{p2}{p3}{p4}{p5}"

    @staticmethod
    def gen_in_aadhaar():
        """Indian Aadhaar — 12 digits, Verhoeff check digit. First digit 2-9, not a palindrome."""
        for _ in range(100):
            d = [random.randint(2, 9)] + [random.randint(0, 9) for _ in range(10)]
            check = verhoeff_check(d)
            n = ''.join(map(str, d)) + str(check)
            if n != n[::-1]:
                return f"{n[:4]} {n[4:8]} {n[8:]}"
        return "2341 2341 2346"

    _GSTIN_ALPHABET = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    @staticmethod
    def _luhn36_check(partial):
        """Find Luhn mod-36 check char for a partial string (alphabet 0-9A-Z)."""
        alph = IntlIdsGenerator._GSTIN_ALPHABET
        n = len(alph)
        for c in alph:
            vals = tuple(alph.index(x) for x in reversed(partial + c))
            cs = (sum(vals[::2]) + sum(sum(divmod(v * 2, n)) for v in vals[1::2])) % n
            if cs == 0:
                return c
        return '0'

    @staticmethod
    def gen_in_gstin():
        """Indian GSTIN — 15 chars: 2-digit state + 10-char PAN + entity + Z + Luhn36 check."""
        state = f"{random.randint(1, 37):02d}"
        pan = IntlIdsGenerator.gen_in_pan()
        entity = str(random.randint(1, 9))
        partial = f"{state}{pan}{entity}Z"
        check = IntlIdsGenerator._luhn36_check(partial)
        return f"{partial}{check}"

    @staticmethod
    def gen_in_epic():
        """Indian Voter ID (EPIC) — 3 uppercase letters + 6 digits + Luhn check digit."""
        prefix = ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(3))
        digits = [random.randint(0, 9) for _ in range(6)]
        total = 0
        for i, d in enumerate(reversed(digits)):
            if i % 2 == 0:
                d = d * 2
                if d > 9:
                    d -= 9
            total += d
        check = (10 - total % 10) % 10
        return f"{prefix}{''.join(map(str, digits))}{check}"

    # ── China ────────────────────────────────────────────────────────────────

    _CN_AREAS = [
        '110000', '120000', '130000', '210000', '220000', '230000',
        '310000', '320000', '330000', '340000', '350000', '360000',
        '370000', '410000', '420000', '430000', '440000',
        '510000', '520000', '530000', '610000', '620000', '630000',
    ]

    @staticmethod
    def gen_cn_ric():
        """Chinese RIC — 18 chars: 6-digit area + 8-digit date + 3-seq + 1 check."""
        area  = random.choice(IntlIdsGenerator._CN_AREAS)
        year  = random.randint(1960, 2005)
        month = random.randint(1, 12)
        day   = random.randint(1, 28)
        seq   = f"{random.randint(1, 999):03d}"
        base  = f"{area}{year:04d}{month:02d}{day:02d}{seq}"
        weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        s     = sum(int(c) * w for c, w in zip(base, weights)) % 11
        check = '10X98765432'[s]
        return base + check

    # ── Mexico ───────────────────────────────────────────────────────────────

    _MX_STATES = [
        'AS', 'BC', 'BS', 'CC', 'CL', 'CM', 'CS', 'CH', 'DF', 'DG',
        'GT', 'GR', 'HG', 'JC', 'MC', 'MN', 'MS', 'NT', 'NL', 'OC',
        'PL', 'QT', 'QR', 'SP', 'SL', 'SR', 'TC', 'TL', 'TS', 'VZ', 'YN', 'ZS', 'NE',
    ]
    _CONSONANTS = 'BCDFGHJKLMNPQRSTVWXYZ'
    _CURP_ALPHABET = '0123456789ABCDEFGHIJKLMN&OPQRSTUVWXYZ'
    _CURP_BLACKLIST = {
        'BACA','BAKA','BUEI','BUEY','CACA','CACO','CAGA','CAGO','CAKA',
        'CAKO','COGE','COGI','COJA','COJE','COJI','COJO','COLA','CULO',
        'FALO','FETO','GETA','GUEI','GUEY','JETA','JOTO','KACA','KACO',
        'KAGA','KAGO','KAKA','KAKO','KOGE','KOGI','KOJA','KOJE','KOJI',
        'KOJO','KOLA','KULO','LELO','LOCA','LOCO','LOKA','LOKO','MAME',
        'MAMO','MEAR','MEAS','MEON','MIAR','MION','MOCO','MULA','MULO',
        'NACA','NACO','PEDA','PEDO','PENE','PIPI','PITO','POPO','PUTA',
        'PUTO','QULO','RATA','ROBA','ROBE','ROBO','RUIN','SENO','TETA',
        'VACA','VAGA','VAGO','VAKA','VUEI','VUEY','WUEI','WUEY',
    }

    @staticmethod
    def gen_mx_curp():
        """Mexican CURP — 18 chars: 4 letters + YYMMDD + gender + state + 3 cons + alnum + check."""
        alph = IntlIdsGenerator._CURP_ALPHABET
        for _ in range(50):
            year  = random.randint(1950, 2005)
            month = random.randint(1, 12)
            day   = random.randint(1, 28)
            # Position 0: vowel, 1-3: any uppercase letters
            p0 = random.choice('AEIOU')
            p1 = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
            p2 = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
            p3 = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
            name_part = p0 + p1 + p2 + p3
            if name_part in IntlIdsGenerator._CURP_BLACKLIST:
                continue
            gender = random.choice('HM')
            state  = random.choice(IntlIdsGenerator._MX_STATES)
            cons   = ''.join(random.choice(IntlIdsGenerator._CONSONANTS) for _ in range(3))
            alnum  = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
            first17 = f"{name_part}{year%100:02d}{month:02d}{day:02d}{gender}{state}{cons}{alnum}"
            check = str((10 - sum(alph.index(c) * (18 - i)
                                  for i, c in enumerate(first17)) % 10) % 10)
            return first17 + check
        return "BOXW310820HNERXN09"

    @staticmethod
    def gen_mx_rfc():
        """Mexican RFC — 12 chars (company) or 13 chars (individual)."""
        year  = random.randint(1950, 2005)
        month = random.randint(1, 12)
        day   = random.randint(1, 28)
        is_individual = random.random() > 0.4
        if is_individual:
            letters = ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(4))
        else:
            letters = ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(3))
        date_part = f"{year%100:02d}{month:02d}{day:02d}"
        homoclave = ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(2))
        hd = str(random.randint(0, 9))
        return f"{letters}{date_part}{homoclave}{hd}"

    # ── Italy ────────────────────────────────────────────────────────────────

    @staticmethod
    def gen_it_codicefiscale():
        """Italian Codice Fiscale — 16 chars with official check digit."""
        cons = 'BCDFGHJKLMNPQRSTVWXYZ'
        vowels = 'AEIOU'

        def _part(n=3):
            pool = [random.choice(cons) for _ in range(4)] + [random.choice(vowels) for _ in range(3)]
            random.shuffle(pool)
            return ''.join(pool[:n])

        surn  = _part(3)
        name  = _part(3)
        year  = random.randint(1950, 2005)
        month = random.randint(1, 12)
        day   = random.randint(1, 28)
        gender = random.choice('MF')
        dd    = day if gender == 'M' else day + 40
        muni  = random.choice(_CF_MUNICIPALITIES)
        base  = f"{surn}{name}{year%100:02d}{_CF_MONTHS[month-1]}{dd:02d}{muni}"
        code  = sum(
            _CF_ODD[x] if n % 2 == 0 else _CF_EVEN.get(x, 0)
            for n, x in enumerate(base)
        )
        return base + 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[code % 26]

    # ── Spain ────────────────────────────────────────────────────────────────

    @staticmethod
    def gen_es_dni():
        """Spanish DNI — 8 digits + letter (MOD-23)."""
        n = random.randint(10000000, 99999999)
        return f"{n}{_ES_DNI_LETTERS[n % 23]}"

    @staticmethod
    def gen_es_nie():
        """Spanish NIE — X/Y/Z + 7 digits + letter (MOD-23)."""
        first = random.choice('XYZ')
        prefix_n = 'XYZ'.index(first)
        rest = random.randint(1000000, 9999999)
        n = int(f"{prefix_n}{rest}")
        return f"{first}{rest:07d}{_ES_DNI_LETTERS[n % 23]}"

    @staticmethod
    def gen_es_ccc():
        """Spanish CCC (bank account) — 4+4+2+10 digits with MOD-11 check digits."""
        bank   = f"{random.randint(1000, 9999):04d}"
        branch = f"{random.randint(1000, 9999):04d}"
        acct   = ''.join(str(random.randint(0, 9)) for _ in range(10))

        def _ccd(s):
            val = sum(int(c) * (2 ** i) for i, c in enumerate(s)) % 11
            return str(val if val < 2 else 11 - val)

        c1 = _ccd('00' + bank + branch)
        c2 = _ccd(acct)
        return f"{bank}-{branch}-{c1}{c2}-{acct}"

    # ── Germany ──────────────────────────────────────────────────────────────

    @staticmethod
    def gen_de_idnr():
        """German personal tax ID (IdNr) — 11 digits, ISO 7064 MOD 11,10."""
        while True:
            base = [random.randint(1, 9)] + [random.randint(0, 9) for _ in range(9)]
            counts = [c for c in Counter(base).values() if c > 1]
            if len(counts) != 1 or counts[0] not in (2, 3):
                continue
            check = iso7064_mod11_10_check(base)
            if check == 10:
                continue
            return ''.join(map(str, base)) + str(check)

    _DE_STATES = ['10', '11', '20', '21', '22', '23', '24', '25', '26', '27',
                  '28', '29', '30', '31', '32', '33', '40', '41', '42', '43',
                  '44', '45', '46', '47', '48', '50', '51', '52', '53', '54',
                  '55', '56', '57', '58', '60', '61', '62', '63', '64', '65',
                  '66', '70', '71', '80', '81', '82', '83', '84', '85', '86',
                  '87', '88', '89', '90', '91', '92', '93', '94', '95']

    @staticmethod
    def gen_de_stnr():
        """German Steuernummer — state-prefixed format (unified ELSTER 13-digit)."""
        state = random.choice(IntlIdsGenerator._DE_STATES)
        dist  = f"{random.randint(100, 999):03d}"
        seq   = f"{random.randint(10000, 99999):05d}"
        check = str(random.randint(0, 9))
        return f"{state}/{dist}/{seq} {check}"

    # ── Pakistan ─────────────────────────────────────────────────────────────

    @staticmethod
    def gen_pk_cnic():
        """Pakistani CNIC — 13 digits (NNNNN-NNNNNNN-N)."""
        province = f"{random.randint(10000, 49999):05d}"
        serial   = f"{random.randint(1000000, 9999999):07d}"
        gender   = str(random.choice([1, 3, 5, 7, 9]))
        return f"{province}-{serial}-{gender}"

    # ── Japan ────────────────────────────────────────────────────────────────

    @staticmethod
    def gen_jp_cn():
        """Japanese Corporate Number — 13 digits, check digit at position 0."""
        # weights applied to reversed 12-digit body
        weights = (1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2)
        body = [random.randint(0, 9) for _ in range(12)]
        s = sum(w * d for w, d in zip(weights, reversed(body))) % 9
        check = 9 - s
        return str(check) + ''.join(map(str, body))

    @staticmethod
    def gen_jp_in():
        """Japanese Individual Number (My Number) — 12 digits, MOD-11 check."""
        base = [random.randint(0, 9) for _ in range(11)]
        weights = [6, 5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
        s = sum(d * w for d, w in zip(base, weights)) % 11
        check = 0 if s <= 1 else 11 - s
        if check >= 10:
            check = 0
        return ''.join(map(str, base)) + str(check)

    # ── South Korea ──────────────────────────────────────────────────────────

    @staticmethod
    def gen_kr_rrn():
        """South Korean RRN — 13 digits: YYMMDD + G + PB(2) + XX(2) + CC + check."""
        weights = [2, 3, 4, 5, 6, 7, 8, 9, 2, 3, 4, 5]
        year  = random.randint(1950, 2005)
        month = random.randint(1, 12)
        day   = random.randint(1, 28)
        yy    = year % 100
        gender = random.choice([1, 2]) if year < 2000 else random.choice([3, 4])
        pb    = random.randint(0, 96)   # place of birth ≤ 96
        xx    = random.randint(0, 99)
        cc    = random.randint(0, 9)    # community center digit
        base  = f"{yy:02d}{month:02d}{day:02d}{gender}{pb:02d}{xx:02d}{cc}"
        s = sum(w * int(d) for w, d in zip(weights, base))
        check = (11 - s % 11) % 10
        return f"{yy:02d}{month:02d}{day:02d}-{gender}{pb:02d}{xx:02d}{cc}{check}"

    @staticmethod
    def gen_kr_brn():
        """South Korean Business Registration Number — NNN-NN-NNNNN; head 101-999 (100 is invalid per stdnum)."""
        head  = random.randint(101, 999)
        mid   = random.randint(10, 99)
        tail  = random.randint(10000, 99999)
        return f"{head:03d}-{mid:02d}-{tail:05d}"

    # ── Netherlands ──────────────────────────────────────────────────────────

    @staticmethod
    def gen_nl_bsn():
        """Dutch BSN — 9 digits, MOD-11 (9*d0+8*d1+...+2*d7-d8 ≡ 0 mod 11)."""
        for _ in range(500):
            d = [random.randint(0, 9) for _ in range(8)]
            if d[0] == 0:
                continue
            s = sum(d[i] * (9 - i) for i in range(8))
            d8 = s % 11
            if d8 <= 9:
                return ''.join(map(str, d)) + str(d8)
        return "123456782"

    # ── Poland ───────────────────────────────────────────────────────────────

    @staticmethod
    def gen_pl_pesel():
        """Polish PESEL — 11 digits with encoded birth date and MOD-10 check."""
        year  = random.randint(1950, 2005)
        month = random.randint(1, 12)
        day   = random.randint(1, 28)
        yy    = year % 100
        mm    = month + (20 if year >= 2000 else 0)
        seq   = random.randint(0, 999)
        gender_d = random.choice([1, 3, 5, 7, 9] if random.random() > 0.5 else [0, 2, 4, 6, 8])
        base = f"{yy:02d}{mm:02d}{day:02d}{seq:03d}{gender_d}"
        weights = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]
        s = sum(int(base[i]) * weights[i] for i in range(10)) % 10
        return base + str((10 - s) % 10)

    # ── Sweden ───────────────────────────────────────────────────────────────

    @staticmethod
    def gen_se_personnummer():
        """Swedish Personnummer — YYYYMMDD-NNNN (Luhn check on YYMMDDNNN)."""
        year  = random.randint(1950, 2005)
        month = random.randint(1, 12)
        day   = random.randint(1, 28)
        seq2  = random.randint(0, 99)
        gender_d = random.choice('0123456789')
        seq_str = f"{seq2:02d}{gender_d}"
        base = f"{year%100:02d}{month:02d}{day:02d}{seq_str}"
        total = 0
        for i, c in enumerate(base):
            n = int(c) * (2 if i % 2 == 0 else 1)
            total += n - 9 if n > 9 else n
        check = (10 - total % 10) % 10
        return f"{year:04d}{month:02d}{day:02d}-{seq_str}{check}"

    # ── Denmark ──────────────────────────────────────────────────────────────

    @staticmethod
    def gen_dk_cpr():
        """Danish CPR — DDMMYY-SSSS. Seq 0000-4999 → 1900s (always past)."""
        year  = random.randint(1950, 2000)
        month = random.randint(1, 12)
        day   = random.randint(1, 28)
        # First digit 0-3 → year+1900; avoids 1800s and future 2000s interpretations
        seq   = random.randint(0, 3999)
        return f"{day:02d}{month:02d}{year%100:02d}-{seq:04d}"

    # ── Finland ──────────────────────────────────────────────────────────────

    _HETU_TABLE = "0123456789ABCDEFHJKLMNPRSTUVWXY"

    @staticmethod
    def gen_fi_hetu():
        """Finnish HETU — DDMMYY[+/-A]NNNC (century separator + MOD-31 check)."""
        year  = random.randint(1950, 2005)
        month = random.randint(1, 12)
        day   = random.randint(1, 28)
        yy    = year % 100
        sep   = '-' if year < 2000 else 'A'
        seq   = random.randint(2, 899)
        num   = int(f"{day:02d}{month:02d}{yy:02d}{seq:03d}")
        check = IntlIdsGenerator._HETU_TABLE[num % 31]
        return f"{day:02d}{month:02d}{yy:02d}{sep}{seq:03d}{check}"

    # ── Norway ───────────────────────────────────────────────────────────────

    @staticmethod
    def gen_no_fodselsnummer():
        """Norwegian Fødselsnummer — 11 digits, two MOD-11 check digits."""
        w1 = [3, 7, 6, 1, 8, 9, 4, 5, 2]
        w2 = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
        for _ in range(200):
            year  = random.randint(1950, 2005)
            month = random.randint(1, 12)
            day   = random.randint(1, 28)
            seq   = random.randint(1, 499)
            base9 = [int(x) for x in f"{day:02d}{month:02d}{year%100:02d}{seq:03d}"]
            s1    = (11 - sum(a * b for a, b in zip(base9, w1))) % 11
            if s1 == 10:
                continue
            base10 = base9 + [s1]
            s2     = (11 - sum(a * b for a, b in zip(base10, w2))) % 11
            if s2 == 10:
                continue
            return ''.join(map(str, base10)) + str(s2)
        return "01019501234"

    # ── Australia ────────────────────────────────────────────────────────────

    @staticmethod
    def gen_au_abn():
        """Australian ABN — 11 digits. First 2 digits are check, last 9 are body."""
        # stdnum: calc_check_digits(body9) = str(11 + (-sum(w*d) - 1) % 89)
        weights = (3, 5, 7, 9, 11, 13, 15, 17, 19)
        body = ''.join(str(random.randint(0, 9)) for _ in range(9))
        s = sum(-w * int(n) for w, n in zip(weights, body))
        check2 = str(11 + (s - 1) % 89)
        return check2 + body

    @staticmethod
    def gen_au_tfn():
        """Australian TFN — 9 digits, weights (1,4,3,7,5,8,6,9,10), sum%11==0."""
        weights = [1, 4, 3, 7, 5, 8, 6, 9, 10]
        for _ in range(1000):
            d = [random.randint(1, 9)] + [random.randint(0, 9) for _ in range(7)]
            s = sum(d[i] * weights[i] for i in range(8))
            for last in range(10):
                if (s + last * 10) % 11 == 0:
                    return ''.join(map(str, d)) + str(last)
        return "123456782"

    @staticmethod
    def gen_au_acn():
        """Australian ACN — 9 digits, weights (8,7,6,5,4,3,2,1), check=(10-sum%10)%10."""
        weights = [8, 7, 6, 5, 4, 3, 2, 1]
        for _ in range(200):
            d = [random.randint(0, 9) for _ in range(8)]
            s = sum(d[i] * weights[i] for i in range(8))
            check = (10 - s % 10) % 10
            n = ''.join(map(str, d)) + str(check)
            if n[0] != '0':
                return n
        return "004085616"

    # ── Malaysia ─────────────────────────────────────────────────────────────

    @staticmethod
    def gen_my_nric():
        """Malaysian NRIC — YYMMDD-PB-NNNN (12 digits, valid birth place code)."""
        year  = random.randint(1960, 2005)
        month = random.randint(1, 12)
        day   = random.randint(1, 28)
        yy    = year % 100
        bp    = random.choice(_MY_BP_CODES)
        seq   = random.randint(1, 9999)
        return f"{yy:02d}{month:02d}{day:02d}-{bp}-{seq:04d}"

    # ── Thailand ─────────────────────────────────────────────────────────────

    @staticmethod
    def gen_th_pin():
        """Thai personal ID — 13 digits, MOD-11 variant check."""
        for _ in range(100):
            d = [random.randint(1, 8)] + [random.randint(0, 9) for _ in range(11)]
            s = sum((2 - i) * d[i] for i in range(12)) % 11
            check = (1 - s) % 10
            return ''.join(map(str, d)) + str(check)
        return "1234567891234"

    @staticmethod
    def gen_th_tin():
        """Thai TIN (business) — 13-digit, same format as PIN."""
        return IntlIdsGenerator.gen_th_pin()

    # ── Singapore ────────────────────────────────────────────────────────────

    @staticmethod
    def gen_sg_uen():
        """Singapore UEN — business format NNNNNNNNC (8 digits + check letter)."""
        d = [random.randint(0, 9) for _ in range(8)]
        weights = [10, 4, 9, 3, 8, 2, 7, 1]
        s = sum(int(x) * w for x, w in zip(d, weights)) % 11
        check = _SG_BIZ_CHECKS[s]
        return ''.join(map(str, d)) + check

    # ── South Africa ─────────────────────────────────────────────────────────

    @staticmethod
    def gen_za_idnr():
        """South African ID — 13 digits: YYMMDD + gender_seq + citizen + 8 + Luhn."""
        year   = random.randint(1950, 2005)
        month  = random.randint(1, 12)
        day    = random.randint(1, 28)
        yy     = year % 100
        gender = random.randint(0, 9999)
        citizen = 0
        base_str = f"{yy:02d}{month:02d}{day:02d}{gender:04d}{citizen}8"
        check = luhn_check_digit([int(c) for c in base_str])
        return base_str + str(check)

    # ── Canada ───────────────────────────────────────────────────────────────

    @staticmethod
    def gen_ca_bn():
        """Canadian Business Number — 9 digits with Luhn check digit."""
        d = [random.randint(1, 9)] + [random.randint(0, 9) for _ in range(7)]
        check = luhn_check_digit(d)
        return ''.join(map(str, d)) + str(check)

    # ── New Zealand ──────────────────────────────────────────────────────────

    @staticmethod
    def gen_nz_ird():
        """New Zealand IRD — 8 or 9 digits, range 10000001-149999999, MOD-11 check."""
        p_weights = [3, 2, 7, 6, 5, 4, 3, 2]
        s_weights = [7, 4, 3, 2, 5, 2, 7, 6]
        for _ in range(500):
            # Generate base in valid range: 1000001-14999999 (8 digits before check)
            base_n = random.randint(1000001, 14999999)
            d = [int(c) for c in f"{base_n:08d}"]
            s = (-sum(w * x for w, x in zip(p_weights, d))) % 11
            if s == 10:
                s = (-sum(w * x for w, x in zip(s_weights, d))) % 11
            if s <= 9:
                return ''.join(map(str, d)) + str(s)
        return "490119268"

    # ── Argentina ────────────────────────────────────────────────────────────

    @staticmethod
    def gen_ar_cuit():
        """Argentinian CUIT — 11 digits, MOD-11 check digit."""
        type_code = random.choice([20, 23, 24, 27, 30, 33, 34])
        base8 = [random.randint(0, 9) for _ in range(8)]
        weights = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
        digits = [int(x) for x in f"{type_code:02d}"] + base8
        s = sum(d * w for d, w in zip(digits, weights))
        check = 11 - s % 11
        if check == 11:
            check = 0
        elif check == 10:
            check = 9
        return f"{type_code:02d}-{''.join(map(str, base8))}-{check}"

    @staticmethod
    def gen_ar_dni():
        """Argentinian DNI — 7 or 8 digits."""
        return str(random.randint(1000000, 99999999))

    # ── Chile ────────────────────────────────────────────────────────────────

    @staticmethod
    def gen_cl_rut():
        """Chilean RUT — 7-8 digits + check digit (MOD-11, digit or 'K')."""
        n = random.randint(1000000, 25000000)
        ns = str(n)
        s = sum(int(d) * (4 + (5 - i) % 6) for i, d in enumerate(ns[::-1]))
        check = '0123456789K'[s % 11]
        return f"{n:,}".replace(',', '.') + '-' + check

    # ── Colombia ─────────────────────────────────────────────────────────────

    @staticmethod
    def gen_co_nit():
        """Colombian NIT — 9 digits + check digit (stdnum table lookup)."""
        weights = (3, 7, 13, 17, 19, 23, 29, 37, 41)
        _table  = '01987654321'
        d = [random.randint(0, 9) for _ in range(9)]
        s = sum(w * x for w, x in zip(weights, reversed(d))) % 11
        check = _table[s]
        return ''.join(map(str, d)) + check

    # ── Israel ───────────────────────────────────────────────────────────────

    @staticmethod
    def gen_il_idnr():
        """Israeli ID — 9 digits, Luhn check."""
        d = [random.randint(0, 9) for _ in range(8)]
        check = luhn_check_digit(d)
        return ''.join(map(str, d)) + str(check)

    # ── Romania ──────────────────────────────────────────────────────────────

    @staticmethod
    def gen_ro_cnp():
        """Romanian CNP — 13 digits, MOD-11 check digit."""
        weights = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]
        year  = random.randint(1950, 2005)
        month = random.randint(1, 12)
        day   = random.randint(1, 28)
        gender_century = random.choice([1, 2])  # 1=M 1900s, 2=F 1900s
        county = random.randint(1, 46)
        seq = random.randint(1, 999)
        base = f"{gender_century}{year%100:02d}{month:02d}{day:02d}{county:02d}{seq:03d}"
        s = sum(w * int(d) for w, d in zip(weights, base)) % 11
        check = 1 if s == 10 else s
        return base + str(check)

    @staticmethod
    def gen_ro_cui():
        """Romanian CUI — company identifier, MOD-11 check digit."""
        weights = [7, 5, 3, 2, 1, 7, 5, 3, 2]
        n = random.randint(1000000, 99999999)
        ns = str(n).zfill(9)
        s = 10 * sum(w * int(d) for w, d in zip(weights, ns)) % 11 % 10
        return f"RO{n}{s}"

    # ── Croatia ──────────────────────────────────────────────────────────────

    @staticmethod
    def gen_hr_oib():
        """Croatian OIB — 11 digits, ISO 7064 MOD 11,10 check."""
        for _ in range(200):
            base = [random.randint(0, 9) for _ in range(10)]
            check = iso7064_mod11_10_check(base)
            if check != 10:
                return ''.join(map(str, base)) + str(check)
        return "00000000001"

    # ── Bulgaria ─────────────────────────────────────────────────────────────

    @staticmethod
    def gen_bg_egn():
        """Bulgarian EGN — 10 digits: birth date + seq + MOD-11 check."""
        weights = [2, 4, 8, 5, 10, 9, 7, 3, 6]
        year  = random.randint(1950, 2005)
        month = random.randint(1, 12)
        day   = random.randint(1, 28)
        yy    = year % 100
        mm    = month + (20 if year >= 2000 else 0)
        seq   = random.randint(0, 999)
        base  = [int(x) for x in f"{yy:02d}{mm:02d}{day:02d}{seq:03d}"]
        s     = sum(w * d for w, d in zip(weights, base)) % 11 % 10
        return ''.join(map(str, base)) + str(s)

    # ── Lithuania ────────────────────────────────────────────────────────────

    @staticmethod
    def gen_lt_asmens():
        """Lithuanian personal code — 11 digits, same algorithm as EE IK."""
        year  = random.randint(1950, 2005)
        month = random.randint(1, 12)
        day   = random.randint(1, 28)
        gender = random.choice([3, 4])  # 3=M 1900s, 4=F 1900s
        seq   = random.randint(0, 999)
        base  = [int(x) for x in f"{gender}{year%100:02d}{month:02d}{day:02d}{seq:03d}"]
        check = ee_lt_check(base)
        return ''.join(map(str, base)) + str(check)

    # ── Estonia ──────────────────────────────────────────────────────────────

    @staticmethod
    def gen_ee_ik():
        """Estonian Isikukood — 11 digits with gender/century prefix, MOD-11 check."""
        year  = random.randint(1950, 2005)
        month = random.randint(1, 12)
        day   = random.randint(1, 28)
        gender = random.choice([3, 4])  # 3=M 1900s, 4=F 1900s
        seq   = random.randint(0, 999)
        base  = [int(x) for x in f"{gender}{year%100:02d}{month:02d}{day:02d}{seq:03d}"]
        check = ee_lt_check(base)
        return ''.join(map(str, base)) + str(check)

    # ── Portugal ─────────────────────────────────────────────────────────────

    @staticmethod
    def gen_pt_cc():
        """Portuguese Citizen Card — 8 digits + 2 letters + 1 check digit."""
        alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        n     = random.randint(10000000, 99999999)
        sfx   = ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(2))
        base  = str(n) + '0' + sfx
        # calc_check_digit using stdnum's cutoff algorithm
        def cutoff(x):
            return x - 9 if x > 9 else x
        s = sum(
            cutoff(alphabet.index(c) * 2) if i % 2 == 0 else alphabet.index(c)
            for i, c in enumerate(base[::-1])
        )
        check = str((10 - s) % 10)
        return f"{n} 0 {sfx}{check}"

    # ── Egypt ────────────────────────────────────────────────────────────────

    @staticmethod
    def gen_eg_tn():
        """Egyptian Tax Registration Number — 9 digits."""
        return ''.join(str(random.randint(0, 9)) for _ in range(9))

    # ── Dispatch ─────────────────────────────────────────────────────────────

    def generate(self, data_type, **kwargs):
        _MAP = {
            'br_cpf':           self.gen_br_cpf,
            'br_cnpj':          self.gen_br_cnpj,
            'in_pan':           self.gen_in_pan,
            'in_aadhaar':       self.gen_in_aadhaar,
            'in_gstin':         self.gen_in_gstin,
            'in_epic':          self.gen_in_epic,
            'cn_ric':           self.gen_cn_ric,
            'mx_curp':          self.gen_mx_curp,
            'mx_rfc':           self.gen_mx_rfc,
            'it_codicefiscale': self.gen_it_codicefiscale,
            'es_dni':           self.gen_es_dni,
            'es_nie':           self.gen_es_nie,
            'es_ccc':           self.gen_es_ccc,
            'de_idnr':          self.gen_de_idnr,
            'de_stnr':          self.gen_de_stnr,
            'pk_cnic':          self.gen_pk_cnic,
            'jp_cn':            self.gen_jp_cn,
            'jp_in':            self.gen_jp_in,
            'kr_rrn':           self.gen_kr_rrn,
            'kr_brn':           self.gen_kr_brn,
            'nl_bsn':           self.gen_nl_bsn,
            'pl_pesel':         self.gen_pl_pesel,
            'se_personnummer':  self.gen_se_personnummer,
            'dk_cpr':           self.gen_dk_cpr,
            'fi_hetu':          self.gen_fi_hetu,
            'no_fodselsnummer': self.gen_no_fodselsnummer,
            'au_abn':           self.gen_au_abn,
            'au_tfn':           self.gen_au_tfn,
            'au_acn':           self.gen_au_acn,
            'my_nric':          self.gen_my_nric,
            'th_pin':           self.gen_th_pin,
            'th_tin':           self.gen_th_tin,
            'sg_uen':           self.gen_sg_uen,
            'za_idnr':          self.gen_za_idnr,
            'ca_bn':            self.gen_ca_bn,
            'nz_ird':           self.gen_nz_ird,
            'ar_cuit':          self.gen_ar_cuit,
            'ar_dni':           self.gen_ar_dni,
            'cl_rut':           self.gen_cl_rut,
            'co_nit':           self.gen_co_nit,
            'il_idnr':          self.gen_il_idnr,
            'ro_cnp':           self.gen_ro_cnp,
            'ro_cui':           self.gen_ro_cui,
            'hr_oib':           self.gen_hr_oib,
            'bg_egn':           self.gen_bg_egn,
            'lt_asmens':        self.gen_lt_asmens,
            'ee_ik':            self.gen_ee_ik,
            'pt_cc':            self.gen_pt_cc,
            'eg_tn':            self.gen_eg_tn,
        }
        fn = _MAP.get(data_type)
        return fn() if fn else f"ERROR: Unknown intl_id type '{data_type}'"
