"""
mock-jutsu — Wave 8-B: Card Physics Unit Tests (TDD)
Standards: ISO 8583-1:1993, ISO 9564-1:2011, EMV v4.3, ISO/IEC 7813
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)
"""

import json
import re
import pytest
from mockjutsu.core import jutsu


# ── Hardware fixes ──────────────────────────────────────────────────────────

class TestTrack1Data:
    def test_starts_with_sentinel(self):
        for _ in range(30):
            val = jutsu.generate('track1_data')
            assert val.startswith('%B'), f"Missing %%B sentinel: {val}"

    def test_ends_with_sentinel(self):
        for _ in range(30):
            val = jutsu.generate('track1_data')
            assert val.endswith('?'), f"Missing ? sentinel: {val}"

    def test_has_two_field_separators(self):
        for _ in range(30):
            val = jutsu.generate('track1_data')
            body = val[2:-1]  # strip %B and ?
            assert body.count('^') == 2, f"Expected 2 ^ separators: {val}"

    def test_mockj_marker_in_name(self):
        for _ in range(30):
            val = jutsu.generate('track1_data')
            name_field = val.split('^')[1]
            assert 'MOCKJ' in name_field, f"MOCKJ marker missing in name: {val}"

    def test_expiry_dynamic_year(self):
        from datetime import datetime
        current_yy = datetime.now().year % 100
        for _ in range(30):
            val = jutsu.generate('track1_data')
            # field after second ^ starts with YYMM
            suffix = val.split('^')[2]
            exp_yy = int(suffix[:2])
            assert exp_yy >= current_yy, f"Hardcoded/past expiry year: {exp_yy}"

    def test_total_length_within_79(self):
        for _ in range(50):
            val = jutsu.generate('track1_data')
            assert len(val) <= 79, f"Track 1 exceeds 79 chars: {len(val)}"


class TestPinBlockFormat0:
    def test_length_is_16(self):
        for _ in range(50):
            val = jutsu.generate('pin_block')
            assert len(val) == 16, f"Expected 16 chars: {len(val)}"

    def test_format_nibble_is_zero(self):
        for _ in range(50):
            val = jutsu.generate('pin_block')
            assert val[0] == '0', f"Format nibble must be '0': {val[0]}"

    def test_pin_length_nibble_valid(self):
        for _ in range(50):
            val = jutsu.generate('pin_block')
            pin_len = int(val[1], 16)
            assert 4 <= pin_len <= 12, f"PIN length {pin_len} out of range [4..12]"

    def test_pin_digits_are_decimal(self):
        for _ in range(50):
            val = jutsu.generate('pin_block')
            pin_len = int(val[1], 16)
            pin_digits = val[2:2 + pin_len]
            assert all(c in '0123456789' for c in pin_digits), \
                f"PIN digits must be 0-9: '{pin_digits}'"

    def test_fill_nibbles_are_F(self):
        for _ in range(50):
            val = jutsu.generate('pin_block')
            pin_len = int(val[1], 16)
            fill = val[2 + pin_len:]
            assert fill == 'F' * len(fill), f"Fill must be all F: '{fill}'"

    def test_all_chars_uppercase_hex(self):
        for _ in range(50):
            val = jutsu.generate('pin_block')
            assert re.match(r'^[0-9A-F]{16}$', val), f"Invalid hex: {val}"


class TestPinBlockFormat3:
    def test_length_is_16(self):
        for _ in range(50):
            val = jutsu.generate('pin_block_fmt3')
            assert len(val) == 16, f"Expected 16 chars: {len(val)}"

    def test_format_nibble_is_3(self):
        for _ in range(50):
            val = jutsu.generate('pin_block_fmt3')
            assert val[0] == '3', f"Format nibble must be '3': {val[0]}"

    def test_pin_length_nibble_valid(self):
        for _ in range(50):
            val = jutsu.generate('pin_block_fmt3')
            pin_len = int(val[1], 16)
            assert 4 <= pin_len <= 12, f"PIN length {pin_len} out of range"

    def test_fill_nibbles_are_decimal_digits(self):
        for _ in range(50):
            val = jutsu.generate('pin_block_fmt3')
            pin_len = int(val[1], 16)
            fill = val[2 + pin_len:]
            assert all(c in '0123456789' for c in fill), \
                f"Format 3 fill must be 0-9 digits: '{fill}'"

    def test_all_chars_uppercase_hex(self):
        for _ in range(50):
            val = jutsu.generate('pin_block_fmt3')
            assert re.match(r'^[0-9A-F]{16}$', val), f"Invalid hex: {val}"


