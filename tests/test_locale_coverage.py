"""
Locale Coverage Tests — Faz 3 / Faz 4
=======================================
Verifies that locale-aware generators produce structurally correct output
for all 6 supported locales (TR, US, UK, DE, FR, RU).

Run:
    pytest tests/test_locale_coverage.py -v
"""
from __future__ import annotations

import json
import re

import pytest

from mockjutsu.core import MockJutsuCore

jutsu = MockJutsuCore()
LOCALES = ["TR", "US", "UK", "DE", "FR", "RU"]
N = 30  # samples per locale


def _gen(type_name, locale, n=N):
    return [jutsu.generate(type_name, locale=locale) for _ in range(n)]


def _assert_locale_all(name, locale, results):
    fails = [i for i, ok in enumerate(results) if not ok]
    assert not fails, (
        f"{name}[{locale}]: {len(fails)}/{len(results)} samples failed. "
        f"First fail index: {fails[0]}"
    )


# ─── IBAN prefix per locale ──────────────────────────────────────────────────


class TestIbanLocale:

    _EXPECTED_PREFIX = {
        "TR": "TR", "DE": "DE", "UK": "GB", "FR": "FR",
        "US": "RT:",  # US uses ABA routing, not IBAN
        "RU": "BIK:", # RU uses BIK format
    }

    def test_iban_prefix_all_locales(self):
        for locale in LOCALES:
            expected = self._EXPECTED_PREFIX[locale]
            results = []
            for v in _gen("iban", locale):
                results.append(v.startswith(expected))
            _assert_locale_all("iban prefix", locale, results)


# ─── IBAN / bankaccount length sanity ────────────────────────────────────────


class TestBankAccountLocale:

    _MIN_LEN = {"TR": 26, "DE": 22, "UK": 22, "FR": 27, "US": 10, "RU": 10}

    def test_bankaccount_length_all_locales(self):
        for locale in LOCALES:
            min_len = self._MIN_LEN[locale]
            results = []
            for v in _gen("bankaccount", locale):
                results.append(len(v) >= min_len)
            _assert_locale_all("bankaccount length", locale, results)


# ─── EMV QR country code ISO 3166-1 ─────────────────────────────────────────


class TestEmvQrLocale:

    _EXPECTED_CC = {
        "TR": "TR", "DE": "DE", "FR": "FR",
        "US": "US", "UK": "GB", "RU": "RU",
    }

    @pytest.mark.parametrize("qr_type", ["emv_qr_p2p", "emv_qr_atm", "emv_qr_pos"])
    def test_emv_qr_country_code_per_locale(self, qr_type):
        for locale in LOCALES:
            expected_cc = self._EXPECTED_CC[locale]
            results = []
            for v in _gen(qr_type, locale):
                m = re.search(r'5802([A-Z]{2})', v)
                results.append(m is not None and m.group(1) == expected_cc)
            _assert_locale_all(f"{qr_type} p58", locale, results)

    @pytest.mark.parametrize("qr_type", ["emv_qr_p2p", "emv_qr_atm", "emv_qr_pos"])
    def test_emv_qr_currency_code_per_locale(self, qr_type):
        _EXPECTED_CURR = {
            "TR": "949", "DE": "978", "FR": "978",
            "US": "840", "UK": "826", "RU": "643",
        }
        for locale in LOCALES:
            expected_curr = _EXPECTED_CURR[locale]
            results = []
            for v in _gen(qr_type, locale):
                results.append(f"5303{expected_curr}" in v)
            _assert_locale_all(f"{qr_type} p53 currency", locale, results)

    @pytest.mark.parametrize("qr_type", ["emv_qr_p2p", "emv_qr_atm", "emv_qr_pos"])
    def test_emv_qr_crc_trailer_per_locale(self, qr_type):
        for locale in LOCALES:
            results = []
            for v in _gen(qr_type, locale):
                results.append(bool(re.search(r'6304[0-9A-F]{4}$', v)))
            _assert_locale_all(f"{qr_type} CRC trailer", locale, results)


# ─── SEPA QR — SEPA-zone IBAN regardless of input locale ────────────────────


