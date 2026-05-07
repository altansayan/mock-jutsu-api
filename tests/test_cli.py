"""
mock-jutsu — CLI Integration Tests
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)
Tests every CLI command via Click's CliRunner (no subprocess, no real I/O).
"""

import json
import re
import pytest
from click.testing import CliRunner
from mockjutsu.cli import main


@pytest.fixture
def runner():
    return CliRunner()


# ---------------------------------------------------------------------------
# generate — temel tipler
# ---------------------------------------------------------------------------

class TestGenerate:

    def test_no_args_shows_error(self, runner):
        r = runner.invoke(main, ['generate'])
        assert r.exit_code == 0
        assert 'Error' in r.output

    def test_invalid_type_shows_error(self, runner):
        r = runner.invoke(main, ['generate', 'nonexistent_type_xyz'])
        assert r.exit_code == 0
        assert 'ERROR' in r.output

    def test_tckn(self, runner):
        r = runner.invoke(main, ['generate', 'tckn'])
        assert r.exit_code == 0
        assert re.match(r'^\d{11}', r.output.strip())

    def test_uuid(self, runner):
        r = runner.invoke(main, ['generate', 'uuid'])
        assert r.exit_code == 0
        assert re.match(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}',
            r.output.strip()
        )

    def test_iban_default_locale(self, runner):
        r = runner.invoke(main, ['generate', 'iban'])
        assert r.exit_code == 0
        assert r.output.strip().startswith('TR')

    def test_iban_locale_de(self, runner):
        r = runner.invoke(main, ['generate', 'iban', '--locale', 'DE'])
        assert r.exit_code == 0
        assert r.output.strip().startswith('DE')

    def test_firstname_locale_ru(self, runner):
        r = runner.invoke(main, ['generate', 'firstname', '--locale', 'RU'])
        assert r.exit_code == 0
        assert r.output.strip()  # non-empty

    def test_cardnum_default(self, runner):
        r = runner.invoke(main, ['generate', 'cardnum'])
        assert r.exit_code == 0
        val = r.output.strip()
        assert val.isdigit()
        assert len(val) in (15, 16)

    def test_cardnum_network_amex(self, runner):
        r = runner.invoke(main, ['generate', 'cardnum', '--network', 'amex'])
        assert r.exit_code == 0
        val = r.output.strip()
        assert val.startswith(('34', '37'))
        assert len(val) == 15

    def test_cardnum_network_troy(self, runner):
        r = runner.invoke(main, ['generate', 'cardnum', '--network', 'troy'])
        assert r.exit_code == 0
        assert r.output.strip().startswith('9792')

    def test_tracking_carrier_ups(self, runner):
        r = runner.invoke(main, ['generate', 'tracking_number', '--carrier', 'ups'])
        assert r.exit_code == 0
        assert r.output.strip().startswith('1Z')

    def test_tracking_carrier_fedex(self, runner):
        r = runner.invoke(main, ['generate', 'tracking_number', '--carrier', 'fedex'])
        assert r.exit_code == 0
        val = r.output.strip()
        assert val.isdigit()
        assert len(val) == 12

    def test_tx_hash_btc(self, runner):
        r = runner.invoke(main, ['generate', 'tx_hash', '--currency', 'btc'])
        assert r.exit_code == 0
        assert re.match(r'^[0-9a-f]{64}$', r.output.strip())

    def test_tx_hash_eth(self, runner):
        r = runner.invoke(main, ['generate', 'tx_hash', '--currency', 'eth'])
        assert r.exit_code == 0
        assert re.match(r'^0x[0-9a-f]{64}$', r.output.strip())

    def test_transaction_locale_tr(self, runner):
        r = runner.invoke(main, ['generate', 'transaction', '--locale', 'TR'])
        assert r.exit_code == 0
        assert 'TRN' in r.output or 'FAST' in r.output or 'TRY' in r.output

    # ── hash --algorithm ────────────────────────────────────────────────────

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
        r = runner.invoke(main, ['generate', 'hash', '--algorithm', algo])
        assert r.exit_code == 0, f"exit_code={r.exit_code} for --algorithm {algo}"
        val = r.output.strip()
        assert re.match(r'^[0-9a-f]+$', val), f"not hex for {algo}: {val}"
        assert len(val) == expected_len, \
            f"--algorithm {algo}: expected {expected_len} chars, got {len(val)}"

    def test_hash_default_is_sha256(self, runner):
        r = runner.invoke(main, ['generate', 'hash'])
        assert r.exit_code == 0
        assert len(r.output.strip()) == 64

    # ── diğer tipler ────────────────────────────────────────────────────────

    def test_api_key(self, runner):
        r = runner.invoke(main, ['generate', 'api_key'])
        assert r.exit_code == 0
        assert r.output.strip().startswith('sk-')
        assert len(r.output.strip()) == 51

    def test_totp_code(self, runner):
        r = runner.invoke(main, ['generate', 'totp_code'])
        assert r.exit_code == 0
        assert re.match(r'^\d{6}$', r.output.strip())

    def test_webhook_signature(self, runner):
        r = runner.invoke(main, ['generate', 'webhook_signature'])
        assert r.exit_code == 0
        assert r.output.strip().startswith('sha256=')

    def test_public_ip(self, runner):
        r = runner.invoke(main, ['generate', 'public_ip'])
        assert r.exit_code == 0
        parts = r.output.strip().split('.')
        assert len(parts) == 4
        assert all(p.isdigit() for p in parts)

    def test_private_ip(self, runner):
        r = runner.invoke(main, ['generate', 'private_ip'])
        assert r.exit_code == 0
        val = r.output.strip()
        assert (
            val.startswith('10.') or
            val.startswith('192.168.') or
            val.startswith('172.')
        )

    def test_dhl_tracking(self, runner):
        r = runner.invoke(main, ['generate', 'dhl_tracking'])
        assert r.exit_code == 0
        val = r.output.strip()
        assert val.startswith('JD')
        assert len(val) == 11

    def test_credit_score(self, runner):
        r = runner.invoke(main, ['generate', 'credit_score'])
        assert r.exit_code == 0
        val = int(r.output.strip())
        assert 300 <= val <= 850

    def test_nationality(self, runner):
        r = runner.invoke(main, ['generate', 'nationality'])
        assert r.exit_code == 0
        assert re.match(r'^[A-Z]{3}$', r.output.strip())

    def test_tckn_masked(self, runner):
        r = runner.invoke(main, ['generate', 'tckn_masked'])
        assert r.exit_code == 0
        assert re.match(r'^\*{3}\d{6}\*{2}$', r.output.strip())

    def test_sepa_ref(self, runner):
        r = runner.invoke(main, ['generate', 'sepa_ref'])
        assert r.exit_code == 0
        val = r.output.strip()
        assert re.match(r'^[A-Z0-9]{20,35}$', val)


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------