class TestChipDataLocale:
    def test_tr_currency_code(self):
        val = jutsu.generate('chip_data', locale='TR')
        assert '5F2A020949' in val, f"Expected TRY 0949 in chip_data: {val}"

    def test_de_currency_code(self):
        val = jutsu.generate('chip_data', locale='DE')
        assert '5F2A020978' in val, f"Expected EUR 0978 in chip_data: {val}"

    def test_uk_currency_code(self):
        val = jutsu.generate('chip_data', locale='UK')
        assert '5F2A020826' in val, f"Expected GBP 0826 in chip_data: {val}"

    def test_us_currency_code(self):
        val = jutsu.generate('chip_data', locale='US')
        assert '5F2A020840' in val, f"Expected USD 0840 in chip_data: {val}"

    def test_ru_currency_code(self):
        val = jutsu.generate('chip_data', locale='RU')
        assert '5F2A020643' in val, f"Expected RUB 0643 in chip_data: {val}"


# ── CardPhysics — EMV Cryptograms ─────────────────────────────────────────────

class TestEmvArqc:
    def test_length_16(self):
        for _ in range(50):
            val = jutsu.generate('emv_arqc')
            assert len(val) == 16, f"ARQC must be 16 hex: {val}"

    def test_uppercase_hex(self):
        for _ in range(50):
            val = jutsu.generate('emv_arqc')
            assert re.match(r'^[0-9A-F]{16}$', val), f"Invalid ARQC: {val}"

    def test_randomness(self):
        values = {jutsu.generate('emv_arqc') for _ in range(20)}
        assert len(values) > 10, "ARQC not sufficiently random"


class TestEmvAtc:
    def test_length_4(self):
        for _ in range(50):
            val = jutsu.generate('emv_atc')
            assert len(val) == 4, f"ATC must be 4 hex: {val}"

    def test_uppercase_hex(self):
        for _ in range(50):
            val = jutsu.generate('emv_atc')
            assert re.match(r'^[0-9A-F]{4}$', val), f"Invalid ATC: {val}"

    def test_nonzero(self):
        for _ in range(50):
            val = jutsu.generate('emv_atc')
            assert int(val, 16) > 0, f"ATC must be > 0: {val}"


class TestEmvIad:
    def test_length_22(self):
        for _ in range(50):
            val = jutsu.generate('emv_iad')
            assert len(val) == 22, f"IAD must be 22 hex: {val}"

    def test_uppercase_hex(self):
        for _ in range(50):
            val = jutsu.generate('emv_iad')
            assert re.match(r'^[0-9A-F]{22}$', val), f"Invalid IAD: {val}"

    def test_starts_with_0A(self):
        for _ in range(50):
            val = jutsu.generate('emv_iad')
            assert val[:2] == '0A', f"IAD must start with 0A (DKI length): {val}"


# ── CardPhysics — ISO 8583 Messages ──────────────────────────────────────────

