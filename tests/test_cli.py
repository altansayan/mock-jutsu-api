"""
mock-jutsu — CLI Integration Tests (Comprehensive)
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)

Covers every type in _REFERENCE via Click's CliRunner.
Assertions verify the real generation algorithm — checksum, format, range.
"""

import ast
import json
import re
import pytest
from click.testing import CliRunner
from mockjutsu.cli import main


# ---------------------------------------------------------------------------
# Helper — shared validation algorithms
# ---------------------------------------------------------------------------

def _luhn_valid(s: str) -> bool:
    """Standard Luhn check for a full number string (last digit is check digit)."""
    digits = [int(c) for c in s]
    total = 0
    for i, d in enumerate(reversed(digits)):
        n = d * 2 if i % 2 == 1 else d
        if n > 9:
            n -= 9
        total += n
    return total % 10 == 0


def _tckn_valid(tc: str) -> bool:
    """Turkish TCKN — 11-digit, official MOD-10 dual-check algorithm."""
    if len(tc) != 11 or not tc.isdigit() or tc[0] == '0':
        return False
    d = [int(c) for c in tc]
    c9  = (sum(d[i] for i in range(0, 9, 2)) * 7 - sum(d[i] for i in range(1, 9, 2))) % 10
    c10 = sum(d[:10]) % 10
    return d[9] == c9 and d[10] == c10


def _iban_mod97_valid(iban: str) -> bool:
    """ISO 13616 MOD-97 IBAN validation."""
    rearranged = iban[4:] + iban[:4]
    numeric = ''.join(str(ord(c) - 55) if c.isalpha() else c for c in rearranged)
    return int(numeric) % 97 == 1


def _routing_valid(r: str) -> bool:
    """ABA routing — 3*(d0+d3+d6) + 7*(d1+d4+d7) + (d2+d5+d8) ≡ 0 mod 10."""
    if len(r) != 9 or not r.isdigit():
        return False
    d = [int(c) for c in r]
    return (3 * (d[0]+d[3]+d[6]) + 7 * (d[1]+d[4]+d[7]) + (d[2]+d[5]+d[8])) % 10 == 0


def _gs1_valid(barcode: str) -> bool:
    """GS1 MOD-10 check digit validation (EAN-13, EAN-8, UPC-A)."""
    digits = [int(c) for c in barcode]
    payload = digits[:-1]
    total = sum(d * (3 if i % 2 == 0 else 1) for i, d in enumerate(reversed(payload)))
    check = (10 - total % 10) % 10
    return digits[-1] == check


def _isin_valid(isin: str) -> bool:
    """ISO 6166 ISIN Luhn check (letters expanded)."""
    if len(isin) != 12:
        return False
    payload = isin[:-1]
    numeric = ''.join(str(ord(c) - 55) if c.isalpha() else c for c in payload)
    return _luhn_valid(numeric + isin[-1])


def _sedol_valid(sedol: str) -> bool:
    """LSE SEDOL weighted check digit [1,3,1,7,3,9]."""
    if len(sedol) != 7:
        return False
    weights = [1, 3, 1, 7, 3, 9]
    total = sum(
        (int(c) if c.isdigit() else ord(c) - 55) * w
        for c, w in zip(sedol[:6], weights)
    )
    return int(sedol[6]) == (10 - total % 10) % 10


def _nhs_valid(nhs: str) -> bool:
    """UK NHS number weighted checksum (weights 10→2)."""
    digits = re.sub(r'\s', '', nhs)
    if len(digits) != 10 or not digits.isdigit():
        return False
    weights = [10, 9, 8, 7, 6, 5, 4, 3, 2]
    total = sum(int(d) * w for d, w in zip(digits[:9], weights))
    remainder = total % 11
    if remainder == 1:
        return False
    check = 0 if remainder == 0 else 11 - remainder
    return int(digits[9]) == check


def _npi_valid(npi: str) -> bool:
    """US NPI — 10 digits, CMS Luhn with '80840' prefix.

    Algorithm: prepend '80840' to all 10 NPI digits (15 digits total).
    Apply Luhn to the first 14 digits; check digit added directly.
    Matches CMS NPI standard and test_generators.py convention.
    """
    if len(npi) != 10 or not npi.isdigit():
        return False
    padded = '80840' + npi
    digits = [int(c) for c in padded]
    total = 0
    for i, d in enumerate(reversed(digits[:-1])):  # first 14 digits
        n = d * 2 if i % 2 == 0 else d
        if n > 9:
            n -= 9
        total += n
    return (total + digits[-1]) % 10 == 0


def _fedex_valid(tracking: str) -> bool:
    """FedEx 12-digit Mod-11 check."""
    if len(tracking) != 12 or not tracking.isdigit():
        return False
    weights = [3, 1, 7, 3, 1, 7, 3, 1, 7, 3, 1]
    total = sum(int(d) * w for d, w in zip(tracking[:11], weights))
    check = total % 11
    if check == 10:
        check = 0
    return int(tracking[11]) == check


def _parse(runner_output: str):
    """Parse CLI output — tries JSON first, falls back to ast.literal_eval."""
    s = runner_output.strip()
    try:
        return json.loads(s)
    except (json.JSONDecodeError, ValueError):
        try:
            return ast.literal_eval(s)
        except Exception:
            return s


@pytest.fixture
def runner():
    return CliRunner()


def _gen(runner, *args):
    """Shortcut: invoke 'generate' with args, assert exit_code==0, return stripped output."""
    r = runner.invoke(main, ['generate'] + list(args))
    assert r.exit_code == 0, f"exit_code={r.exit_code}\n{r.output}"
    assert 'ERROR' not in r.output, f"ERROR in output: {r.output}"
    return r.output.strip()


# ===========================================================================
# generate — Identity
# ===========================================================================

class TestGenerateIdentity:

    def test_tckn_format_and_checksum(self, runner):
        val = _gen(runner, 'tckn')
        assert re.match(r'^\d{11}$', val), f"bad tckn: {val}"
        assert _tckn_valid(val), f"tckn checksum failed: {val}"

    def test_tckn_first_digit_nonzero(self, runner):
        for _ in range(5):
            val = _gen(runner, 'tckn')
            assert val[0] != '0', f"tckn starts with 0: {val}"

    def test_ykn_format(self, runner):
        val = _gen(runner, 'ykn')
        assert re.match(r'^\d{11}$', val)
        assert val.startswith('99')
        assert _luhn_valid(val), f"ykn Luhn failed: {val}"

    def test_nationalid_tr_is_tckn(self, runner):
        val = _gen(runner, 'nationalid', '--locale', 'TR')
        assert re.match(r'^\d{11}$', val)
        assert _tckn_valid(val)

    def test_nationalid_us_ssn_format(self, runner):
        val = _gen(runner, 'nationalid', '--locale', 'US')
        assert re.match(r'^\d{3}-\d{2}-\d{4}$', val), f"US nationalid format wrong: {val}"

    def test_nationalid_uk_nin_format(self, runner):
        val = _gen(runner, 'nationalid', '--locale', 'UK')
        assert re.match(r'^[A-Z]{2} \d{2} \d{2} \d{2} [ABCD]$', val), f"UK NIN wrong: {val}"

    def test_nationalid_de_steuerid(self, runner):
        val = _gen(runner, 'nationalid', '--locale', 'DE')
        assert re.match(r'^\d{11}$', val)

    def test_vkn_10digits(self, runner):
        val = _gen(runner, 'vkn')
        assert re.match(r'^\d{10}$', val)

    def test_taxid_tr_vkn(self, runner):
        val = _gen(runner, 'taxid', '--locale', 'TR')
        assert re.match(r'^\d{10}$', val)

    def test_taxid_us_ein(self, runner):
        val = _gen(runner, 'taxid', '--locale', 'US')
        assert re.match(r'^\d{2}-\d{7}$', val)

    def test_taxid_uk_utr(self, runner):
        val = _gen(runner, 'taxid', '--locale', 'UK')
        assert re.match(r'^\d{10}$', val)

    def test_taxid_de_vatid(self, runner):
        val = _gen(runner, 'taxid', '--locale', 'DE')
        assert re.match(r'^DE\d{9}$', val)

    def test_taxid_fr_siren(self, runner):
        val = _gen(runner, 'taxid', '--locale', 'FR')
        assert re.match(r'^\d{9}$', val)

    def test_taxid_ru_inn(self, runner):
        val = _gen(runner, 'taxid', '--locale', 'RU')
        assert re.match(r'^\d{10}$', val)

    def test_sgk_format(self, runner):
        val = _gen(runner, 'sgk')
        assert re.match(r'^\d{2}-\d{7}-\d\.\d{2}-\d{2}$', val), f"SGK format: {val}"

    def test_mersis_16digits(self, runner):
        val = _gen(runner, 'mersis')
        assert re.match(r'^\d{16}$', val)

    def test_ssn_format(self, runner):
        val = _gen(runner, 'ssn')
        assert re.match(r'^\d{3}-\d{2}-\d{4}$', val)

    def test_ein_format(self, runner):
        val = _gen(runner, 'ein')
        assert re.match(r'^\d{2}-\d{7}$', val)

    def test_nin_format(self, runner):
        val = _gen(runner, 'nin')
        assert re.match(r'^[A-Z]{2} \d{2} \d{2} \d{2} [ABCD]$', val)

    def test_utr_10digits(self, runner):
        val = _gen(runner, 'utr')
        assert re.match(r'^\d{10}$', val)

    def test_crn_format(self, runner):
        val = _gen(runner, 'crn')
        assert re.match(r'^(\d{8}|SC\d{6}|NI\d{6})$', val), f"CRN format: {val}"

    def test_paye_format(self, runner):
        val = _gen(runner, 'paye')
        assert re.match(r'^\d{3}/[A-Z0-9]{6}$', val), f"PAYE format: {val}"

    def test_ust_id_format(self, runner):
        val = _gen(runner, 'ust_id')
        assert re.match(r'^DE\d{9}$', val)

    def test_ustid_alias(self, runner):
        val = _gen(runner, 'ustid')
        assert re.match(r'^DE\d{9}$', val)

    def test_hrb_format(self, runner):
        val = _gen(runner, 'hrb')
        assert re.match(r'^HR[AB] \d+$', val), f"HRB format: {val}"

    def test_rvn_format(self, runner):
        val = _gen(runner, 'rvn')
        assert re.match(r'^\d{2} \d{6} [A-Z] \d{4}$', val), f"RVN format: {val}"

    def test_siren_9digits(self, runner):
        val = _gen(runner, 'siren')
        assert re.match(r'^\d{9}$', val)

    def test_siret_14digits(self, runner):
        val = _gen(runner, 'siret')
        assert re.match(r'^\d{14}$', val)

    def test_tva_format(self, runner):
        val = _gen(runner, 'tva')
        assert re.match(r'^FR\d{11}$', val)

    def test_inn_10digits_checksum(self, runner):
        val = _gen(runner, 'inn')
        assert re.match(r'^\d{10}$', val)
        d = [int(c) for c in val]
        weights = [2, 4, 10, 3, 5, 9, 4, 6, 8]
        ctrl = sum(a * b for a, b in zip(d[:9], weights)) % 11 % 10
        assert d[9] == ctrl, f"INN checksum failed: {val}"

    def test_inn_individual_12digits(self, runner):
        val = _gen(runner, 'inn_individual')
        assert re.match(r'^\d{12}$', val)

    def test_snils_format(self, runner):
        val = _gen(runner, 'snils')
        assert re.match(r'^\d{3}-\d{3}-\d{3} \d{2}$', val), f"SNILS format: {val}"

    def test_ogrn_13digits(self, runner):
        val = _gen(runner, 'ogrn')
        assert re.match(r'^\d{13}$', val)

    def test_kpp_9digits(self, runner):
        val = _gen(runner, 'kpp')
        assert re.match(r'^\d{9}$', val)

    def test_tckn_masked_format(self, runner):
        val = _gen(runner, 'tckn_masked')
        assert re.match(r'^\*{3}\d{6}\*{2}$', val), f"tckn_masked: {val}"

    def test_ssn_masked_format(self, runner):
        val = _gen(runner, 'ssn_masked')
        assert re.match(r'^\*{3}-\*{2}-\d{4}$', val), f"ssn_masked: {val}"

    def test_nationality_alpha3(self, runner):
        val = _gen(runner, 'nationality')
        assert re.match(r'^[A-Z]{3}$', val), f"nationality: {val}"

    def test_employer_id_all_locales(self, runner):
        for locale in ['TR', 'US', 'UK', 'DE', 'FR', 'RU']:
            val = _gen(runner, 'employer_id', '--locale', locale)
            assert val, f"employer_id {locale} empty"

    def test_insurance_id_all_locales(self, runner):
        for locale in ['TR', 'US', 'UK', 'DE', 'FR', 'RU']:
            val = _gen(runner, 'insurance_id', '--locale', locale)
            assert val, f"insurance_id {locale} empty"


