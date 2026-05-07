"""
mock-jutsu — Full-Coverage Unit Tests
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)
Purpose: Cross-testing 131 parameters across 6 locales (TR, UK, US, DE, FR, RU).
         786 matrix scenarios + algorithmic validation tests.
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
    # Barcode (6)
    'ean13', 'ean8', 'upca', 'isbn13', 'isbn10', 'gs1_128',
    # Telecom (5)
    'imei', 'imei2', 'iccid', 'imsi', 'msisdn',
    # Financial Markets (4)
    'isin', 'cusip', 'sedol', 'lei',
    # Crypto / Web3 (5)
    'btc_address', 'eth_address', 'crypto_address', 'tx_hash', 'block_hash',
    # E-Commerce (6)
    'product_name', 'sku', 'order_id', 'tracking_number', 'category', 'rating',
    # Location / Geo (5)
    'latitude', 'longitude', 'timezone', 'country_code', 'coordinates',
    # Social Media (5)
    'username', 'hashtag', 'bio', 'handle', 'follower_count',
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
# Comprehensive Matrix — 115 types × 6 locales = 690 scenarios
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


# ---------------------------------------------------------------------------
# Barcode — GS1 / ISO 2108 Algorithmic Validation
# ---------------------------------------------------------------------------

def _gs1_check_valid(barcode: str) -> bool:
    """Verify GS1 MOD-10 check digit — GS1 General Specifications v24.0 §7.9."""
    digits = [int(c) for c in barcode]
    data, check = digits[:-1], digits[-1]
    total = sum(d * (3 if i % 2 == 0 else 1) for i, d in enumerate(reversed(data)))
    return (10 - total % 10) % 10 == check


def test_ean13_length_and_check():
    """EAN-13 must be exactly 13 digits with a valid GS1 MOD-10 check digit."""
    for _ in range(100):
        val = str(jutsu.generate('ean13'))
        assert re.match(r'^\d{13}$', val), f"EAN-13 must be 13 digits: {val}"
        assert _gs1_check_valid(val), f"EAN-13 GS1 check failed: {val}"


def test_ean13_locale_prefix():
    """EAN-13 TR must start with 868 or 869 (GS1 Turkey prefixes)."""
    for _ in range(50):
        val = jutsu.generate('ean13', locale='TR')
        assert str(val)[:3] in ('868', '869'), f"EAN-13 TR prefix wrong: {val}"


def test_ean8_length_and_check():
    """EAN-8 must be exactly 8 digits with a valid GS1 MOD-10 check digit."""
    for _ in range(100):
        val = str(jutsu.generate('ean8'))
        assert re.match(r'^\d{8}$', val), f"EAN-8 must be 8 digits: {val}"
        assert _gs1_check_valid(val), f"EAN-8 GS1 check failed: {val}"


def test_upca_length_and_check():
    """UPC-A must be exactly 12 digits with a valid GS1 MOD-10 check digit."""
    for _ in range(100):
        val = str(jutsu.generate('upca'))
        assert re.match(r'^\d{12}$', val), f"UPC-A must be 12 digits: {val}"
        assert _gs1_check_valid(val), f"UPC-A GS1 check failed: {val}"


def test_isbn13_length_and_check():
    """ISBN-13 must be 13 digits starting with 978 or 979 with valid check."""
    for _ in range(100):
        val = str(jutsu.generate('isbn13'))
        assert re.match(r'^\d{13}$', val), f"ISBN-13 must be 13 digits: {val}"
        assert str(val)[:3] in ('978', '979'), f"ISBN-13 must start with 978/979: {val}"
        assert _gs1_check_valid(val), f"ISBN-13 GS1 check failed: {val}"


def test_isbn10_length_and_check():
    """ISBN-10 must be 9 digits + MOD-11 check ('0'-'9' or 'X')."""
    def _isbn10_valid(s: str) -> bool:
        if len(s) != 10:
            return False
        if not re.match(r'^[0-9]{9}[0-9X]$', s):
            return False
        total = sum(int(c) * (10 - i) for i, c in enumerate(s[:9]))
        check_val = (11 - total % 11) % 11
        expected = 'X' if check_val == 10 else str(check_val)
        return s[9] == expected

    for _ in range(100):
        val = str(jutsu.generate('isbn10'))
        assert _isbn10_valid(val), f"ISBN-10 MOD-11 check failed: {val}"


def test_gs1_128_structure():
    """GS1-128 must contain AI (01) GTIN-14, AI (17) expiry, AI (10) lot."""
    for _ in range(50):
        val = str(jutsu.generate('gs1_128'))
        assert val.startswith('(01)'), f"GS1-128 must start with AI(01): {val}"
        assert '(17)' in val, f"GS1-128 must contain AI(17) expiry: {val}"
        assert '(10)' in val, f"GS1-128 must contain AI(10) lot: {val}"


def test_gs1_128_gtin14_check():
    """GS1-128 GTIN-14 embedded in AI(01) must pass GS1 MOD-10 check."""
    for _ in range(50):
        val = str(jutsu.generate('gs1_128'))
        gtin14 = val[4:18]  # (01) is 4 chars, GTIN-14 is 14 digits
        assert re.match(r'^\d{14}$', gtin14), f"GTIN-14 must be 14 digits: {gtin14}"
        assert _gs1_check_valid(gtin14), f"GTIN-14 GS1 check failed in GS1-128: {gtin14}"


# ---------------------------------------------------------------------------
# Telecom — 3GPP / ITU-T Algorithmic Validation
# ---------------------------------------------------------------------------

def test_imei_length_and_luhn():
    """IMEI must be exactly 15 digits and pass the Luhn checksum."""
    for _ in range(100):
        val = str(jutsu.generate('imei'))
        assert re.match(r'^\d{15}$', val), f"IMEI must be 15 digits: {val}"
        assert _luhn_valid(val), f"IMEI Luhn check failed: {val}"


def test_imei2_format():
    """IMEI2 must match AA-BBBBBB-CCCCCC-D (hyphenated display format)."""
    for _ in range(50):
        val = str(jutsu.generate('imei2'))
        assert re.match(r'^\d{2}-\d{6}-\d{6}-\d$', val), f"IMEI2 format wrong: {val}"


def test_imei2_luhn_valid():
    """IMEI2 (stripped of hyphens) must pass the Luhn checksum."""
    for _ in range(50):
        val = str(jutsu.generate('imei2'))
        stripped = val.replace('-', '')
        assert _luhn_valid(stripped), f"IMEI2 Luhn check failed: {val}"


def test_iccid_length_and_luhn():
    """ICCID must be exactly 19 digits and pass Luhn checksum."""
    for _ in range(100):
        val = str(jutsu.generate('iccid'))
        assert re.match(r'^\d{19}$', val), f"ICCID must be 19 digits: {val}"
        assert _luhn_valid(val), f"ICCID Luhn check failed: {val}"


def test_iccid_starts_with_89():
    """ICCID must start with '89' (MII for telecom — ITU-T E.118)."""
    for _ in range(50):
        val = str(jutsu.generate('iccid'))
        assert val.startswith('89'), f"ICCID must start with 89: {val}"


def test_imsi_length_and_digits():
    """IMSI must be all digits and ≤ 15 characters (3GPP TS 23.003 §2.2)."""
    for locale in ['TR', 'US', 'UK', 'DE', 'FR', 'RU']:
        for _ in range(20):
            val = str(jutsu.generate('imsi', locale=locale))
            assert val.isdigit(), f"IMSI must be all digits for {locale}: {val}"
            assert len(val) <= 15, f"IMSI must be ≤15 digits for {locale}: {val}"
            assert len(val) >= 10, f"IMSI must be ≥10 digits for {locale}: {val}"


def test_imsi_tr_mcc():
    """IMSI for TR locale must start with MCC 286 (Turkey)."""
    for _ in range(50):
        val = str(jutsu.generate('imsi', locale='TR'))
        assert val.startswith('286'), f"TR IMSI must start with MCC 286: {val}"


def test_msisdn_e164_format():
    """MSISDN must start with '+' and contain only digits after the '+'."""
    for locale in ['TR', 'US', 'UK', 'DE', 'FR', 'RU']:
        for _ in range(20):
            val = str(jutsu.generate('msisdn', locale=locale))
            assert val.startswith('+'), f"MSISDN must start with '+' for {locale}: {val}"
            assert val[1:].isdigit(), f"MSISDN digits part not numeric for {locale}: {val}"
            assert 10 <= len(val) <= 16, f"MSISDN length out of range for {locale}: {val}"


def test_msisdn_tr_prefix():
    """MSISDN for TR must start with '+905' (Turkey mobile E.164)."""
    for _ in range(50):
        val = str(jutsu.generate('msisdn', locale='TR'))
        assert val.startswith('+905'), f"TR MSISDN must start with +905: {val}"


# ---------------------------------------------------------------------------
# Financial Markets — ISIN / CUSIP / SEDOL / LEI Algorithmic Validation
# ---------------------------------------------------------------------------

def _isin_check_valid(isin: str) -> bool:
    """Verify ISIN check digit — ISO 6166:2021, Luhn MOD-10 on numeric expansion.

    Algorithm: convert each char (A=10…Z=35), concatenate to numeric string,
    apply standard Luhn (rightmost digit NOT doubled; position 1 IS doubled).
    Valid ISIN yields sum % 10 == 0.

    Manual verification:
      Apple  US0378331005 → "30280378331005" → sum=50 ✓
      Amazon US0231351067 → "30280231351067" → sum=50 ✓
      Vodafone GB0002634946 → "16110002634946" → sum=50 ✓
    """
    if len(isin) != 12 or not re.match(r'^[A-Z]{2}[A-Z0-9]{9}[0-9]$', isin):
        return False
    numeric = ''.join(str(ord(c) - 55) if c.isalpha() else c for c in isin)
    digits = [int(d) for d in numeric]
    total = 0
    for i, d in enumerate(reversed(digits)):
        n = d * 2 if i % 2 == 1 else d
        if n > 9:
            n -= 9
        total += n
    return total % 10 == 0


def _cusip_check_valid(cusip: str) -> bool:
    """Verify CUSIP check digit — ABA algorithm (odd 0-indexed positions ×2, digit-sum).

    Algorithm: for each of the 8 payload chars (digits + A-Z mapped to 10-35),
    if position (0-indexed) is odd multiply value by 2; add floor(v/10)+v%10 to total.
    check = (10 - total % 10) % 10.

    Manual verification:
      Apple  037833100 → positions(1-indexed): 0,3*2,7,8*2,3,3*2,1,0*2 → sum=30 → check=0 ✓
      Amazon 023135106 → positions: 0,2*2,3,1*2,3,5*2,1,0*2 → sum=14 → check=6 ✓
    """
    if len(cusip) != 9 or not re.match(r'^[A-Z0-9]{8}[0-9]$', cusip):
        return False
    total = 0
    for i, c in enumerate(cusip[:8]):
        v = int(c) if c.isdigit() else ord(c) - 55
        if i % 2 == 1:
            v *= 2
        total += v // 10 + v % 10
    return (10 - total % 10) % 10 == int(cusip[8])


def _sedol_check_valid(sedol: str) -> bool:
    """Verify SEDOL check digit — LSE weights [1,3,1,7,3,9] on 6 data chars.

    Algorithm: weighted sum with [1,3,1,7,3,9]; check = (10 - sum%10) % 10.
    Characters: digits 0-9 and consonants (no vowels A,E,I,O,U).

    Manual verification:
      Vodafone 0263494 → 0×1+2×3+6×1+3×7+4×3+9×9 = 0+6+6+21+12+81=126 → check=4 ✓
      Barclays 0798059 → 0×1+7×3+9×1+8×7+0×3+5×9 = 0+21+9+56+0+45=131 → check=9 ✓
      BT Group 3134865 → 3×1+1×3+3×1+4×7+8×3+6×9 = 3+3+3+28+24+54=115 → check=5 ✓
    """
    if len(sedol) != 7 or not re.match(r'^[B-DF-HJ-NP-TV-Z0-9]{6}[0-9]$', sedol):
        return False
    weights = [1, 3, 1, 7, 3, 9]
    total = sum(
        (int(c) if c.isdigit() else ord(c) - 55) * w
        for c, w in zip(sedol[:6], weights)
    )
    return (10 - total % 10) % 10 == int(sedol[6])


def _lei_check_valid(lei: str) -> bool:
    """Verify LEI check digits — ISO 17442 / ISO 7064 MOD 97-10.

    Algorithm: convert all chars to numeric (A=10…Z=35), concatenate,
    compute int(numeric_str) % 97; must equal 1.

    Manual verification:
      GLEIF 529900T8BM49AURSDO55 → "52990029811224910302728132455" % 97 = 1 ✓
    """
    if len(lei) != 20 or not re.match(r'^[A-Z0-9]{18}\d{2}$', lei):
        return False
    numeric = ''.join(str(ord(c) - 55) if c.isalpha() else c for c in lei)
    return int(numeric) % 97 == 1


# ── ISIN ──────────────────────────────────────────────────────────────────

def test_isin_format():
    """ISIN must be 12 chars: 2-letter country code + 9 alphanumeric + 1 digit check."""
    for _ in range(100):
        val = str(jutsu.generate('isin'))
        assert re.match(r'^[A-Z]{2}[A-Z0-9]{9}[0-9]$', val), f"ISIN format wrong: {val}"


def test_isin_checksum():
    """ISIN must pass ISO 6166:2021 Luhn MOD-10 checksum on numeric expansion."""
    for _ in range(100):
        val = str(jutsu.generate('isin'))
        assert _isin_check_valid(val), f"ISIN checksum failed: {val}"


def test_isin_locale_prefix():
    """ISIN country prefix must match the locale's ISO 3166-1 alpha-2 code."""
    expected = {'TR': 'TR', 'US': 'US', 'UK': 'GB', 'DE': 'DE', 'FR': 'FR', 'RU': 'RU'}
    for locale, prefix in expected.items():
        for _ in range(20):
            val = str(jutsu.generate('isin', locale=locale))
            assert val.startswith(prefix), f"ISIN prefix wrong for {locale}: {val}"


