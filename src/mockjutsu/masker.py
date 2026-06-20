"""
Mock Jutsu — Data Masking Engine
=================================
apply_mask(type_name, value) returns a privacy-safe display version of any
generated value, following the regulation rules defined in regulations.py.

Rules by category:
  PCI DSS SAD (never_store=True) → all chars replaced with *
  PCI DSS PAN (cardnum)          → first 6 + last 4 (BIN + last4)
  KVKK / GDPR national IDs       → first 2 + last 2
  SSN (US)                       → ***-**-last4
  UK NIN                         → AB ** ** ** C
  NHS Number                     → first3 *** ***last1
  Aadhaar                        → XXXX XXXX last4
  IBAN                           → country+check (4) + **** + last4
  Email                          → first2***@domain
  Phone / MSISDN                 → country_code + *** *** + last2
  Birthdate                      → YYYY-**-**
  Names                          → First char + *** per word
  Credit card CVV / PIN          → *** (SAD — never display)
  Health numeric (bmi/height)    → ** units
  Types with no mask rule        → returned unchanged
"""

import re
from .regulations import REGULATION_TAGS, must_never_store, mask_format


# ── Helpers ───────────────────────────────────────────────────────────────────

def _digits_only(s: str) -> str:
    return re.sub(r"\D", "", s)


def _mask_digits(s: str, show_first: int, show_last: int, char: str = "*") -> str:
    """Mask middle digits of a digit-only string."""
    d = _digits_only(s)
    n = len(d)
    if n <= show_first + show_last:
        return char * n
    return d[:show_first] + char * (n - show_first - show_last) + d[-show_last:]


def _reformat_like(original: str, masked_digits: str) -> str:
    """Re-insert non-digit characters from original into masked_digits string."""
    result = []
    digit_iter = iter(masked_digits)
    for ch in original:
        if ch.isdigit():
            result.append(next(digit_iter, "*"))
        else:
            result.append(ch)
    return "".join(result)


def _mask_alphanum(s: str, show_first: int, show_last: int, char: str = "*") -> str:
    """Mask middle alphanumeric chars, keep structural separators in place."""
    alphanum = [c for c in s if c.isalnum()]
    n = len(alphanum)
    if n <= show_first + show_last:
        return char * n
    masked = alphanum[:show_first] + [char] * (n - show_first - show_last) + alphanum[-show_last:]
    result = []
    an_iter = iter(masked)
    for ch in s:
        if ch.isalnum():
            result.append(next(an_iter, char))
        else:
            result.append(ch)
    return "".join(result)


# ── Type-specific maskers ─────────────────────────────────────────────────────

def _mask_tckn(v: str) -> str:
    # KVKK Rehber: 25*******10  (first 2 + last 2)
    d = _digits_only(v)
    if len(d) != 11:
        return _mask_digits(d, 2, 2)
    return d[:2] + "*" * 7 + d[-2:]


def _mask_ssn(v: str) -> str:
    # IRS: ***-**-last4
    d = _digits_only(v)
    if len(d) != 9:
        d = d.ljust(9, "*")
    return f"***-**-{d[-4:]}"


def _mask_ein(v: str) -> str:
    # EIN: **-***last4
    d = _digits_only(v)
    last4 = d[-4:] if len(d) >= 4 else d
    prefix = "*" * max(0, len(d) - 4)
    return f"**-{prefix}{last4}"[0:10]  # keep format length


def _mask_nin(v: str) -> str:
    # UK NIN format: AB 12 34 56 C → AB ** ** ** C
    s = v.replace(" ", "").upper()
    if len(s) != 9:
        return v
    return f"{s[0]}{s[1]} ** ** ** {s[8]}"


def _mask_utr(v: str) -> str:
    # UTR 10 digits: show first 5, mask last 5
    d = _digits_only(v)
    return d[:5] + "*" * max(0, len(d) - 5)


def _mask_nhs(v: str) -> str:
    # NHS: 943 476 5919 → 943 *** ***9  (first group + last digit)
    d = _digits_only(v)
    if len(d) != 10:
        return _mask_digits(d, 3, 1)
    return f"{d[:3]} *** ***{d[-1]}"


def _mask_cardnum(v: str) -> str:
    # PCI DSS 4.0.1 Req 3.4.1: first 6 (BIN) + last 4
    d = _digits_only(v)
    n = len(d)
    if n < 13:
        return "*" * n
    bin6   = d[:6]
    last4  = d[-4:]
    middle = "*" * (n - 10)
    raw    = bin6 + middle + last4
    # Reformat as groups of 4 (standard card display)
    groups = [raw[i:i+4] for i in range(0, len(raw), 4)]
    return " ".join(groups)


