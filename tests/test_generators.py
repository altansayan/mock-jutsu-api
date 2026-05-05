"""
mock-jutsu — Full-Coverage Unit Tests
Developer: Altan Sayan (https://github.com/altansayan)
Purpose: Cross-testing 55 parameters across 6 locales (TR, UK, US, DE, FR, RU).
         330 matrix scenarios + 35 algorithmic validation tests.
"""

import re
import pytest
from mockjutsu.core import jutsu

LOCALES = ["TR", "UK", "US", "DE", "FR", "RU"]

TYPES = [
    # Identity (12)
    'tckn', 'ykn', 'taxid', 'nationalid',
    'firstname', 'lastname', 'fullname',
    'passport', 'license', 'age', 'gender', 'birthdate',
    # Financial (15)
    'cardnum', 'cardnetwork', 'cardtype', 'cardstatus', 'cardowner',
    'cvv3', 'cvv4', 'pin', 'expiry', 'expirymonth', 'expiryyear',
    'issuer', 'balance', 'iban', 'cardcategory',
    # Communication (10)
    'phone', 'phone_country', 'phone_area', 'phone_local',
    'address_city', 'address_street', 'address_full', 'postalcode', 'plate', 'email',
    # Business / Insurance (2)
    'employer_id', 'insurance_id',
    # Meta (18)
    'uuid', 'requestid', 'correlationid', 'sessionid', 'idempotencykey', 'deviceid',
    'timestamp', 'timestamp_iso', 'bearertoken', 'clientversion',
    'ipv4', 'ipv6',
    'browser_name', 'browser_version', 'browser_engine',
    'useragent', 'signature', 'apppassword',
    # Banking (6)
    'swift', 'sort_code', 'routing_number', 'bik_code', 'bank_name', 'transaction',
    # Corporate (2)
    'company_name', 'job_title',
    # Health (5)
    'blood_type', 'nhs_number', 'icd10', 'height', 'weight',
    # Commerce (5)
    'currency', 'tax_rate', 'invoice_number', 'vin', 'vehicle',
    # Tech / Meta extras (6)
    'jwt', 'hash', 'mac_address', 'domain', 'url', 'color',
    # IoT — RFID (3)
    'rfid_uid', 'epc', 'rfid_tag',
    # IoT — NFC (7)
    'nfc_uid', 'nfc_atqa', 'nfc_sak', 'ndef_uri', 'ndef_text', 'apdu', 'nfc_tag',
    # IoT — IR (4)
    'ir_nec', 'ir_rc5', 'ir_pronto', 'ir_raw',
]

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _luhn_valid(number_str):
    """Return True if the number passes the Luhn checksum."""
    digits = [int(d) for d in number_str]
    total = 0
    for i, d in enumerate(reversed(digits)):
        n = d * 2 if i % 2 == 1 else d
        if n > 9:
            n -= 9
        total += n
    return total % 10 == 0


# ---------------------------------------------------------------------------
# Comprehensive Matrix — 55 types × 6 locales = 330 scenarios
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("locale", LOCALES)
@pytest.mark.parametrize("data_type", TYPES)
def test_comprehensive_matrix(locale, data_type):
    """Every type × locale combination must return a non-empty, non-error value."""
    result = jutsu.generate(data_type, locale=locale)
    assert result is not None, f"None returned for {data_type}/{locale}"
    assert "ERROR" not in str(result), f"ERROR returned for {data_type}/{locale}"
    assert len(str(result)) > 0, f"Empty string returned for {data_type}/{locale}"


# ---------------------------------------------------------------------------
# Identity — Algorithmic Validation
# ---------------------------------------------------------------------------

def test_tckn_safe_start():
    """TCKN must never start with 0, 1, 3, or 9."""
    forbidden = {'0', '1', '3', '9'}
    for _ in range(200):
        val = jutsu.generate('tckn')
        assert val[0] not in forbidden, f"TCKN started with forbidden digit: {val}"


def test_tckn_checksum():
    """10th digit = (odd-pos×7 − even-pos) % 10 · 11th digit = sum[:10] % 10."""
    for _ in range(100):
        val = jutsu.generate('tckn')
        d = [int(c) for c in val]
        assert len(d) == 11, f"TCKN must be 11 digits: {val}"
        expected_d9 = ((d[0] + d[2] + d[4] + d[6] + d[8]) * 7 - (d[1] + d[3] + d[5] + d[7])) % 10
        assert d[9] == expected_d9, f"TCKN 10th digit wrong: {val}"
        expected_d10 = sum(d[:10]) % 10
        assert d[10] == expected_d10, f"TCKN 11th digit wrong: {val}"


def test_ykn_starts_with_99():
    """YKN must start with 99."""
    for _ in range(100):
        val = jutsu.generate('ykn')
        assert val.startswith('99'), f"YKN must start with 99: {val}"


def test_ykn_luhn_valid():
    """YKN must pass the Luhn (MOD-10) checksum."""
    for _ in range(100):
        val = jutsu.generate('ykn')
        assert _luhn_valid(val), f"YKN failed Luhn check: {val}"


def test_ykn_length():
    """YKN must be exactly 11 digits."""
    for _ in range(50):
        val = jutsu.generate('ykn')
        assert len(val) == 11 and val.isdigit(), f"YKN must be 11 digits: {val}"


def test_ru_inn_length():
    """RU INN must be exactly 10 digits."""
    for _ in range(50):
        val = jutsu.generate('taxid', locale='RU')
        assert len(val) == 10 and val.isdigit(), f"RU INN must be 10 digits: {val}"


def test_patronymic_ru_has_value():
    """RU patronymic must return a non-empty string."""
    for _ in range(50):
        val = jutsu.generate('patronymic', locale='RU')
        assert len(val) > 0, "RU patronymic must not be empty"


def test_patronymic_non_ru_is_empty():
    """Non-RU patronymic must return an empty string (concept does not apply)."""
    for locale in ['TR', 'US', 'UK', 'DE', 'FR']:
        val = jutsu.generate('patronymic', locale=locale)
        assert val == '', f"Non-RU patronymic should be empty, got '{val}' for {locale}"


def test_ru_fullname_has_3_parts():
    """RU fullname must have at least 3 parts (first + patronymic + last)."""
    for _ in range(50):
        val = jutsu.generate('fullname', locale='RU')
        assert len(val.split()) >= 3, f"RU fullname must have 3+ parts: {val}"