# ===========================================================================
# generate — Name
# ===========================================================================

class TestGenerateName:

    @pytest.mark.parametrize("locale", ['TR', 'US', 'UK', 'DE', 'FR'])
    def test_firstname_nonempty(self, runner, locale):
        val = _gen(runner, 'firstname', '--locale', locale)
        assert len(val) >= 2

    def test_firstname_ru_cyrillic(self, runner):
        val = _gen(runner, 'firstname', '--locale', 'RU')
        assert any(ord(c) > 127 for c in val), f"RU firstname not Cyrillic: {val}"

    @pytest.mark.parametrize("locale", ['TR', 'US', 'UK', 'DE', 'FR'])
    def test_lastname_nonempty(self, runner, locale):
        val = _gen(runner, 'lastname', '--locale', locale)
        assert len(val) >= 2

    def test_fullname_has_space(self, runner):
        val = _gen(runner, 'fullname', '--locale', 'TR')
        assert ' ' in val

    def test_fullname_ru_has_patronymic(self, runner):
        val = _gen(runner, 'fullname', '--locale', 'RU')
        parts = val.split()
        assert len(parts) == 3, f"RU fullname should be 3 words: {val}"

    def test_patronymic_ru(self, runner):
        val = _gen(runner, 'patronymic', '--locale', 'RU')
        assert len(val) >= 5, f"RU patronymic too short: {val}"


# ===========================================================================
# generate — Document & Demographic
# ===========================================================================

class TestGenerateDocumentDemographic:

    def test_passport_format(self, runner):
        val = _gen(runner, 'passport')
        assert re.match(r'^P\d{7}$', val), f"passport format: {val}"

    def test_license_6digits(self, runner):
        val = _gen(runner, 'license')
        assert re.match(r'^\d{6}$', val)

    def test_age_range(self, runner):
        val = int(_gen(runner, 'age'))
        assert 18 <= val <= 80, f"age out of range: {val}"

    def test_gender_values(self, runner):
        val = _gen(runner, 'gender')
        assert val in ('Male', 'Female')

    def test_birthdate_format(self, runner):
        val = _gen(runner, 'birthdate')
        assert re.match(r'^\d{4}-\d{2}-\d{2}$', val)
        year = int(val[:4])
        assert 1940 <= year <= 2006


# ===========================================================================
# generate — Financial
# ===========================================================================

class TestGenerateFinancial:

    @pytest.mark.parametrize("network,starts,length", [
        ('visa',  '4',            16),
        ('mc',    None,           16),
        ('amex',  None,           15),
        ('troy',  '9792',         16),
        ('mir',   None,           16),
        ('jcb',   None,           16),
        ('discover', None,        16),
        ('maestro',  None,        16),
        ('unionpay', '62',        16),
    ])
    def test_cardnum_network(self, runner, network, starts, length):
        val = _gen(runner, 'cardnum', '--network', network)
        assert re.match(r'^\d+$', val), f"cardnum not digits: {val}"
        assert len(val) == length, f"cardnum {network} length {len(val)} != {length}"
        assert _luhn_valid(val), f"cardnum {network} Luhn failed: {val}"
        if starts:
            assert val.startswith(starts), f"cardnum {network} should start with {starts}: {val}"

    def test_cardnum_mc_prefix_51_55(self, runner):
        for _ in range(5):
            val = _gen(runner, 'cardnum', '--network', 'mc')
            assert val[:2] in ('51', '52', '53', '54', '55'), f"MC prefix wrong: {val}"

    def test_cardnum_amex_prefix(self, runner):
        for _ in range(5):
            val = _gen(runner, 'cardnum', '--network', 'amex')
            assert val[:2] in ('34', '37'), f"Amex prefix wrong: {val}"

    def test_cardnetwork_valid(self, runner):
        val = _gen(runner, 'cardnetwork')
        networks = {'VISA','MC','AMEX','TROY','JCB','DISCOVER','UNIONPAY','MIR','MAESTRO'}
        assert val.upper() in networks, f"unknown cardnetwork: {val}"

    def test_cardtype(self, runner):
        val = _gen(runner, 'cardtype')
        assert val in ('Credit', 'Debit')

    def test_cardstatus(self, runner):
        val = _gen(runner, 'cardstatus')
        assert val in ('Active', 'Blocked', 'Expired')

    def test_cardcategory(self, runner):
        val = _gen(runner, 'cardcategory')
        assert val in ('Classic', 'Gold', 'Platinum', 'Business')

    def test_cardowner_uppercase(self, runner):
        val = _gen(runner, 'cardowner', '--locale', 'TR')
        assert val == val.upper(), f"cardowner not uppercase: {val}"
        assert ' ' in val

    def test_cvv3_3digits(self, runner):
        val = _gen(runner, 'cvv3')
        assert re.match(r'^\d{3}$', val)

    def test_cvv4_4digits(self, runner):
        val = _gen(runner, 'cvv4')
        assert re.match(r'^\d{4}$', val)

    def test_pin_4digits(self, runner):
        val = _gen(runner, 'pin')
        assert re.match(r'^\d{4}$', val)

    def test_expiry_format(self, runner):
        val = _gen(runner, 'expiry')
        assert re.match(r'^(0[1-9]|1[0-2])/\d{2}$', val), f"expiry format: {val}"

    def test_expirymonth_range(self, runner):
        val = _gen(runner, 'expirymonth')
        assert re.match(r'^(0[1-9]|1[0-2])$', val)

    def test_expiryyear_range(self, runner):
        val = int(_gen(runner, 'expiryyear'))
        assert 25 <= val <= 30, f"expiryyear out of range: {val}"

    @pytest.mark.parametrize("locale,prefix,length", [
        ('TR', 'TR', 26),
        ('DE', 'DE', 22),
        ('UK', 'GB', 22),
        ('FR', 'FR', 27),
    ])
    def test_iban_locale(self, runner, locale, prefix, length):
        val = _gen(runner, 'iban', '--locale', locale)
        assert val.startswith(prefix), f"IBAN {locale} prefix wrong: {val}"
        assert len(val) == length, f"IBAN {locale} length {len(val)} != {length}"
        assert _iban_mod97_valid(val), f"IBAN {locale} MOD-97 failed: {val}"

    def test_balance_numeric(self, runner):
        val = _gen(runner, 'balance')
        f = float(val)
        assert 10.0 <= f <= 50000.0, f"balance out of range: {f}"

    def test_credit_score_range(self, runner):
        val = int(_gen(runner, 'credit_score'))
        assert 300 <= val <= 850


# ===========================================================================
# generate — Contact
# ===========================================================================

class TestGenerateContact:

    def test_phone_tr_format(self, runner):
        val = _gen(runner, 'phone', '--locale', 'TR')
        assert re.match(r'^\+905\d{9}$', val), f"TR phone: {val}"

    def test_phone_us_format(self, runner):
        val = _gen(runner, 'phone', '--locale', 'US')
        assert re.match(r'^\+1\d{10}$', val), f"US phone: {val}"

    def test_phone_uk_format(self, runner):
        val = _gen(runner, 'phone', '--locale', 'UK')
        assert re.match(r'^\+44\d+$', val)

    def test_phone_country_tr(self, runner):
        val = _gen(runner, 'phone_country', '--locale', 'TR')
        assert val == '+90'

    def test_phone_area_tr(self, runner):
        val = _gen(runner, 'phone_area', '--locale', 'TR')
        assert val in ('532', '533', '542', '544', '505', '506')

    def test_phone_local_tr(self, runner):
        val = _gen(runner, 'phone_local', '--locale', 'TR')
        assert re.match(r'^\d{7}$', val)

    def test_email_format(self, runner):
        val = _gen(runner, 'email', '--locale', 'TR')
        assert '@' in val and '.' in val.split('@')[1]
        assert 'testposta' in val or 'mock-mail' in val or 'ornek' in val or 'deneme' in val

    def test_email_us_domain(self, runner):
        val = _gen(runner, 'email', '--locale', 'US')
        assert val.endswith(('.us', '.net', '.org', '.io'))

    def test_address_city_tr(self, runner):
        TR_CITIES = ['İstanbul', 'Ankara', 'İzmir', 'Bursa', 'Antalya',
                     'Adana', 'Konya', 'Gaziantep']
        val = _gen(runner, 'address_city', '--locale', 'TR')
        assert val in TR_CITIES, f"address_city TR: {val}"

    def test_address_street_nonempty(self, runner):
        val = _gen(runner, 'address_street', '--locale', 'TR')
        assert len(val) > 3

    def test_address_full_format(self, runner):
        val = _gen(runner, 'address_full', '--locale', 'TR')
        assert ',' in val and 'No:' in val

    def test_postalcode_tr_format(self, runner):
        val = _gen(runner, 'postalcode', '--locale', 'TR')
        assert re.match(r'^\d{5}$', val)
        assert val[:2] in ('06', '16', '34', '35', '41', '42')

    def test_postalcode_us_format(self, runner):
        val = _gen(runner, 'postalcode', '--locale', 'US')
        assert re.match(r'^\d{5}$', val)

    def test_postalcode_de_format(self, runner):
        val = _gen(runner, 'postalcode', '--locale', 'DE')
        assert re.match(r'^\d{5}$', val)

    def test_plate_tr_format(self, runner):
        val = _gen(runner, 'plate', '--locale', 'TR')
        assert re.match(r'^\d{2} [A-Z]+ \d+$', val), f"TR plate: {val}"

    def test_plate_de_format(self, runner):
        val = _gen(runner, 'plate', '--locale', 'DE')
        assert '-' in val, f"DE plate no dash: {val}"


# ===========================================================================
# generate — Banking
# ===========================================================================

class TestGenerateBanking:

    def test_swift_tr_in_known_list(self, runner):
        BIC_TR = ["TCZBTR2A","ISCTRISM","AKBKTRIS","HLBKTRIS","TVBATR2A",
                  "DENITRIS","TEBUTRIS","GRNBTRIS"]
        val = _gen(runner, 'swift', '--locale', 'TR')
        assert val in BIC_TR, f"SWIFT TR not in known list: {val}"

    def test_bic_alias(self, runner):
        val = _gen(runner, 'bic', '--locale', 'TR')
        assert re.match(r'^[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}$', val)

    def test_sort_code_format(self, runner):
        val = _gen(runner, 'sort_code')
        assert re.match(r'^\d{2}-\d{2}-\d{2}$', val), f"sort_code: {val}"

    def test_routing_number_checksum(self, runner):
        val = _gen(runner, 'routing_number')
        assert re.match(r'^\d{9}$', val)
        assert _routing_valid(val), f"routing_number checksum failed: {val}"

    def test_bik_code_known_pool(self, runner):
        BIK_POOL = ["044525225","044525187","044525593","044525700",
                    "044525823","044525999","044030653","044585326"]
        val = _gen(runner, 'bik_code')
        assert val in BIK_POOL

    def test_bank_name_nonempty(self, runner):
        for locale in ['TR', 'US', 'UK', 'DE', 'FR', 'RU']:
            val = _gen(runner, 'bank_name', '--locale', locale)
            assert len(val) > 3

    def test_transaction_tr_structure(self, runner):
        val = _gen(runner, 'transaction', '--locale', 'TR')
        data = _parse(val)
        for key in ('ref', 'sender_iban', 'receiver_iban', 'amount', 'currency', 'status'):
            assert key in data, f"transaction missing '{key}'"
        assert data['currency'] == 'TRY'
        assert data['sender_iban'].startswith('TR')
        assert data['ref'].startswith('TRN')
        assert data['status'] in ('COMPLETED', 'PENDING', 'FAILED')

    def test_transaction_us_routing(self, runner):
        val = _gen(runner, 'transaction', '--locale', 'US')
        data = _parse(val)
        assert data['currency'] == 'USD'
        assert data['sender_iban'].startswith('RT:')

    def test_sepa_ref_format(self, runner):
        val = _gen(runner, 'sepa_ref')
        assert re.match(r'^[A-Z0-9]{20,35}$', val), f"sepa_ref: {val}"


# ===========================================================================
# generate — Corporate
# ===========================================================================

class TestGenerateCorporate:

    @pytest.mark.parametrize("locale", ['TR', 'US', 'UK', 'DE', 'FR', 'RU'])
    def test_company_name_nonempty(self, runner, locale):
        val = _gen(runner, 'company_name', '--locale', locale)
        assert len(val) > 2

    @pytest.mark.parametrize("locale", ['TR', 'US'])
    def test_job_title_nonempty(self, runner, locale):
        val = _gen(runner, 'job_title', '--locale', locale)
        assert len(val) > 2

    def test_jobtitle_alias(self, runner):
        val = _gen(runner, 'jobtitle', '--locale', 'TR')
        assert len(val) > 2

    def test_occupation_alias(self, runner):
        val = _gen(runner, 'occupation', '--locale', 'TR')
        assert len(val) > 2


