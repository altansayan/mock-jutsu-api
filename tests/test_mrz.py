"""
Tests for God Mode #21 — MRZ (Machine Readable Zone) Generator
Types: mrz_td3, mrz_td1

ICAO Document 9303:
  mrz_td3 — Passport MRZ: 2 lines × 44 characters
  mrz_td1 — ID Card MRZ:  3 lines × 30 characters

Core invariants:
  - All characters in A-Z | 0-9 | '<' (filler)
  - Check digit algorithm: weights=[7,3,1] cyclic, char_val(0-9=0-9, A-Z=10-35, <<=0), sum % 10
  - TD3: doc_no check, dob check, expiry check, personal_no check, composite check
  - TD1: doc_no check, dob check, expiry check, composite check
  - Composite check digit covers specific fields per ICAO 9303 spec
"""

import json
import re
import pytest
from mockjutsu.core import MockJutsuCore

jutsu = MockJutsuCore()

_MRZ_CHARS = re.compile(r'^[A-Z0-9<]+$')
_COUNTRY_RE = re.compile(r'^[A-Z]{1,3}<*$')  # 3-char field, letters or <

_WEIGHTS = [7, 3, 1]

def _char_val(c: str) -> int:
    if c == '<':
        return 0
    if c.isdigit():
        return int(c)
    return ord(c) - ord('A') + 10

def _check_digit(s: str) -> int:
    """ICAO 9303 check digit over a string."""
    total = sum(_char_val(c) * _WEIGHTS[i % 3] for i, c in enumerate(s))
    return total % 10


# ── mrz_td3 (Passport 2 × 44) ────────────────────────────────────────────────