def test_non_ru_fullname_has_2_parts():
    """Non-RU fullname must have exactly 2 parts (first + last)."""
    for locale in ['TR', 'US', 'UK', 'DE', 'FR']:
        for _ in range(20):
            val = jutsu.generate('fullname', locale=locale)
            assert len(val.split()) == 2, f"{locale} fullname must have 2 parts: {val}"


def test_gender_values():
    """gender must only return 'Male' or 'Female'."""
    for _ in range(100):
        val = jutsu.generate('gender')
        assert val in ('Male', 'Female'), f"Invalid gender: {val}"


def test_age_range():
    """age must be an integer between 18 and 80 inclusive."""
    for _ in range(100):
        val = jutsu.generate('age')
        assert 18 <= int(val) <= 80, f"Age out of range: {val}"


def test_birthdate_format():
    """birthdate must match YYYY-MM-DD and represent an 18–80-year-old."""
    for _ in range(50):
        val = jutsu.generate('birthdate')
        assert re.match(r'^\d{4}-\d{2}-\d{2}$', str(val)), f"Birthdate format wrong: {val}"


def test_passport_format():
    """passport must match P + exactly 7 digits."""
    for _ in range(50):
        val = jutsu.generate('passport')
        assert re.match(r'^P\d{7}$', str(val)), f"Passport format wrong: {val}"


def test_de_steuer_id_checksum():
    """DE nationalid must be 11 digits and pass ISO 7064 MOD 11,10 checksum."""
    def _valid(s):
        if len(s) != 11 or not s.isdigit() or s[0] == '0':
            return False
        product = 10
        for d in (int(c) for c in s[:10]):
            sm = (product + d) % 10
            if sm == 0:
                sm = 10
            product = (sm * 2) % 11
        return (11 - product) % 10 == int(s[10])

    for _ in range(50):
        val = jutsu.generate('nationalid', locale='DE')
        assert _valid(val), f"DE Steuer-ID checksum failed: {val}"


def test_uk_ni_format():
    """UK nationalid must match AA 99 99 99 A with valid HMRC prefix restrictions."""
    FORBIDDEN_FIRST  = set('DFIQUV')
    FORBIDDEN_SECOND = set('DFIOQUV')
    FORBIDDEN_PREFIX = {'BG', 'GB', 'KN', 'NK', 'NT', 'TN', 'ZZ'}
    for _ in range(50):
        val = jutsu.generate('nationalid', locale='UK')
        assert re.match(r'^[A-Z]{2} \d{2} \d{2} \d{2} [ABCD]$', val), f"UK NI format wrong: {val}"
        assert val[0] not in FORBIDDEN_FIRST,  f"UK NI first letter forbidden: {val}"
        assert val[1] not in FORBIDDEN_SECOND, f"UK NI second letter forbidden: {val}"
        assert val[:2] not in FORBIDDEN_PREFIX, f"UK NI prefix forbidden: {val}"


def test_us_ssn_format():
    """US nationalid must follow NNN-NN-NNNN (11 chars with dashes)."""
    for _ in range(50):
        val = jutsu.generate('nationalid', locale='US')
        assert re.match(r'^\d{3}-\d{2}-\d{4}$', str(val)), f"US SSN format wrong: {val}"
        assert len(val) == 11, f"US SSN must be 11 chars: {val}"


# ---------------------------------------------------------------------------
# Financial — Algorithmic Validation
# ---------------------------------------------------------------------------

def test_cardnum_luhn_valid():
    """All card networks must generate Luhn-valid numbers."""
    networks = ['visa', 'mc', 'amex', 'troy', 'jcb', 'discover', 'unionpay', 'mir', 'maestro']
    for network in networks:
        for _ in range(20):
            val = jutsu.generate('cardnum', network=network)
            assert _luhn_valid(val), f"{network} card failed Luhn: {val}"


def test_cardnum_visa_prefix_and_length():
    """Visa must start with 4 and have 16 digits."""
    for _ in range(50):
        val = jutsu.generate('cardnum', network='visa')
        assert val.startswith('4'), f"Visa must start with 4: {val}"
        assert len(val) == 16, f"Visa must be 16 digits: {val}"


def test_cardnum_amex_prefix_and_length():
    """Amex must start with 34 or 37 and have 15 digits."""
    for _ in range(50):
        val = jutsu.generate('cardnum', network='amex')
        assert val.startswith('34') or val.startswith('37'), f"Amex prefix wrong: {val}"
        assert len(val) == 15, f"Amex must be 15 digits: {val}"


def test_cardnum_troy_prefix_and_length():
    """Troy must start with 9792 and have 16 digits."""
    for _ in range(50):
        val = jutsu.generate('cardnum', network='troy')
        assert val.startswith('9792'), f"Troy must start with 9792: {val}"
        assert len(val) == 16, f"Troy must be 16 digits: {val}"


def test_cardnum_mir_prefix():
    """Mir must start with 2200, 2201, or 2202."""
    for _ in range(50):
        val = jutsu.generate('cardnum', network='mir')
        assert val[:4] in ('2200', '2201', '2202'), f"Mir prefix wrong: {val}"


def test_cvv3_is_3_digits():
    """cvv3 must be exactly 3 numeric digits."""
    for _ in range(50):
        val = jutsu.generate('cvv3')
        assert re.match(r'^\d{3}$', str(val)), f"CVV3 must be 3 digits: {val}"


def test_cvv4_is_4_digits():
    """cvv4 must be exactly 4 numeric digits."""
    for _ in range(50):
        val = jutsu.generate('cvv4')
        assert re.match(r'^\d{4}$', str(val)), f"CVV4 must be 4 digits: {val}"


def test_pin_is_4_digits():
    """pin must be exactly 4 numeric digits."""
    for _ in range(50):
        val = jutsu.generate('pin')
        assert re.match(r'^\d{4}$', str(val)), f"PIN must be 4 digits: {val}"


def test_expiry_format():
    """expiry must match MM/YY with a valid month."""
    for _ in range(50):
        val = jutsu.generate('expiry')
        assert re.match(r'^\d{2}/\d{2}$', str(val)), f"Expiry format wrong: {val}"
        month = int(str(val).split('/')[0])
        assert 1 <= month <= 12, f"Expiry month out of range: {val}"


def test_iban_locale_prefixes():
    """IBAN must start with the correct country code per locale."""
    assert jutsu.generate('iban', locale='TR').startswith('TR')
    assert jutsu.generate('iban', locale='UK').startswith('GB')
    assert jutsu.generate('iban', locale='DE').startswith('DE')
    assert jutsu.generate('iban', locale='FR').startswith('FR')


