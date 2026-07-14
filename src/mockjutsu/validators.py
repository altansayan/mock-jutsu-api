"""
Mock Jutsu — Input Validator
=============================
validate(type_name, value) → (is_valid, error_message)

Return values:
  (True,  None)   — value is valid for this type
  (False, str)    — value is invalid; str explains why
  (None,  None)   — no validator defined for this type (not an error)
"""

from .algorithms import (
    luhn_valid,
    iban_valid,
    tckn_valid,
    ykn_valid,
    vkn_valid,
    ssn_valid,
    nin_valid,
    bic_valid,
)


def _luhn(value: str, label: str):
    if not luhn_valid(value):
        return False, f"Invalid {label}: Luhn checksum failed"
    return True, None


def _check_tckn(value: str):
    if not tckn_valid(value):
        return False, "Invalid TCKN: must be 11 digits, not start with 0, and pass dual MOD-10"
    return True, None


def _check_iban(value: str):
    if not iban_valid(value):
        return False, "Invalid IBAN: ISO 13616 MOD-97 checksum failed"
    return True, None


def _check_vkn(value: str):
    if not vkn_valid(value):
        return False, "Invalid VKN: must be 10 digits and pass GİB checksum"
    return True, None


def _check_ssn(value: str):
    if not ssn_valid(value):
        return False, "Invalid SSN: expected AAA-GG-SSSS (area 001-899 excl. 000/666)"
    return True, None


def _check_nin(value: str):
    if not nin_valid(value):
        return False, "Invalid NIN: HMRC format XX 99 99 99 X with valid prefix"
    return True, None


def _check_bic(value: str):
    if not bic_valid(value):
        return False, "Invalid BIC/SWIFT: ISO 9362 format required (8 or 11 chars)"
    return True, None


_VALIDATORS = {
    # Turkish
    "tckn":     _check_tckn,
    "ykn":      lambda v: (True, None) if ykn_valid(v) else (False, "Invalid YKN: must start with 99, 11 digits, Luhn valid"),
    "vkn":      _check_vkn,
    "taxid":    _check_vkn,
    # Banking / Financial
    "iban":     _check_iban,
    "cardnum":  lambda v: _luhn(v, "card number"),
    "bic":      _check_bic,
    "swift":    _check_bic,
    # US
    "ssn":      _check_ssn,
    "ein":      lambda v: (True, None),   # format-only, no checksum
    # UK
    "nin":      _check_nin,
    # Telecom (Luhn)
    "imei":     lambda v: _luhn(v, "IMEI"),
    "iccid":    lambda v: _luhn(v, "ICCID"),
}


def validate(type_name: str, value: str):
    """Validate *value* for the given Mock Jutsu *type_name*.

    Returns:
        (True,  None)  — valid
        (False, str)   — invalid; str is a human-readable reason
        (None,  None)  — no validator registered for this type
    """
    fn = _VALIDATORS.get(type_name.lower().strip())
    if fn is None:
        return None, None
    return fn(str(value))