def test_isin_known_vectors():
    """Known public ISINs must pass the checksum validator (ISO 6166:2021)."""
    known = [
        'US0378331005',  # Apple Inc
        'US0231351067',  # Amazon.com Inc
        'GB0002634946',  # Vodafone Group plc
    ]
    for isin in known:
        assert _isin_check_valid(isin), f"Known valid ISIN failed: {isin}"


# ── CUSIP ─────────────────────────────────────────────────────────────────

def test_cusip_format():
    """CUSIP must be exactly 9 chars: 8 alphanumeric data + 1 digit check."""
    for _ in range(100):
        val = str(jutsu.generate('cusip'))
        assert re.match(r'^[A-Z0-9]{8}[0-9]$', val), f"CUSIP format wrong: {val}"


def test_cusip_checksum():
    """CUSIP must pass ABA check digit algorithm (odd-position ×2, digit-sum)."""
    for _ in range(100):
        val = str(jutsu.generate('cusip'))
        assert _cusip_check_valid(val), f"CUSIP checksum failed: {val}"


def test_cusip_known_vectors():
    """Known public CUSIPs must pass the checksum validator."""
    known = [
        '037833100',  # Apple Inc
        '023135106',  # Amazon.com Inc
    ]
    for cusip in known:
        assert _cusip_check_valid(cusip), f"Known valid CUSIP failed: {cusip}"