def _mask_cvv(length: int) -> str:
    return "*" * length


def _mask_iban(v: str) -> str:
    # Show country code (2) + check digits (2) = 4 chars, then mask, last 4
    s = v.replace(" ", "").upper()
    n = len(s)
    if n < 8:
        return "*" * n
    visible_prefix = s[:4]
    visible_suffix = s[-4:]
    middle         = "*" * (n - 8)
    raw = visible_prefix + middle + visible_suffix
    # Reformat with spaces every 4 chars
    groups = [raw[i:i+4] for i in range(0, len(raw), 4)]
    return " ".join(groups)


def _mask_email(v: str) -> str:
    # al***@gmail.com — first 2 of local part visible
    if "@" not in v:
        return v[:2] + "***"
    local, domain = v.split("@", 1)
    visible = local[:2] if len(local) >= 2 else local[:1]
    return f"{visible}***@{domain}"


def _mask_phone(v: str) -> str:
    # +905325551234 → +90 *** *** ** 34
    # Always treat first 3 chars as country prefix (+XX) for E.164 numbers
    if v.startswith("+") and len(v) >= 4:
        # Single-digit country codes: +1 (US/CA), +7 (RU)
        if len(v) >= 2 and v[1] in "17":
            prefix = v[:2]
            rest   = _digits_only(v[2:])
        else:
            prefix = v[:3]       # "+90", "+44", "+49" etc. (2-digit CC)
            rest   = _digits_only(v[3:])
        last2 = rest[-2:] if len(rest) >= 2 else rest
        return f"{prefix} *** *** ** {last2}"
    d     = _digits_only(v)
    last2 = d[-2:] if len(d) >= 2 else d
    return f"*** *** ** {last2}"


def _mask_birthdate(v: str) -> str:
    # 1990-05-14 → 1990-**-**
    m = re.match(r"(\d{4})([-/])(\d{2})([-/])(\d{2})", v)
    if m:
        return f"{m.group(1)}{m.group(2)}**{m.group(4)}**"
    return v[:4] + "-**-**" if len(v) >= 4 else "****-**-**"


def _mask_name(v: str) -> str:
    # Emre Kaya → E*** K***
    words = v.split()
    masked = []
    for w in words:
        if w:
            masked.append(w[0] + "***")
    return " ".join(masked) if masked else v


def _mask_passport(v: str) -> str:
    # P1234567 → P1****67  (first 2 + last 2)
    s = v.strip()
    if len(s) <= 4:
        return "*" * len(s)
    return s[:2] + "*" * (len(s) - 4) + s[-2:]


def _mask_vkn(v: str) -> str:
    # Turkish VKN 10 digits: first 3 + last 3
    d = _digits_only(v)
    if len(d) <= 6:
        return "*" * len(d)
    return d[:3] + "*" * (len(d) - 6) + d[-3:]


def _mask_sgk(v: str) -> str:
    # 34-0012345-1.01-02 → 34-*******-1.01-02
    parts = v.split("-", 1)
    if len(parts) < 2:
        return v
    # Mask the middle number block
    return re.sub(r"(\d{2}-)(\d+)(-\d+\.\d+-\d+)", lambda m: m.group(1) + "*" * len(m.group(2)) + m.group(3), v)


def _mask_aadhaar(v: str) -> str:
    # UIDAI: XXXX XXXX last4
    d = _digits_only(v)
    if len(d) != 12:
        last4 = d[-4:] if len(d) >= 4 else d
        return f"XXXX XXXX {last4}"
    return f"XXXX XXXX {d[-4:]}"


def _mask_generic_id(v: str, show_first: int = 2, show_last: int = 2) -> str:
    """Generic: show first N and last N alphanumeric, mask middle."""
    return _mask_alphanum(v, show_first, show_last)


def _mask_pci_sad(v: str) -> str:
    """PCI SAD — replace all alphanumeric with *, keep structural chars."""
    return re.sub(r"[A-Za-z0-9]", "*", str(v))


def _mask_health_numeric(v: str) -> str:
    """Health numeric (bmi, height, weight): mask digits, keep units."""
    # 178 cm → *** cm | 22.5 → **.5 | 74 kg → ** kg
    return re.sub(r"\d", "*", str(v))