class TestSepaQrLocale:

    _SEPA_PREFIXES = ("GB", "DE", "FR")
    _NON_SEPA_PREFIXES = ("TR", "US", "RU")

    def test_sepa_qr_always_sepa_zone(self):
        for locale in LOCALES:
            results = []
            for v in _gen("sepa_qr", locale):
                try:
                    lines = v.strip().split("\n")
                    iban_line = lines[6]
                    ok = (
                        any(iban_line.startswith(p) for p in self._SEPA_PREFIXES) and
                        not any(iban_line.startswith(p) for p in self._NON_SEPA_PREFIXES)
                    )
                    results.append(ok)
                except Exception:
                    results.append(False)
            _assert_locale_all("sepa_qr SEPA IBAN", locale, results)

    def test_sepa_qr_header_all_locales(self):
        for locale in LOCALES:
            results = []
            for v in _gen("sepa_qr", locale):
                try:
                    lines = v.strip().split("\n")
                    results.append(
                        lines[0] == "BCD" and lines[1] == "002" and lines[3] == "SCT"
                    )
                except Exception:
                    results.append(False)
            _assert_locale_all("sepa_qr EPC header", locale, results)


# ─── ATM Session — currency and expiry per locale ────────────────────────────


class TestAtmSessionLocale:

    _EXPECTED_CURRENCY = {
        "TR": "TRY", "DE": "EUR", "FR": "EUR",
        "UK": "GBP", "US": "USD", "RU": "RUB",
    }

    def test_atm_session_currency_per_locale(self):
        for locale in LOCALES:
            expected_curr = self._EXPECTED_CURRENCY[locale]
            results = []
            for v in _gen("atm_session", locale):
                try:
                    obj = json.loads(v)
                    results.append(obj.get("currency") == expected_curr)
                except Exception:
                    results.append(False)
            _assert_locale_all("atm_session currency", locale, results)

    def test_atm_session_expiry_mmyy_all_locales(self):
        for locale in LOCALES:
            results = []
            for v in _gen("atm_session", locale):
                try:
                    obj = json.loads(v)
                    expiry = obj["expiry"]
                    m = re.match(r'^(0[1-9]|1[0-2])/\d{2}$', expiry)
                    results.append(m is not None)
                except Exception:
                    results.append(False)
            _assert_locale_all("atm_session expiry MM/YY", locale, results)

    def test_atm_session_mockj_all_locales(self):
        for locale in LOCALES:
            results = []
            for v in _gen("atm_session", locale):
                try:
                    obj = json.loads(v)
                    results.append(
                        "MOCKJ" in obj.get("session_id", "") and
                        "MOCKJ" in obj.get("auth_code", "")
                    )
                except Exception:
                    results.append(False)
            _assert_locale_all("atm_session MOCKJ", locale, results)


# ─── POS Receipt — MOCKJ marker all locales ──────────────────────────────────


class TestPosReceiptLocale:

    def test_pos_receipt_mockj_all_locales(self):
        for locale in LOCALES:
            results = []
            for v in _gen("pos_receipt", locale):
                results.append("MOCKJ" in v)
            _assert_locale_all("pos_receipt MOCKJ", locale, results)

    def test_pos_receipt_width_all_locales(self):
        for locale in LOCALES:
            results = []
            for v in _gen("pos_receipt", locale):
                try:
                    lines = v.split("\n")
                    results.append(all(len(ln) <= 40 for ln in lines if ln))
                except Exception:
                    results.append(False)
            _assert_locale_all("pos_receipt width<=40", locale, results)


# ─── Issuer — locale-specific names ──────────────────────────────────────────


class TestIssuerLocale:

    def test_issuer_non_empty_all_locales(self):
        for locale in LOCALES:
            results = []
            for v in _gen("issuer", locale):
                results.append(isinstance(v, str) and len(v) > 0)
            _assert_locale_all("issuer non-empty", locale, results)


# ─── ISO 8583 messages — locale currency ─────────────────────────────────────


class TestIso8583Locale:

    _EXPECTED_DE049 = {
        "TR": "949", "DE": "978", "FR": "978",
        "UK": "826", "US": "840", "RU": "643",
    }

    @pytest.mark.parametrize("msg_type", [
        "iso8583_auth_request", "iso8583_reversal"
    ])
    def test_iso8583_currency_per_locale(self, msg_type):
        for locale in LOCALES:
            expected = self._EXPECTED_DE049[locale]
            results = []
            for v in _gen(msg_type, locale):
                results.append(f"DE049:{expected}" in v)
            _assert_locale_all(f"{msg_type} DE049", locale, results)