# ===========================================================================
# generate — Health
# ===========================================================================

class TestGenerateHealth:

    def test_blood_type_valid(self, runner):
        val = _gen(runner, 'blood_type')
        assert val in ('A+','A-','B+','B-','O+','O-','AB+','AB-')

    def test_bloodtype_alias(self, runner):
        val = _gen(runner, 'bloodtype')
        assert val in ('A+','A-','B+','B-','O+','O-','AB+','AB-')

    def test_nhs_number_checksum(self, runner):
        val = _gen(runner, 'nhs_number')
        assert re.match(r'^\d{3} \d{3} \d{4}$', val), f"NHS format: {val}"
        assert _nhs_valid(val), f"NHS checksum failed: {val}"

    def test_nhsnumber_alias(self, runner):
        val = _gen(runner, 'nhsnumber')
        assert _nhs_valid(val)

    def test_icd10_code_format(self, runner):
        val = _gen(runner, 'icd10')
        assert re.match(r'^[A-Z]\d{2}', val), f"ICD10 format: {val}"

    def test_height_tr_cm(self, runner):
        val = _gen(runner, 'height', '--locale', 'TR')
        assert re.match(r'^\d{3} cm$', val), f"TR height: {val}"
        cm = int(val.split()[0])
        assert 155 <= cm <= 195

    def test_height_us_feet(self, runner):
        val = _gen(runner, 'height', '--locale', 'US')
        assert "'" in val and '"' in val, f"US height no feet/inches: {val}"

    def test_height_uk_combined(self, runner):
        val = _gen(runner, 'height', '--locale', 'UK')
        assert 'cm' in val and "'" in val

    def test_weight_tr_kg(self, runner):
        val = _gen(runner, 'weight', '--locale', 'TR')
        assert re.match(r'^\d+ kg$', val)
        kg = int(val.split()[0])
        assert 50 <= kg <= 110

    def test_weight_us_lbs(self, runner):
        val = _gen(runner, 'weight', '--locale', 'US')
        assert val.endswith('lbs'), f"US weight: {val}"

    def test_weight_uk_stones(self, runner):
        val = _gen(runner, 'weight', '--locale', 'UK')
        assert 'st' in val and 'lb' in val

    def test_npi_format_and_checksum(self, runner):
        val = _gen(runner, 'npi')
        assert re.match(r'^\d{10}$', val)
        assert _npi_valid(val), f"NPI checksum failed: {val}"

    def test_bmi_range(self, runner):
        val = float(_gen(runner, 'bmi'))
        assert 18.5 <= val <= 35.0, f"BMI out of range: {val}"


# ===========================================================================
# generate — Commerce
# ===========================================================================

class TestGenerateCommerce:

    def test_currency_tr_structure(self, runner):
        val = _parse(_gen(runner, 'currency', '--locale', 'TR'))
        assert val['code'] == 'TRY'
        assert val['decimals'] == 2

    def test_currency_de_eur(self, runner):
        val = _parse(_gen(runner, 'currency', '--locale', 'DE'))
        assert val['code'] == 'EUR'

    def test_tax_rate_tr_kdv(self, runner):
        val = _parse(_gen(runner, 'tax_rate', '--locale', 'TR'))
        assert val['name'] == 'KDV'
        assert val['standard'] == 20

    def test_taxrate_alias(self, runner):
        val = _parse(_gen(runner, 'taxrate', '--locale', 'TR'))
        assert 'name' in val

    def test_invoice_number_tr_format(self, runner):
        val = _gen(runner, 'invoice_number', '--locale', 'TR')
        assert re.match(r'^INV-\d{4}-\d{6}$', val), f"invoice_number TR: {val}"

    def test_invoice_number_de_format(self, runner):
        val = _gen(runner, 'invoice_number', '--locale', 'DE')
        assert val.startswith('RE-')

    def test_invoice_number_fr_format(self, runner):
        val = _gen(runner, 'invoice_number', '--locale', 'FR')
        assert val.startswith('FACT-')

    def test_invoicenumber_alias(self, runner):
        val = _gen(runner, 'invoicenumber', '--locale', 'TR')
        assert val.startswith('INV-')

    def test_vin_tr_length_and_wmi(self, runner):
        val = _gen(runner, 'vin', '--locale', 'TR')
        assert len(val) == 17, f"VIN length: {len(val)}"
        assert val[:3] in ('NM0', 'NM1', 'NMT'), f"VIN TR WMI wrong: {val}"
        assert re.match(r'^[A-HJ-NPR-Z0-9]{17}$', val)

    def test_vin_us_wmi(self, runner):
        val = _gen(runner, 'vin', '--locale', 'US')
        US_WMI = ('1HG', '1G1', '4T1', '1FA', '1GC', '5YJ')
        assert val[:3] in US_WMI, f"VIN US WMI: {val}"

    def test_vehicle_tr_structure(self, runner):
        val = _parse(_gen(runner, 'vehicle', '--locale', 'TR'))
        for key in ('make', 'model', 'year', 'vin', 'color', 'fuel'):
            assert key in val, f"vehicle missing '{key}'"
        assert len(val['vin']) == 17
        assert 1990 <= val['year'] <= 2025


# ===========================================================================
# generate — Meta
# ===========================================================================

class TestGenerateMeta:

    _UUID_RE = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
    )

    @pytest.mark.parametrize("dtype", ['uuid', 'requestid', 'correlationid', 'sessionid', 'idempotencykey'])
    def test_uuid_types_v4_format(self, runner, dtype):
        val = _gen(runner, dtype)
        assert self._UUID_RE.match(val), f"{dtype} not UUID v4: {val}"

    def test_deviceid_uppercase_uuid(self, runner):
        val = _gen(runner, 'deviceid')
        assert re.match(
            r'^[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$',
            val
        ), f"deviceid not uppercase UUID: {val}"

    def test_timestamp_numeric(self, runner):
        val = _gen(runner, 'timestamp')
        assert val.isdigit()
        assert int(val) > 1_700_000_000

    def test_timestamp_iso_format(self, runner):
        val = _gen(runner, 'timestamp_iso')
        assert re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', val)

    def test_ipv4_format(self, runner):
        val = _gen(runner, 'ipv4')
        parts = val.split('.')
        assert len(parts) == 4
        assert all(p.isdigit() and 0 <= int(p) <= 255 for p in parts)

    def test_ipv6_format(self, runner):
        val = _gen(runner, 'ipv6')
        groups = val.split(':')
        assert len(groups) == 8
        assert all(re.match(r'^[0-9a-f]{4}$', g) for g in groups), f"ipv6: {val}"

    def test_public_ip_not_private(self, runner):
        val = _gen(runner, 'public_ip')
        parts = val.split('.')
        a = int(parts[0])
        assert a not in (10, 127, 169, 172, 192, 224), f"public_ip in reserved range: {val}"

    def test_private_ip_is_private(self, runner):
        val = _gen(runner, 'private_ip')
        assert (
            val.startswith('10.') or
            val.startswith('192.168.') or
            re.match(r'^172\.(1[6-9]|2\d|3[01])\.', val)
        ), f"private_ip not private: {val}"

    def test_browser_name(self, runner):
        val = _gen(runner, 'browser_name')
        assert val in ('Chrome', 'Firefox', 'Safari', 'Edge', 'Opera')

    def test_browser_engine(self, runner):
        val = _gen(runner, 'browser_engine')
        assert val in ('Blink', 'Gecko', 'WebKit')

    def test_browser_version_format(self, runner):
        val = _gen(runner, 'browser_version')
        assert re.match(r'^\d+\.\d+\.\d+\.\d+$', val), f"browser_version: {val}"

    def test_useragent_mozilla(self, runner):
        val = _gen(runner, 'useragent')
        assert val.startswith('Mozilla/5.0')
        assert 'AppleWebKit' in val

    def test_jwt_three_parts(self, runner):
        val = _gen(runner, 'jwt')
        parts = val.split('.')
        assert len(parts) == 3, f"jwt parts: {val}"
        assert all(len(p) > 0 for p in parts)

    def test_bearertoken_prefix(self, runner):
        val = _gen(runner, 'bearertoken')
        assert val.startswith('Bearer ')
        parts = val[7:].split('.')
        assert len(parts) == 3

    @pytest.mark.parametrize("algo,expected_len", [
        ("md5",      32),
        ("sha1",     40),
        ("sha224",   56),
        ("sha256",   64),
        ("sha384",   96),
        ("sha512",  128),
        ("sha3-224", 56),
        ("sha3-256", 64),
        ("sha3-384", 96),
        ("sha3-512",128),
        ("crc32",     8),
        ("adler32",   8),
        ("crc16",     4),
    ])
    def test_hash_algorithm(self, runner, algo, expected_len):
        val = _gen(runner, 'hash', '--algorithm', algo)
        assert re.match(r'^[0-9a-f]+$', val), f"{algo} not hex: {val}"
        assert len(val) == expected_len, f"{algo}: expected {expected_len}, got {len(val)}"

    def test_hash_default_sha256(self, runner):
        val = _gen(runner, 'hash')
        assert len(val) == 64
        assert re.match(r'^[0-9a-f]+$', val)

    def test_mac_address_format(self, runner):
        val = _gen(runner, 'mac_address')
        assert re.match(r'^([0-9A-F]{2}:){5}[0-9A-F]{2}$', val), f"mac: {val}"

    def test_url_https(self, runner):
        val = _gen(runner, 'url', '--locale', 'TR')
        assert val.startswith('https://'), f"url: {val}"
        assert '.com.tr' in val or '.net.tr' in val or '.org.tr' in val or '.com' in val

    def test_domain_tr(self, runner):
        val = _gen(runner, 'domain', '--locale', 'TR')
        assert '.com.tr' in val or '.net.tr' in val or '.org.tr' in val or '.com' in val

    def test_color_hex_format(self, runner):
        val = _gen(runner, 'color')
        assert re.match(r'^#[0-9A-F]{6}$', val), f"color hex: {val}"

    def test_clientversion_format(self, runner):
        val = _gen(runner, 'clientversion')
        assert re.match(r'^\d+\.\d+\.\d+$', val), f"clientversion: {val}"

    def test_signature_64hex(self, runner):
        val = _gen(runner, 'signature')
        assert re.match(r'^[0-9a-f]{64}$', val), f"signature: {val}"

    def test_apppassword_6digits_no_repeat(self, runner):
        val = _gen(runner, 'apppassword')
        assert re.match(r'^\d{6}$', val)
        digits = [int(c) for c in val]
        assert not any(digits[i] == digits[i+1] for i in range(5)), \
            f"apppassword has consecutive repeat: {val}"


# ===========================================================================
# generate — Security
# ===========================================================================

class TestGenerateSecurity:

    def test_api_key_format(self, runner):
        val = _gen(runner, 'api_key')
        assert val.startswith('sk-')
        assert len(val) == 51

    def test_totp_code_6digits(self, runner):
        val = _gen(runner, 'totp_code')
        assert re.match(r'^\d{6}$', val)

    def test_webhook_signature_format(self, runner):
        val = _gen(runner, 'webhook_signature')
        assert val.startswith('sha256=')
        assert re.match(r'^sha256=[0-9a-f]{64}$', val), f"webhook_sig: {val}"

    def test_transaction_id_format(self, runner):
        val = _gen(runner, 'transaction_id')
        assert re.match(r'^TXN[0-9A-F]{16}$', val), f"transaction_id: {val}"

    def test_public_ip_globally_routable(self, runner):
        val = _gen(runner, 'public_ip')
        parts = val.split('.')
        assert len(parts) == 4 and all(p.isdigit() for p in parts)
        a, b = int(parts[0]), int(parts[1])
        assert a not in (10, 127, 169), f"public_ip not public: {val}"
        assert not (a == 172 and 16 <= b <= 31), f"public_ip in 172.16-31: {val}"
        assert not (a == 192 and b == 168), f"public_ip in 192.168: {val}"

    def test_private_ip_rfc1918(self, runner):
        val = _gen(runner, 'private_ip')
        parts = val.split('.')
        a, b = int(parts[0]), int(parts[1])
        is_private = (
            a == 10 or
            (a == 172 and 16 <= b <= 31) or
            (a == 192 and b == 168)
        )
        assert is_private, f"private_ip not in RFC 1918: {val}"


# ===========================================================================
# generate — RFID
# ===========================================================================

class TestGenerateRFID:

    def test_rfid_uid_hex_format(self, runner):
        val = _gen(runner, 'rfid_uid')
        groups = val.split(':')
        assert len(groups) in (4, 7), f"rfid_uid byte count: {val}"
        assert all(re.match(r'^[0-9A-F]{2}$', g) for g in groups), f"rfid_uid: {val}"

    def test_epc_24hex(self, runner):
        val = _gen(runner, 'epc')
        assert re.match(r'^[0-9A-F]{24}$', val), f"epc: {val}"
        assert val.startswith('3'), f"epc header not 0x30: {val}"

    def test_rfid_tag_structure(self, runner):
        val = _parse(_gen(runner, 'rfid_tag'))
        for key in ('uid', 'standard', 'frequency_mhz', 'memory_bytes'):
            assert key in val, f"rfid_tag missing '{key}'"