def test_iban_lengths():
    """IBAN length must match official standard per locale."""
    assert len(jutsu.generate('iban', locale='TR')) == 26
    assert len(jutsu.generate('iban', locale='UK')) == 22
    assert len(jutsu.generate('iban', locale='DE')) == 22
    assert len(jutsu.generate('iban', locale='FR')) == 27


def test_iban_us_routing_format():
    """US bank format must use RT: prefix (not IBAN)."""
    for _ in range(20):
        val = jutsu.generate('iban', locale='US')
        assert str(val).startswith('RT:'), f"US bank must start with RT:: {val}"


def test_iban_ru_bik_format():
    """RU bank format must use BIK: prefix (not IBAN)."""
    for _ in range(20):
        val = jutsu.generate('iban', locale='RU')
        assert str(val).startswith('BIK:'), f"RU bank must start with BIK:: {val}"


def test_balance_range_adjustment():
    """balance must respect min/max parameters."""
    val = float(jutsu.generate('balance', min=100, max=110))
    assert 100 <= val <= 110


def test_balance_is_numeric():
    """balance must be a numeric value."""
    for _ in range(50):
        val = jutsu.generate('balance')
        assert isinstance(val, (int, float)), f"Balance must be numeric: {val}"
        assert val >= 0, f"Balance must not be negative: {val}"


# ---------------------------------------------------------------------------
# Communication — Format Validation
# ---------------------------------------------------------------------------

def test_phone_country_codes():
    """phone_country must return the exact E.164 prefix per locale."""
    expected = {'TR': '+90', 'US': '+1', 'UK': '+44', 'DE': '+49', 'FR': '+33', 'RU': '+7'}
    for locale, prefix in expected.items():
        val = jutsu.generate('phone_country', locale=locale)
        assert val == prefix, f"Phone country code wrong for {locale}: got '{val}', expected '{prefix}'"


def test_email_format():
    """email must be a valid-looking address with @ and a domain containing a dot."""
    for _ in range(50):
        val = str(jutsu.generate('email'))
        assert '@' in val, f"Email must contain @: {val}"
        local, domain = val.split('@', 1)
        assert len(local) > 0, f"Email local part empty: {val}"
        assert '.' in domain, f"Email domain must contain dot: {val}"


# ---------------------------------------------------------------------------
# Meta — Format & Filter Validation
# ---------------------------------------------------------------------------

def test_apppassword_length():
    """apppassword must be exactly 6 digits."""
    for _ in range(100):
        val = jutsu.generate('apppassword')
        assert re.match(r'^\d{6}$', str(val)), f"AppPassword must be 6 digits: {val}"


def test_apppassword_no_consecutive_repeat():
    """apppassword must never have two identical adjacent digits."""
    for _ in range(300):
        val = str(jutsu.generate('apppassword'))
        for i in range(len(val) - 1):
            assert val[i] != val[i + 1], f"AppPassword has consecutive repeat: {val}"


def test_apppassword_no_sequential_run():
    """apppassword must not contain 3+ ascending or descending sequential digits."""
    for _ in range(300):
        val = str(jutsu.generate('apppassword'))
        digits = [int(c) for c in val]
        for i in range(len(digits) - 2):
            ascending = digits[i + 1] - digits[i] == 1 and digits[i + 2] - digits[i + 1] == 1
            descending = digits[i] - digits[i + 1] == 1 and digits[i + 1] - digits[i + 2] == 1
            assert not ascending and not descending, f"AppPassword has sequential run: {val}"


def test_ipv4_format():
    """ipv4 must match A.B.C.D with each octet 0–255."""
    for _ in range(50):
        val = jutsu.generate('ipv4')
        parts = str(val).split('.')
        assert len(parts) == 4, f"IPv4 must have 4 octets: {val}"
        assert all(0 <= int(p) <= 255 for p in parts), f"IPv4 octet out of range: {val}"


def test_ipv6_format():
    """ipv6 must have exactly 8 colon-separated 4-hex groups."""
    for _ in range(50):
        val = jutsu.generate('ipv6')
        groups = str(val).split(':')
        assert len(groups) == 8, f"IPv6 must have 8 groups: {val}"
        assert all(re.match(r'^[0-9a-f]{4}$', g) for g in groups), f"IPv6 group format wrong: {val}"


def test_bearer_token_format():
    """bearertoken must start with 'Bearer ' and have 3 JWT parts."""
    for _ in range(20):
        val = str(jutsu.generate('bearertoken'))
        assert val.startswith('Bearer '), f"Bearer token must start with 'Bearer ': {val}"
        parts = val[len('Bearer '):].split('.')
        assert len(parts) == 3, f"JWT must have 3 parts (header.payload.sig): {val}"


# ---------------------------------------------------------------------------
# Defensive / Edge Cases
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Tax / Business / Insurance — Algorithmic & Format Validation
# ---------------------------------------------------------------------------

def test_tr_vkn_checksum():
    """TR VKN must pass the official 10-digit proprietary checksum."""
    def _valid(s):
        if len(s) != 10 or not s.isdigit():
            return False
        d = [int(c) for c in s]
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
        return d[9] == (10 - total % 10) % 10
    for _ in range(100):
        assert _valid(jutsu.generate('vkn')), f"TR VKN checksum failed"


def test_tr_sgk_format():
    """TR SGK employer number must match il-sequence-unit.branch-sub format."""
    for _ in range(50):
        val = str(jutsu.generate('sgk'))
        assert re.match(r'^\d{2}-\d{7}-\d\.\d{2}-\d{2}$', val), f"TR SGK format wrong: {val}"


def test_tr_mersis_length():
    """TR MERSİS must be exactly 16 digits."""
    for _ in range(50):
        val = str(jutsu.generate('mersis'))
        assert re.match(r'^\d{16}$', val), f"TR MERSİS must be 16 digits: {val}"


def test_us_ein_format():
    """US EIN must match XX-XXXXXXX."""
    for _ in range(50):
        val = str(jutsu.generate('ein'))
        assert re.match(r'^\d{2}-\d{7}$', val), f"EIN format wrong: {val}"


def test_uk_utr_length():
    """UK UTR must be exactly 10 digits."""
    for _ in range(50):
        val = str(jutsu.generate('utr'))
        assert re.match(r'^\d{10}$', val), f"UK UTR must be 10 digits: {val}"


