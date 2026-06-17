"""
mock-jutsu — Telecom Generator
Standards:
  3GPP TS 23.003 v17.5.0 §2.2 (IMSI), §3.3 (MSISDN), §6.2 (IMEI)
  ITU-T E.118 §3.2 (ICCID)
  ITU-T E.164 §6 (MSISDN / E.164 format)
  ITU-T E.212 (MCC/MNC assignments, public list at itu.int)
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)

Entropy:
  IMEI   : ~5.6×10^11 (16 RBI codes × 10^6 model × 10^6 SNR / Luhn constraint)
  ICCID  : ~10^10 per MNO (10-11 serial digits)
  IMSI   : ~10^9-10^10 per MCC/MNC pair (MSIN length varies 9-10)
  MSISDN : ~10^8 per locale (locale-fixed prefix + 8-9 random digits)
"""

import random
import secrets

# ──────────────────────────────────────────────────────────────────────────────
# RBI (Reporting Body Identifier) codes — 3GPP TS 23.003 v17.5.0 Annex B
# Published by GSMA at gsma.com/services/numbering/imei
# ──────────────────────────────────────────────────────────────────────────────
_RBI_CODES: list[str] = [
    "00", "01",   # BABT (UK)
    "10",         # CTIA (US)
    "13",         # ARCEP (France)
    "20",         # TCA (Taiwan)
    "30", "35",   # IMDA (Singapore)
    "40", "44",   # GSMA / PTCRB
    "53",         # TTA (Korea)
    "54",         # ANATEL (Brazil)
    "55",         # RCM (Australia)
    "86",         # MIIT (China)
    "91",         # NCC (Nigeria)
    "98",         # TRAI (India)
    "99",         # TA (UK)
]

# ──────────────────────────────────────────────────────────────────────────────
# MCC/MNC pairs — ITU-T E.212, public table at itu.int/pub/T-SP-E.212
# Only widely-active pairs included; synthetic MSIN digits follow.
# ──────────────────────────────────────────────────────────────────────────────
_MCC_MNC: dict[str, list[tuple[str, str]]] = {
    "TR": [("286", "01"), ("286", "02"), ("286", "03"), ("286", "04")],
    "US": [("310", "010"), ("310", "260"), ("311", "480"), ("310", "030")],
    "UK": [("234", "10"), ("234", "20"), ("234", "30"), ("234", "50")],
    "DE": [("262", "01"), ("262", "02"), ("262", "03"), ("262", "07")],
    "FR": [("208", "01"), ("208", "10"), ("208", "20"), ("208", "25")],
    "RU": [("250", "01"), ("250", "02"), ("250", "20"), ("250", "99")],
}

# ──────────────────────────────────────────────────────────────────────────────
# ICCID issuer codes — ITU-T E.118 §3 (synthetic; follows 89+CC+issuer structure)
# Format stored as (cc, issuer1, issuer2, ...) to allow random selection.
# ──────────────────────────────────────────────────────────────────────────────
_ICCID_ISSUERS: dict[str, tuple[str, ...]] = {
    "TR": ("90", "0534", "0542", "0552"),
    "US": ("1",  "1234", "4567", "7890"),
    "UK": ("44", "7900", "7800", "7700"),
    "DE": ("49", "1511", "1521", "1601"),
    "FR": ("33", "0600", "0601", "0602"),
    "RU": ("7",  "9101", "9211", "9261"),
}

# ──────────────────────────────────────────────────────────────────────────────
# MSISDN / E.164 locale configuration
# (country_code_str, valid_subscriber_prefixes, trailing_random_digits)
# Prefixes sourced from ITU-T E.164 national numbering plans.
# ──────────────────────────────────────────────────────────────────────────────
_MSISDN_FORMAT: dict[str, tuple[str, list, int]] = {
    "TR": ("+90", [
        "505","506","507","508","509",
        "530","531","532","533","534","535","537","538","539",
        "540","541","542","543","544","545","546","547","548","549",
        "551","552","553","554","555","556","559","562",
    ], 7),  # +90 5XX-XXX-XXXX (10 subscriber digits)
    "US": ("+1", [
        "201","202","203","212","213","310","312","404","407",
        "408","415","425","469","512","617","646","650","702",
        "714","718","773","818","917","949",
    ], 7),  # +1 NXX-NXX-XXXX; exchange first digit enforced to 2-9 in generator
    "UK": ("+44", [
        "7300","7400","7500","7600","7800","7900",
    ], 6),  # +44 7XXX-XXXXXX (10 subscriber digits); 7700 omitted (reserved ranges)
    "DE": ("+49", [
        "160","162","163",
        "170","171","172","173","174","175","176","177","178","179",
    ], 7),  # +49 1XX-XXXXXXX; 15x omitted (not in phonenumbers number plan)
    "FR": ("+33", [
        "601","602","603","610","611","612","613","614","615",
        "616","617","618","619","620","621","622","623","624","625",
    ], 6),  # +33 6XX-XXX-XXX (9 subscriber digits)
    "RU": ("+7", [
        "901","902","903","904","905","906","907","908","909",
        "910","911","912","913","914","915","916","917","918","919",
        "920","921","922","923","924","925","926","927","928","929",
    ], 7),  # +7 9XX-XXX-XXXX (10 subscriber digits)
}