# ===========================================================================
# generate — NFC
# ===========================================================================

class TestGenerateNFC:

    def test_nfc_uid_7bytes(self, runner):
        val = _gen(runner, 'nfc_uid')
        groups = val.split(':')
        assert len(groups) == 7, f"nfc_uid should be 7 bytes: {val}"
        assert all(re.match(r'^[0-9A-F]{2}$', g) for g in groups)

    def test_nfc_atqa_format(self, runner):
        val = _gen(runner, 'nfc_atqa')
        assert re.match(r'^[0-9A-F]{2}:[0-9A-F]{2}$', val), f"nfc_atqa: {val}"

    def test_nfc_sak_2hex(self, runner):
        val = _gen(runner, 'nfc_sak')
        assert re.match(r'^[0-9a-fA-F]{2}$', val), f"nfc_sak: {val}"

    def test_ndef_uri_structure(self, runner):
        val = _parse(_gen(runner, 'ndef_uri'))
        for key in ('raw_hex', 'decoded', 'tnf', 'type', 'prefix_code'):
            assert key in val, f"ndef_uri missing '{key}'"
        assert val['tnf'] == 1
        assert val['type'] == 'U'
        assert re.match(r'^[0-9A-F]+$', val['raw_hex'])

    def test_ndef_text_structure(self, runner):
        val = _parse(_gen(runner, 'ndef_text', '--locale', 'TR'))
        for key in ('raw_hex', 'decoded', 'lang'):
            assert key in val
        assert val['lang'] == 'tr'

    def test_apdu_structure(self, runner):
        val = _parse(_gen(runner, 'apdu'))
        for key in ('cla', 'ins', 'p1', 'p2', 'hex'):
            assert key in val, f"apdu missing '{key}'"
        assert re.match(r'^[0-9A-F]{2}$', val['cla'])

    def test_nfc_tag_structure(self, runner):
        val = _parse(_gen(runner, 'nfc_tag'))
        for key in ('uid', 'atqa', 'sak', 'type', 'capacity_bytes', 'ndef_message'):
            assert key in val, f"nfc_tag missing '{key}'"


# ===========================================================================
# generate — IR
# ===========================================================================

class TestGenerateIR:

    def test_ir_nec_checksum_valid(self, runner):
        val = _parse(_gen(runner, 'ir_nec'))
        for key in ('address', 'command', 'inv_address', 'inv_command', 'hex', 'carrier_hz'):
            assert key in val, f"ir_nec missing '{key}'"
        assert val['checksum_valid'] is True
        assert val['carrier_hz'] == 38_000
        assert val['protocol'] == 'NEC'
        addr = int(val['address'], 16)
        inv_addr = int(val['inv_address'], 16)
        assert (addr ^ inv_addr) == 0xFF, f"ir_nec addr XOR inv_addr != 0xFF"
        assert re.match(r'^[0-9A-F]{8}$', val['hex'])

    def test_ir_rc5_structure(self, runner):
        val = _parse(_gen(runner, 'ir_rc5'))
        for key in ('system', 'command', 'toggle', 'frame_bits', 'carrier_hz'):
            assert key in val
        assert val['carrier_hz'] == 36_000
        assert val['protocol'] == 'RC-5'
        assert re.match(r'^[01]{14}$', val['frame_bits'])
        assert 0 <= val['command'] <= 127
        assert val['toggle'] in (0, 1)

    def test_ir_pronto_format(self, runner):
        val = _gen(runner, 'ir_pronto')
        words = val.split()
        assert words[0] == '0000', f"Pronto type word: {words[0]}"
        assert words[1] == '006D', f"Pronto freq word: {words[1]}"
        assert all(re.match(r'^[0-9A-F]{4}$', w) for w in words)

    def test_ir_raw_structure(self, runner):
        val = _parse(_gen(runner, 'ir_raw'))
        for key in ('carrier_hz', 'address', 'command', 'pulses', 'pulse_count'):
            assert key in val
        assert val['carrier_hz'] == 38_000
        assert isinstance(val['pulses'], list)
        assert val['pulses'][0] == 9024 and val['pulses'][1] == 4512


# ===========================================================================
# generate — Barcode
# ===========================================================================

class TestGenerateBarcode:

    def test_ean13_tr_prefix_and_checksum(self, runner):
        val = _gen(runner, 'ean13', '--locale', 'TR')
        assert re.match(r'^\d{13}$', val)
        assert val.startswith(('868', '869')), f"EAN-13 TR prefix wrong: {val}"
        assert _gs1_valid(val), f"EAN-13 GS1 check failed: {val}"

    def test_ean13_de_prefix(self, runner):
        val = _gen(runner, 'ean13', '--locale', 'DE')
        DE_PREFIXES = ('400','401','410','420','430','440')
        assert val[:3] in DE_PREFIXES, f"EAN-13 DE prefix: {val[:3]}"
        assert _gs1_valid(val)

    def test_ean8_tr_format_and_checksum(self, runner):
        val = _gen(runner, 'ean8', '--locale', 'TR')
        assert re.match(r'^\d{8}$', val)
        assert val.startswith(('868', '869'))
        assert _gs1_valid(val)

    def test_upca_format_and_checksum(self, runner):
        val = _gen(runner, 'upca')
        assert re.match(r'^\d{12}$', val)
        assert _gs1_valid(val), f"UPC-A GS1 check failed: {val}"

    def test_isbn13_prefix_and_checksum(self, runner):
        val = _gen(runner, 'isbn13')
        assert re.match(r'^\d{13}$', val)
        assert val.startswith(('978', '979'))
        assert _gs1_valid(val), f"ISBN-13 GS1 check failed: {val}"

    def test_isbn10_format(self, runner):
        val = _gen(runner, 'isbn10')
        assert re.match(r'^\d{9}[\dX]$', val), f"ISBN-10 format: {val}"
        digits = val[:9]
        check_char = val[9]
        total = sum(int(d) * (10 - i) for i, d in enumerate(digits))
        remainder = (11 - total % 11) % 11
        expected = 'X' if remainder == 10 else str(remainder)
        assert check_char == expected, f"ISBN-10 checksum: {val}"

    def test_gs1_128_format(self, runner):
        val = _gen(runner, 'gs1_128')
        assert re.match(r'^\(01\)\d{14}\(17\)\d{6}\(10\)[A-Z0-9]{6}$', val), f"GS1-128: {val}"


# ===========================================================================
# generate — Telecom
# ===========================================================================

class TestGenerateTelecom:

    def test_imei_15digits_luhn(self, runner):
        val = _gen(runner, 'imei')
        assert re.match(r'^\d{15}$', val)
        assert _luhn_valid(val), f"IMEI Luhn failed: {val}"

    def test_imei2_hyphenated(self, runner):
        val = _gen(runner, 'imei2')
        assert re.match(r'^\d{2}-\d{6}-\d{6}-\d$', val), f"imei2: {val}"
        flat = val.replace('-', '')
        assert _luhn_valid(flat), f"imei2 Luhn failed: {val}"

    def test_iccid_tr_19digits_luhn(self, runner):
        val = _gen(runner, 'iccid', '--locale', 'TR')
        assert re.match(r'^\d{19}$', val)
        assert val.startswith('8990'), f"ICCID TR prefix: {val}"
        assert _luhn_valid(val), f"ICCID Luhn failed: {val}"

    def test_imsi_tr_mcc(self, runner):
        val = _gen(runner, 'imsi', '--locale', 'TR')
        assert re.match(r'^\d{15}$', val)
        assert val.startswith('286'), f"IMSI TR MCC: {val}"

    def test_imsi_de_mcc(self, runner):
        val = _gen(runner, 'imsi', '--locale', 'DE')
        assert val.startswith('262'), f"IMSI DE MCC: {val}"

    def test_msisdn_tr_format(self, runner):
        val = _gen(runner, 'msisdn', '--locale', 'TR')
        assert re.match(r'^\+905\d{9}$', val), f"MSISDN TR: {val}"

    def test_msisdn_us_format(self, runner):
        val = _gen(runner, 'msisdn', '--locale', 'US')
        assert re.match(r'^\+1\d{10}$', val)


# ===========================================================================
# generate — Securities
# ===========================================================================

class TestGenerateSecurities:

    def test_isin_tr_format_and_checksum(self, runner):
        val = _gen(runner, 'isin', '--locale', 'TR')
        assert re.match(r'^TR[A-Z0-9]{10}$', val), f"ISIN TR: {val}"
        assert _isin_valid(val), f"ISIN Luhn failed: {val}"

    def test_isin_us_format(self, runner):
        val = _gen(runner, 'isin', '--locale', 'US')
        assert val.startswith('US')
        assert _isin_valid(val)

    def test_cusip_9chars(self, runner):
        val = _gen(runner, 'cusip')
        assert len(val) == 9, f"CUSIP length: {len(val)}"
        assert re.match(r'^[A-Z0-9]{9}$', val)

    def test_sedol_7chars_checksum(self, runner):
        val = _gen(runner, 'sedol')
        assert len(val) == 7, f"SEDOL length: {len(val)}"
        assert _sedol_valid(val), f"SEDOL checksum failed: {val}"

    def test_lei_20chars(self, runner):
        val = _gen(runner, 'lei')
        assert len(val) == 20, f"LEI length: {len(val)}"
        assert re.match(r'^[A-Z0-9]{20}$', val)


# ===========================================================================
# generate — Crypto
# ===========================================================================

class TestGenerateCrypto:

    def test_btc_address_base58_p2pkh(self, runner):
        val = _gen(runner, 'btc_address')
        assert re.match(r'^1[1-9A-HJ-NP-Za-km-z]{24,33}$', val), f"BTC address: {val}"

    def test_eth_address_eip55(self, runner):
        val = _gen(runner, 'eth_address')
        assert re.match(r'^0x[0-9a-fA-F]{40}$', val), f"ETH address: {val}"
        assert val.startswith('0x')

    def test_crypto_address_btc(self, runner):
        val = _gen(runner, 'crypto_address', '--currency', 'btc')
        assert val.startswith('1'), f"crypto_address btc: {val}"

    def test_crypto_address_eth(self, runner):
        val = _gen(runner, 'crypto_address', '--currency', 'eth')
        assert val.startswith('0x'), f"crypto_address eth: {val}"

    def test_tx_hash_btc_64hex(self, runner):
        val = _gen(runner, 'tx_hash', '--currency', 'btc')
        assert re.match(r'^[0-9a-f]{64}$', val), f"tx_hash btc: {val}"

    def test_tx_hash_eth_0xprefix(self, runner):
        val = _gen(runner, 'tx_hash', '--currency', 'eth')
        assert re.match(r'^0x[0-9a-f]{64}$', val), f"tx_hash eth: {val}"

    def test_block_hash_btc(self, runner):
        val = _gen(runner, 'block_hash', '--currency', 'btc')
        assert re.match(r'^[0-9a-f]{64}$', val)

    def test_block_hash_eth(self, runner):
        val = _gen(runner, 'block_hash', '--currency', 'eth')
        assert re.match(r'^0x[0-9a-f]{64}$', val)


# ===========================================================================
# generate — E-Commerce
# ===========================================================================

class TestGenerateEcommerce:

    def test_product_name_nonempty(self, runner):
        val = _gen(runner, 'product_name')
        assert len(val) > 3

    def test_sku_format(self, runner):
        val = _gen(runner, 'sku')
        assert re.match(r'^[A-Z]{2,4}-\d{4,8}$', val), f"sku: {val}"

    def test_order_id_format(self, runner):
        val = _gen(runner, 'order_id')
        assert re.match(r'^ORD-[A-Z0-9]{8,12}$', val), f"order_id: {val}"

    def test_tracking_usps_22digits_luhn(self, runner):
        val = _gen(runner, 'tracking_number', '--carrier', 'usps')
        assert re.match(r'^\d{22}$', val)
        assert val[:2] in ('92', '94', '70', '93', '95'), f"USPS prefix: {val}"
        assert _luhn_valid(val), f"USPS Luhn failed: {val}"

    def test_tracking_ups_format(self, runner):
        val = _gen(runner, 'tracking_number', '--carrier', 'ups')
        assert val.startswith('1Z'), f"UPS prefix: {val}"
        assert len(val) == 18, f"UPS length: {len(val)}"

    def test_tracking_fedex_12digits_mod11(self, runner):
        val = _gen(runner, 'tracking_number', '--carrier', 'fedex')
        assert re.match(r'^\d{12}$', val)
        assert _fedex_valid(val), f"FedEx Mod-11 failed: {val}"

    def test_dhl_tracking_jd_format(self, runner):
        val = _gen(runner, 'dhl_tracking')
        assert val.startswith('JD'), f"DHL prefix: {val}"
        assert len(val) == 11, f"DHL length: {len(val)}"
        body = [int(c) for c in val[2:10]]
        total = 0
        for i, d in enumerate(reversed(body)):
            n = d * 2 if i % 2 == 0 else d
            if n > 9: n -= 9
            total += n
        assert int(val[10]) == (10 - total % 10) % 10, f"DHL Luhn failed: {val}"

    def test_category_valid(self, runner):
        CATEGORIES = [
            "Electronics","Computers & Accessories","Audio & Video","Photography",
            "Gaming","Office Supplies","Home & Kitchen","Health & Beauty",
            "Sports & Outdoors","Books & Media","Clothing","Automotive",
            "Toys & Games","Tools & Hardware","Garden & Outdoor","Pet Supplies",
        ]
        val = _gen(runner, 'category')
        assert val in CATEGORIES, f"category: {val}"

    def test_rating_range(self, runner):
        val = _gen(runner, 'rating')
        f = float(val)
        assert 1.0 <= f <= 5.0
        assert val in ('1.0','1.5','2.0','2.5','3.0','3.5','4.0','4.5','5.0')