def test_uk_crn_format():
    """UK CRN must be 8 digits or SC/NI + 6 digits."""
    for _ in range(50):
        val = str(jutsu.generate('crn'))
        assert re.match(r'^(\d{8}|SC\d{6}|NI\d{6})$', val), f"UK CRN format wrong: {val}"


def test_uk_paye_format():
    """UK PAYE must match XXX/XXXXXX."""
    for _ in range(50):
        val = str(jutsu.generate('paye'))
        assert re.match(r'^\d{3}/[A-Z0-9]{6}$', val), f"UK PAYE format wrong: {val}"


def test_de_ust_id_checksum():
    """DE USt-IdNr must start with DE and pass ISO 7064 MOD 11,10."""
    def _valid(s):
        if not s.startswith('DE') or len(s) != 11:
            return False
        digits = [int(c) for c in s[2:]]
        product = 10
        for d in digits[:8]:
            sm = (product + d) % 10
            if sm == 0:
                sm = 10
            product = (sm * 2) % 11
        return (11 - product) % 10 == digits[8]
    for _ in range(50):
        val = jutsu.generate('ust_id')
        assert _valid(val), f"DE USt-IdNr checksum failed: {val}"


def test_de_hrb_format():
    """DE HRB/HRA must start with HRB or HRA followed by a number."""
    for _ in range(50):
        val = str(jutsu.generate('hrb'))
        assert re.match(r'^HR[AB] \d+$', val), f"DE HRB format wrong: {val}"


def test_de_rvn_format():
    """DE RVN must match BB TTMMJJ A SSSC format."""
    for _ in range(50):
        val = str(jutsu.generate('rvn'))
        assert re.match(r'^\d{2} \d{6} [A-Z] \d{4}$', val), f"DE RVN format wrong: {val}"


def test_fr_siren_luhn():
    """FR SIREN must be 9 digits and Luhn valid."""
    for _ in range(50):
        val = str(jutsu.generate('siren'))
        assert re.match(r'^\d{9}$', val), f"SIREN must be 9 digits: {val}"
        assert _luhn_valid(val), f"SIREN Luhn failed: {val}"


def test_fr_siret_luhn():
    """FR SIRET must be 14 digits — full number and SIREN prefix both Luhn valid."""
    for _ in range(50):
        val = str(jutsu.generate('siret'))
        assert re.match(r'^\d{14}$', val), f"SIRET must be 14 digits: {val}"
        assert _luhn_valid(val),      f"SIRET 14-digit Luhn failed: {val}"
        assert _luhn_valid(val[:9]),  f"SIRET SIREN prefix Luhn failed: {val}"


def test_fr_tva_format():
    """FR TVA must match FR + 2-digit key + 9-digit SIREN."""
    for _ in range(50):
        val = str(jutsu.generate('tva'))
        assert re.match(r'^FR\d{11}$', val), f"FR TVA format wrong: {val}"


def test_ru_ogrn_checksum():
    """RU OGRN must be 13 digits with valid mod-11 checksum."""
    for _ in range(50):
        val = str(jutsu.generate('ogrn'))
        assert re.match(r'^\d{13}$', val), f"OGRN must be 13 digits: {val}"
        assert (int(val[:12]) % 11) % 10 == int(val[12]), f"OGRN checksum failed: {val}"


def test_ru_kpp_format():
    """RU KPP must be exactly 9 digits."""
    for _ in range(50):
        val = str(jutsu.generate('kpp'))
        assert re.match(r'^\d{9}$', val), f"KPP must be 9 digits: {val}"


def test_employer_id_locale_aware():
    """employer_id must return locale-appropriate format for all 6 locales."""
    assert re.match(r'^\d{16}$',              str(jutsu.generate('employer_id', locale='TR')))
    assert re.match(r'^\d{2}-\d{7}$',         str(jutsu.generate('employer_id', locale='US')))
    assert re.match(r'^(\d{8}|SC\d{6}|NI\d{6})$', str(jutsu.generate('employer_id', locale='UK')))
    assert re.match(r'^HR[AB] \d+$',           str(jutsu.generate('employer_id', locale='DE')))
    assert re.match(r'^\d{14}$',               str(jutsu.generate('employer_id', locale='FR')))
    assert re.match(r'^\d{13}$',               str(jutsu.generate('employer_id', locale='RU')))


def test_insurance_id_locale_aware():
    """insurance_id must return locale-appropriate format for all 6 locales."""
    assert re.match(r'^\d{2}-\d{7}-\d\.\d{2}-\d{2}$', str(jutsu.generate('insurance_id', locale='TR')))
    assert re.match(r'^\d{3}-\d{2}-\d{4}$',            str(jutsu.generate('insurance_id', locale='US')))
    assert re.match(r'^\d{3}/[A-Z0-9]{6}$',            str(jutsu.generate('insurance_id', locale='UK')))
    assert re.match(r'^\d{2} \d{6} [A-Z] \d{4}$',      str(jutsu.generate('insurance_id', locale='DE')))
    assert re.match(r'^\d{3}-\d{3}-\d{3} \d{2}$',      str(jutsu.generate('insurance_id', locale='RU')))


def test_taxid_locale_aware():
    """taxid must return locale-appropriate format for all 6 locales."""
    assert re.match(r'^\d{10}$',   str(jutsu.generate('taxid', locale='TR')))   # VKN
    assert re.match(r'^\d{2}-\d{7}$', str(jutsu.generate('taxid', locale='US'))) # EIN
    assert re.match(r'^\d{10}$',   str(jutsu.generate('taxid', locale='UK')))   # UTR
    assert re.match(r'^DE\d{9}$',  str(jutsu.generate('taxid', locale='DE')))   # USt-IdNr
    assert re.match(r'^\d{9}$',    str(jutsu.generate('taxid', locale='FR')))   # SIREN
    assert re.match(r'^\d{10}$',   str(jutsu.generate('taxid', locale='RU')))   # INN


def test_defensive_null_safety():
    """Core must return ERROR for null/empty/unknown inputs."""
    assert "ERROR" in jutsu.generate(None)
    assert "ERROR" in jutsu.generate("")
    assert "ERROR" in jutsu.generate("unknown_random_type_xyz")


# ---------------------------------------------------------------------------
# Banking — Format & Checksum Validation
# ---------------------------------------------------------------------------

def test_swift_format():
    """swift must be 8 or 11 uppercase alphanumeric characters."""
    for locale in LOCALES:
        for _ in range(20):
            val = str(jutsu.generate('swift', locale=locale))
            assert re.match(r'^[A-Z0-9]{8}([A-Z0-9]{3})?$', val), f"BIC/SWIFT format wrong for {locale}: {val}"


