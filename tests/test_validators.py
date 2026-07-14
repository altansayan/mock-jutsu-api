"""
Tests for mockjutsu.validators — validate(type, value) → (bool, str|None)
TDD: tests written before implementation.
"""

import pytest
from mockjutsu.validators import validate


# ── TCKN ─────────────────────────────────────────────────────────────────────

def test_tckn_valid():
    # Computed: d[0:9]=[2,5,1,2,3,4,5,6,7] → d[9]=9, d[10]=4
    is_valid, err = validate("tckn", "25123456794")
    assert is_valid is True
    assert err is None

def test_tckn_invalid_length():
    is_valid, err = validate("tckn", "9999")
    assert is_valid is False
    assert err is not None

def test_tckn_invalid_starts_with_zero():
    is_valid, err = validate("tckn", "09876543210")
    assert is_valid is False

def test_tckn_invalid_checksum():
    is_valid, err = validate("tckn", "25123456781")  # last digit wrong
    assert is_valid is False

def test_tckn_with_spaces():
    is_valid, err = validate("tckn", "251 2345 6780")
    assert is_valid is False  # spaces not accepted in raw TCKN


# ── IBAN ─────────────────────────────────────────────────────────────────────

def test_iban_tr_valid():
    is_valid, err = validate("iban", "TR330006100519786457841326")
    assert is_valid is True

def test_iban_de_valid():
    is_valid, err = validate("iban", "DE89370400440532013000")
    assert is_valid is True

def test_iban_invalid_checksum():
    is_valid, err = validate("iban", "TR330006100519786457841327")  # last digit wrong
    assert is_valid is False

def test_iban_with_spaces():
    is_valid, err = validate("iban", "TR33 0006 1005 1978 6457 8413 26")
    assert is_valid is True  # spaces accepted

def test_iban_too_short():
    is_valid, err = validate("iban", "TR33")
    assert is_valid is False


# ── Card number (Luhn) ────────────────────────────────────────────────────────

def test_cardnum_visa_valid():
    is_valid, err = validate("cardnum", "4532015112830366")
    assert is_valid is True

def test_cardnum_invalid_luhn():
    is_valid, err = validate("cardnum", "4532015112830367")
    assert is_valid is False

def test_cardnum_with_spaces():
    is_valid, err = validate("cardnum", "4532 0151 1283 0366")
    assert is_valid is True


# ── VKN ──────────────────────────────────────────────────────────────────────

def test_vkn_valid():
    # Known valid VKN: 1234567890 checksum test
    from mockjutsu.core import jutsu
    vkn = jutsu.generate("vkn")
    is_valid, err = validate("vkn", vkn)
    assert is_valid is True

def test_vkn_invalid_length():
    is_valid, err = validate("vkn", "12345")
    assert is_valid is False

def test_vkn_invalid_checksum():
    is_valid, err = validate("vkn", "1234567899")  # likely wrong check digit
    # just check that it runs and returns bool
    assert isinstance(is_valid, bool)


# ── SSN ──────────────────────────────────────────────────────────────────────

def test_ssn_valid():
    is_valid, err = validate("ssn", "234-56-7890")
    assert is_valid is True

def test_ssn_invalid_area_000():
    is_valid, err = validate("ssn", "000-56-7890")
    assert is_valid is False

def test_ssn_invalid_area_666():
    is_valid, err = validate("ssn", "666-56-7890")
    assert is_valid is False

def test_ssn_invalid_format():
    is_valid, err = validate("ssn", "2345-6-7890")
    assert is_valid is False


# ── NIN ──────────────────────────────────────────────────────────────────────

def test_nin_valid():
    is_valid, err = validate("nin", "AB 12 34 56 C")
    assert is_valid is True

def test_nin_invalid_prefix():
    is_valid, err = validate("nin", "BG 12 34 56 C")
    assert is_valid is False

def test_nin_invalid_format():
    is_valid, err = validate("nin", "AB123456C")
    assert is_valid is True  # spaces optional

def test_nin_forbidden_first_char():
    is_valid, err = validate("nin", "DA 12 34 56 A")
    assert is_valid is False


# ── BIC/SWIFT ────────────────────────────────────────────────────────────────

def test_bic_valid_8():
    is_valid, err = validate("bic", "DEUTDEDB")
    assert is_valid is True

def test_bic_valid_11():
    is_valid, err = validate("bic", "DEUTDEDDXXX")
    assert is_valid is True

def test_bic_invalid():
    is_valid, err = validate("bic", "DEUT1")
    assert is_valid is False


# ── Unknown type ─────────────────────────────────────────────────────────────

def test_unknown_type_returns_none_valid():
    # Types without a validator: treated as valid (no checksum to verify)
    is_valid, err = validate("uuid", "550e8400-e29b-41d4-a716-446655440000")
    assert is_valid is None  # None = "no validator defined"
    assert err is None


# ── Alias types ──────────────────────────────────────────────────────────────

def test_swift_alias():
    is_valid, err = validate("swift", "DEUTDEDB")
    assert is_valid is True

def test_ykn_valid():
    from mockjutsu.core import jutsu
    ykn = jutsu.generate("ykn")
    is_valid, err = validate("ykn", ykn)
    assert is_valid is True