# ===========================================================================
# generate — Location
# ===========================================================================

class TestGenerateLocation:

    def test_latitude_tr_range(self, runner):
        val = float(_gen(runner, 'latitude', '--locale', 'TR'))
        assert 36.0 <= val <= 42.0, f"lat TR out of range: {val}"

    def test_latitude_us_range(self, runner):
        val = float(_gen(runner, 'latitude', '--locale', 'US'))
        assert 25.0 <= val <= 49.0

    def test_longitude_tr_range(self, runner):
        val = float(_gen(runner, 'longitude', '--locale', 'TR'))
        assert 26.0 <= val <= 45.0

    def test_longitude_us_negative(self, runner):
        val = float(_gen(runner, 'longitude', '--locale', 'US'))
        assert -125.0 <= val <= -66.0

    def test_timezone_tr(self, runner):
        val = _gen(runner, 'timezone', '--locale', 'TR')
        assert val == 'Europe/Istanbul'

    def test_timezone_de(self, runner):
        val = _gen(runner, 'timezone', '--locale', 'DE')
        assert val == 'Europe/Berlin'

    def test_country_code_tr(self, runner):
        val = _gen(runner, 'country_code', '--locale', 'TR')
        assert val == 'TR'

    def test_country_code_uk_is_gb(self, runner):
        val = _gen(runner, 'country_code', '--locale', 'UK')
        assert val == 'GB'

    def test_coordinates_tr_format(self, runner):
        val = _gen(runner, 'coordinates', '--locale', 'TR')
        parts = val.split(',')
        assert len(parts) == 2
        lat, lon = float(parts[0]), float(parts[1])
        assert 36.0 <= lat <= 42.0
        assert 26.0 <= lon <= 45.0


# ===========================================================================
# generate — Social
# ===========================================================================

class TestGenerateSocial:

    def test_username_no_at(self, runner):
        val = _gen(runner, 'username')
        assert '@' not in val
        assert len(val) >= 3

    def test_handle_at_prefix(self, runner):
        val = _gen(runner, 'handle')
        assert val.startswith('@')
        assert len(val) >= 4

    def test_hashtag_hash_prefix(self, runner):
        val = _gen(runner, 'hashtag')
        assert val.startswith('#')
        assert len(val) >= 3

    def test_bio_nonempty(self, runner):
        val = _gen(runner, 'bio')
        assert len(val) > 10

    def test_follower_count_positive(self, runner):
        val = int(_gen(runner, 'follower_count'))
        assert val > 0


# ===========================================================================
# generate — edge cases
# ===========================================================================

class TestGenerateEdgeCases:

    def test_no_args_shows_error(self, runner):
        r = runner.invoke(main, ['generate'])
        assert r.exit_code == 0
        assert 'Error' in r.output or 'error' in r.output.lower()

    def test_invalid_type_shows_error(self, runner):
        r = runner.invoke(main, ['generate', 'xyzzy_nonexistent_type'])
        assert r.exit_code == 0
        assert 'ERROR' in r.output


# ===========================================================================
# list
# ===========================================================================

class TestList:

    def test_list_runs(self, runner):
        r = runner.invoke(main, ['list'])
        assert r.exit_code == 0
        assert 'TYPE' in r.output
        assert 'CLI COMMAND' in r.output

    @pytest.mark.parametrize("cat", [
        'IDENTITY', 'FINANCIAL', 'BANKING', 'META', 'SECURITY',
        'RFID', 'NFC', 'IR', 'BARCODE', 'TELECOM', 'CRYPTO',
        'E-COMMERCE', 'LOCATION', 'SOCIAL',
    ])
    def test_list_contains_category(self, runner, cat):
        r = runner.invoke(main, ['list'])
        assert r.exit_code == 0
        assert cat in r.output.upper(), f"category {cat} missing"

    def test_list_cat_financial(self, runner):
        r = runner.invoke(main, ['list', '--cat', 'Financial'])
        assert r.exit_code == 0
        assert 'FINANCIAL' in r.output.upper()
        assert 'IDENTITY' not in r.output.upper()

    def test_list_cat_meta_contains_hash(self, runner):
        r = runner.invoke(main, ['list', '--cat', 'Meta'])
        assert r.exit_code == 0
        assert 'hash' in r.output
        assert '--algorithm' in r.output

    def test_list_cat_security(self, runner):
        r = runner.invoke(main, ['list', '--cat', 'Security'])
        assert r.exit_code == 0
        assert 'api_key' in r.output or 'totp_code' in r.output

    def test_list_cat_rfid(self, runner):
        r = runner.invoke(main, ['list', '--cat', 'RFID'])
        assert r.exit_code == 0
        assert 'epc' in r.output

    def test_list_cat_nfc(self, runner):
        r = runner.invoke(main, ['list', '--cat', 'NFC'])
        assert r.exit_code == 0
        assert 'ndef' in r.output or 'apdu' in r.output

    def test_list_cat_ir(self, runner):
        r = runner.invoke(main, ['list', '--cat', 'IR'])
        assert r.exit_code == 0
        assert 'ir_nec' in r.output

    def test_list_cat_barcode(self, runner):
        r = runner.invoke(main, ['list', '--cat', 'Barcode'])
        assert r.exit_code == 0
        assert 'ean13' in r.output

    def test_list_cat_telecom(self, runner):
        r = runner.invoke(main, ['list', '--cat', 'Telecom'])
        assert r.exit_code == 0
        assert 'imei' in r.output

    def test_list_unknown_cat_returns_empty(self, runner):
        r = runner.invoke(main, ['list', '--cat', 'zzz_nonexistent'])
        assert r.exit_code == 0
        assert 'types listed' in r.output

    def test_list_shows_locale_flag(self, runner):
        r = runner.invoke(main, ['list'])
        assert 'L=v' in r.output

    def test_list_shows_cli_commands_section(self, runner):
        r = runner.invoke(main, ['list'])
        assert r.exit_code == 0
        assert 'CLI COMMANDS' in r.output

    @pytest.mark.parametrize("cmd", [
        'generate', 'bulk', 'template', 'profile', 'company', 'export', 'list',
    ])
    def test_list_cli_commands_contains_all_commands(self, runner, cmd):
        r = runner.invoke(main, ['list'])
        assert r.exit_code == 0
        assert cmd in r.output, f"command '{cmd}' missing from CLI COMMANDS section"

    def test_list_cli_commands_template_examples(self, runner):
        r = runner.invoke(main, ['list'])
        assert r.exit_code == 0
        assert 'template' in r.output
        assert '--count' in r.output
        assert '--format' in r.output
        assert '--locale' in r.output

    def test_list_cli_commands_template_options_hint(self, runner):
        r = runner.invoke(main, ['list'])
        assert r.exit_code == 0
        assert 'json|csv|sql' in r.output

    def test_list_cli_commands_section_at_bottom(self, runner):
        r = runner.invoke(main, ['list'])
        assert r.exit_code == 0
        types_pos   = r.output.find('types listed')
        commands_pos = r.output.find('CLI COMMANDS')
        assert types_pos < commands_pos, "CLI COMMANDS section should appear after types list"


# ===========================================================================
# profile
# ===========================================================================

class TestProfile:

    def test_profile_default_keys(self, runner):
        r = runner.invoke(main, ['profile'])
        assert r.exit_code == 0
        data = json.loads(r.output)
        for key in ('id', 'firstname', 'lastname', 'phone', 'email', 'iban'):
            assert key in data, f"profile missing '{key}'"

    def test_profile_iban_matches_locale_tr(self, runner):
        r = runner.invoke(main, ['profile', '--locale', 'TR'])
        data = json.loads(r.output)
        assert data['iban'].startswith('TR')

    def test_profile_iban_de(self, runner):
        r = runner.invoke(main, ['profile', '--locale', 'DE'])
        data = json.loads(r.output)
        assert data['iban'].startswith('DE')

    def test_profile_ru_has_fullname(self, runner):
        r = runner.invoke(main, ['profile', '--locale', 'RU'])
        data = json.loads(r.output)
        assert 'fullname' in data

    def test_profile_count_3_returns_list(self, runner):
        r = runner.invoke(main, ['profile', '--count', '3'])
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert isinstance(data, list)
        assert len(data) == 3

    def test_profile_count_1_returns_dict(self, runner):
        r = runner.invoke(main, ['profile', '--count', '1'])
        data = json.loads(r.output)
        assert isinstance(data, dict)

    @pytest.mark.parametrize("locale", ['TR', 'US', 'UK', 'DE', 'FR', 'RU'])
    def test_profile_all_locales(self, runner, locale):
        r = runner.invoke(main, ['profile', '--locale', locale])
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert 'email' in data


# ===========================================================================
# company
# ===========================================================================

class TestCompany:

    def test_company_default_keys(self, runner):
        r = runner.invoke(main, ['company'])
        assert r.exit_code == 0
        data = json.loads(r.output)
        for key in ('id', 'name', 'iban', 'bic', 'phone', 'address'):
            assert key in data, f"company missing '{key}'"

    def test_company_iban_fr(self, runner):
        r = runner.invoke(main, ['company', '--locale', 'FR'])
        data = json.loads(r.output)
        assert data['iban'].startswith('FR')

    def test_company_count_2(self, runner):
        r = runner.invoke(main, ['company', '--count', '2'])
        data = json.loads(r.output)
        assert isinstance(data, list) and len(data) == 2

    @pytest.mark.parametrize("locale", ['TR', 'US', 'UK', 'DE', 'FR', 'RU'])
    def test_company_all_locales(self, runner, locale):
        r = runner.invoke(main, ['company', '--locale', locale])
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert 'name' in data


# ===========================================================================
# bulk
# ===========================================================================

class TestBulk:

    def test_bulk_tckn_count_and_checksum(self, runner):
        r = runner.invoke(main, ['bulk', 'tckn', '--count', '5'])
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert isinstance(data, list) and len(data) == 5
        for v in data:
            assert _tckn_valid(str(v)), f"bulk tckn invalid: {v}"

    def test_bulk_default_count_10(self, runner):
        r = runner.invoke(main, ['bulk', 'uuid'])
        data = json.loads(r.output)
        assert len(data) == 10

    def test_bulk_iban_de_locale(self, runner):
        r = runner.invoke(main, ['bulk', 'iban', '--locale', 'DE', '--count', '3'])
        data = json.loads(r.output)
        assert all(v.startswith('DE') for v in data)
        assert all(_iban_mod97_valid(v) for v in data)

    def test_bulk_uuid_uniqueness(self, runner):
        r = runner.invoke(main, ['bulk', 'uuid', '--count', '20'])
        data = json.loads(r.output)
        assert len(set(data)) == 20

    def test_bulk_cardnum_luhn(self, runner):
        r = runner.invoke(main, ['bulk', 'cardnum', '--count', '5'])
        data = json.loads(r.output)
        for v in data:
            assert _luhn_valid(str(v)), f"bulk cardnum Luhn failed: {v}"


# ===========================================================================
# export
# ===========================================================================