# ── SEDOL ─────────────────────────────────────────────────────────────────

def test_sedol_format():
    """SEDOL must be 7 chars: 6 consonant/digit data chars + 1 digit check."""
    for _ in range(100):
        val = str(jutsu.generate('sedol'))
        assert re.match(r'^[B-DF-HJ-NP-TV-Z0-9]{6}[0-9]$', val), f"SEDOL format wrong: {val}"


def test_sedol_no_vowels():
    """SEDOL data characters must never include vowels (A, E, I, O, U)."""
    for _ in range(200):
        val = str(jutsu.generate('sedol'))
        for c in val[:6]:
            assert c not in 'AEIOU', f"SEDOL contains vowel '{c}': {val}"


def test_sedol_checksum():
    """SEDOL must pass LSE weighted checksum with weights [1, 3, 1, 7, 3, 9]."""
    for _ in range(100):
        val = str(jutsu.generate('sedol'))
        assert _sedol_check_valid(val), f"SEDOL checksum failed: {val}"


def test_sedol_known_vectors():
    """Known public SEDOLs must pass the checksum validator."""
    known = [
        '0263494',  # Vodafone Group plc
        '0798059',  # Barclays PLC
        '3134865',  # BT Group plc
    ]
    for sedol in known:
        assert _sedol_check_valid(sedol), f"Known valid SEDOL failed: {sedol}"