# ──────────────────────────────────────────────────────────────────────────────
# Luhn check digit — 3GPP TS 23.003 §6.2.1 (IMEI), ITU-T E.118 (ICCID)
# Verified test vector: payload 49015420323751 → check digit 8
# ──────────────────────────────────────────────────────────────────────────────
def _luhn_check(digits: list[int]) -> int:
    total = 0
    for i, d in enumerate(reversed(digits)):
        if i % 2 == 0:
            doubled = d * 2
            total += doubled - 9 if doubled > 9 else doubled
        else:
            total += d
    return (10 - total % 10) % 10


# ──────────────────────────────────────────────────────────────────────────────
# Generator
# ──────────────────────────────────────────────────────────────────────────────

class TelecomGenerator:
    """3GPP / ITU-T compliant telecom identifier generators for 6 locales."""

    @staticmethod
    def generate_imei() -> str:
        """
        IMEI: TAC(8) + SNR(6) + Luhn check(1) = 15 digits.
        3GPP TS 23.003 v17.5.0 §6.2.
        TAC = RBI(2 digits, from public GSMA list) + 6 synthetic model digits.
        """
        rbi        = random.choice(_RBI_CODES)
        model_code = "".join(str(random.randrange(10)) for _ in range(6))
        snr        = "".join(str(random.randrange(10)) for _ in range(6))
        payload    = [int(c) for c in rbi + model_code + snr]
        return rbi + model_code + snr + str(_luhn_check(payload))

    @staticmethod
    def generate_imei2() -> str:
        """IMEI hyphenated display format AA-BBBBBB-CCCCCC-D (3GPP TS 23.003 §6.2)."""
        raw = TelecomGenerator.generate_imei()
        return f"{raw[:2]}-{raw[2:8]}-{raw[8:14]}-{raw[14]}"

    @staticmethod
    def generate_iccid(locale: str = "TR") -> str:
        """
        ICCID: 89 + CC + issuer(4) + serial + Luhn check = 19 digits.
        ITU-T E.118 §3.2.
        CC = ITU-T E.164 country calling code (1-2 digits).
        """
        cc, *issuers = _ICCID_ISSUERS.get(locale.upper(), _ICCID_ISSUERS["TR"])
        issuer     = random.choice(issuers)
        prefix     = "89" + cc + issuer                  # 7-8 digits
        serial_len = 18 - len(prefix)                    # fill to 18 data digits
        serial     = "".join(str(random.randrange(10)) for _ in range(serial_len))
        payload    = [int(c) for c in prefix + serial]
        return prefix + serial + str(_luhn_check(payload))

    @staticmethod
    def generate_imsi(locale: str = "TR") -> str:
        """
        IMSI: MCC(3) + MNC(2-3) + MSIN(variable) ≤ 15 digits total.
        3GPP TS 23.003 v17.5.0 §2.2. No check digit.
        MCC/MNC from ITU-T E.212 public table.
        """
        pairs    = _MCC_MNC.get(locale.upper(), _MCC_MNC["TR"])
        mcc, mnc = random.choice(pairs)
        msin_len = 15 - len(mcc) - len(mnc)
        msin     = "".join(str(random.randrange(10)) for _ in range(msin_len))
        return mcc + mnc + msin

    @staticmethod
    def generate_msisdn(locale: str = "TR") -> str:
        """
        MSISDN in E.164 format: +CC subscriber_number (max 15 digits after +).
        ITU-T E.164 §6 / 3GPP TS 23.003 §3.3.
        Prefixes from national numbering plans — all generated numbers are valid E.164.
        US/NANP: exchange first digit enforced to 2-9 (NANP rule N11/N0X reserved).
        """
        cc, prefixes, rand_len = _MSISDN_FORMAT.get(locale.upper(), _MSISDN_FORMAT["TR"])
        prefix = random.choice(prefixes)
        if locale.upper() == "US":
            # NANP: exchange (first 3 of rand_len=7) first digit must be 2-9
            exchange = str(random.randint(2, 9)) + "".join(str(random.randrange(10)) for _ in range(2))
            line = "".join(str(random.randrange(10)) for _ in range(4))
            digits = exchange + line
        else:
            digits = "".join(str(random.randrange(10)) for _ in range(rand_len))
        return cc + prefix + digits

    def generate(self, data_type: str, locale: str = "TR", **_) -> str:
        dt = data_type.lower().replace("_", "")
        if dt == "imei":
            return self.generate_imei()
        if dt == "imei2":
            return self.generate_imei2()
        if dt == "iccid":
            return self.generate_iccid(locale)
        if dt == "imsi":
            return self.generate_imsi(locale)
        if dt == "msisdn":
            return self.generate_msisdn(locale)
        return None