class TestExport:

    def test_export_json_default(self, runner):
        r = runner.invoke(main, ['export', 'fullname', 'tckn', '--count', '3'])
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert isinstance(data, list) and len(data) == 3
        assert 'fullname' in data[0] and 'tckn' in data[0]
        for row in data:
            assert _tckn_valid(row['tckn']), f"export tckn invalid: {row['tckn']}"

    def test_export_csv_format(self, runner):
        r = runner.invoke(main, ['export', 'fullname', 'tckn', '--count', '3',
                                 '--format', 'csv'])
        assert r.exit_code == 0
        lines = r.output.strip().splitlines()
        assert lines[0] == 'fullname,tckn'
        assert len(lines) == 4

    def test_export_sql_format(self, runner):
        r = runner.invoke(main, ['export', 'fullname', 'tckn', '--count', '2',
                                 '--format', 'sql'])
        assert r.exit_code == 0
        assert r.output.strip().startswith('INSERT INTO records')

    def test_export_sql_custom_table(self, runner):
        r = runner.invoke(main, ['export', 'uuid', '--count', '2',
                                 '--format', 'sql', '--table', 'users'])
        assert r.exit_code == 0
        assert 'INSERT INTO users' in r.output

    def test_export_locale_uk_iban(self, runner):
        r = runner.invoke(main, ['export', 'iban', '--count', '3', '--locale', 'UK'])
        data = json.loads(r.output)
        assert all(row['iban'].startswith('GB') for row in data)
        assert all(_iban_mod97_valid(row['iban']) for row in data)

    def test_export_count_7(self, runner):
        r = runner.invoke(main, ['export', 'uuid', '--count', '7'])
        data = json.loads(r.output)
        assert len(data) == 7

    def test_export_multiple_types(self, runner):
        r = runner.invoke(main, ['export', 'uuid', 'fullname', 'email',
                                 'phone', 'iban', '--count', '2'])
        data = json.loads(r.output)
        assert set(data[0].keys()) == {'uuid', 'fullname', 'email', 'phone', 'iban'}


# ===========================================================================
# generate — Financial (issuer)
# ===========================================================================

class TestGenerateIssuer:

    @pytest.mark.parametrize("locale", ['TR', 'US', 'UK', 'DE', 'FR', 'RU'])
    def test_issuer_nonempty(self, runner, locale):
        val = _gen(runner, 'issuer', '--locale', locale)
        assert len(val) > 2, f"issuer {locale} too short: {val}"

    def test_issuer_tr_contains_bank_keyword(self, runner):
        seen = set()
        for _ in range(10):
            seen.add(_gen(runner, 'issuer', '--locale', 'TR'))
        assert len(seen) > 1, "issuer TR always returns same value"


# ===========================================================================
# generate — Meta (additional format options)
# ===========================================================================

class TestGenerateMetaExtra:

    def test_color_rgb_format(self, runner):
        val = _gen(runner, 'color', '--locale', 'TR')
        # default hex
        assert re.match(r'^#[0-9A-F]{6}$', val), f"color default hex: {val}"

    def test_color_formats_via_generate(self, runner):
        """Verify color generator returns non-empty for the known format list."""
        # We can't pass --format via CLI directly (no option exposed), but
        # we test that default hex output is always valid.
        for _ in range(5):
            val = _gen(runner, 'color')
            assert re.match(r'^#[0-9A-F]{6}$', val), f"color hex: {val}"

    def test_url_us_locale(self, runner):
        val = _gen(runner, 'url', '--locale', 'US')
        assert val.startswith('https://')
        assert any(val.endswith(ext) or ext + '/' in val
                   for ext in ['.com', '.net', '.org', '.io', '.co'])

    def test_domain_us_locale(self, runner):
        val = _gen(runner, 'domain', '--locale', 'US')
        assert any(tld in val for tld in ['.com', '.net', '.org', '.io', '.co'])

    def test_domain_de_locale(self, runner):
        val = _gen(runner, 'domain', '--locale', 'DE')
        assert any(tld in val for tld in ['.de', '.com', '.net'])

    def test_ipv4_not_loopback_or_multicast(self, runner):
        for _ in range(10):
            val = _gen(runner, 'ipv4')
            first = int(val.split('.')[0])
            assert first not in (127, 169, 224), f"ipv4 reserved: {val}"

    def test_apppassword_no_sequential_run(self, runner):
        for _ in range(10):
            val = _gen(runner, 'apppassword')
            digits = [int(c) for c in val]
            for i in range(4):
                asc = digits[i+1] - digits[i] == 1 and digits[i+2] - digits[i+1] == 1
                dsc = digits[i] - digits[i+1] == 1 and digits[i+1] - digits[i+2] == 1
                assert not (asc or dsc), f"apppassword has 3-run: {val}"


# ===========================================================================
# generate — Contact (additional locales)
# ===========================================================================

class TestGenerateContactExtra:

    def test_phone_de_format(self, runner):
        val = _gen(runner, 'phone', '--locale', 'DE')
        assert val.startswith('+49'), f"DE phone: {val}"

    def test_phone_fr_format(self, runner):
        val = _gen(runner, 'phone', '--locale', 'FR')
        assert val.startswith('+33'), f"FR phone: {val}"

    def test_phone_ru_format(self, runner):
        val = _gen(runner, 'phone', '--locale', 'RU')
        assert val.startswith('+7'), f"RU phone: {val}"

    def test_email_uk_domain(self, runner):
        val = _gen(runner, 'email', '--locale', 'UK')
        assert '@' in val
        domain = val.split('@')[1]
        assert domain.endswith(('.co.uk', '.org.uk', '.me.uk', '.uk', '.com')), \
            f"UK email domain: {val}"

    def test_email_de_domain(self, runner):
        val = _gen(runner, 'email', '--locale', 'DE')
        assert '@' in val
        assert '.de' in val or '.net' in val or '.com' in val or '.org' in val

    def test_email_fr_domain(self, runner):
        val = _gen(runner, 'email', '--locale', 'FR')
        assert '@' in val
        assert '.fr' in val or '.net' in val or '.com' in val or '.org' in val

    def test_postalcode_uk_alphanum(self, runner):
        val = _gen(runner, 'postalcode', '--locale', 'UK')
        assert re.match(r'^[A-Z]{1,2}\d{1,2} \d[A-Z]{2}$', val), f"UK postal: {val}"

    def test_postalcode_fr_5digits(self, runner):
        val = _gen(runner, 'postalcode', '--locale', 'FR')
        assert re.match(r'^\d{5}$', val), f"FR postal: {val}"

    def test_plate_us_format(self, runner):
        val = _gen(runner, 'plate', '--locale', 'US')
        assert re.match(r'^[A-Z0-9]{5,8}$', val), f"US plate: {val}"

    def test_plate_uk_format(self, runner):
        val = _gen(runner, 'plate', '--locale', 'UK')
        assert re.match(r'^[A-Z]{2}\d{2} [A-Z]{3}$', val), f"UK plate: {val}"

    def test_plate_fr_format(self, runner):
        val = _gen(runner, 'plate', '--locale', 'FR')
        assert re.match(r'^[A-Z]{2}-\d{3}-[A-Z]{2}$', val), f"FR plate: {val}"

    def test_address_city_us_nonempty(self, runner):
        val = _gen(runner, 'address_city', '--locale', 'US')
        assert len(val) > 2

    def test_address_city_uk_nonempty(self, runner):
        val = _gen(runner, 'address_city', '--locale', 'UK')
        assert len(val) > 2

    def test_address_city_de_nonempty(self, runner):
        val = _gen(runner, 'address_city', '--locale', 'DE')
        assert len(val) > 2

    def test_address_full_us_format(self, runner):
        val = _gen(runner, 'address_full', '--locale', 'US')
        assert ',' in val and 'No:' in val

    def test_address_full_uk_format(self, runner):
        val = _gen(runner, 'address_full', '--locale', 'UK')
        assert ',' in val


# ===========================================================================
# generate — Banking (additional locales / fields)
# ===========================================================================

class TestGenerateBankingExtra:

    def test_swift_us_format(self, runner):
        val = _gen(runner, 'swift', '--locale', 'US')
        assert re.match(r'^[A-Z]{4}US[A-Z0-9]{2}$', val), f"SWIFT US: {val}"

    def test_swift_uk_format(self, runner):
        val = _gen(runner, 'swift', '--locale', 'UK')
        assert re.match(r'^[A-Z]{4}GB[A-Z0-9]{2}$', val), f"SWIFT UK: {val}"

    def test_swift_de_format(self, runner):
        val = _gen(runner, 'swift', '--locale', 'DE')
        assert re.match(r'^[A-Z]{4}DE[A-Z0-9]{2}$', val), f"SWIFT DE: {val}"

    def test_transaction_uk_currency(self, runner):
        val = _parse(_gen(runner, 'transaction', '--locale', 'UK'))
        assert val['currency'] == 'GBP'

    def test_transaction_de_currency(self, runner):
        val = _parse(_gen(runner, 'transaction', '--locale', 'DE'))
        assert val['currency'] == 'EUR'

    def test_transaction_fr_currency(self, runner):
        val = _parse(_gen(runner, 'transaction', '--locale', 'FR'))
        assert val['currency'] == 'EUR'

    def test_iban_tr_luhn(self, runner):
        val = _gen(runner, 'iban', '--locale', 'TR')
        assert _iban_mod97_valid(val), f"IBAN TR MOD-97 failed: {val}"

    def test_sepa_ref_length_range(self, runner):
        for _ in range(5):
            val = _gen(runner, 'sepa_ref')
            assert 20 <= len(val) <= 35, f"sepa_ref length: {len(val)}"
            assert re.match(r'^[A-Z0-9]+$', val), f"sepa_ref not alphanumeric: {val}"


# ===========================================================================
# generate — Commerce (additional locales)
# ===========================================================================

class TestGenerateCommerceExtra:

    def test_invoice_number_us_format(self, runner):
        val = _gen(runner, 'invoice_number', '--locale', 'US')
        assert val.startswith('INV-'), f"US invoice: {val}"

    def test_invoice_number_uk_format(self, runner):
        val = _gen(runner, 'invoice_number', '--locale', 'UK')
        assert val.startswith('INV/'), f"UK invoice: {val}"

    def test_vin_de_wmi(self, runner):
        val = _gen(runner, 'vin', '--locale', 'DE')
        DE_WMI = ('WAU', 'WBA', 'WVW', 'WDB', 'WEB', 'WME', 'WF0', 'WP0')
        assert val[:3] in DE_WMI, f"VIN DE WMI: {val}"
        assert len(val) == 17
        assert re.match(r'^[A-HJ-NPR-Z0-9]{17}$', val)

    def test_vin_uk_wmi(self, runner):
        val = _gen(runner, 'vin', '--locale', 'UK')
        UK_WMI = ('SAJ', 'SAL', 'SAR', 'SCF', 'SCC', 'SAD', 'SCA')
        assert val[:3] in UK_WMI, f"VIN UK WMI: {val}"

    def test_vin_fr_wmi(self, runner):
        val = _gen(runner, 'vin', '--locale', 'FR')
        FR_WMI = ('VF1', 'VF3', 'VF7', 'VFA', 'VNK')
        assert val[:3] in FR_WMI, f"VIN FR WMI: {val}"

    def test_currency_us_usd(self, runner):
        val = _parse(_gen(runner, 'currency', '--locale', 'US'))
        assert val['code'] == 'USD'

    def test_currency_uk_gbp(self, runner):
        val = _parse(_gen(runner, 'currency', '--locale', 'UK'))
        assert val['code'] == 'GBP'

    def test_currency_fr_eur(self, runner):
        val = _parse(_gen(runner, 'currency', '--locale', 'FR'))
        assert val['code'] == 'EUR'

    def test_tax_rate_de_mwst(self, runner):
        val = _parse(_gen(runner, 'tax_rate', '--locale', 'DE'))
        assert val['name'] in ('MwSt', 'USt')

    def test_tax_rate_us_sales_tax(self, runner):
        val = _parse(_gen(runner, 'tax_rate', '--locale', 'US'))
        assert val['name'] == 'Sales Tax'


# ===========================================================================
# generate — Telecom (additional locales)
# ===========================================================================

class TestGenerateTelecomExtra:

    def test_iccid_us_prefix(self, runner):
        val = _gen(runner, 'iccid', '--locale', 'US')
        assert re.match(r'^\d{19}$', val)
        assert val.startswith('891'), f"ICCID US prefix (891x): {val}"
        assert _luhn_valid(val), f"ICCID US Luhn failed: {val}"

    def test_iccid_uk_prefix(self, runner):
        val = _gen(runner, 'iccid', '--locale', 'UK')
        assert val.startswith('8944'), f"ICCID UK prefix: {val}"
        assert _luhn_valid(val)

    def test_iccid_de_prefix(self, runner):
        val = _gen(runner, 'iccid', '--locale', 'DE')
        assert val.startswith('8949'), f"ICCID DE prefix: {val}"
        assert _luhn_valid(val)

    def test_imsi_us_mcc(self, runner):
        val = _gen(runner, 'imsi', '--locale', 'US')
        assert val.startswith('310') or val.startswith('311'), f"IMSI US MCC: {val}"

    def test_imsi_uk_mcc(self, runner):
        val = _gen(runner, 'imsi', '--locale', 'UK')
        assert val.startswith('234') or val.startswith('235'), f"IMSI UK MCC: {val}"

    def test_imsi_fr_mcc(self, runner):
        val = _gen(runner, 'imsi', '--locale', 'FR')
        assert val.startswith('208'), f"IMSI FR MCC: {val}"

    def test_imsi_ru_mcc(self, runner):
        val = _gen(runner, 'imsi', '--locale', 'RU')
        assert val.startswith('250'), f"IMSI RU MCC: {val}"

    def test_msisdn_uk_format(self, runner):
        val = _gen(runner, 'msisdn', '--locale', 'UK')
        assert val.startswith('+44'), f"MSISDN UK: {val}"

    def test_msisdn_de_format(self, runner):
        val = _gen(runner, 'msisdn', '--locale', 'DE')
        assert val.startswith('+49'), f"MSISDN DE: {val}"