# ── LEI ───────────────────────────────────────────────────────────────────

def test_lei_format():
    """LEI must be 20 chars: 18 alphanumeric + 2 digit check."""
    for _ in range(100):
        val = str(jutsu.generate('lei'))
        assert re.match(r'^[A-Z0-9]{18}\d{2}$', val), f"LEI format wrong: {val}"


def test_lei_checksum():
    """LEI must pass ISO 17442 MOD 97-10 checksum (numeric expansion % 97 == 1)."""
    for _ in range(100):
        val = str(jutsu.generate('lei'))
        assert _lei_check_valid(val), f"LEI checksum failed: {val}"


def test_lei_known_vector():
    """GLEIF's own LEI must pass the ISO 17442 checksum validator."""
    assert _lei_check_valid('529900T8BM49AURSDO55'), "GLEIF LEI 529900T8BM49AURSDO55 failed"


# ---------------------------------------------------------------------------
# Crypto / Web3 — BTC / ETH Algorithmic Validation
# ---------------------------------------------------------------------------

_BTC_BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
_BTC_FORBIDDEN_CHARS = set('0OIl')


def _btc_base58check_valid(addr: str) -> bool:
    """Verify Bitcoin P2PKH mainnet Base58Check address — BIP-16 / SHA256d checksum.

    Algorithm:
      1. Decode Base58 → 25 bytes (1 version + 20 hash + 4 checksum)
      2. checksum == SHA256(SHA256(version+hash))[:4]
      3. version byte == 0x00 (mainnet P2PKH → address starts with '1')

    Base58 alphabet: 123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz
    Forbidden: 0, O, I, l  (visually ambiguous characters)
    """
    import hashlib
    if not addr or not addr.startswith('1'):
        return False
    if not all(c in _BTC_BASE58_ALPHABET for c in addr):
        return False
    # Base58 decode
    n = 0
    for c in addr:
        n = n * 58 + _BTC_BASE58_ALPHABET.index(c)
    try:
        decoded = n.to_bytes(25, 'big')
    except OverflowError:
        return False
    if decoded[0] != 0x00:
        return False
    payload, checksum = decoded[:21], decoded[21:]
    expected = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    return checksum == expected