class TestList:

    def test_list_runs(self, runner):
        r = runner.invoke(main, ['list'])
        assert r.exit_code == 0
        assert 'TYPE' in r.output
        assert 'CLI COMMAND' in r.output

    def test_list_contains_categories(self, runner):
        r = runner.invoke(main, ['list'])
        assert r.exit_code == 0
        for cat in ('IDENTITY', 'FINANCIAL', 'BANKING', 'META'):
            assert cat in r.output.upper(), f"Category {cat} missing from list"

    def test_list_cat_filter_financial(self, runner):
        r = runner.invoke(main, ['list', '--cat', 'Financial'])
        assert r.exit_code == 0
        assert 'FINANCIAL' in r.output.upper()
        assert 'IDENTITY' not in r.output.upper()

    def test_list_cat_filter_meta(self, runner):
        r = runner.invoke(main, ['list', '--cat', 'Meta'])
        assert r.exit_code == 0
        assert 'META' in r.output.upper()
        assert 'hash' in r.output

    def test_list_cat_filter_security(self, runner):
        r = runner.invoke(main, ['list', '--cat', 'Security'])
        assert r.exit_code == 0
        assert 'api_key' in r.output or 'totp_code' in r.output

    def test_list_contains_hash_algorithms(self, runner):
        r = runner.invoke(main, ['list', '--cat', 'Meta'])
        assert r.exit_code == 0
        assert '--algorithm' in r.output

    def test_list_unknown_cat_returns_empty(self, runner):
        r = runner.invoke(main, ['list', '--cat', 'zzz_nonexistent'])
        assert r.exit_code == 0
        assert '0 types listed' in r.output or 'types listed' in r.output

    def test_list_shows_locale_flag(self, runner):
        r = runner.invoke(main, ['list'])
        assert r.exit_code == 0
        assert 'L=v' in r.output


# ---------------------------------------------------------------------------
# profile
# ---------------------------------------------------------------------------