def _mask_iccid(v: str) -> str:
    # 19-20 digit ICCID: show first 6 (IIN) + last 4
    d = _digits_only(v)
    return _mask_digits(d, 6, 4)


def _mask_imsi(v: str) -> str:
    # 15 digit IMSI: show first 5 (MCC+MNC) + last 4
    d = _digits_only(v)
    return _mask_digits(d, 5, 4)


def _mask_imei(v: str) -> str:
    # 15 digit IMEI: show first 8 (TAC) + last 2
    d = _digits_only(v)
    raw = _mask_digits(d, 8, 2)
    return _reformat_like(v, raw)


def _mask_credit_score(v: str) -> str:
    # 720 → 7**
    s = str(v).strip()
    if not s:
        return v
    return s[0] + "*" * (len(s) - 1)


def _mask_balance(v: str) -> str:
    # 12450.75 → ****50.75 (last 2 integer digits visible)
    m = re.match(r"(-?)(\d+)(\.\d+)?", str(v))
    if not m:
        return v
    sign, intpart, dec = m.group(1), m.group(2), m.group(3) or ""
    visible_int = intpart[-2:] if len(intpart) > 2 else intpart
    masked_int  = "*" * (len(intpart) - len(visible_int)) + visible_int
    return f"{sign}{masked_int}{dec}"


def _mask_mac(v: str) -> str:
    # A4:C3:F0:3D:8E:21 → A4:C3:F0:**:**:**
    parts = v.split(":")
    if len(parts) == 6:
        return ":".join(parts[:3] + ["**", "**", "**"])
    return v


def _mask_plate(v: str) -> str:
    # 34 ABC 123 → 34 A** 123
    parts = v.split()
    if len(parts) >= 2:
        letters = parts[1]
        masked  = letters[0] + "*" * (len(letters) - 1)
        parts[1] = masked
    return " ".join(parts)


def _mask_vin(v: str) -> str:
    # WBA3A5C5XMD123456 → WBA3A5C5X****456  (first 9 WMI+VDS + last 3)
    if len(v) == 17:
        return v[:9] + "****" + v[-4:]
    return _mask_alphanum(v, 4, 4)


def _mask_pnr(v: str) -> str:
    # K7XR2B → K7****
    return v[:2] + "*" * (len(v) - 2) if len(v) > 2 else v


def _mask_iata_ticket(v: str) -> str:
    d = _digits_only(v)
    return _mask_digits(d, 3, 3)


def _mask_session_id(v: str) -> str:
    # UUID-like: 550e8400-e29b-41d4-a716-446655440000 → 550e***...
    parts = v.split("-")
    if len(parts) == 5:
        return parts[0] + "-****-****-****-" + parts[-1]
    return v[:8] + "***..."


def _mask_ip(v: str) -> str:
    # 192.168.1.42 → 192.168.*.*  (GDPR: last 2 octets masked)
    parts = v.split(".")
    if len(parts) == 4:
        return f"{parts[0]}.{parts[1]}.*.*"
    return v


def _mask_br_cpf(v: str) -> str:
    # 123.456.789-09 → 123.***.***-09
    d = _digits_only(v)
    return _mask_digits(d, 3, 2)


def _mask_cn_ric(v: str) -> str:
    # 110000198001011234 → 110000****1234  (area+year first6, last 4)
    d = _digits_only(v)
    return _mask_digits(d, 6, 4)


def _mask_kr_rrn(v: str) -> str:
    # 700101-1280009 → 700101-1*****
    m = re.match(r"(\d{6})-(\d)(\d+)", v)
    if m:
        return f"{m.group(1)}-{m.group(2)}{'*' * len(m.group(3))}"
    return _mask_generic_id(v, 6, 1)


def _mask_nl_bsn(v: str) -> str:
    d = _digits_only(v)
    return _mask_digits(d, 3, 2)


def _mask_se_personnummer(v: str) -> str:
    # 19700101-1234 → 19700101-****
    m = re.match(r"(\d{8})-(.+)", v)
    if m:
        return f"{m.group(1)}-****"
    return _mask_generic_id(v, 8, 0)


def _mask_dk_cpr(v: str) -> str:
    # 010170-1234 → 010170-****
    m = re.match(r"(\d{6})-(.+)", v)
    if m:
        return f"{m.group(1)}-****"
    return _mask_generic_id(v, 6, 0)


# ── Main dispatcher ───────────────────────────────────────────────────────────