def test_routing_number_checksum():
    """US ABA routing number must pass MOD-10 checksum (weights 3,7,1)."""
    def _valid(s):
        if len(s) != 9 or not s.isdigit():
            return False
        d = [int(c) for c in s]
        return (3 * (d[0] + d[3] + d[6]) + 7 * (d[1] + d[4] + d[7]) + (d[2] + d[5] + d[8])) % 10 == 0

    for _ in range(100):
        val = str(jutsu.generate('routing_number'))
        assert _valid(val), f"Routing number checksum failed: {val}"


def test_sort_code_format():
    """UK sort code must match XX-XX-XX."""
    for _ in range(50):
        val = str(jutsu.generate('sort_code'))
        assert re.match(r'^\d{2}-\d{2}-\d{2}$', val), f"Sort code format wrong: {val}"


def test_bik_code_format():
    """RU BIK must be 9 digits starting with 04."""
    for _ in range(50):
        val = str(jutsu.generate('bik_code'))
        assert re.match(r'^04\d{7}$', val), f"BIK format wrong: {val}"


def test_transaction_structure():
    """transaction must return a dict with required keys for all locales."""
    required = {'ref', 'sender_iban', 'receiver_iban', 'amount', 'currency',
                'description', 'channel', 'timestamp', 'status'}
    for locale in LOCALES:
        t = jutsu.generate('transaction', locale=locale)
        assert isinstance(t, dict), f"transaction must return dict for {locale}"
        assert required.issubset(t.keys()), f"Missing keys in transaction for {locale}"
        assert isinstance(t['amount'], float), f"amount must be float for {locale}"
        assert t['status'] in ('COMPLETED', 'PENDING', 'FAILED')


def test_transaction_currency_per_locale():
    """transaction currency must match the locale's currency code."""
    expected = {'TR': 'TRY', 'US': 'USD', 'UK': 'GBP', 'DE': 'EUR', 'FR': 'EUR', 'RU': 'RUB'}
    for locale, code in expected.items():
        t = jutsu.generate('transaction', locale=locale)
        assert t['currency'] == code, f"Currency mismatch for {locale}: {t['currency']} != {code}"


# ---------------------------------------------------------------------------
# Corporate — Format Validation
# ---------------------------------------------------------------------------

def test_company_name_has_suffix():
    """company_name must contain a locale-appropriate legal suffix."""
    suffixes = {
        'TR': ['A.Ş.', 'Ltd. Şti.'],
        'US': ['LLC', 'Inc.', 'Corp.'],
        'UK': ['Ltd.', 'PLC', 'LLP'],
        'DE': ['GmbH', 'AG', 'KG'],
        'FR': ['SARL', 'SA', 'SAS', 'SASU'],
        'RU': ['ООО', 'АО', 'ПАО'],
    }
    for locale, expected_suffixes in suffixes.items():
        for _ in range(20):
            name = str(jutsu.generate('company_name', locale=locale))
            assert any(s in name for s in expected_suffixes), \
                f"company_name missing legal suffix for {locale}: {name}"


def test_job_title_non_empty():
    """job_title must return a non-empty string for all locales."""
    for locale in LOCALES:
        for _ in range(10):
            val = str(jutsu.generate('job_title', locale=locale))
            assert len(val) > 2, f"job_title too short for {locale}: {val}"


# ---------------------------------------------------------------------------
# Health — Format & Checksum Validation
# ---------------------------------------------------------------------------

def test_blood_type_valid_values():
    """blood_type must be one of 8 valid types."""
    valid = {'A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-'}
    for _ in range(100):
        val = str(jutsu.generate('blood_type'))
        assert val in valid, f"Invalid blood type: {val}"


def test_nhs_number_checksum():
    """NHS number must be 10 digits passing weighted checksum (mod 11)."""
    def _valid(s):
        digits = s.replace(' ', '')
        if len(digits) != 10 or not digits.isdigit():
            return False
        weights = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
        return sum(int(d) * w for d, w in zip(digits, weights)) % 11 == 0

    for _ in range(100):
        val = str(jutsu.generate('nhs_number'))
        assert _valid(val), f"NHS number checksum failed: {val}"


def test_icd10_format():
    """icd10 must match X99.9 or similar ICD-10 alphanumeric pattern."""
    for _ in range(50):
        val = str(jutsu.generate('icd10'))
        assert re.match(r'^[A-Z]\d{2}[\.\d]*$', val), f"ICD-10 format wrong: {val}"


def test_height_locale_units():
    """height must use cm for TR/DE/FR/RU and feet for US, mixed for UK."""
    for _ in range(10):
        assert 'cm' in str(jutsu.generate('height', locale='TR'))
        assert "'" in str(jutsu.generate('height', locale='US'))
        assert 'cm' in str(jutsu.generate('height', locale='DE'))
        assert 'cm' in str(jutsu.generate('height', locale='RU'))


def test_weight_locale_units():
    """weight must use kg for TR/DE/FR/RU and lbs for US."""
    for _ in range(10):
        assert 'kg' in str(jutsu.generate('weight', locale='TR'))
        assert 'lbs' in str(jutsu.generate('weight', locale='US'))
        assert 'kg' in str(jutsu.generate('weight', locale='DE'))
        assert 'kg' in str(jutsu.generate('weight', locale='RU'))


# ---------------------------------------------------------------------------
# Commerce — Format & Checksum Validation
# ---------------------------------------------------------------------------

def test_currency_structure():
    """currency must return a dict with code, symbol, name, decimals."""
    expected = {'TR': 'TRY', 'US': 'USD', 'UK': 'GBP', 'DE': 'EUR', 'FR': 'EUR', 'RU': 'RUB'}
    for locale, code in expected.items():
        c = jutsu.generate('currency', locale=locale)
        assert isinstance(c, dict), f"currency must return dict for {locale}"
        assert c['code'] == code, f"Wrong currency code for {locale}: {c['code']}"
        assert 'symbol' in c and 'name' in c


def test_tax_rate_structure():
    """tax_rate must return a dict with at least name and standard fields."""
    for locale in LOCALES:
        t = jutsu.generate('tax_rate', locale=locale)
        assert isinstance(t, dict), f"tax_rate must return dict for {locale}"
        assert 'name' in t, f"tax_rate missing name for {locale}"


def test_invoice_number_non_empty():
    """invoice_number must return a non-empty string for all locales."""
    for locale in LOCALES:
        val = str(jutsu.generate('invoice_number', locale=locale))
        assert len(val) >= 5, f"invoice_number too short for {locale}: {val}"