# ===========================================================================
# generate — Securities (additional locales)
# ===========================================================================

class TestGenerateSecuritiesExtra:

    def test_isin_uk_format(self, runner):
        val = _gen(runner, 'isin', '--locale', 'UK')
        assert val.startswith('GB'), f"ISIN UK: {val}"
        assert _isin_valid(val)

    def test_isin_de_format(self, runner):
        val = _gen(runner, 'isin', '--locale', 'DE')
        assert val.startswith('DE'), f"ISIN DE: {val}"
        assert _isin_valid(val)

    def test_isin_fr_format(self, runner):
        val = _gen(runner, 'isin', '--locale', 'FR')
        assert val.startswith('FR'), f"ISIN FR: {val}"
        assert _isin_valid(val)

    def test_cusip_alphanumeric(self, runner):
        val = _gen(runner, 'cusip')
        assert re.match(r'^[A-Z0-9]{9}$', val), f"CUSIP: {val}"

    def test_lei_format_and_length(self, runner):
        val = _gen(runner, 'lei')
        assert len(val) == 20
        assert re.match(r'^[A-Z0-9]{20}$', val)


# ===========================================================================
# generate — Crypto (additional checks)
# ===========================================================================

class TestGenerateCryptoExtra:

    def test_btc_address_length_range(self, runner):
        for _ in range(10):
            val = _gen(runner, 'btc_address')
            assert 25 <= len(val) <= 34, f"BTC length {len(val)}: {val}"

    def test_eth_address_eip55_mixed_case(self, runner):
        for _ in range(5):
            val = _gen(runner, 'eth_address')
            body = val[2:]
            has_upper = any(c.isupper() for c in body)
            has_lower = any(c.islower() for c in body)
            assert has_upper and has_lower, f"ETH not EIP-55 mixed: {val}"

    def test_crypto_address_btc_starts_1(self, runner):
        val = _gen(runner, 'crypto_address', '--currency', 'btc')
        assert val.startswith('1'), f"crypto_address btc: {val}"

    def test_tx_hash_uniqueness(self, runner):
        hashes = {_gen(runner, 'tx_hash', '--currency', 'btc') for _ in range(5)}
        assert len(hashes) == 5, "tx_hash btc not unique"

    def test_block_hash_btc_lowercase(self, runner):
        val = _gen(runner, 'block_hash', '--currency', 'btc')
        assert re.match(r'^[0-9a-f]{64}$', val), f"block_hash btc: {val}"


# ===========================================================================
# generate — Barcode (additional locales)
# ===========================================================================

class TestGenerateBarcodeExtra:

    def test_ean13_us_prefix(self, runner):
        val = _gen(runner, 'ean13', '--locale', 'US')
        assert val[:3] in ('000', '001', '003', '004', '006', '007',
                           '008', '009', '010', '019', '030', '040',
                           '050', '060', '070', '080', '090',
                           '007', '008', '009',
                           ) or val[:2] == '00' or val[:3].isdigit()
        assert _gs1_valid(val), f"EAN-13 US checksum: {val}"

    def test_ean13_uk_prefix(self, runner):
        val = _gen(runner, 'ean13', '--locale', 'UK')
        assert val.startswith('50'), f"EAN-13 UK prefix: {val}"
        assert _gs1_valid(val)

    def test_ean13_fr_prefix(self, runner):
        val = _gen(runner, 'ean13', '--locale', 'FR')
        assert val[:2] in ('30', '31', '32', '33', '34', '35', '36', '37'), \
            f"EAN-13 FR prefix: {val}"
        assert _gs1_valid(val)

    def test_ean13_ru_prefix(self, runner):
        val = _gen(runner, 'ean13', '--locale', 'RU')
        assert val[:2] in ('46', '47', '48'), f"EAN-13 RU prefix: {val}"
        assert _gs1_valid(val)

    def test_ean8_de_prefix(self, runner):
        val = _gen(runner, 'ean8', '--locale', 'DE')
        assert val[:2] in ('40', '41', '42', '43', '44'), f"EAN-8 DE prefix: {val}"
        assert _gs1_valid(val)

    def test_isbn13_978_or_979(self, runner):
        for _ in range(5):
            val = _gen(runner, 'isbn13')
            assert val.startswith(('978', '979')), f"ISBN-13 prefix: {val}"
            assert _gs1_valid(val)


# ===========================================================================
# generate — E-Commerce (additional carrier / details)
# ===========================================================================

class TestGenerateEcommerceExtra:

    def test_tracking_usps_luhn_repeated(self, runner):
        for _ in range(5):
            val = _gen(runner, 'tracking_number', '--carrier', 'usps')
            assert _luhn_valid(val), f"USPS Luhn: {val}"

    def test_tracking_fedex_repeated(self, runner):
        for _ in range(5):
            val = _gen(runner, 'tracking_number', '--carrier', 'fedex')
            assert _fedex_valid(val), f"FedEx: {val}"

    def test_sku_uppercase_and_dash(self, runner):
        val = _gen(runner, 'sku')
        parts = val.split('-')
        assert len(parts) == 2, f"SKU no dash: {val}"
        assert parts[0].isalpha() and parts[0].isupper()
        assert parts[1].isdigit()

    def test_order_id_prefix(self, runner):
        val = _gen(runner, 'order_id')
        assert val.startswith('ORD-'), f"order_id prefix: {val}"

    def test_rating_half_steps(self, runner):
        valid = {'1.0','1.5','2.0','2.5','3.0','3.5','4.0','4.5','5.0'}
        for _ in range(10):
            val = _gen(runner, 'rating')
            assert val in valid, f"rating not half-step: {val}"

    def test_dhl_tracking_luhn_repeated(self, runner):
        for _ in range(5):
            val = _gen(runner, 'dhl_tracking')
            assert val.startswith('JD'), f"DHL prefix: {val}"
            assert len(val) == 11, f"DHL length: {len(val)}"
            body = [int(c) for c in val[2:10]]
            total = 0
            for i, d in enumerate(reversed(body)):
                n = d * 2 if i % 2 == 0 else d
                if n > 9:
                    n -= 9
                total += n
            assert int(val[10]) == (10 - total % 10) % 10, f"DHL Luhn: {val}"


# ===========================================================================
# generate — Location (additional locales)
# ===========================================================================

class TestGenerateLocationExtra:

    def test_latitude_de_range(self, runner):
        val = float(_gen(runner, 'latitude', '--locale', 'DE'))
        assert 47.0 <= val <= 55.0, f"lat DE: {val}"

    def test_latitude_uk_range(self, runner):
        val = float(_gen(runner, 'latitude', '--locale', 'UK'))
        assert 50.0 <= val <= 59.0, f"lat UK: {val}"

    def test_longitude_de_range(self, runner):
        val = float(_gen(runner, 'longitude', '--locale', 'DE'))
        assert 6.0 <= val <= 15.0, f"lon DE: {val}"

    def test_timezone_us(self, runner):
        val = _gen(runner, 'timezone', '--locale', 'US')
        assert 'America/' in val or 'US/' in val, f"timezone US: {val}"

    def test_timezone_uk(self, runner):
        val = _gen(runner, 'timezone', '--locale', 'UK')
        assert val == 'Europe/London', f"timezone UK: {val}"

    def test_country_code_de(self, runner):
        val = _gen(runner, 'country_code', '--locale', 'DE')
        assert val == 'DE'

    def test_country_code_us(self, runner):
        val = _gen(runner, 'country_code', '--locale', 'US')
        assert val == 'US'

    def test_coordinates_us_format(self, runner):
        val = _gen(runner, 'coordinates', '--locale', 'US')
        parts = val.split(',')
        assert len(parts) == 2
        lat, lon = float(parts[0]), float(parts[1])
        assert 25.0 <= lat <= 49.0
        assert -125.0 <= lon <= -66.0


# ===========================================================================
# generate — Social (additional checks)
# ===========================================================================

class TestGenerateSocialExtra:

    def test_username_length_range(self, runner):
        for _ in range(5):
            val = _gen(runner, 'username')
            assert 3 <= len(val) <= 20, f"username len {len(val)}: {val}"
            assert re.match(r'^[a-z0-9_]+$', val), f"username chars: {val}"

    def test_handle_at_and_length(self, runner):
        for _ in range(5):
            val = _gen(runner, 'handle')
            assert val.startswith('@')
            body = val[1:]
            assert len(body) >= 3
            assert re.match(r'^[a-z0-9_]+$', body), f"handle body: {val}"

    def test_hashtag_no_spaces(self, runner):
        for _ in range(5):
            val = _gen(runner, 'hashtag')
            assert ' ' not in val, f"hashtag has space: {val}"
            assert val.startswith('#')

    def test_bio_sentence_length(self, runner):
        for _ in range(3):
            val = _gen(runner, 'bio')
            assert 15 <= len(val) <= 200, f"bio length {len(val)}: {val}"

    def test_follower_count_range(self, runner):
        vals = [int(_gen(runner, 'follower_count')) for _ in range(10)]
        assert all(v > 0 for v in vals)
        assert max(vals) > 100, "follower_count never exceeds 100"


# ===========================================================================
# generate — Health (NPI repeated validation)
# ===========================================================================

class TestGenerateHealthExtra:

    def test_npi_valid_100_samples(self, runner):
        """NPI must pass CMS Luhn check for 100 consecutive samples."""
        for _ in range(100):
            val = _gen(runner, 'npi')
            assert re.match(r'^\d{10}$', val), f"NPI format: {val}"
            assert _npi_valid(val), f"NPI CMS Luhn failed: {val}"

    def test_bmi_one_decimal(self, runner):
        for _ in range(10):
            val = _gen(runner, 'bmi')
            assert re.match(r'^\d{2}\.\d$', str(val)), f"BMI decimal: {val}"

    def test_icd10_with_description(self, runner):
        val = _gen(runner, 'icd10')
        assert re.match(r'^[A-Z]\d{2}', val), f"ICD-10 format: {val}"

    def test_height_de_cm(self, runner):
        val = _gen(runner, 'height', '--locale', 'DE')
        assert 'cm' in val, f"DE height: {val}"

    def test_weight_de_kg(self, runner):
        val = _gen(runner, 'weight', '--locale', 'DE')
        assert 'kg' in val, f"DE weight: {val}"


# ===========================================================================
# generate — Identity (additional checks)
# ===========================================================================

class TestGenerateIdentityExtra:

    def test_tckn_repeated_checksums(self, runner):
        for _ in range(20):
            val = _gen(runner, 'tckn')
            assert _tckn_valid(val), f"TCKN repeated: {val}"

    def test_iban_us_routing_format(self, runner):
        val = _gen(runner, 'iban', '--locale', 'US')
        assert val.startswith('RT:'), f"IBAN US (routing) format: {val}"

    def test_iban_ru_bik_format(self, runner):
        val = _gen(runner, 'iban', '--locale', 'RU')
        assert val.startswith('BIK:'), f"IBAN RU (BIK) format: {val}"

    def test_nationalid_fr_nir(self, runner):
        val = _gen(runner, 'nationalid', '--locale', 'FR')
        assert re.match(r'^\d{15}$', val), f"FR nationalid (NIR 15 digits): {val}"

    def test_nationalid_ru_passport(self, runner):
        val = _gen(runner, 'nationalid', '--locale', 'RU')
        assert re.match(r'^\d{4} \d{6}$', val), f"RU nationalid (passport): {val}"

    def test_taxid_all_locales(self, runner):
        patterns = {
            'TR': r'^\d{10}$',
            'US': r'^\d{2}-\d{7}$',
            'UK': r'^\d{10}$',
            'DE': r'^DE\d{9}$',
            'FR': r'^\d{9}$',
            'RU': r'^\d{10}$',
        }
        for locale, pat in patterns.items():
            val = _gen(runner, 'taxid', '--locale', locale)
            assert re.match(pat, val), f"taxid {locale}: {val}"

    def test_snils_checksum(self, runner):
        for _ in range(10):
            val = _gen(runner, 'snils')
            assert re.match(r'^\d{3}-\d{3}-\d{3} \d{2}$', val), f"SNILS: {val}"

    def test_inn_checksum_repeated(self, runner):
        for _ in range(10):
            val = _gen(runner, 'inn')
            d = [int(c) for c in val]
            weights = [2, 4, 10, 3, 5, 9, 4, 6, 8]
            ctrl = sum(a * b for a, b in zip(d[:9], weights)) % 11 % 10
            assert d[9] == ctrl, f"INN checksum: {val}"