_MASKERS = {
    # ── PCI SAD — full redact ──────────────────────────────────────────────
    "cvv3":          lambda v: _mask_cvv(3),
    "cvv4":          lambda v: _mask_cvv(4),
    "pin":           lambda v: _mask_cvv(4),
    "track1_data":   _mask_pci_sad,
    "track2_data":   _mask_pci_sad,
    "chip_data":     _mask_pci_sad,
    "pin_block":     _mask_pci_sad,
    "pin_block_fmt3": _mask_pci_sad,
    "3ds_cavv":      _mask_pci_sad,
    "password":      _mask_pci_sad,
    "password_hash": _mask_pci_sad,

    # ── Payment cards ──────────────────────────────────────────────────────
    "cardnum":       _mask_cardnum,
    "cardowner":     _mask_name,
    "expiry":        lambda v: "**/**",
    "expirymonth":   lambda v: "**",
    "expiryyear":    lambda v: "**",

    # ── Banking / Financial ────────────────────────────────────────────────
    "iban":          _mask_iban,
    "balance":       _mask_balance,
    "credit_score":  _mask_credit_score,

    # ── Turkish ID ─────────────────────────────────────────────────────────
    "tckn":          _mask_tckn,
    "tckn_masked":   lambda v: v,          # already masked
    "ykn":           _mask_tckn,           # same 11-digit format
    "vkn":           _mask_vkn,
    "sgk":           _mask_sgk,
    "mersis":        lambda v: _mask_generic_id(v, 4, 4),

    # ── US IDs ─────────────────────────────────────────────────────────────
    "ssn":           _mask_ssn,
    "ssn_masked":    lambda v: v,          # already masked
    "ein":           _mask_ein,
    "npi":           lambda v: _mask_digits(_digits_only(v), 5, 4),

    # ── UK IDs ─────────────────────────────────────────────────────────────
    "nin":           _mask_nin,
    "utr":           _mask_utr,
    "paye":          lambda v: _mask_alphanum(v, 4, 3),
    "crn":           lambda v: _mask_generic_id(v, 2, 2),
    "nhs_number":    _mask_nhs,
    "nhsnumber":     _mask_nhs,
    "sort_code":     lambda v: re.sub(r"\d{2}", "**", v),

    # ── German IDs ─────────────────────────────────────────────────────────
    "rvn":           lambda v: _mask_alphanum(v, 4, 4),
    "de_idnr":       lambda v: _mask_digits(_digits_only(v), 4, 4),
    "de_stnr":       lambda v: _mask_generic_id(v, 3, 2),

    # ── Russian IDs ────────────────────────────────────────────────────────
    "inn":           lambda v: _mask_digits(_digits_only(v), 3, 3),
    "inn_individual": lambda v: _mask_digits(_digits_only(v), 3, 3),
    "snils":         lambda v: _mask_generic_id(v, 3, 2),

    # ── Documents ─────────────────────────────────────────────────────────
    "passport":      _mask_passport,
    "license":       _mask_passport,
    "mrz_td3":       lambda v: re.sub(r"[A-Z0-9](?=[A-Z0-9]{3,})", "*", v),
    "mrz_td1":       lambda v: re.sub(r"[A-Z0-9](?=[A-Z0-9]{3,})", "*", v),

    # ── Demographics ───────────────────────────────────────────────────────
    "birthdate":     _mask_birthdate,
    "age":           lambda v: "**",
    "gender":        lambda v: v,
    "nationality":   lambda v: v,

    # ── Names ─────────────────────────────────────────────────────────────
    "firstname":     _mask_name,
    "lastname":      _mask_name,
    "fullname":      _mask_name,
    "patronymic":    _mask_name,

    # ── Contact ───────────────────────────────────────────────────────────
    "email":         _mask_email,
    "phone":         _mask_phone,
    "msisdn":        _mask_phone,
    "phone_local":   lambda v: "***" + v[-2:],
    "phone_area":    lambda v: v,
    "phone_country": lambda v: v,
    "address_full":  _mask_name,
    "address_street": _mask_name,
    "address_city":  lambda v: v,
    "postalcode":    lambda v: v[:2] + "***",
    "plate":         _mask_plate,

    # ── Telecom ───────────────────────────────────────────────────────────
    "imei":          _mask_imei,
    "imei2":         _mask_imei,
    "iccid":         _mask_iccid,
    "imsi":          _mask_imsi,

    # ── Health ─────────────────────────────────────────────────────────────
    "bloodtype":     lambda v: v,
    "blood_type":    lambda v: v,
    "icd10":         lambda v: re.sub(r"\d", "*", v),
    "bmi":           _mask_health_numeric,
    "height":        _mask_health_numeric,
    "weight":        _mask_health_numeric,
    "npi":           lambda v: _mask_digits(_digits_only(v), 5, 4),
    "hl7_message":   lambda v: re.sub(r"(?<=\|)[^\|]{4,}", "****", v),
    "fhir_patient":  lambda v: re.sub(r'"(family|given|text|value)":\s*"[^"]{2,}"', r'"\1":"***"', v),
    "dicom_uid":     lambda v: ".".join(v.split(".")[:3]) + ".*****",

    # ── Commerce ──────────────────────────────────────────────────────────
    "vin":           _mask_vin,
    "vehicle":       lambda v: re.sub(r'"vin":\s*"[^"]{5,}"', '"vin":"***"', v),

    # ── Meta / technical ──────────────────────────────────────────────────
    "sessionid":     _mask_session_id,
    "deviceid":      _mask_session_id,
    "ipv4":          _mask_ip,
    "public_ip":     _mask_ip,
    "mac_address":   _mask_mac,
    "username":      lambda v: v[:2] + "***" + v[-2:] if len(v) > 4 else v[0] + "***",
    "handle":        lambda v: "@" + (v.lstrip("@")[:2] + "***" if len(v.lstrip("@")) > 2 else v.lstrip("@")),

    # ── E-Commerce ─────────────────────────────────────────────────────────
    "order_id":      lambda v: v[:6] + "****" + v[-4:] if len(v) > 10 else v,
    "tracking_number": lambda v: _mask_digits(_digits_only(v), 4, 4),

    # ── Aviation ──────────────────────────────────────────────────────────
    "pnr_code":      _mask_pnr,
    "iata_ticket":   _mask_iata_ticket,

    # ── OIDC / Auth ───────────────────────────────────────────────────────
    "oidc_token_set": lambda v: re.sub(r'"token":\s*"eyJ[^"]+', '"token":"eyJ***', v),
    "oidc_token":    lambda v: v[:10] + "***." + v[-4:] if len(v) > 14 else "eyJ***",

    # ── CardPhysics ────────────────────────────────────────────────────────
    "iso8583_auth_request":  lambda v: re.sub(r"(?<=DE002:)\d+", lambda m: _mask_cardnum(m.group(0)), v),
    "iso8583_auth_response": lambda v: re.sub(r"(?<=DE002:)\d+", lambda m: _mask_cardnum(m.group(0)), v),
    "iso8583_reversal":      lambda v: re.sub(r"(?<=DE002:)\d+", lambda m: _mask_cardnum(m.group(0)), v),
    "emv_arqc":      lambda v: v[:8] + "****" + v[-4:] if len(v) == 16 else _mask_pci_sad(v),
    "emv_atc":       lambda v: "**" + v[-2:] if len(v) >= 4 else "****",
    "emv_iad":       lambda v: v[:4] + "****" + v[-4:] if len(v) >= 12 else _mask_pci_sad(v),
    "atm_session":   lambda v: v,   # already contains masked_pan field
    "pos_receipt":   lambda v: v,   # already shows **** **** **** XXXX

    # ── Location ───────────────────────────────────────────────────────────
    "latitude":      lambda v: re.sub(r"(\d+\.\d{2})\d+", r"\g<1>*****", str(v)),
    "longitude":     lambda v: re.sub(r"(\d+\.\d{2})\d+", r"\g<1>*****", str(v)),
    "coordinates":   lambda v: ",".join(
        re.sub(r"(\d+\.\d{2})\d+", r"\g<1>*****", p) for p in v.split(",")
    ),

    # ── IntlIDs ────────────────────────────────────────────────────────────
    "br_cpf":         _mask_br_cpf,
    "br_cnpj":        lambda v: _mask_generic_id(v, 4, 4),
    "in_pan":         lambda v: v[:5] + "****" + v[-1:],
    "in_aadhaar":     _mask_aadhaar,
    "in_gstin":       lambda v: v[:2] + v[2:7] + "****" + v[-2:],
    "in_epic":        lambda v: v[:3] + "****" + v[-2:],
    "cn_ric":         _mask_cn_ric,
    "mx_curp":        lambda v: _mask_generic_id(v, 4, 2),
    "mx_rfc":         lambda v: _mask_generic_id(v, 4, 2),
    "it_codicefiscale": lambda v: v[:4] + "**" + v[6:8] + "****" + v[-1:],
    "es_dni":         lambda v: _mask_generic_id(v, 2, 2),
    "es_nie":         lambda v: _mask_generic_id(v, 2, 2),
    "es_ccc":         lambda v: _mask_generic_id(v, 4, 4),
    "pk_cnic":        lambda v: _mask_generic_id(v, 5, 2),
    "jp_in":          lambda v: _mask_digits(_digits_only(v), 4, 4),
    "jp_cn":          lambda v: _mask_digits(_digits_only(v), 4, 4),
    "kr_rrn":         _mask_kr_rrn,
    "kr_brn":         lambda v: _mask_generic_id(v, 3, 3),
    "nl_bsn":         _mask_nl_bsn,
    "pl_pesel":       lambda v: _mask_digits(_digits_only(v), 6, 2),
    "se_personnummer": _mask_se_personnummer,
    "dk_cpr":         _mask_dk_cpr,
    "fi_hetu":        lambda v: v[:6] + "-****",
    "no_fodselsnummer": lambda v: _mask_digits(_digits_only(v), 6, 2),
    "au_abn":         lambda v: _mask_digits(_digits_only(v), 3, 3),
    "au_tfn":         lambda v: _mask_digits(_digits_only(v), 3, 2),
    "au_acn":         lambda v: _mask_digits(_digits_only(v), 3, 3),
    "my_nric":        lambda v: _mask_generic_id(v, 6, 4),
    "th_pin":         lambda v: _mask_digits(_digits_only(v), 4, 4),
    "th_tin":         lambda v: _mask_digits(_digits_only(v), 4, 4),
    "sg_uen":         lambda v: _mask_alphanum(v, 4, 2),
    "za_idnr":        lambda v: _mask_digits(_digits_only(v), 6, 3),
    "ca_bn":          lambda v: _mask_digits(_digits_only(v), 3, 2),
    "nz_ird":         lambda v: _mask_digits(_digits_only(v), 3, 2),
    "ar_cuit":        lambda v: _mask_generic_id(v, 4, 2),
    "ar_dni":         lambda v: _mask_generic_id(v, 2, 2),
    "cl_rut":         lambda v: _mask_generic_id(v, 3, 2),
    "co_nit":         lambda v: _mask_generic_id(v, 3, 3),
    "il_idnr":        lambda v: _mask_digits(_digits_only(v), 3, 2),
    "ro_cnp":         lambda v: _mask_digits(_digits_only(v), 4, 3),
    "ro_cui":         lambda v: _mask_generic_id(v, 4, 3),
    "hr_oib":         lambda v: _mask_digits(_digits_only(v), 4, 3),
    "bg_egn":         lambda v: _mask_digits(_digits_only(v), 6, 2),
    "lt_asmens":      lambda v: _mask_digits(_digits_only(v), 5, 2),
    "ee_ik":          lambda v: _mask_digits(_digits_only(v), 5, 2),
    "pt_cc":          lambda v: _mask_generic_id(v, 4, 3),
    "eg_tn":          lambda v: _mask_digits(_digits_only(v), 3, 2),

    # ── Misc with mask defined ─────────────────────────────────────────────
    "psd2_consent":  lambda v: v[:12] + "***" if len(v) > 12 else v,
    "mnemonic":      lambda v: v.split()[0] + " *** *** ... ***",
    "swift_mt103":   lambda v: re.sub(r"(IBAN|BIC|ACC)[: ]+(\w{2,6})\w+", r"\1: \2****", v),
}


def apply_mask(type_name: str, value: str) -> str:
    """
    Return a privacy-safe masked version of `value` for the given generator type.

    - PCI SAD types → all alphanumeric replaced with *
    - Types with no masking rule → returned unchanged
    - All other types → type-specific regulation-compliant masking
    """
    v = str(value)
    tn = type_name.lower().strip()

    masker_fn = _MASKERS.get(tn)
    if masker_fn:
        try:
            return masker_fn(v)
        except Exception:
            return v  # fallback: return original on any error

    # Types not in _MASKERS: check if regulations.py says there's a mask
    entry = REGULATION_TAGS.get(tn, {})
    if entry and entry.get("mask"):
        # Generic fallback: mask middle, show first 2 + last 2 alphanumeric
        return _mask_generic_id(v, 2, 2)

    # No masking needed for this type
    return v