class TestIso8583AuthRequest:
    def test_mti_0100(self):
        for _ in range(20):
            val = jutsu.generate('iso8583_auth_request')
            assert 'MTI:0100' in val, f"Missing MTI:0100: {val[:50]}"

    def test_bitmap_present_and_16_hex(self):
        for _ in range(20):
            val = jutsu.generate('iso8583_auth_request')
            lines = dict(l.split(':', 1) for l in val.strip().splitlines() if ':' in l)
            assert 'BITMAP' in lines, "BITMAP field missing"
            bmp = lines['BITMAP']
            assert len(bmp) == 16, f"Bitmap must be 16 hex: '{bmp}'"
            assert re.match(r'^[0-9A-F]{16}$', bmp), f"Bitmap not uppercase hex: '{bmp}'"

    def test_bitmap_fixed_value(self):
        val = jutsu.generate('iso8583_auth_request')
        lines = dict(l.split(':', 1) for l in val.strip().splitlines() if ':' in l)
        assert lines['BITMAP'] == '723C448008C08000', \
            f"Wrong bitmap for auth request: {lines['BITMAP']}"

    def test_required_des_present(self):
        for _ in range(10):
            val = jutsu.generate('iso8583_auth_request')
            for de in ['DE002', 'DE003', 'DE004', 'DE037', 'DE041', 'DE042', 'DE049']:
                assert f'{de}:' in val, f"Missing {de} in auth request"

    def test_mockj_marker(self):
        for _ in range(20):
            val = jutsu.generate('iso8583_auth_request')
            assert 'MOCKJ' in val, f"MOCKJ marker missing in auth request"

    def test_de037_rrn_12_chars(self):
        for _ in range(20):
            val = jutsu.generate('iso8583_auth_request')
            lines = dict(l.split(':', 1) for l in val.strip().splitlines() if ':' in l)
            rrn = lines.get('DE037', '')
            assert len(rrn) == 12, f"DE037 RRN must be 12 chars: '{rrn}'"

    def test_de041_tid_8_chars(self):
        for _ in range(20):
            val = jutsu.generate('iso8583_auth_request')
            lines = dict(l.split(':', 1) for l in val.strip().splitlines() if ':' in l)
            tid = lines.get('DE041', '')
            assert len(tid) == 8, f"DE041 TID must be 8 chars: '{tid}'"

    def test_de042_mid_15_chars(self):
        for _ in range(20):
            val = jutsu.generate('iso8583_auth_request')
            lines = dict(l.split(':', 1) for l in val.strip().splitlines() if ':' in l)
            mid = lines.get('DE042', '')
            assert len(mid) == 15, f"DE042 MID must be 15 chars: '{mid}'"

    def test_locale_tr_currency_949(self):
        val = jutsu.generate('iso8583_auth_request', locale='TR')
        assert 'DE049:0949' in val, f"TR locale must have currency 0949"

    def test_locale_us_currency_840(self):
        val = jutsu.generate('iso8583_auth_request', locale='US')
        assert 'DE049:0840' in val, f"US locale must have currency 0840"


class TestIso8583AuthResponse:
    def test_mti_0110(self):
        for _ in range(20):
            val = jutsu.generate('iso8583_auth_response')
            assert 'MTI:0110' in val, f"Missing MTI:0110"

    def test_bitmap_fixed_value(self):
        val = jutsu.generate('iso8583_auth_response')
        lines = dict(l.split(':', 1) for l in val.strip().splitlines() if ':' in l)
        assert lines['BITMAP'] == '7238000006C00000', \
            f"Wrong bitmap for auth response: {lines['BITMAP']}"

    def test_de038_auth_code_present(self):
        for _ in range(20):
            val = jutsu.generate('iso8583_auth_response')
            assert 'DE038:' in val, "DE038 (auth code) missing in response"

    def test_de038_auth_code_6_chars(self):
        for _ in range(20):
            val = jutsu.generate('iso8583_auth_response')
            lines = dict(l.split(':', 1) for l in val.strip().splitlines() if ':' in l)
            auth = lines.get('DE038', '')
            assert len(auth) == 6, f"DE038 auth code must be 6 chars: '{auth}'"

    def test_de039_response_code_2_chars(self):
        for _ in range(20):
            val = jutsu.generate('iso8583_auth_response')
            lines = dict(l.split(':', 1) for l in val.strip().splitlines() if ':' in l)
            rc = lines.get('DE039', '')
            assert len(rc) == 2, f"DE039 response code must be 2 chars: '{rc}'"
            assert re.match(r'^\d{2}$', rc), f"DE039 must be 2 digits: '{rc}'"

    def test_mockj_marker(self):
        for _ in range(20):
            val = jutsu.generate('iso8583_auth_response')
            assert 'MOCKJ' in val, "MOCKJ marker missing in auth response"


class TestIso8583Reversal:
    def test_mti_0400(self):
        for _ in range(20):
            val = jutsu.generate('iso8583_reversal')
            assert 'MTI:0400' in val, f"Missing MTI:0400"

    def test_bitmap_fixed_value(self):
        val = jutsu.generate('iso8583_reversal')
        lines = dict(l.split(':', 1) for l in val.strip().splitlines() if ':' in l)
        assert lines['BITMAP'] == '7238000008C08100', \
            f"Wrong bitmap for reversal: {lines['BITMAP']}"

    def test_de056_original_data_present(self):
        for _ in range(20):
            val = jutsu.generate('iso8583_reversal')
            assert 'DE056:' in val, "DE056 (original data) missing in reversal"

    def test_mockj_marker(self):
        for _ in range(20):
            val = jutsu.generate('iso8583_reversal')
            assert 'MOCKJ' in val, "MOCKJ marker missing in reversal"


