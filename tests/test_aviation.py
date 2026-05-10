"""
Tests for God Mode #8 — Aviation & Maritime Mocks
Types: iata_ticket, imo_number, pnr_code

Standards referenced:
  IATA ETN — Electronic Ticket Number: 3-digit airline code + 9-digit serial + MOD-7 check digit (13 digits total)
  IMO number — International Maritime Organization: 7 digits, check = weighted sum MOD 10 (weights 7,6,5,4,3,2)
  PNR code — Passenger Name Record: 6 uppercase alphanumeric, GDS charset (no 0, 1, I, O)
"""

import re
import pytest
from mockjutsu.core import MockJutsuCore

jutsu = MockJutsuCore()


# ── IATA Ticket Number ────────────────────────────────────────────────────────

class TestIATATicket:
    def test_format_13_digits(self):
        val = jutsu.generate('iata_ticket')
        assert re.match(r'^\d{13}$', val), f"Expected 13-digit string, got: {val!r}"

    def test_airline_code_nonzero(self):
        for _ in range(20):
            val = jutsu.generate('iata_ticket')
            airline = int(val[:3])
            assert 1 <= airline <= 999, f"Airline code out of range: {airline}"

    def test_mod7_check_digit(self):
        for _ in range(50):
            val = jutsu.generate('iata_ticket')
            # digits 4–12 (index 3:12) = 9-digit serial, digit 13 (index 12) = check
            serial_9 = int(val[3:12])
            check = int(val[12])
            assert serial_9 % 7 == check, (
                f"MOD-7 check failed: serial={serial_9}, check={check}, expected={serial_9 % 7}"
            )

    def test_check_digit_range(self):
        for _ in range(30):
            val = jutsu.generate('iata_ticket')
            check = int(val[12])
            assert 0 <= check <= 6, f"MOD-7 check digit must be 0–6, got: {check}"

    def test_bulk_unique(self):
        results = jutsu.bulk('iata_ticket', 30)
        assert len(set(results)) > 1, "iata_ticket bulk should produce distinct values"

    def test_via_api_string(self):
        val = jutsu.generate('iata_ticket')
        assert isinstance(val, str)

    def test_no_error_prefix(self):
        val = jutsu.generate('iata_ticket')
        assert not val.startswith("ERROR")

    def test_serial_nonzero(self):
        for _ in range(20):
            val = jutsu.generate('iata_ticket')
            serial_9 = int(val[3:12])
            assert serial_9 > 0, "Serial number should be positive"


# ── IMO Number ────────────────────────────────────────────────────────────────

class TestIMONumber:
    def test_format(self):
        val = jutsu.generate('imo_number')
        assert re.match(r'^IMO \d{7}$', val), f"Expected 'IMO NNNNNNN', got: {val!r}"

    def test_prefix(self):
        val = jutsu.generate('imo_number')
        assert val.startswith('IMO ')

    def test_check_digit_mod10(self):
        weights = [7, 6, 5, 4, 3, 2]
        for _ in range(50):
            val = jutsu.generate('imo_number')
            digits = val[4:]  # 7-digit string after 'IMO '
            total = sum(int(digits[i]) * weights[i] for i in range(6))
            expected_check = total % 10
            actual_check = int(digits[6])
            assert actual_check == expected_check, (
                f"IMO check digit failed: {val}, sum={total}, expected={expected_check}"
            )

    def test_first_digit_nonzero(self):
        for _ in range(20):
            val = jutsu.generate('imo_number')
            digits = val[4:]
            assert int(digits[0]) != 0, f"First digit of IMO number must not be 0: {val}"

    def test_bulk_unique(self):
        results = jutsu.bulk('imo_number', 30)
        assert len(set(results)) > 1

    def test_via_api_string(self):
        val = jutsu.generate('imo_number')
        assert isinstance(val, str)

    def test_no_error_prefix(self):
        val = jutsu.generate('imo_number')
        assert not val.startswith("ERROR")

    def test_seven_digit_number(self):
        for _ in range(20):
            val = jutsu.generate('imo_number')
            numeric_part = val[4:]
            assert len(numeric_part) == 7
            assert numeric_part.isdigit()


# ── PNR Code ──────────────────────────────────────────────────────────────────

class TestPNRCode:
    _VALID_CHARS = set('ABCDEFGHJKLMNPQRSTUVWXYZ23456789')

    def test_length_6(self):
        val = jutsu.generate('pnr_code')
        assert len(val) == 6, f"PNR must be 6 characters, got: {val!r}"

    def test_uppercase_only(self):
        for _ in range(30):
            val = jutsu.generate('pnr_code')
            assert val == val.upper(), f"PNR must be uppercase: {val!r}"

    def test_no_ambiguous_chars(self):
        """GDS PNR codes exclude 0, 1, I, O to avoid visual confusion."""
        ambiguous = set('01IO')
        for _ in range(100):
            val = jutsu.generate('pnr_code')
            found = ambiguous & set(val)
            assert not found, f"PNR contains ambiguous chars {found}: {val!r}"

    def test_valid_charset(self):
        for _ in range(50):
            val = jutsu.generate('pnr_code')
            invalid = set(val) - self._VALID_CHARS
            assert not invalid, f"PNR contains invalid chars {invalid}: {val!r}"

    def test_no_special_chars(self):
        for _ in range(30):
            val = jutsu.generate('pnr_code')
            assert re.match(r'^[A-Z2-9]{6}$', val), f"Invalid PNR format: {val!r}"

    def test_bulk_unique(self):
        results = jutsu.bulk('pnr_code', 50)
        assert len(set(results)) > 10, "PNR bulk should produce many distinct values"

    def test_via_api_string(self):
        val = jutsu.generate('pnr_code')
        assert isinstance(val, str)

    def test_no_error_prefix(self):
        val = jutsu.generate('pnr_code')
        assert not val.startswith("ERROR")

    def test_entropy_not_constant(self):
        """PNR codes must not all be identical."""
        results = set(jutsu.bulk('pnr_code', 20))
        assert len(results) > 1