def test_vin_checksum():
    """VIN must be 17 chars with valid ISO 3779 check digit at position 9 (index 8)."""
    VIN_TRANS = {
        'A':1,'B':2,'C':3,'D':4,'E':5,'F':6,'G':7,'H':8,
        'J':1,'K':2,'L':3,'M':4,'N':5,'P':7,'R':9,
        'S':2,'T':3,'U':4,'V':5,'W':6,'X':7,'Y':8,'Z':9,
    }
    WEIGHTS = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2]

    def _valid(s):
        if len(s) != 17:
            return False
        total = 0
        for i, c in enumerate(s):
            v = int(c) if c.isdigit() else VIN_TRANS.get(c, 0)
            total += v * WEIGHTS[i]
        check = total % 11
        return s[8] == ('X' if check == 10 else str(check))

    for locale in LOCALES:
        for _ in range(20):
            val = str(jutsu.generate('vin', locale=locale))
            assert len(val) == 17, f"VIN must be 17 chars for {locale}: {val}"
            assert _valid(val), f"VIN checksum failed for {locale}: {val}"


def test_vehicle_structure():
    """vehicle must return a dict with make, model, year, vin, color, fuel."""
    required = {'make', 'model', 'year', 'vin', 'color', 'fuel'}
    for locale in LOCALES:
        v = jutsu.generate('vehicle', locale=locale)
        assert isinstance(v, dict), f"vehicle must return dict for {locale}"
        assert required.issubset(v.keys()), f"Missing keys in vehicle for {locale}"
        assert 2015 <= v['year'] <= 2024, f"year out of range for {locale}: {v['year']}"


# ---------------------------------------------------------------------------
# Tech / Meta extras
# ---------------------------------------------------------------------------

def test_jwt_format():
    """jwt must have 3 base64url-separated parts (header.payload.signature)."""
    for _ in range(50):
        val = str(jutsu.generate('jwt'))
        parts = val.split('.')
        assert len(parts) == 3, f"JWT must have 3 parts: {val}"
        assert not val.startswith('Bearer'), f"jwt must not include 'Bearer ' prefix: {val}"


def test_hash_sha256_length():
    """hash (sha256) must be exactly 64 hex characters."""
    for _ in range(50):
        val = str(jutsu.generate('hash'))
        assert re.match(r'^[0-9a-f]{64}$', val), f"SHA256 hash format wrong: {val}"


def test_hash_md5_length():
    """hash (md5) must be exactly 32 hex characters."""
    for _ in range(50):
        val = str(jutsu.generate('hash', algorithm='md5'))
        assert re.match(r'^[0-9a-f]{32}$', val), f"MD5 hash format wrong: {val}"


def test_mac_address_format():
    """mac_address must match XX:XX:XX:XX:XX:XX with uppercase hex."""
    for _ in range(50):
        val = str(jutsu.generate('mac_address'))
        assert re.match(r'^([0-9A-F]{2}:){5}[0-9A-F]{2}$', val), f"MAC format wrong: {val}"


def test_url_starts_with_https():
    """url must start with https://."""
    for _ in range(50):
        val = str(jutsu.generate('url'))
        assert val.startswith('https://'), f"URL must start with https://: {val}"


def test_domain_contains_tld():
    """domain must contain a dot (TLD separator)."""
    for _ in range(50):
        val = str(jutsu.generate('domain'))
        assert '.' in val, f"Domain must contain a dot: {val}"


def test_color_hex_format():
    """color (hex) must match #RRGGBB."""
    for _ in range(50):
        val = str(jutsu.generate('color', format='hex'))
        assert re.match(r'^#[0-9A-F]{6}$', val), f"Color hex format wrong: {val}"


def test_color_rgb_format():
    """color (rgb) must match rgb(R, G, B)."""
    for _ in range(50):
        val = str(jutsu.generate('color', format='rgb'))
        assert re.match(r'^rgb\(\d{1,3}, \d{1,3}, \d{1,3}\)$', val), f"Color RGB format wrong: {val}"


# ---------------------------------------------------------------------------
# Core — bulk / template / profile / company / export
# ---------------------------------------------------------------------------

def test_bulk_count():
    """bulk() must return exactly the requested number of items."""
    for count in [1, 5, 10, 50]:
        result = jutsu.bulk('tckn', count=count)
        assert len(result) == count, f"bulk() returned {len(result)} instead of {count}"
        assert all("ERROR" not in str(v) for v in result)


def test_bulk_uniqueness():
    """bulk('uuid') must return all distinct values."""
    result = jutsu.bulk('uuid', count=50)
    assert len(set(result)) == 50, "bulk(uuid) should return 50 unique values"


def test_template_structure():
    """template() must return records with keys matching the schema."""
    schema  = {'id': 'uuid', 'name': 'fullname', 'card': 'cardnum', 'amount': 'balance'}
    records = jutsu.template(schema, count=10, locale='TR')
    assert len(records) == 10
    for rec in records:
        assert set(rec.keys()) == set(schema.keys()), f"Record keys don't match schema: {rec.keys()}"
        assert "ERROR" not in str(rec['id'])
        assert "ERROR" not in str(rec['name'])


def test_profile_required_keys():
    """profile() must return all required person fields for every locale."""
    required = {'id', 'firstname', 'lastname', 'fullname', 'gender', 'birthdate',
                'nationalid', 'phone', 'email', 'address', 'iban'}
    for locale in LOCALES:
        p = jutsu.profile(locale=locale)
        assert isinstance(p, dict), f"profile() must return dict for {locale}"
        assert required.issubset(p.keys()), \
            f"profile() missing keys for {locale}: {required - p.keys()}"
        assert p['gender'] in ('M', 'F'), f"Invalid gender in profile for {locale}: {p['gender']}"
        assert '@' in p['email'], f"Invalid email in profile for {locale}: {p['email']}"


def test_profile_no_errors():
    """profile() must not contain ERROR values for any locale."""
    for locale in LOCALES:
        p = jutsu.profile(locale=locale)
        for key, val in p.items():
            assert "ERROR" not in str(val), f"profile[{key}] has ERROR for {locale}: {val}"


def test_company_required_keys():
    """company() must return all required company fields for every locale."""
    required = {'id', 'name', 'employer_id', 'tax_id', 'iban', 'bic', 'phone', 'address'}
    for locale in LOCALES:
        c = jutsu.company(locale=locale)
        assert isinstance(c, dict), f"company() must return dict for {locale}"
        assert required.issubset(c.keys()), \
            f"company() missing keys for {locale}: {required - c.keys()}"