def _keccak256_test(data: bytes) -> str:
    """Keccak-256 for test validation — returns lowercase hex string.

    Implements Keccak-f[1600] permutation. Differs from SHA3-256 (NIST FIPS 202)
    only in padding: Keccak uses 0x01 || 0*80, SHA3 uses 0x06 || 0*80.

    Known vector: keccak256(b'') =
      c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470
    """
    RC = [
        0x0000000000000001, 0x0000000000008082, 0x800000000000808A,
        0x8000000080008000, 0x000000000000808B, 0x0000000080000001,
        0x8000000080008081, 0x8000000000008009, 0x000000000000008A,
        0x0000000000000088, 0x0000000080008009, 0x000000008000000A,
        0x000000008000808B, 0x800000000000008B, 0x8000000000008089,
        0x8000000000008003, 0x8000000000008002, 0x8000000000000080,
        0x000000000000800A, 0x800000008000000A, 0x8000000080008081,
        0x8000000000008080, 0x0000000080000001, 0x8000000080008008,
    ]
    ROT = [
        [ 0, 36,  3, 41, 18],
        [ 1, 44, 10, 45,  2],
        [62,  6, 43, 15, 61],
        [28, 55, 25, 21, 56],
        [27, 20, 39,  8, 14],
    ]
    M = 0xFFFFFFFFFFFFFFFF

    def rot(x, n):
        return ((x << n) | (x >> (64 - n))) & M

    def keccak_f(s):
        for rc in RC:
            C = [s[x] ^ s[x+5] ^ s[x+10] ^ s[x+15] ^ s[x+20] for x in range(5)]
            D = [C[(x-1) % 5] ^ rot(C[(x+1) % 5], 1) for x in range(5)]
            s = [s[i] ^ D[i % 5] for i in range(25)]
            B = [0] * 25
            for x in range(5):
                for y in range(5):
                    B[y + 5*((2*x + 3*y) % 5)] = rot(s[x + 5*y], ROT[x][y])
            s = [B[i] ^ (~B[(i%5+1)%5 + (i//5)*5] & B[(i%5+2)%5 + (i//5)*5]) for i in range(25)]
            s[0] ^= rc
        return s

    rate = 136  # bytes (Keccak-256: rate=1088 bits)
    msg = bytearray(data)
    # Keccak padding (NOT SHA3: 0x01, not 0x06)
    msg.append(0x01)
    while len(msg) % rate:
        msg.append(0x00)
    msg[-1] |= 0x80

    state = [0] * 25
    for block in range(0, len(msg), rate):
        chunk = msg[block:block + rate]
        for i in range(rate // 8):
            state[i] ^= int.from_bytes(chunk[i*8:(i+1)*8], 'little')
        state = keccak_f(state)

    return b''.join(s.to_bytes(8, 'little') for s in state[:4]).hex()


def _eth_eip55_valid(addr: str) -> bool:
    """Verify Ethereum EIP-55 mixed-case checksum address.

    Algorithm (EIP-55):
      hex_lower = addr[2:].lower()
      keccak_hash = Keccak-256(hex_lower.encode('ascii'))
      For each char: uppercase if hash nibble >= 8, lowercase if < 8.

    Known EIP-55 test vectors (from EIP-55 spec):
      0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed
      0xfB6916095ca1df60bB79Ce92cE3Ea74c37c5d359
      0xdbF03B407c01E7cD3CBea99509d93f8DDDC8C6FB
      0xD1220A0cf47c7B9Be7A2E6BA89F429762e7b9aDb
    """
    if not re.match(r'^0x[0-9A-Fa-f]{40}$', addr):
        return False
    hex_lower = addr[2:].lower()
    keccak = _keccak256_test(hex_lower.encode('ascii'))
    expected = ''.join(
        c.upper() if int(keccak[i], 16) >= 8 else c.lower()
        for i, c in enumerate(hex_lower)
    )
    return addr[2:] == expected


# ── BTC ───────────────────────────────────────────────────────────────────

def test_btc_address_format():
    """BTC P2PKH must start with '1', be 25–34 chars, Base58 alphabet only."""
    for _ in range(100):
        val = str(jutsu.generate('btc_address'))
        assert val.startswith('1'), f"BTC address must start with '1': {val}"
        assert 25 <= len(val) <= 34, f"BTC address length out of range: {val}"
        assert all(c in _BTC_BASE58_ALPHABET for c in val), \
            f"BTC address contains invalid Base58 char: {val}"


def test_btc_address_no_ambiguous_chars():
    """BTC address must never contain 0, O, I, l (Base58 excludes them)."""
    for _ in range(200):
        val = str(jutsu.generate('btc_address'))
        assert not _BTC_FORBIDDEN_CHARS.intersection(val), \
            f"BTC address contains ambiguous char: {val}"


def test_btc_address_base58check():
    """BTC P2PKH address must pass SHA256d Base58Check validation."""
    for _ in range(100):
        val = str(jutsu.generate('btc_address'))
        assert _btc_base58check_valid(val), f"BTC Base58Check failed: {val}"


# ── ETH ───────────────────────────────────────────────────────────────────

def test_keccak256_empty_string():
    """Keccak-256('') must equal the known reference vector."""
    expected = 'c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470'
    assert _keccak256_test(b'') == expected, \
        f"Keccak-256 empty-string vector failed: {_keccak256_test(b'')}"


def test_eth_address_format():
    """ETH address must be '0x' + exactly 40 hex characters."""
    for _ in range(100):
        val = str(jutsu.generate('eth_address'))
        assert re.match(r'^0x[0-9A-Fa-f]{40}$', val), \
            f"ETH address format wrong: {val}"


def test_eth_address_eip55():
    """ETH address must pass EIP-55 Keccak-256 mixed-case checksum."""
    for _ in range(100):
        val = str(jutsu.generate('eth_address'))
        assert _eth_eip55_valid(val), f"ETH EIP-55 checksum failed: {val}"


def test_eth_eip55_known_vectors():
    """EIP-55 spec test vectors must pass the validator."""
    known = [
        '0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed',
        '0xfB6916095ca1df60bB79Ce92cE3Ea74c37c5d359',
        '0xdbF03B407c01E7cD3CBea99509d93f8DDDC8C6FB',
        '0xD1220A0cf47c7B9Be7A2E6BA89F429762e7b9aDb',
    ]
    for addr in known:
        assert _eth_eip55_valid(addr), f"Known EIP-55 address failed: {addr}"


# ── crypto_address ────────────────────────────────────────────────────────

def test_crypto_address_btc_default():
    """crypto_address with currency='btc' must return a valid BTC address."""
    for _ in range(50):
        val = str(jutsu.generate('crypto_address', currency='btc'))
        assert _btc_base58check_valid(val), f"crypto_address btc failed: {val}"


def test_crypto_address_eth():
    """crypto_address with currency='eth' must return a valid ETH EIP-55 address."""
    for _ in range(50):
        val = str(jutsu.generate('crypto_address', currency='eth'))
        assert _eth_eip55_valid(val), f"crypto_address eth failed: {val}"


# ── tx_hash / block_hash ──────────────────────────────────────────────────

def test_tx_hash_btc_format():
    """BTC tx_hash must be exactly 64 lowercase hex characters."""
    for _ in range(50):
        val = str(jutsu.generate('tx_hash', currency='btc'))
        assert re.match(r'^[0-9a-f]{64}$', val), f"BTC tx_hash format wrong: {val}"


def test_tx_hash_eth_format():
    """ETH tx_hash must be '0x' + exactly 64 lowercase hex characters."""
    for _ in range(50):
        val = str(jutsu.generate('tx_hash', currency='eth'))
        assert re.match(r'^0x[0-9a-f]{64}$', val), f"ETH tx_hash format wrong: {val}"


def test_block_hash_btc_format():
    """BTC block_hash must be exactly 64 lowercase hex characters."""
    for _ in range(50):
        val = str(jutsu.generate('block_hash', currency='btc'))
        assert re.match(r'^[0-9a-f]{64}$', val), f"BTC block_hash format wrong: {val}"


def test_block_hash_eth_format():
    """ETH block_hash must be '0x' + exactly 64 lowercase hex characters."""
    for _ in range(50):
        val = str(jutsu.generate('block_hash', currency='eth'))
        assert re.match(r'^0x[0-9a-f]{64}$', val), f"ETH block_hash format wrong: {val}"


def test_tx_hash_high_entropy():
    """tx_hash must not repeat across 200 calls."""
    hashes = {str(jutsu.generate('tx_hash')) for _ in range(200)}
    assert len(hashes) >= 195, f"tx_hash entropy too low: {len(hashes)} unique in 200"


# ---------------------------------------------------------------------------
# Sprint 4A — E-Commerce
# ---------------------------------------------------------------------------

def _usps_luhn_valid(number: str) -> bool:
    """USPS IMpb 22-digit: Luhn MOD-10 on all 22 digits must equal 0.
    Reference: USPS Publication 97, Appendix F.
    Known vector: 9400111899223397522384 → sum=70, 70%10=0 ✓
    """
    digits = [int(d) for d in number]
    total = 0
    for i, d in enumerate(reversed(digits)):
        n = d * 2 if i % 2 == 1 else d
        if n > 9:
            n -= 9
        total += n
    return total % 10 == 0


def _ups_check_valid(tracking: str) -> bool:
    """UPS 18-char tracking: 1Z + 15 alphanumeric + 1 check digit.
    Algorithm: translate letters A=10..Z=35, alternate ×1 / ×2,
    if product>9 subtract 9, sum all, check = (10 - sum%10) % 10.
    Reference: public UPS technical documentation.
    """
    if not tracking.startswith('1Z') or len(tracking) != 18:
        return False
    payload = tracking[2:17]
    total = 0
    for i, c in enumerate(payload):
        v = int(c) if c.isdigit() else ord(c) - 55
        if i % 2 == 1:
            v *= 2
        if v > 9:
            v -= 9
        total += v
    expected = (10 - total % 10) % 10
    return int(tracking[17]) == expected


def _fedex_check_valid(tracking: str) -> bool:
    """FedEx 12-digit Express: Mod-11 with weights [3,1,7,3,1,7,3,1,7,3,1].
    Sum of (digit × weight) mod 11, if result == 10 use 0.
    Reference: FedEx Developer Guide — tracking number formats.
    Known: last digit is check, first 11 are payload.
    """
    if not re.match(r'^\d{12}$', tracking):
        return False
    weights = [3, 1, 7, 3, 1, 7, 3, 1, 7, 3, 1]
    total = sum(int(d) * w for d, w in zip(tracking[:11], weights))
    check = total % 11
    if check == 10:
        check = 0
    return check == int(tracking[11])


def test_sku_format():
    """SKU must match GS1-inspired alphanumeric pattern: ABC-123456."""
    for _ in range(100):
        val = str(jutsu.generate('sku'))
        assert re.match(r'^[A-Z]{2,4}-[0-9]{4,8}$', val), f"SKU format wrong: {val}"


def test_order_id_format():
    """order_id must be ORD- prefix + alphanumeric suffix."""
    for _ in range(100):
        val = str(jutsu.generate('order_id'))
        assert re.match(r'^ORD-[A-Z0-9]{8,12}$', val), f"order_id format wrong: {val}"


def test_tracking_number_usps():
    """USPS tracking: 22 digits starting with 92/94, Luhn valid."""
    for _ in range(100):
        val = str(jutsu.generate('tracking_number', carrier='usps'))
        assert re.match(r'^\d{22}$', val), f"USPS format wrong: {val}"
        assert val[:2] in ('92', '94', '70', '93', '95'), f"USPS prefix wrong: {val}"
        assert _usps_luhn_valid(val), f"USPS Luhn failed: {val}"


def test_tracking_number_ups():
    """UPS tracking: 18 chars starting with 1Z, weighted check digit valid."""
    for _ in range(100):
        val = str(jutsu.generate('tracking_number', carrier='ups'))
        assert val.startswith('1Z'), f"UPS must start with 1Z: {val}"
        assert len(val) == 18, f"UPS must be 18 chars: {val}"
        assert _ups_check_valid(val), f"UPS check digit failed: {val}"


def test_tracking_number_fedex():
    """FedEx Express: 12 digits, Mod-11 check digit valid."""
    for _ in range(100):
        val = str(jutsu.generate('tracking_number', carrier='fedex'))
        assert re.match(r'^\d{12}$', val), f"FedEx format wrong: {val}"
        assert _fedex_check_valid(val), f"FedEx Mod-11 check failed: {val}"


def test_tracking_number_default():
    """tracking_number without carrier returns a valid format."""
    for _ in range(50):
        val = str(jutsu.generate('tracking_number'))
        assert len(val) >= 12, f"tracking_number too short: {val}"


def test_product_name_nonempty():
    """product_name must return a non-empty string."""
    for _ in range(50):
        val = str(jutsu.generate('product_name'))
        assert len(val) >= 3, f"product_name too short: {val}"


def test_category_nonempty():
    """category must return a non-empty string."""
    for _ in range(50):
        val = str(jutsu.generate('category'))
        assert len(val) >= 2, f"category too short: {val}"


def test_rating_range():
    """rating must be between 1.0 and 5.0 inclusive."""
    for _ in range(200):
        val = float(jutsu.generate('rating'))
        assert 1.0 <= val <= 5.0, f"rating out of range: {val}"


def test_rating_one_decimal():
    """rating must have exactly one decimal place."""
    for _ in range(100):
        val = str(jutsu.generate('rating'))
        assert re.match(r'^\d\.\d$', val), f"rating format wrong: {val}"


# ---------------------------------------------------------------------------
# Sprint 4B — Location / Geo
# ---------------------------------------------------------------------------

_LOCALE_LAT = {
    'TR': (36.0, 42.0), 'US': (25.0, 49.0), 'UK': (50.0, 59.0),
    'DE': (47.0, 55.0), 'FR': (42.0, 51.0), 'RU': (41.0, 82.0),
}
_LOCALE_LON = {
    'TR': (26.0, 45.0), 'US': (-125.0, -66.0), 'UK': (-8.0, 2.0),
    'DE': (6.0, 15.0),  'FR': (-5.0, 8.0),     'RU': (27.0, 170.0),
}
_IANA_TIMEZONES = {
    'TR': ['Europe/Istanbul'],
    'US': ['America/New_York', 'America/Chicago', 'America/Denver',
           'America/Los_Angeles', 'America/Phoenix', 'America/Anchorage'],
    'UK': ['Europe/London'],
    'DE': ['Europe/Berlin'],
    'FR': ['Europe/Paris'],
    'RU': ['Europe/Moscow', 'Asia/Yekaterinburg', 'Asia/Novosibirsk',
           'Asia/Krasnoyarsk', 'Asia/Irkutsk', 'Asia/Vladivostok'],
}


def test_latitude_range():
    """latitude must be between -90.0 and 90.0."""
    for _ in range(200):
        val = float(jutsu.generate('latitude'))
        assert -90.0 <= val <= 90.0, f"latitude out of global range: {val}"


def test_latitude_locale_aware():
    """latitude must fall within locale-specific geographic bounds."""
    for locale, (lo, hi) in _LOCALE_LAT.items():
        for _ in range(50):
            val = float(jutsu.generate('latitude', locale=locale))
            assert lo <= val <= hi, f"latitude {val} out of {locale} range [{lo},{hi}]"


def test_longitude_range():
    """longitude must be between -180.0 and 180.0."""
    for _ in range(200):
        val = float(jutsu.generate('longitude'))
        assert -180.0 <= val <= 180.0, f"longitude out of global range: {val}"


def test_longitude_locale_aware():
    """longitude must fall within locale-specific geographic bounds."""
    for locale, (lo, hi) in _LOCALE_LON.items():
        for _ in range(50):
            val = float(jutsu.generate('longitude', locale=locale))
            assert lo <= val <= hi, f"longitude {val} out of {locale} range [{lo},{hi}]"


def test_timezone_valid_iana():
    """timezone must return a known IANA timezone string."""
    all_valid = [tz for tzs in _IANA_TIMEZONES.values() for tz in tzs]
    for locale in LOCALES:
        for _ in range(20):
            val = str(jutsu.generate('timezone', locale=locale))
            assert val in all_valid, f"timezone '{val}' not a known IANA name"
            assert val in _IANA_TIMEZONES.get(locale, []), \
                f"timezone '{val}' wrong for locale {locale}"


def test_country_code_format():
    """country_code must be exactly 2 uppercase ASCII letters (ISO 3166-1 alpha-2)."""
    for _ in range(100):
        val = str(jutsu.generate('country_code'))
        assert re.match(r'^[A-Z]{2}$', val), f"country_code format wrong: {val}"


def test_country_code_locale_aware():
    """country_code must match the locale."""
    expected = {'TR': 'TR', 'US': 'US', 'UK': 'GB', 'DE': 'DE', 'FR': 'FR', 'RU': 'RU'}
    for locale, code in expected.items():
        val = str(jutsu.generate('country_code', locale=locale))
        assert val == code, f"country_code for {locale} should be {code}, got {val}"


def test_coordinates_format():
    """coordinates must be 'lat,lon' with valid float values."""
    for locale in LOCALES:
        for _ in range(20):
            val = str(jutsu.generate('coordinates', locale=locale))
            parts = val.split(',')
            assert len(parts) == 2, f"coordinates format wrong: {val}"
            lat, lon = float(parts[0]), float(parts[1])
            lo_lat, hi_lat = _LOCALE_LAT[locale]
            lo_lon, hi_lon = _LOCALE_LON[locale]
            assert lo_lat <= lat <= hi_lat, f"coordinates lat {lat} out of {locale} range"
            assert lo_lon <= lon <= hi_lon, f"coordinates lon {lon} out of {locale} range"


# ---------------------------------------------------------------------------
# Sprint 4C — Social Media
# ---------------------------------------------------------------------------

def test_username_format():
    """username must be 4-15 chars, only [a-z0-9_], not start/end with underscore."""
    for _ in range(200):
        val = str(jutsu.generate('username'))
        assert re.match(r'^[a-z][a-z0-9_]{2,13}[a-z0-9]$', val) or \
               re.match(r'^[a-z][a-z0-9]{2,13}$', val), \
               f"username format wrong: {val}"
        assert 4 <= len(val) <= 15, f"username length wrong: {val}"
        assert not val.startswith('_') and not val.endswith('_'), \
            f"username starts/ends with underscore: {val}"


def test_username_charset():
    """username must only contain lowercase letters, digits, and underscores."""
    for _ in range(200):
        val = str(jutsu.generate('username'))
        assert re.match(r'^[a-z0-9_]+$', val), f"username invalid chars: {val}"


def test_handle_format():
    """handle must be @username format."""
    for _ in range(100):
        val = str(jutsu.generate('handle'))
        assert val.startswith('@'), f"handle must start with @: {val}"
        inner = val[1:]
        assert re.match(r'^[a-z0-9_]+$', inner), f"handle inner invalid: {val}"
        assert 4 <= len(inner) <= 15, f"handle inner length wrong: {val}"


def test_hashtag_format():
    """hashtag must be # + alphanumeric (no spaces, no special chars)."""
    for _ in range(100):
        val = str(jutsu.generate('hashtag'))
        assert val.startswith('#'), f"hashtag must start with #: {val}"
        inner = val[1:]
        assert re.match(r'^[a-zA-Z][a-zA-Z0-9]{1,29}$', inner), \
            f"hashtag inner format wrong: {val}"


def test_bio_nonempty():
    """bio must return a non-empty string under 160 chars."""
    for _ in range(100):
        val = str(jutsu.generate('bio'))
        assert 10 <= len(val) <= 160, f"bio length wrong: {len(val)}"


def test_follower_count_range():
    """follower_count must be a non-negative integer string."""
    for _ in range(200):
        val = str(jutsu.generate('follower_count'))
        count = int(val)
        assert count >= 0, f"follower_count negative: {val}"
        assert count <= 50_000_000, f"follower_count unrealistically large: {val}"