class TestMrzTd3:

    def test_no_error(self):
        assert not jutsu.generate('mrz_td3').startswith('ERROR')

    def test_returns_string(self):
        assert isinstance(jutsu.generate('mrz_td3'), str)

    def test_is_valid_json(self):
        json.loads(jutsu.generate('mrz_td3'))

    def test_is_dict(self):
        assert isinstance(json.loads(jutsu.generate('mrz_td3')), dict)

    def test_has_lines_field(self):
        data = json.loads(jutsu.generate('mrz_td3'))
        assert 'lines' in data

    def test_lines_is_list_of_2(self):
        data = json.loads(jutsu.generate('mrz_td3'))
        assert isinstance(data['lines'], list)
        assert len(data['lines']) == 2

    def test_each_line_is_44_chars(self):
        for _ in range(10):
            lines = json.loads(jutsu.generate('mrz_td3'))['lines']
            for line in lines:
                assert len(line) == 44, f"Expected 44 chars, got {len(line)}: {line}"

    def test_mrz_type_is_td3(self):
        assert json.loads(jutsu.generate('mrz_td3'))['mrz_type'] == 'TD3'

    def test_characters_valid(self):
        for _ in range(10):
            lines = json.loads(jutsu.generate('mrz_td3'))['lines']
            for line in lines:
                assert _MRZ_CHARS.match(line), f"Invalid MRZ chars in: {line}"

    def test_line1_starts_with_P(self):
        """TD3 line 1 position 0 must be 'P' (document type Passport)."""
        for _ in range(10):
            line1 = json.loads(jutsu.generate('mrz_td3'))['lines'][0]
            assert line1[0] == 'P', f"Line 1 must start with P: {line1}"

    def test_line1_has_name_separator(self):
        """Line 1 must contain '<<' separating surname and given names."""
        for _ in range(10):
            line1 = json.loads(jutsu.generate('mrz_td3'))['lines'][0]
            assert '<<' in line1, f"No '<<' in line 1: {line1}"

    def test_line1_country_code_3chars(self):
        """Line 1 positions 2-4: 3-char issuing state code (alpha or <)."""
        for _ in range(10):
            line1 = json.loads(jutsu.generate('mrz_td3'))['lines'][0]
            country = line1[2:5]
            assert country.replace('<', '').isalpha() or country == '<<<', \
                f"Invalid country code: {country}"

    def test_line2_doc_number_check_digit(self):
        """Line 2 position 9: check digit over positions 0-8 (document number)."""
        for _ in range(20):
            line2 = json.loads(jutsu.generate('mrz_td3'))['lines'][1]
            doc_no = line2[0:9]
            expected = _check_digit(doc_no)
            actual = int(line2[9])
            assert actual == expected, \
                f"Doc no check digit failed: {doc_no}+{actual} (expected {expected})"

    def test_line2_dob_check_digit(self):
        """Line 2 position 19: check digit over positions 13-18 (date of birth)."""
        for _ in range(20):
            line2 = json.loads(jutsu.generate('mrz_td3'))['lines'][1]
            dob = line2[13:19]
            expected = _check_digit(dob)
            actual = int(line2[19])
            assert actual == expected, \
                f"DOB check digit failed: {dob}+{actual} (expected {expected})"

    def test_line2_dob_is_valid_date(self):
        """DOB positions 13-18: YYMMDD format, MM 01-12, DD 01-31."""
        for _ in range(20):
            line2 = json.loads(jutsu.generate('mrz_td3'))['lines'][1]
            dob = line2[13:19]
            assert dob.isdigit(), f"DOB not digits: {dob}"
            mm = int(dob[2:4])
            dd = int(dob[4:6])
            assert 1 <= mm <= 12, f"Invalid DOB month: {mm}"
            assert 1 <= dd <= 31, f"Invalid DOB day: {dd}"

    def test_line2_sex_field(self):
        """Line 2 position 20: sex must be M, F, or <."""
        for _ in range(20):
            line2 = json.loads(jutsu.generate('mrz_td3'))['lines'][1]
            assert line2[20] in ('M', 'F', '<'), \
                f"Invalid sex field: {line2[20]}"

    def test_line2_expiry_check_digit(self):
        """Line 2 position 27: check digit over positions 21-26 (expiry date)."""
        for _ in range(20):
            line2 = json.loads(jutsu.generate('mrz_td3'))['lines'][1]
            expiry = line2[21:27]
            expected = _check_digit(expiry)
            actual = int(line2[27])
            assert actual == expected, \
                f"Expiry check digit failed: {expiry}+{actual} (expected {expected})"

    def test_line2_expiry_is_future(self):
        """Expiry YYMMDD at positions 21-26 should be in the future (YY >= 26)."""
        for _ in range(20):
            line2 = json.loads(jutsu.generate('mrz_td3'))['lines'][1]
            expiry = line2[21:27]
            assert expiry.isdigit(), f"Expiry not digits: {expiry}"
            yy = int(expiry[0:2])
            assert yy >= 26, f"Expiry year should be future: {expiry}"

    def test_line2_personal_number_check_digit(self):
        """Line 2 position 42: check digit over positions 28-41 (personal number)."""
        for _ in range(20):
            line2 = json.loads(jutsu.generate('mrz_td3'))['lines'][1]
            personal = line2[28:42]
            expected = _check_digit(personal)
            actual = int(line2[42])
            assert actual == expected, \
                f"Personal no check digit failed: {personal}+{actual} (expected {expected})"

    def test_line2_composite_check_digit(self):
        """Line 2 position 43: composite check over doc_no+check+dob+check+expiry+check+personal+check."""
        for _ in range(20):
            line2 = json.loads(jutsu.generate('mrz_td3'))['lines'][1]
            composite_input = line2[0:10] + line2[13:20] + line2[21:43]
            expected = _check_digit(composite_input)
            actual = int(line2[43])
            assert actual == expected, \
                f"Composite check digit failed for line2: {line2} (expected {expected})"

    def test_has_parsed_fields(self):
        """Result dict should include parsed field names for convenience."""
        data = json.loads(jutsu.generate('mrz_td3'))
        assert 'surname' in data
        assert 'given_names' in data
        assert 'nationality' in data

    def test_bulk_unique_lines(self):
        results = [json.loads(r)['lines'][1] for r in jutsu.bulk('mrz_td3', 5)]
        assert len(set(results)) == 5


# ── mrz_td1 (ID Card 3 × 30) ─────────────────────────────────────────────────