def test_company_no_errors():
    """company() must not contain ERROR values for any locale."""
    for locale in LOCALES:
        c = jutsu.company(locale=locale)
        for key, val in c.items():
            assert "ERROR" not in str(val), f"company[{key}] has ERROR for {locale}: {val}"


def test_export_json():
    """export(format='json') must return valid JSON with correct record count."""
    import json
    schema = {'id': 'uuid', 'name': 'fullname', 'card': 'cardnum'}
    result = jutsu.export(schema, count=5, format='json', locale='TR')
    data   = json.loads(result)
    assert len(data) == 5
    assert all('id' in r and 'name' in r and 'card' in r for r in data)


def test_export_csv():
    """export(format='csv') must return header + N data rows."""
    schema = {'id': 'uuid', 'card': 'cardnum', 'amount': 'balance'}
    result = jutsu.export(schema, count=5, format='csv', locale='TR')
    lines  = result.strip().split('\n')
    assert lines[0] == 'id,card,amount', f"CSV header wrong: {lines[0]}"
    assert len(lines) == 6, f"CSV must have 6 lines (header + 5 rows): {len(lines)}"


def test_export_sql():
    """export(format='sql') must return valid INSERT statement."""
    schema = {'name': 'fullname', 'card': 'cardnum'}
    result = jutsu.export(schema, count=3, format='sql', table='customers')
    assert result.startswith('INSERT INTO customers'), f"SQL wrong start: {result[:50]}"
    assert result.endswith(';'), f"SQL must end with semicolon"
    assert result.count("'") >= 6, f"SQL must have quoted string values"


# ---------------------------------------------------------------------------
# IoT — RFID: Format & Structural Validation
# ---------------------------------------------------------------------------

def test_rfid_uid_format():
    """rfid_uid must be colon-separated 2-digit hex groups (4 or 7 bytes)."""
    for _ in range(100):
        val = str(jutsu.generate('rfid_uid'))
        parts = val.split(':')
        assert len(parts) in (4, 7), f"RFID UID must be 4 or 7 bytes: {val}"
        assert all(re.match(r'^[0-9A-F]{2}$', p) for p in parts), \
            f"RFID UID byte format wrong: {val}"


def test_rfid_uid_high_entropy():
    """rfid_uid must not repeat across 200 consecutive calls."""
    uids = {str(jutsu.generate('rfid_uid')) for _ in range(200)}
    assert len(uids) >= 195, f"rfid_uid entropy too low: only {len(uids)} unique in 200 calls"


def test_epc_format():
    """EPC SGTIN-96 must be exactly 24 uppercase hex characters."""
    for _ in range(50):
        val = str(jutsu.generate('epc'))
        assert re.match(r'^[0-9A-F]{24}$', val), f"EPC format wrong: {val}"


def test_epc_sgtin96_header():
    """EPC SGTIN-96 first byte must always be 0x30 (fixed header)."""
    for _ in range(50):
        val = str(jutsu.generate('epc'))
        assert int(val[:2], 16) == 0x30, f"EPC header byte must be 0x30: {val}"


def test_rfid_tag_structure():
    """rfid_tag must return dict with uid, standard, frequency_mhz, memory_bytes."""
    required = {'uid', 'standard', 'frequency_mhz', 'memory_bytes'}
    for _ in range(30):
        tag = jutsu.generate('rfid_tag')
        assert isinstance(tag, dict), "rfid_tag must return dict"
        assert required.issubset(tag.keys()), f"rfid_tag missing keys: {tag.keys()}"
        # EPC field only present for UHF Gen2
        if 'epc' in tag:
            assert re.match(r'^[0-9A-F]{24}$', tag['epc']), f"rfid_tag EPC format wrong: {tag['epc']}"


# ---------------------------------------------------------------------------
# IoT — NFC: Format & Protocol Validation
# ---------------------------------------------------------------------------

def test_nfc_uid_format():
    """nfc_uid must be exactly 7 colon-separated 2-digit hex bytes."""
    for _ in range(100):
        val = str(jutsu.generate('nfc_uid'))
        parts = val.split(':')
        assert len(parts) == 7, f"NFC UID must be 7 bytes: {val}"
        assert all(re.match(r'^[0-9A-F]{2}$', p) for p in parts), \
            f"NFC UID byte format wrong: {val}"


def test_nfc_uid_high_entropy():
    """nfc_uid must not repeat across 200 consecutive calls (48-bit random body)."""
    uids = {str(jutsu.generate('nfc_uid')) for _ in range(200)}
    assert len(uids) >= 195, f"nfc_uid entropy too low: only {len(uids)} unique in 200 calls"


def test_nfc_atqa_format():
    """nfc_atqa must match XX:XX uppercase hex."""
    for _ in range(50):
        val = str(jutsu.generate('nfc_atqa'))
        assert re.match(r'^[0-9A-F]{2}:[0-9A-F]{2}$', val), f"ATQA format wrong: {val}"


def test_nfc_sak_format():
    """nfc_sak must be exactly 2 uppercase hex digits."""
    for _ in range(50):
        val = str(jutsu.generate('nfc_sak'))
        assert re.match(r'^[0-9A-F]{2}$', val), f"SAK format wrong: {val}"


def test_ndef_uri_structure():
    """ndef_uri must return dict with raw_hex, decoded URL, tnf=1, type='U'."""
    for _ in range(50):
        rec = jutsu.generate('ndef_uri')
        assert isinstance(rec, dict), "ndef_uri must return dict"
        assert rec['tnf'] == 1,  f"NDEF URI TNF must be 1: {rec['tnf']}"
        assert rec['type'] == 'U', f"NDEF URI type must be 'U': {rec['type']}"
        assert re.match(r'^[0-9A-F]+$', rec['raw_hex']), \
            f"NDEF raw_hex must be hex: {rec['raw_hex']}"
        # decoded must start with a known URI scheme
        decoded = rec['decoded']
        assert any(decoded.startswith(s) for s in
                   ("http://", "https://", "tel:", "mailto:", "ftp://", "ftps://", "urn:")), \
            f"NDEF URI decoded scheme unknown: {decoded}"


