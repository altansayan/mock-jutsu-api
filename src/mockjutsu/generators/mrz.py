"""
mock-jutsu — MRZ (Machine Readable Zone) Generator
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)

ICAO Document 9303 compliant Machine Readable Travel Documents:
  mrz_td3 — Passport MRZ: 2 lines × 44 characters (ICAO 9303 Part 3)
  mrz_td1 — ID Card MRZ:  3 lines × 30 characters (ICAO 9303 Part 5)

Check digit algorithm (ICAO 9303 Section 4.9):
  weights = [7, 3, 1] repeating
  char_val: '0'-'9' → 0-9, 'A'-'Z' → 10-35, '<' → 0
  check_digit = sum(char_val × weight) % 10

Zero external dependencies: json, random (stdlib only).
"""

import json
import random


# ── Check digit ───────────────────────────────────────────────────────────────

_WEIGHTS = [7, 3, 1]


def _char_val(c: str) -> int:
    if c == '<':
        return 0
    if c.isdigit():
        return int(c)
    return ord(c) - ord('A') + 10


def _check_digit(s: str) -> str:
    total = sum(_char_val(c) * _WEIGHTS[i % 3] for i, c in enumerate(s))
    return str(total % 10)


# ── Data pools ────────────────────────────────────────────────────────────────

_COUNTRIES = [
    'TUR', 'USA', 'GBR', 'DEU', 'FRA', 'RUS', 'CHN', 'JPN', 'ITA', 'ESP',
    'CAN', 'AUS', 'BRA', 'IND', 'KOR', 'NLD', 'BEL', 'SWE', 'NOR', 'CHE',
    'AUT', 'POL', 'CZE', 'HUN', 'PRT', 'GRC', 'FIN', 'DNK', 'UKR', 'IRN',
]

_SURNAMES = [
    'SMITH', 'JOHNSON', 'WILLIAMS', 'BROWN', 'JONES', 'GARCIA', 'MILLER',
    'DAVIS', 'WILSON', 'TAYLOR', 'YILMAZ', 'DEMIR', 'KAYA', 'SAHIN', 'CELIK',
    'MUELLER', 'SCHMIDT', 'FISCHER', 'WEBER', 'MARTIN', 'BERNARD', 'THOMAS',
    'IVANOV', 'SMIRNOV', 'KUZNETSOV', 'TANAKA', 'YAMAMOTO', 'NAKAMURA',
    'WANG', 'LI', 'ZHANG', 'ROSSI', 'FERRARI', 'ESPOSITO',
]

_GIVEN_NAMES = [
    'JOHN', 'JAMES', 'ROBERT', 'MICHAEL', 'WILLIAM', 'DAVID', 'RICHARD',
    'JOSEPH', 'THOMAS', 'CHARLES', 'MARY', 'PATRICIA', 'JENNIFER', 'LINDA',
    'BARBARA', 'ELIZABETH', 'SUSAN', 'JESSICA', 'SARAH', 'KAREN',
    'AHMET', 'MEHMET', 'MUSTAFA', 'ALI', 'AYSE', 'FATMA', 'ZEYNEP',
    'HANS', 'PETRA', 'ANNA', 'IVAN', 'OLGA', 'YUKI', 'HIROSHI',
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _pad(s: str, length: int, fill: str = '<') -> str:
    """Right-pad or truncate string to exactly `length` characters."""
    s = s[:length]
    return s + fill * (length - len(s))


def _mrz_name(surname: str, given: str, total_len: int) -> str:
    """Format name field: SURNAME<<GIVENNAME padded to total_len."""
    name = f"{surname}<<{given}"
    return _pad(name, total_len)


def _random_doc_number() -> str:
    """Generate 9-char alphanumeric document number (uppercase + digits + <)."""
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    prefix = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=2))
    digits = ''.join(random.choices('0123456789', k=7))
    return prefix + digits


def _random_date(past: bool = False) -> str:
    """Generate YYMMDD. past=True → birth date, past=False → expiry (future)."""
    if past:
        yy = random.randint(40, 99)    # 1940-1999
        yy2 = random.randint(0, 9)
        yy = random.choice([yy, yy2 + 0])
        # Combine: birth years 40-99 or 00-09
        yy = random.choice([
            str(random.randint(40, 99)),
            f"0{random.randint(0, 9)}",
        ])
    else:
        # Expiry: future (2026-2035)
        yy = str(random.randint(26, 35))
    mm = f"{random.randint(1, 12):02d}"
    dd = f"{random.randint(1, 28):02d}"   # 28 to avoid invalid dates
    return yy + mm + dd


