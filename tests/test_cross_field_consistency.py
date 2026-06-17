"""
Cross-Field Consistency Tests — Adım 4
========================================
Verifies that related fields generated together are mutually consistent.
No external libraries required — stdlib only.

Run:
    pytest tests/test_cross_field_consistency.py -v
"""
from __future__ import annotations

import json
import re

import pytest

from mockjutsu.core import MockJutsuCore

jutsu = MockJutsuCore()
LOCALES = ["TR", "US", "UK", "DE", "FR", "RU"]
N = 30


# ─── profile() cross-field consistency ───────────────────────────────────────


class TestProfileConsistency:

    _IBAN_PREFIX = {
        "TR": "TR", "DE": "DE", "UK": "GB", "FR": "FR",
        "US": "RT:",  # ABA routing
        "RU": "BIK:", # BIK format
    }

    def test_profile_iban_matches_locale(self):
        """profile()['iban'] prefix must match the requested locale."""
        for locale in LOCALES:
            expected_prefix = self._IBAN_PREFIX[locale]
            for _ in range(N):
                p = jutsu.profile(locale=locale)
                assert p["iban"].startswith(expected_prefix), (
                    f"locale={locale}: iban={p['iban']!r} should start with {expected_prefix!r}"
                )

    def test_profile_required_keys(self):
        """profile() must always return the same fixed set of keys."""
        required = {"id", "firstname", "lastname", "fullname", "gender",
                    "birthdate", "nationalid", "phone", "email", "iban"}
        for locale in LOCALES:
            for _ in range(N):
                p = jutsu.profile(locale=locale)
                missing = required - set(p.keys())
                assert not missing, f"locale={locale}: missing keys {missing}"

    def test_profile_gender_values(self):
        """profile()['gender'] must be 'M' or 'F' — never empty or other."""
        for locale in LOCALES:
            for _ in range(N):
                p = jutsu.profile(locale=locale)
                assert p["gender"] in ("M", "F"), (
                    f"locale={locale}: unexpected gender={p['gender']!r}"
                )

    def test_profile_email_format(self):
        """profile()['email'] must contain '@' and a domain."""
        pattern = re.compile(r'^[^@]+@[^@]+\.[^@]+$')
        for locale in LOCALES:
            for _ in range(N):
                p = jutsu.profile(locale=locale)
                assert pattern.match(p["email"]), (
                    f"locale={locale}: invalid email={p['email']!r}"
                )

    def test_profile_uuid_format(self):
        """profile()['id'] must be a valid UUID v4."""
        import uuid
        for locale in LOCALES:
            for _ in range(N):
                p = jutsu.profile(locale=locale)
                obj = uuid.UUID(p["id"])
                assert obj.version == 4, f"locale={locale}: id not UUID v4: {p['id']!r}"

    def test_profile_non_empty_strings(self):
        """profile() string fields must not be empty."""
        str_fields = ["firstname", "lastname", "fullname", "birthdate",
                      "nationalid", "phone", "email", "address"] if "address" in jutsu.profile() else \
                     ["firstname", "lastname", "fullname", "birthdate",
                      "nationalid", "phone", "email"]
        for locale in LOCALES:
            for _ in range(N):
                p = jutsu.profile(locale=locale)
                for field in str_fields:
                    if field in p:
                        assert p[field], (
                            f"locale={locale}: field '{field}' is empty"
                        )


# ─── company() cross-field consistency ───────────────────────────────────────


class TestCompanyConsistency:

    def test_company_required_keys(self):
        """company() must return the fixed key set."""
        required = {"id", "name", "employer_id", "tax_id", "iban", "bic", "phone", "address"}
        for locale in LOCALES:
            for _ in range(N):
                c = jutsu.company(locale=locale)
                missing = required - set(c.keys())
                assert not missing, f"locale={locale}: missing keys {missing}"

    def test_company_non_empty_strings(self):
        for locale in LOCALES:
            for _ in range(N):
                c = jutsu.company(locale=locale)
                for k, v in c.items():
                    assert v, f"locale={locale}: field '{k}' is empty"


# ─── Card data cross-field consistency ───────────────────────────────────────