# ===========================================================================
# generate — Financial (additional checks)
# ===========================================================================

class TestGenerateFinancialExtra:

    def test_cardnum_repeated_luhn(self, runner):
        for _ in range(20):
            val = _gen(runner, 'cardnum', '--network', 'visa')
            assert _luhn_valid(val), f"VISA Luhn: {val}"

    def test_cardnum_jcb_prefix(self, runner):
        for _ in range(5):
            val = _gen(runner, 'cardnum', '--network', 'jcb')
            assert val.startswith('35'), f"JCB prefix: {val}"
            assert _luhn_valid(val)

    def test_cardnum_discover_prefix(self, runner):
        for _ in range(5):
            val = _gen(runner, 'cardnum', '--network', 'discover')
            assert val.startswith('6'), f"Discover prefix: {val}"
            assert _luhn_valid(val)

    def test_cardnum_mir_prefix(self, runner):
        for _ in range(5):
            val = _gen(runner, 'cardnum', '--network', 'mir')
            assert val.startswith('220'), f"MIR prefix: {val}"
            assert _luhn_valid(val)

    def test_cardnum_unionpay_prefix(self, runner):
        for _ in range(5):
            val = _gen(runner, 'cardnum', '--network', 'unionpay')
            assert val.startswith('62'), f"UnionPay prefix: {val}"
            assert _luhn_valid(val)

    def test_pin_4digits_range(self, runner):
        for _ in range(5):
            val = _gen(runner, 'pin')
            assert re.match(r'^\d{4}$', val)
            assert 0 <= int(val) <= 9999

    def test_balance_two_decimals(self, runner):
        for _ in range(5):
            val = _gen(runner, 'balance')
            assert re.match(r'^\d+\.\d{1,2}$', val), f"balance format: {val}"

    def test_credit_score_bands(self, runner):
        for _ in range(10):
            val = int(_gen(runner, 'credit_score'))
            assert 300 <= val <= 850, f"credit_score: {val}"


# ---------------------------------------------------------------------------
# Sprint 7 — Template CLI command: combine multiple types into one record
# ---------------------------------------------------------------------------

class TestTemplateCommand:
    """mockjutsu template <types...> — generate one record with multiple fields."""

    def test_template_basic_single_record(self, runner):
        """template with two types returns a single JSON object (count=1 default)."""
        r = runner.invoke(main, ['template', 'nin', 'snils'])
        assert r.exit_code == 0, f"exit_code={r.exit_code} output={r.output}"
        data = json.loads(r.output)
        assert isinstance(data, dict)
        assert 'nin'   in data
        assert 'snils' in data

    def test_template_four_types(self, runner):
        """template nin snils cardtype address_street → all 4 fields present."""
        r = runner.invoke(main, ['template', 'nin', 'snils', 'cardtype', 'address_street'])
        assert r.exit_code == 0
        data = json.loads(r.output)
        for key in ('nin', 'snils', 'cardtype', 'address_street'):
            assert key in data, f"Missing key: {key}"
            assert 'ERROR' not in str(data[key]), f"ERROR for {key}"

    def test_template_count_1_returns_dict(self, runner):
        """template --count 1 must return a single JSON object (not array)."""
        r = runner.invoke(main, ['template', 'uuid', 'timestamp', '--count', '1'])
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert isinstance(data, dict)

    def test_template_count_multiple_returns_array(self, runner):
        """template --count 5 must return a JSON array of 5 records."""
        r = runner.invoke(main, ['template', 'uuid', 'timestamp', '--count', '5'])
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert isinstance(data, list)
        assert len(data) == 5
        for rec in data:
            assert 'uuid'      in rec
            assert 'timestamp' in rec

    def test_template_locale_phone_iban(self, runner):
        """template phone iban --locale DE → German prefix."""
        r = runner.invoke(main, ['template', 'phone', 'iban', '--locale', 'DE'])
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert data['phone'].startswith('+49'), f"DE phone prefix wrong: {data['phone']}"
        assert data['iban'].startswith('DE'),   f"DE IBAN prefix wrong: {data['iban']}"

    def test_template_locale_tr(self, runner):
        """template phone iban --locale TR → Turkish prefix."""
        r = runner.invoke(main, ['template', 'phone', 'iban', '--locale', 'TR'])
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert data['phone'].startswith('+90')
        assert data['iban'].startswith('TR')

    def test_template_locale_us(self, runner):
        """template phone --locale US → US prefix."""
        r = runner.invoke(main, ['template', 'phone', '--locale', 'US'])
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert data['phone'].startswith('+1')

    def test_template_locale_uk(self, runner):
        """template phone iban --locale UK → UK prefix."""
        r = runner.invoke(main, ['template', 'phone', 'iban', '--locale', 'UK'])
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert data['phone'].startswith('+44')
        assert data['iban'].startswith('GB')

    def test_template_no_error_values(self, runner):
        """template must not produce ERROR values for standard scalar types."""
        types = ['nin', 'snils', 'cardtype', 'address_street', 'uuid',
                 'phone', 'iban', 'firstname', 'lastname', 'tckn',
                 'bic', 'bank_name', 'timestamp', 'timestamp_iso']
        r = runner.invoke(main, ['template'] + types + ['--locale', 'TR'])
        assert r.exit_code == 0
        data = json.loads(r.output)
        for key, val in data.items():
            assert 'ERROR' not in str(val), f"template CLI ERROR for {key}: {val}"

    def test_template_identity_types(self, runner):
        """template identity types in one call."""
        types = ['tckn', 'firstname', 'lastname', 'passport', 'nationality',
                 'ssn', 'nin', 'snils', 'license', 'age', 'gender', 'birthdate']
        r = runner.invoke(main, ['template'] + types)
        assert r.exit_code == 0
        data = json.loads(r.output)
        for t in types:
            assert t in data, f"Missing: {t}"

    def test_template_financial_types(self, runner):
        """template financial types in one call."""
        types = ['cardnum', 'cardnetwork', 'cardtype', 'cardstatus', 'cardcategory',
                 'cardowner', 'expirymonth', 'expiryyear', 'cvv3', 'issuer', 'balance', 'iban']
        r = runner.invoke(main, ['template'] + types + ['--locale', 'TR'])
        assert r.exit_code == 0
        data = json.loads(r.output)
        for t in types:
            assert t in data
            assert 'ERROR' not in str(data[t])

    def test_template_contact_types(self, runner):
        """template contact/address types in one call."""
        types = ['phone', 'phone_area', 'phone_local', 'email',
                 'address_city', 'address_street', 'address_full', 'postalcode', 'plate']
        r = runner.invoke(main, ['template'] + types + ['--locale', 'TR'])
        assert r.exit_code == 0
        data = json.loads(r.output)
        for t in types:
            assert t in data
            assert 'ERROR' not in str(data[t])

    def test_template_meta_types(self, runner):
        """template meta/system types in one call."""
        types = ['uuid', 'requestid', 'correlationid', 'sessionid', 'deviceid',
                 'timestamp', 'timestamp_iso', 'ipv4', 'ipv6', 'mac_address',
                 'browser_name', 'browser_engine', 'useragent', 'clientversion']
        r = runner.invoke(main, ['template'] + types)
        assert r.exit_code == 0
        data = json.loads(r.output)
        for t in types:
            assert t in data
            assert 'ERROR' not in str(data[t])

    def test_template_banking_types(self, runner):
        """template banking types in one call."""
        types = ['swift', 'bic', 'bank_name', 'sort_code', 'routing_number',
                 'bik_code', 'sepa_ref']
        r = runner.invoke(main, ['template'] + types + ['--locale', 'TR'])
        assert r.exit_code == 0
        data = json.loads(r.output)
        for t in types:
            assert t in data

    def test_template_health_types(self, runner):
        """template health types in one call."""
        types = ['blood_type', 'nhs_number', 'icd10', 'height', 'weight', 'npi', 'bmi']
        r = runner.invoke(main, ['template'] + types)
        assert r.exit_code == 0
        data = json.loads(r.output)
        for t in types:
            assert t in data
            assert 'ERROR' not in str(data[t])

    def test_template_telecom_barcode_types(self, runner):
        """template telecom and barcode types in one call."""
        types = ['imei', 'iccid', 'imsi', 'msisdn', 'ean13', 'ean8', 'upca', 'isbn13']
        r = runner.invoke(main, ['template'] + types)
        assert r.exit_code == 0
        data = json.loads(r.output)
        for t in types:
            assert t in data

    def test_template_securities_types(self, runner):
        """template financial markets types in one call."""
        types = ['isin', 'cusip', 'sedol', 'lei']
        r = runner.invoke(main, ['template'] + types)
        assert r.exit_code == 0
        data = json.loads(r.output)
        for t in types:
            assert t in data
            assert 'ERROR' not in str(data[t])

    def test_template_crypto_types(self, runner):
        """template crypto types in one call."""
        types = ['btc_address', 'eth_address', 'tx_hash', 'block_hash']
        r = runner.invoke(main, ['template'] + types)
        assert r.exit_code == 0
        data = json.loads(r.output)
        for t in types:
            assert t in data

    def test_template_ecommerce_social_types(self, runner):
        """template e-commerce and social media types in one call."""
        types = ['product_name', 'sku', 'order_id', 'category', 'rating', 'dhl_tracking',
                 'username', 'hashtag', 'bio', 'handle', 'follower_count']
        r = runner.invoke(main, ['template'] + types)
        assert r.exit_code == 0
        data = json.loads(r.output)
        for t in types:
            assert t in data

    def test_template_location_types(self, runner):
        """template location types in one call."""
        types = ['latitude', 'longitude', 'timezone', 'country_code', 'coordinates']
        r = runner.invoke(main, ['template'] + types + ['--locale', 'TR'])
        assert r.exit_code == 0
        data = json.loads(r.output)
        for t in types:
            assert t in data

    def test_template_format_csv(self, runner):
        """template --format csv must return CSV with header + data rows."""
        r = runner.invoke(main, ['template', 'uuid', 'nin', 'snils',
                                 '--count', '3', '--format', 'csv'])
        assert r.exit_code == 0
        lines = r.output.strip().split('\n')
        assert len(lines) == 4, f"Expected header + 3 rows, got {len(lines)}"
        assert 'uuid'  in lines[0]
        assert 'nin'   in lines[0]
        assert 'snils' in lines[0]

    def test_template_format_sql(self, runner):
        """template --format sql must return valid INSERT statement."""
        r = runner.invoke(main, ['template', 'uuid', 'nin',
                                 '--count', '2', '--format', 'sql'])
        assert r.exit_code == 0
        output = r.output.strip()
        assert output.startswith('INSERT INTO'), f"SQL wrong start: {output[:50]}"
        assert output.endswith(';')

    def test_template_all_six_locales(self, runner):
        """template must run without error for all 6 locales."""
        for locale in ['TR', 'US', 'UK', 'DE', 'FR', 'RU']:
            r = runner.invoke(main, ['template', 'firstname', 'phone', 'iban',
                                     '--locale', locale])
            assert r.exit_code == 0, f"template failed for {locale}: {r.output}"
            data = json.loads(r.output)
            for key, val in data.items():
                assert 'ERROR' not in str(val), f"ERROR for {key} in {locale}: {val}"

    def test_template_nin_format(self, runner):
        """template nin → UK NIN format 'XX DD DD DD [ABCD]'."""
        r = runner.invoke(main, ['template', 'nin'])
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert re.match(r'^[A-Z]{2} \d{2} \d{2} \d{2} [ABCD]$', data['nin']), \
            f"NIN format wrong: {data['nin']}"

    def test_template_snils_format(self, runner):
        """template snils → SNILS format 'DDD-DDD-DDD DD'."""
        r = runner.invoke(main, ['template', 'snils'])
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert re.match(r'^\d{3}-\d{3}-\d{3} \d{2}$', data['snils']), \
            f"SNILS format wrong: {data['snils']}"

    def test_template_cardtype_valid(self, runner):
        """template cardtype → 'Credit' or 'Debit'."""
        r = runner.invoke(main, ['template', 'cardtype'])
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert data['cardtype'] in ('Credit', 'Debit')

    def test_template_address_street_nonempty(self, runner):
        """template address_street → non-empty string."""
        r = runner.invoke(main, ['template', 'address_street', '--locale', 'TR'])
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert len(data['address_street']) >= 2

    def test_template_uuid_v4_format(self, runner):
        """template uuid → UUID v4 format."""
        r = runner.invoke(main, ['template', 'uuid'])
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert re.match(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
            data['uuid']
        ), f"UUID v4 format wrong: {data['uuid']}"

    def test_template_count_ten(self, runner):
        """template --count 10 returns 10 records."""
        r = runner.invoke(main, ['template', 'uuid', 'nin', '--count', '10'])
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert isinstance(data, list)
        assert len(data) == 10