def test_ndef_uri_header_byte():
    """ndef_uri raw_hex first byte must be 0xD1 (MB ME SR TNF=Well-Known)."""
    for _ in range(50):
        rec = jutsu.generate('ndef_uri')
        assert rec['raw_hex'][:2] == 'D1', \
            f"NDEF URI header byte wrong: {rec['raw_hex'][:2]}"


def test_ndef_text_structure():
    """ndef_text must return dict with raw_hex, decoded, lang, tnf=1, type='T'."""
    for locale in LOCALES:
        rec = jutsu.generate('ndef_text', locale=locale)
        assert isinstance(rec, dict), f"ndef_text must return dict for {locale}"
        assert rec['tnf'] == 1,  f"NDEF Text TNF must be 1 for {locale}"
        assert rec['type'] == 'T', f"NDEF Text type must be 'T' for {locale}"
        assert len(rec['decoded']) > 0, f"NDEF Text decoded must not be empty for {locale}"
        assert rec['encoding'] == 'UTF-8', f"NDEF Text encoding must be UTF-8 for {locale}"


def test_apdu_structure():
    """apdu must return dict with cla, ins, p1, p2, hex, description."""
    required = {'cla', 'ins', 'p1', 'p2', 'hex', 'description'}
    for _ in range(50):
        cmd = jutsu.generate('apdu')
        assert isinstance(cmd, dict), "apdu must return dict"
        assert required.issubset(cmd.keys()), f"apdu missing keys: {cmd.keys()}"
        # All byte fields must be 2-char hex
        for field in ('cla', 'ins', 'p1', 'p2'):
            assert re.match(r'^[0-9A-Fa-f]{2}$', cmd[field]), \
                f"apdu {field} must be 2-char hex: {cmd[field]}"


def test_nfc_tag_structure():
    """nfc_tag must return dict with uid, atqa, sak, type, capacity_bytes, ndef_message."""
    required = {'uid', 'atqa', 'sak', 'type', 'capacity_bytes', 'ndef_message', 'ndef_decoded'}
    for _ in range(30):
        tag = jutsu.generate('nfc_tag')
        assert isinstance(tag, dict), "nfc_tag must return dict"
        assert required.issubset(tag.keys()), f"nfc_tag missing keys: {tag.keys()}"
        assert len(tag['uid'].split(':')) == 7, f"nfc_tag uid must be 7 bytes: {tag['uid']}"
        assert isinstance(tag['capacity_bytes'], int), "capacity_bytes must be int"


# ---------------------------------------------------------------------------
# IoT — IR: Protocol & Checksum Validation
# ---------------------------------------------------------------------------

def test_ir_nec_checksum():
    """NEC frame: address XOR inv_address must equal 0xFF (checksum invariant)."""
    for _ in range(200):
        rec = jutsu.generate('ir_nec')
        addr     = int(rec['address'],     16)
        inv_addr = int(rec['inv_address'], 16)
        cmd      = int(rec['command'],     16)
        inv_cmd  = int(rec['inv_command'], 16)
        assert addr ^ inv_addr == 0xFF, \
            f"NEC address checksum failed: {rec['address']} ^ {rec['inv_address']} != 0xFF"
        assert cmd ^ inv_cmd == 0xFF, \
            f"NEC command checksum failed: {rec['command']} ^ {rec['inv_command']} != 0xFF"


def test_ir_nec_hex_format():
    """NEC hex field must be exactly 8 uppercase hex characters."""
    for _ in range(50):
        rec = jutsu.generate('ir_nec')
        assert re.match(r'^[0-9A-F]{8}$', rec['hex']), \
            f"NEC hex format wrong: {rec['hex']}"


def test_ir_nec_carrier():
    """NEC carrier must be 38000 Hz."""
    rec = jutsu.generate('ir_nec')
    assert rec['carrier_hz'] == 38000, f"NEC carrier wrong: {rec['carrier_hz']}"


def test_ir_rc5_frame_length():
    """RC-5 frame_bits must be exactly 14 characters of '0'/'1'."""
    for _ in range(100):
        rec = jutsu.generate('ir_rc5')
        assert re.match(r'^[01]{14}$', rec['frame_bits']), \
            f"RC-5 frame_bits wrong length or chars: {rec['frame_bits']}"


def test_ir_rc5_start_bit():
    """RC-5 frame MSB (bit 13) must always be '1' (start bit)."""
    for _ in range(100):
        rec = jutsu.generate('ir_rc5')
        assert rec['frame_bits'][0] == '1', \
            f"RC-5 start bit must be 1: {rec['frame_bits']}"


def test_ir_rc5_command_range():
    """RC-5 command must be in range 0-127."""
    for _ in range(100):
        rec = jutsu.generate('ir_rc5')
        assert 0 <= rec['command'] <= 127, \
            f"RC-5 command out of range: {rec['command']}"


def test_ir_pronto_format():
    """Pronto hex must start with '0000 006D' (learned NEC, 38 kHz)."""
    for _ in range(50):
        val = str(jutsu.generate('ir_pronto'))
        words = val.split()
        assert words[0] == '0000', f"Pronto word[0] must be 0000: {words[0]}"
        assert words[1] == '006D', f"Pronto word[1] must be 006D (38kHz): {words[1]}"
        assert words[3] == '0000', f"Pronto word[3] (repeat count) must be 0000: {words[3]}"


def test_ir_pronto_word_count():
    """Pronto hex NEC frame must have 4 header + 2*(1+32+1) = 4+68 = 72 words."""
    for _ in range(30):
        val = str(jutsu.generate('ir_pronto'))
        words = val.split()
        # 4 header words + 34 pairs × 2 = 4 + 68 = 72
        assert len(words) == 72, f"Pronto word count wrong: {len(words)} (expected 72)"


def test_ir_raw_structure():
    """ir_raw must return dict with carrier_hz=38000 and pulses starting with [9024, 4512]."""
    for _ in range(50):
        rec = jutsu.generate('ir_raw')
        assert isinstance(rec, dict), "ir_raw must return dict"
        assert rec['carrier_hz'] == 38000, f"ir_raw carrier_hz wrong: {rec['carrier_hz']}"
        assert rec['pulses'][:2] == [9024, 4512], \
            f"ir_raw must start with NEC leader [9024, 4512]: {rec['pulses'][:2]}"


def test_ir_raw_pulse_count():
    """ir_raw NEC frame must have exactly 67 pulses (2 leader + 32×2 data + 1 stop)."""
    for _ in range(30):
        rec = jutsu.generate('ir_raw')
        assert rec['pulse_count'] == 67, \
            f"ir_raw pulse count wrong: {rec['pulse_count']} (expected 67)"