class TestCardConsistency:

    def test_expiry_month_in_range(self):
        """expirymonth must be 01-12."""
        for _ in range(N * 3):
            m = jutsu.generate("expirymonth")
            assert re.match(r'^(0[1-9]|1[0-2])$', str(m)), f"invalid expirymonth: {m!r}"

    def test_expiry_year_future(self):
        """expiryyear must be current year or later (2-digit)."""
        from datetime import datetime
        current_yy = datetime.now().year % 100
        for _ in range(N * 3):
            y = int(jutsu.generate("expiryyear"))
            assert y >= current_yy, f"expiryyear {y} is in the past (current={current_yy})"

    def test_expiry_combined_format(self):
        """expiry must be MM/YY format."""
        for _ in range(N * 3):
            v = jutsu.generate("expiry")
            assert re.match(r'^(0[1-9]|1[0-2])/\d{2}$', str(v)), f"invalid expiry: {v!r}"

    def test_cvv3_length(self):
        """cvv3 must be exactly 3 digits."""
        for _ in range(N * 3):
            v = str(jutsu.generate("cvv3"))
            assert re.match(r'^\d{3}$', v), f"invalid cvv3: {v!r}"

    def test_cvv4_length(self):
        """cvv4 must be exactly 4 digits (Amex CID)."""
        for _ in range(N * 3):
            v = str(jutsu.generate("cvv4"))
            assert re.match(r'^\d{4}$', v), f"invalid cvv4: {v!r}"

    def test_pin_length(self):
        """pin must be exactly 4 digits."""
        for _ in range(N * 3):
            v = str(jutsu.generate("pin"))
            assert re.match(r'^\d{4}$', v), f"invalid pin: {v!r}"

    def test_cardnum_luhn(self):
        """cardnum must pass the Luhn check (ISO/IEC 7812)."""
        def luhn_ok(number: str) -> bool:
            digits = [int(d) for d in number]
            total = 0
            for i, d in enumerate(reversed(digits)):
                if i % 2 == 1:
                    d *= 2
                    if d > 9:
                        d -= 9
                total += d
            return total % 10 == 0

        for network in ["visa", "mc", "amex", "troy", "jcb", "discover", "unionpay"]:
            for _ in range(N):
                v = str(jutsu.generate("cardnum", network=network))
                assert luhn_ok(v), f"network={network}: Luhn fail: {v}"


# ─── ATM / POS cross-field consistency ───────────────────────────────────────


class TestAtmPosConsistency:

    _EXPECTED_CURRENCY = {
        "TR": "TRY", "DE": "EUR", "FR": "EUR",
        "UK": "GBP", "US": "USD", "RU": "RUB",
    }

    def test_atm_session_fields_consistent(self):
        """atm_session: currency matches locale, expiry is MM/YY, MOCKJ in IDs."""
        for locale in LOCALES:
            expected_curr = self._EXPECTED_CURRENCY[locale]
            for _ in range(N):
                obj = json.loads(jutsu.generate("atm_session", locale=locale))
                assert obj["currency"] == expected_curr, (
                    f"locale={locale}: expected currency {expected_curr}, got {obj['currency']}"
                )
                assert re.match(r'^(0[1-9]|1[0-2])/\d{2}$', obj["expiry"]), (
                    f"locale={locale}: bad expiry format {obj['expiry']!r}"
                )
                assert "MOCKJ" in obj["session_id"]
                assert "MOCKJ" in obj["auth_code"]

    def test_pos_receipt_amount_positive(self):
        """pos_receipt amount must be a positive number."""
        for locale in LOCALES:
            for _ in range(N):
                receipt = jutsu.generate("pos_receipt", locale=locale)
                m = re.search(r'Amount:\s+\S+\s+([\d.]+)', receipt)
                if m:
                    assert float(m.group(1)) > 0, f"locale={locale}: non-positive amount"


# ─── EMV QR cross-field consistency ──────────────────────────────────────────


class TestEmvQrConsistency:

    _EXPECTED_CURR = {
        "TR": "949", "DE": "978", "FR": "978",
        "US": "840", "UK": "826", "RU": "643",
    }
    _EXPECTED_CC = {
        "TR": "TR", "DE": "DE", "FR": "FR",
        "US": "US", "UK": "GB", "RU": "RU",
    }

    @pytest.mark.parametrize("qr_type", ["emv_qr_p2p", "emv_qr_atm", "emv_qr_pos"])
    def test_emv_qr_currency_and_country_consistent(self, qr_type):
        """EMV QR currency code (5303) and country code (5802) must both match locale."""
        for locale in LOCALES:
            expected_curr = self._EXPECTED_CURR[locale]
            expected_cc = self._EXPECTED_CC[locale]
            for _ in range(N):
                v = jutsu.generate(qr_type, locale=locale)
                assert f"5303{expected_curr}" in v, (
                    f"{qr_type}[{locale}]: currency {expected_curr} not found in: {v[:80]}"
                )
                m = re.search(r'5802([A-Z]{2})', v)
                assert m and m.group(1) == expected_cc, (
                    f"{qr_type}[{locale}]: country_code mismatch, got {m.group(1) if m else None}"
                )