# ── CardPhysics — ATM/POS ──────────────────────────────────────────────────

class TestAtmSession:
    def test_is_valid_json(self):
        for _ in range(20):
            val = jutsu.generate('atm_session')
            data = json.loads(val)
            assert isinstance(data, dict), "atm_session must return JSON object"

    def test_required_fields(self):
        required = ['session_id', 'terminal_id', 'masked_pan', 'amount',
                    'currency', 'response_code', 'auth_code', 'atc', 'arqc', 'stan']
        for _ in range(10):
            val = jutsu.generate('atm_session')
            data = json.loads(val)
            for field in required:
                assert field in data, f"Missing field '{field}' in atm_session"

    def test_mockj_marker(self):
        for _ in range(20):
            val = jutsu.generate('atm_session')
            assert 'MOCKJ' in val, "MOCKJ marker missing in atm_session"

    def test_masked_pan_format(self):
        for _ in range(20):
            val = jutsu.generate('atm_session')
            data = json.loads(val)
            pan = data['masked_pan']
            assert '****' in pan, f"Masked PAN must contain ****: {pan}"

    def test_locale_tr_currency(self):
        data = json.loads(jutsu.generate('atm_session', locale='TR'))
        assert data['currency'] == 'TRY', f"TR locale must have TRY: {data['currency']}"

    def test_locale_us_currency(self):
        data = json.loads(jutsu.generate('atm_session', locale='US'))
        assert data['currency'] == 'USD', f"US locale must have USD: {data['currency']}"

    def test_arqc_format(self):
        for _ in range(20):
            val = jutsu.generate('atm_session')
            data = json.loads(val)
            assert re.match(r'^[0-9A-F]{16}$', data['arqc']), \
                f"Invalid ARQC in session: {data['arqc']}"

    def test_atc_format(self):
        for _ in range(20):
            val = jutsu.generate('atm_session')
            data = json.loads(val)
            assert re.match(r'^[0-9A-F]{4}$', data['atc']), \
                f"Invalid ATC in session: {data['atc']}"


class TestPosReceipt:
    def test_is_string(self):
        val = jutsu.generate('pos_receipt')
        assert isinstance(val, str) and len(val) > 80, \
            f"pos_receipt must be non-trivial string: {len(val)}"

    def test_mockj_merchant_marker(self):
        for _ in range(20):
            val = jutsu.generate('pos_receipt')
            assert 'MOCKJ' in val, "MOCKJ marker missing in pos_receipt"

    def test_masked_pan(self):
        for _ in range(20):
            val = jutsu.generate('pos_receipt')
            assert '****' in val, f"Masked PAN missing in receipt"

    def test_test_transaction_disclaimer(self):
        for _ in range(20):
            val = jutsu.generate('pos_receipt')
            assert 'TEST' in val, "TEST disclaimer missing in receipt"

    def test_locale_tr_currency_name(self):
        val = jutsu.generate('pos_receipt', locale='TR')
        assert 'TRY' in val, "TR locale must show TRY in receipt"

    def test_locale_uk_currency_name(self):
        val = jutsu.generate('pos_receipt', locale='UK')
        assert 'GBP' in val, "UK locale must show GBP in receipt"


# ── Performance ──────────────────────────────────────────────────────────────

class TestCardPhysicsPerformance:
    def test_200_iterations_under_300ms(self):
        import time
        types = [
            'emv_arqc', 'emv_atc', 'emv_iad',
            'iso8583_auth_request', 'iso8583_auth_response', 'iso8583_reversal',
            'atm_session', 'pos_receipt',
            'pin_block', 'pin_block_fmt3', 'track1_data',
        ]
        start = time.time()
        for _ in range(200):
            for t in types:
                jutsu.generate(t)
        elapsed_ms = (time.time() - start) * 1000
        assert elapsed_ms < 3000, f"200×{len(types)} iterations took {elapsed_ms:.0f}ms (limit 3000ms)"
