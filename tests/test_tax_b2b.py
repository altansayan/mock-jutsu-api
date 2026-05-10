"""
Tests for God Mode #9 — Global Vergi ve B2B Mocks
Types: creditor_ref, vat_number

Standards referenced:
  ISO 11649    — Creditor Reference: RF + 2-digit MOD-97 check + 3-21 alphanumeric chars
  EU VIES      — VAT Information Exchange System: country-specific formats (TR/DE/FR/UK/US/RU)
  HMRC / BZSt  — UK/DE VAT format rules
"""

import re
import pytest
from mockjutsu.core import MockJutsuCore

jutsu = MockJutsuCore()


# ── ISO 11649 Creditor Reference ──────────────────────────────────────────────

def _creditor_ref_checksum_valid(val: str) -> bool:
    """Verify MOD-97 check: move first 4 chars to end, convert, mod 97 == 1."""
    rearranged = val[4:] + val[:4]  # reference + RF + check_digits
    numeric = ''.join(str(ord(c) - 55) if c.isalpha() else c for c in rearranged)
    return int(numeric) % 97 == 1


class TestCreditorRef:
    def test_starts_with_rf(self):
        val = jutsu.generate('creditor_ref')
        assert val.startswith('RF'), f"Must start with 'RF', got: {val!r}"

    def test_check_digits_two_digits(self):
        val = jutsu.generate('creditor_ref')
        check = val[2:4]
        assert check.isdigit() and len(check) == 2, f"Check digits invalid: {val!r}"

    def test_total_length_range(self):
        for _ in range(30):
            val = jutsu.generate('creditor_ref')
            # RF(2) + check(2) + ref(3-21) = 7-25 chars
            assert 7 <= len(val) <= 25, f"Length out of range: {len(val)} — {val!r}"

    def test_reference_part_alphanumeric(self):
        for _ in range(30):
            val = jutsu.generate('creditor_ref')
            ref_part = val[4:]  # after RF + 2 check digits
            assert re.match(r'^[A-Z0-9]+$', ref_part), f"Ref part invalid: {ref_part!r}"

    def test_mod97_check_valid(self):
        """ISO 11649: rearranged MOD 97 must equal 1 (same invariant as IBAN)."""
        for _ in range(50):
            val = jutsu.generate('creditor_ref')
            assert _creditor_ref_checksum_valid(val), f"MOD-97 check failed for: {val!r}"

    def test_check_digit_not_01_or_00(self):
        """Check digits 00 and 01 are reserved/invalid in ISO 11649."""
        for _ in range(50):
            val = jutsu.generate('creditor_ref')
            check = val[2:4]
            assert check not in ('00', '01'), f"Invalid check digits {check!r} in: {val!r}"

    def test_bulk_unique(self):
        results = jutsu.bulk('creditor_ref', 30)
        assert len(set(results)) > 1

    def test_no_error_prefix(self):
        val = jutsu.generate('creditor_ref')
        assert not val.startswith('ERROR')

    def test_via_api_string(self):
        val = jutsu.generate('creditor_ref')
        assert isinstance(val, str)


# ── Global VAT Numbers ────────────────────────────────────────────────────────

class TestVatNumber:
    def test_tr_format(self):
        val = jutsu.generate('vat_number', locale='TR')
        assert re.match(r'^TR\d{10}$', val), f"TR VAT format invalid: {val!r}"

    def test_de_format(self):
        val = jutsu.generate('vat_number', locale='DE')
        assert re.match(r'^DE\d{9}$', val), f"DE VAT format invalid: {val!r}"

    def test_fr_format(self):
        """FR VAT: FR + 2 alphanumeric key chars + 9-digit SIREN."""
        val = jutsu.generate('vat_number', locale='FR')
        assert re.match(r'^FR[A-HJ-NP-Z0-9]{2}\d{9}$', val), f"FR VAT format invalid: {val!r}"

    def test_uk_format(self):
        val = jutsu.generate('vat_number', locale='UK')
        assert re.match(r'^GB\d{9}$', val), f"UK VAT format invalid: {val!r}"

    def test_us_format(self):
        """US EIN-style tax ID: XX-XXXXXXX format."""
        val = jutsu.generate('vat_number', locale='US')
        assert re.match(r'^US\d{2}-\d{7}$', val), f"US tax ID format invalid: {val!r}"

    def test_ru_format(self):
        val = jutsu.generate('vat_number', locale='RU')
        assert re.match(r'^RU\d{10}$', val), f"RU VAT format invalid: {val!r}"

    def test_default_locale_returns_string(self):
        val = jutsu.generate('vat_number')
        assert isinstance(val, str)
        assert not val.startswith('ERROR')

    def test_bulk_unique_per_locale(self):
        for locale in ('TR', 'DE', 'FR', 'UK', 'US', 'RU'):
            results = jutsu.bulk('vat_number', 10, locale=locale)
            assert len(set(results)) > 1, f"vat_number bulk not unique for locale {locale}"

    def test_no_error_prefix(self):
        for locale in ('TR', 'DE', 'FR', 'UK', 'US', 'RU'):
            val = jutsu.generate('vat_number', locale=locale)
            assert not val.startswith('ERROR'), f"locale={locale}: {val!r}"

    def test_fr_key_excludes_io(self):
        """French VAT key chars exclude I and O to avoid confusion."""
        for _ in range(100):
            val = jutsu.generate('vat_number', locale='FR')
            key = val[2:4]
            assert 'I' not in key and 'O' not in key, f"FR VAT key contains I or O: {val!r}"