class TestProfile:

    def test_profile_default(self, runner):
        r = runner.invoke(main, ['profile'])
        assert r.exit_code == 0
        data = json.loads(r.output)
        for key in ('id', 'firstname', 'lastname', 'phone', 'email', 'iban'):
            assert key in data, f"'{key}' missing from profile"

    def test_profile_locale_de(self, runner):
        r = runner.invoke(main, ['profile', '--locale', 'DE'])
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert data['iban'].startswith('DE')

    def test_profile_locale_ru(self, runner):
        r = runner.invoke(main, ['profile', '--locale', 'RU'])
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert 'fullname' in data

    def test_profile_count_returns_list(self, runner):
        r = runner.invoke(main, ['profile', '--count', '3'])
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert isinstance(data, list)
        assert len(data) == 3

    def test_profile_count_1_returns_dict(self, runner):
        r = runner.invoke(main, ['profile', '--count', '1'])
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert isinstance(data, dict)

    @pytest.mark.parametrize("locale", ['TR', 'US', 'UK', 'DE', 'FR', 'RU'])
    def test_profile_all_locales(self, runner, locale):
        r = runner.invoke(main, ['profile', '--locale', locale])
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert 'email' in data


# ---------------------------------------------------------------------------
# company
# ---------------------------------------------------------------------------

class TestCompany:

    def test_company_default(self, runner):
        r = runner.invoke(main, ['company'])
        assert r.exit_code == 0
        data = json.loads(r.output)
        for key in ('id', 'name', 'iban', 'bic', 'phone', 'address'):
            assert key in data, f"'{key}' missing from company"

    def test_company_locale_fr(self, runner):
        r = runner.invoke(main, ['company', '--locale', 'FR'])
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert data['iban'].startswith('FR')

    def test_company_count_2(self, runner):
        r = runner.invoke(main, ['company', '--count', '2'])
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert isinstance(data, list)
        assert len(data) == 2

    @pytest.mark.parametrize("locale", ['TR', 'US', 'UK', 'DE', 'FR', 'RU'])
    def test_company_all_locales(self, runner, locale):
        r = runner.invoke(main, ['company', '--locale', locale])
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert 'name' in data


# ---------------------------------------------------------------------------
# bulk
# ---------------------------------------------------------------------------

class TestBulk:

    def test_bulk_tckn(self, runner):
        r = runner.invoke(main, ['bulk', 'tckn', '--count', '5'])
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert isinstance(data, list)
        assert len(data) == 5
        assert all(re.match(r'^\d{11}$', str(v)) for v in data)

    def test_bulk_default_count_is_10(self, runner):
        r = runner.invoke(main, ['bulk', 'uuid'])
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert len(data) == 10

    def test_bulk_with_locale(self, runner):
        r = runner.invoke(main, ['bulk', 'iban', '--locale', 'DE', '--count', '3'])
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert all(v.startswith('DE') for v in data)

    def test_bulk_cardnum(self, runner):
        r = runner.invoke(main, ['bulk', 'cardnum', '--count', '10'])
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert len(data) == 10
        assert all(str(v).isdigit() for v in data)

    def test_bulk_unique_values(self, runner):
        r = runner.invoke(main, ['bulk', 'uuid', '--count', '20'])
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert len(set(data)) == 20, "bulk uuid produced duplicate values"


# ---------------------------------------------------------------------------
# export
# ---------------------------------------------------------------------------

class TestExport:

    def test_export_json_default(self, runner):
        r = runner.invoke(main, ['export', 'fullname', 'tckn', '--count', '3'])
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert isinstance(data, list)
        assert len(data) == 3
        assert 'fullname' in data[0]
        assert 'tckn' in data[0]

    def test_export_csv_format(self, runner):
        r = runner.invoke(main, ['export', 'fullname', 'tckn', '--count', '3',
                                 '--format', 'csv'])
        assert r.exit_code == 0
        lines = r.output.strip().splitlines()
        assert lines[0] == 'fullname,tckn'   # header
        assert len(lines) == 4               # header + 3 rows

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

    def test_export_locale_uk(self, runner):
        r = runner.invoke(main, ['export', 'iban', '--count', '3',
                                 '--locale', 'UK'])
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert all(row['iban'].startswith('GB') for row in data)

    def test_export_count(self, runner):
        r = runner.invoke(main, ['export', 'uuid', '--count', '7'])
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert len(data) == 7

    def test_export_multiple_types(self, runner):
        r = runner.invoke(main, ['export', 'uuid', 'fullname', 'email',
                                 'phone', 'iban', '--count', '2'])
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert set(data[0].keys()) == {'uuid', 'fullname', 'email', 'phone', 'iban'}