def _random_personal_number() -> str:
    """14-char personal number field, may be all filler '<'."""
    if random.random() < 0.4:
        return '<' * 14
    n = random.randint(6, 14)
    chars = ''.join(random.choices('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=n))
    return _pad(chars, 14)


# ── TD3 Passport (2 × 44) ─────────────────────────────────────────────────────

def generate_mrz_td3() -> str:
    """
    ICAO 9303 Part 3 — Passport TD3 MRZ, 2 lines × 44 characters.

    Line 1: P<CCC + surname<<givennames (padded to 44)
    Line 2: doc_no(9)+cd + nationality(3) + dob(6)+cd + sex + expiry(6)+cd
            + personal(14)+cd + composite_cd
    """
    surname     = random.choice(_SURNAMES)
    given       = random.choice(_GIVEN_NAMES)
    country     = random.choice(_COUNTRIES)
    nationality = country

    # ── Line 1 ──────────────────────────────────────────────
    doc_type = 'P'
    subtype  = '<'
    name_field = _mrz_name(surname, given, 39)  # 44 - 5 = 39
    line1 = doc_type + subtype + country + name_field
    assert len(line1) == 44

    # ── Line 2 ──────────────────────────────────────────────
    doc_no   = _random_doc_number()       # 9 chars
    cd1      = _check_digit(doc_no)       # [9]

    dob      = _random_date(past=True)    # YYMMDD [13:19]
    cd_dob   = _check_digit(dob)          # [19]

    sex      = random.choice(['M', 'F', '<'])

    expiry   = _random_date(past=False)   # YYMMDD [21:27]
    cd_exp   = _check_digit(expiry)       # [27]

    personal = _random_personal_number()  # 14 chars [28:42]
    cd_per   = _check_digit(personal)     # [42]

    # Composite covers: line2[0:10] + line2[13:20] + line2[21:43]
    # = doc_no+cd1 + dob+cd_dob + expiry+cd_exp+personal+cd_per (sex excluded)
    composite_input = (doc_no + cd1 +
                       dob    + cd_dob +
                       expiry + cd_exp +
                       personal + cd_per)
    cd_comp = _check_digit(composite_input)  # [43]

    line2 = (doc_no + cd1 +
             nationality +
             dob    + cd_dob +
             sex    +
             expiry + cd_exp +
             personal + cd_per +
             cd_comp)
    assert len(line2) == 44

    return json.dumps({
        'mrz_type':   'TD3',
        'lines':      [line1, line2],
        'surname':    surname,
        'given_names': given,
        'nationality': nationality,
        'doc_number':  doc_no,
        'dob':         dob,
        'sex':         sex,
        'expiry':      expiry,
    }, ensure_ascii=False)


# ── TD1 ID Card (3 × 30) ──────────────────────────────────────────────────────

def generate_mrz_td1() -> str:
    """
    ICAO 9303 Part 5 — ID Card TD1 MRZ, 3 lines × 30 characters.

    Line 1: doc_type(2) + country(3) + doc_no(9)+cd + optional_data(15)
    Line 2: dob(6)+cd + sex + expiry(6)+cd + nationality(3) + optional(11) + composite_cd
    Line 3: surname<<givennames (padded to 30)
    """
    surname     = random.choice(_SURNAMES)
    given       = random.choice(_GIVEN_NAMES)
    country     = random.choice(_COUNTRIES)
    nationality = country

    doc_type_char = random.choice(['I', 'A', 'C'])
    doc_subtype   = '<'

    doc_no   = _random_doc_number()   # 9 chars
    cd1      = _check_digit(doc_no)   # [14]

    # optional_data in line 1: 15 chars, can be all filler
    opt1 = '<' * 15

    # ── Line 1 ──────────────────────────────────────────────
    line1 = doc_type_char + doc_subtype + country + doc_no + cd1 + opt1
    assert len(line1) == 30

    # ── Line 2 ──────────────────────────────────────────────
    dob      = _random_date(past=True)    # YYMMDD [0:6]
    cd_dob   = _check_digit(dob)          # [6]

    sex      = random.choice(['M', 'F', '<'])

    expiry   = _random_date(past=False)   # YYMMDD [8:14]
    cd_exp   = _check_digit(expiry)       # [14]

    opt2     = '<' * 11

    # Composite: line1[5:30] + line2[0:7] + line2[8:29] (sex at [7] excluded)
    composite_input = (line1[5:30] +
                       dob + cd_dob +
                       expiry + cd_exp +
                       nationality + opt2)
    cd_comp = _check_digit(composite_input)  # line2[29]

    line2 = (dob + cd_dob +
             sex +
             expiry + cd_exp +
             nationality +
             opt2 +
             cd_comp)
    assert len(line2) == 30

    # ── Line 3 ──────────────────────────────────────────────
    line3 = _mrz_name(surname, given, 30)
    assert len(line3) == 30

    return json.dumps({
        'mrz_type':    'TD1',
        'lines':       [line1, line2, line3],
        'surname':     surname,
        'given_names': given,
        'nationality': nationality,
        'doc_number':  doc_no,
        'dob':         dob,
        'sex':         sex,
        'expiry':      expiry,
    }, ensure_ascii=False)


# ── Generator class ────────────────────────────────────────────────────────────

class MrzGenerator:
    """ICAO 9303 Machine Readable Zone generator (TD3 Passport + TD1 ID Card)."""

    def generate(self, data_type: str, **kwargs) -> str:
        if data_type == 'mrz_td3':
            return generate_mrz_td3()
        if data_type == 'mrz_td1':
            return generate_mrz_td1()
        return f"ERROR: Unknown type '{data_type}'"