class TestMrzTd1:

    def test_no_error(self):
        assert not jutsu.generate('mrz_td1').startswith('ERROR')

    def test_returns_string(self):
        assert isinstance(jutsu.generate('mrz_td1'), str)

    def test_is_valid_json(self):
        json.loads(jutsu.generate('mrz_td1'))

    def test_is_dict(self):
        assert isinstance(json.loads(jutsu.generate('mrz_td1')), dict)

    def test_has_lines_field(self):
        assert 'lines' in json.loads(jutsu.generate('mrz_td1'))

    def test_lines_is_list_of_3(self):
        data = json.loads(jutsu.generate('mrz_td1'))
        assert isinstance(data['lines'], list)
        assert len(data['lines']) == 3

    def test_each_line_is_30_chars(self):
        for _ in range(10):
            lines = json.loads(jutsu.generate('mrz_td1'))['lines']
            for i, line in enumerate(lines):
                assert len(line) == 30, f"Line {i} expected 30 chars, got {len(line)}: {line}"

    def test_mrz_type_is_td1(self):
        assert json.loads(jutsu.generate('mrz_td1'))['mrz_type'] == 'TD1'

    def test_characters_valid(self):
        for _ in range(10):
            lines = json.loads(jutsu.generate('mrz_td1'))['lines']
            for line in lines:
                assert _MRZ_CHARS.match(line), f"Invalid MRZ chars: {line}"

    def test_line1_doc_type(self):
        """Line 1 position 0 must be 'I', 'A', or 'C' (ID card types)."""
        for _ in range(20):
            line1 = json.loads(jutsu.generate('mrz_td1'))['lines'][0]
            assert line1[0] in ('I', 'A', 'C'), f"Invalid TD1 doc type: {line1[0]}"

    def test_line1_doc_number_check_digit(self):
        """Line 1 position 14: check digit over positions 5-13 (document number)."""
        for _ in range(20):
            line1 = json.loads(jutsu.generate('mrz_td1'))['lines'][0]
            doc_no = line1[5:14]
            expected = _check_digit(doc_no)
            actual = int(line1[14])
            assert actual == expected, \
                f"TD1 doc no check digit failed: {doc_no}+{actual} (expected {expected})"

    def test_line2_dob_check_digit(self):
        """Line 2 position 6: check digit over positions 0-5 (date of birth)."""
        for _ in range(20):
            line2 = json.loads(jutsu.generate('mrz_td1'))['lines'][1]
            dob = line2[0:6]
            expected = _check_digit(dob)
            actual = int(line2[6])
            assert actual == expected, \
                f"TD1 DOB check digit failed: {dob}+{actual} (expected {expected})"

    def test_line2_sex_field(self):
        """Line 2 position 7: sex must be M, F, or <."""
        for _ in range(20):
            line2 = json.loads(jutsu.generate('mrz_td1'))['lines'][1]
            assert line2[7] in ('M', 'F', '<'), f"Invalid TD1 sex: {line2[7]}"

    def test_line2_expiry_check_digit(self):
        """Line 2 position 14: check digit over positions 8-13 (expiry date)."""
        for _ in range(20):
            line2 = json.loads(jutsu.generate('mrz_td1'))['lines'][1]
            expiry = line2[8:14]
            expected = _check_digit(expiry)
            actual = int(line2[14])
            assert actual == expected, \
                f"TD1 expiry check digit failed: {expiry}+{actual} (expected {expected})"

    def test_line2_composite_check_digit(self):
        """Line 2 position 29: ICAO 9303-5 composite — sex and nationality excluded."""
        for _ in range(20):
            lines = json.loads(jutsu.generate('mrz_td1'))['lines']
            line1, line2 = lines[0], lines[1]
            composite_input = line1[5:30] + line2[0:7] + line2[8:15] + line2[18:29]
            expected = _check_digit(composite_input)
            actual = int(line2[29])
            assert actual == expected, \
                f"TD1 composite check digit failed (expected {expected})"

    def test_line3_has_name_separator(self):
        """Line 3 contains '<<' between surname and given names."""
        for _ in range(10):
            line3 = json.loads(jutsu.generate('mrz_td1'))['lines'][2]
            assert '<<' in line3, f"No '<<' in TD1 line 3: {line3}"

    def test_has_parsed_fields(self):
        data = json.loads(jutsu.generate('mrz_td1'))
        assert 'surname' in data
        assert 'given_names' in data
        assert 'nationality' in data

    def test_bulk_unique_lines(self):
        results = [json.loads(r)['lines'][0] for r in jutsu.bulk('mrz_td1', 5)]
        assert len(set(results)) == 5
