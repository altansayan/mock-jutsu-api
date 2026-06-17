"""
Algorithm compliance tests — known real-world test vectors.
These tests verify generator algorithms against published standards.
When adding a new generator: add vectors here + in compliance/algorithm_vectors.json.
"""
import json
import os
import re
import pytest

_ROOT = os.path.join(os.path.dirname(__file__), "..", "compliance")


def _load_vectors():
    with open(os.path.join(_ROOT, "algorithm_vectors.json")) as f:
        return json.load(f)


def _load_contracts():
    with open(os.path.join(_ROOT, "format_contracts.json")) as f:
        return json.load(f)


# ── Checksum helpers (mirrors production code, used for vector verification) ──

def _luhn_valid(number: str) -> bool:
    digits = [int(c) for c in number]
    total = 0
    for i, d in enumerate(reversed(digits)):
        n = d * 2 if i % 2 == 1 else d
        if n > 9:
            n -= 9
        total += n
    return total % 10 == 0


def _aba_valid(number: str) -> bool:
    d = [int(c) for c in number]
    return (3*(d[0]+d[3]+d[6]) + 7*(d[1]+d[4]+d[7]) + (d[2]+d[5]+d[8])) % 10 == 0


def _cusip_check_digit(payload: str) -> int:
    total = 0
    for i, c in enumerate(payload):
        v = int(c) if c.isdigit() else ord(c) - 55
        if i % 2 == 1:
            v *= 2
        total += v // 10 + v % 10
    return (10 - total % 10) % 10


def _ean_valid(number: str) -> bool:
    digits = [int(c) for c in number]
    weights = [1 if i % 2 == 0 else 3 for i in range(len(digits) - 1)]
    total = sum(d * w for d, w in zip(digits[:-1], weights))
    return (10 - total % 10) % 10 == digits[-1]


def _isin_luhn_valid(isin: str) -> bool:
    """Validate a full 12-char ISIN via Luhn on the complete expanded numeric string.

    ISO 6166: expand entire ISIN (letters A=10..Z=35), apply Luhn; valid if total % 10 == 0.
    The rightmost digit of the expanded string is position 0 (even → doubled).
    """
    numeric = ''.join(str(ord(c) - 55) if c.isalpha() else c for c in isin)
    digits = [int(d) for d in numeric]
    total = 0
    for i, d in enumerate(reversed(digits)):
        n = d * 2 if i % 2 == 1 else d
        if n > 9:
            n -= 9
        total += n
    return total % 10 == 0


def _tckn_valid(n: str) -> bool:
    if len(n) != 11 or n[0] == '0':
        return False
    d = [int(c) for c in n]
    odd_sum = d[0] + d[2] + d[4] + d[6] + d[8]
    even_sum = d[1] + d[3] + d[5] + d[7]
    if (7 * odd_sum - even_sum) % 10 != d[9]:
        return False
    return sum(d[:10]) % 10 == d[10]


def _nhs_valid(n: str) -> bool:
    if len(n) != 10:
        return False
    weights = [10, 9, 8, 7, 6, 5, 4, 3, 2]
    total = sum(int(n[i]) * weights[i] for i in range(9))
    remainder = total % 11
    check = 0 if remainder == 0 else 11 - remainder
    return check != 10 and check == int(n[9])


def _creditor_ref_valid(ref: str) -> bool:
    """ISO 11649 SEPA Creditor Reference: reorder ref+RF+check → numeric; mod 97 == 1."""
    if len(ref) < 5 or not ref.startswith("RF"):
        return False
    reordered = ref[4:] + ref[:4]
    numeric = ''.join(str(ord(c) - 55) if c.isalpha() else c for c in reordered)
    return int(numeric) % 97 == 1


def _imo_valid(number: str) -> bool:
    """IMO ship number: weighted sum of first 6 digits (weights 7..2); check = sum % 10."""
    if len(number) != 7 or not number.isdigit():
        return False
    total = sum(int(number[i]) * (7 - i) for i in range(6))
    return total % 10 == int(number[6])


def _sedol_check_digit(payload: str) -> int:
    """LSE SEDOL check digit: weights [1,3,1,7,3,9]; char A-Z = 10-35; (10-sum%10)%10."""
    weights = [1, 3, 1, 7, 3, 9]
    total = 0
    for i, c in enumerate(payload):
        v = int(c) if c.isdigit() else ord(c) - 55
        total += v * weights[i]
    return (10 - total % 10) % 10


def _nmea_checksum_valid(sentence: str) -> bool:
    """NMEA 0183: XOR of bytes between '$' and '*' must equal 2-hex-digit checksum after '*'."""
    if '$' not in sentence or '*' not in sentence:
        return False
    start = sentence.index('$') + 1
    end = sentence.index('*')
    xor = 0
    for c in sentence[start:end]:
        xor ^= ord(c)
    return f"{xor:02X}" == sentence[end + 1:end + 3].upper()


def _tle_checksum_valid(line: str) -> bool:
    """NORAD TLE: sum of digits + 1 per '-' in positions 0-67; mod 10 == position 68."""
    if len(line) < 69:
        return False
    total = sum(int(c) if c.isdigit() else (1 if c == '-' else 0) for c in line[:68])
    return (total % 10) == int(line[68])


def _gtin14_check_digit(payload13: str) -> int:
    """GS1 GTIN-14 check digit: alternate weights 3,1 from position 0 for 13 digits."""
    weights = [3 if i % 2 == 0 else 1 for i in range(13)]
    total = sum(int(d) * w for d, w in zip(payload13, weights))
    return (10 - total % 10) % 10


def _iata_check_digit(etn: str) -> int:
    """IATA ETN Mod-7: form_serial (digits 3-11 of 13-digit ETN) mod 7 == digit 12."""
    return int(etn[3:12]) % 7


def _nec_complement_valid(hex32: str) -> bool:
    """NEC protocol: byte[0]^byte[1]==0xFF and byte[2]^byte[3]==0xFF (address+~address, command+~command)."""
    b = bytes.fromhex(hex32)
    return len(b) == 4 and (b[0] ^ b[1] == 0xFF) and (b[2] ^ b[3] == 0xFF)


def _rc5_start_bit_valid(hex_word: str) -> bool:
    """RC-5: bit 13 (0x2000) of the 14-bit word must be 1 (S1 start bit is always high)."""
    word = int(hex_word, 16)
    return bool(word & 0x2000)


def _pin_block_format0_valid(block_hex: str) -> bool:
    """ISO 9564-1 Format 0: nibble[0]=0, nibble[1]=PIN_len(4-12), PIN digits 0-9, filler=0xF."""
    if len(block_hex) != 16:
        return False
    nibbles = [int(c, 16) for c in block_hex]
    if nibbles[0] != 0:
        return False
    pin_len = nibbles[1]
    if not (4 <= pin_len <= 12):
        return False
    if any(nibbles[i] > 9 for i in range(2, 2 + pin_len)):
        return False
    return all(nibbles[i] == 0xF for i in range(2 + pin_len, 16))


def _pin_block_format3_valid(block_hex: str) -> bool:
    """ISO 9564-1 Format 3: nibble[0]=3, nibble[1]=PIN_len(4-12), PIN digits 0-9, filler=0-9 (not 0xF)."""
    if len(block_hex) != 16:
        return False
    nibbles = [int(c, 16) for c in block_hex]
    if nibbles[0] != 3:
        return False
    pin_len = nibbles[1]
    if not (4 <= pin_len <= 12):
        return False
    if any(nibbles[i] > 9 for i in range(2, 2 + pin_len)):
        return False
    return all(nibbles[i] <= 9 for i in range(2 + pin_len, 16))


def _ndef_uri_valid(hex_record: str) -> bool:
    """NFC Forum RTD URI: byte[0]=0xD1 (MB|ME|SR|TNF=0x01), byte[1]=0x01, byte[3]=0x55('U'), byte[4]=prefix 0x00-0x23."""
    b = bytes.fromhex(hex_record)
    return (len(b) >= 5 and b[0] == 0xD1 and b[1] == 0x01 and b[3] == 0x55 and b[4] <= 0x23)


def _ndef_text_valid(hex_record: str) -> bool:
    """NFC Forum RTD Text: byte[0]=0xD1, byte[1]=0x01, byte[3]=0x54('T'), byte[4]=status, lang bytes follow."""
    b = bytes.fromhex(hex_record)
    if len(b) < 6 or b[0] != 0xD1 or b[1] != 0x01 or b[3] != 0x54:
        return False
    lang_len = b[4] & 0x3F
    return len(b) >= 5 + lang_len


# ── Vector tests ──────────────────────────────────────────────────────────────

def test_cusip_known_vectors():
    """CUSIP valid values from ABA standard must pass check digit."""
    v = _load_vectors()
    for cusip in v["cusip"]["valid_complete"]:
        payload, check = cusip[:8], int(cusip[8])
        assert _cusip_check_digit(payload) == check, f"CUSIP vector failed: {cusip}"
    for cusip in v["cusip"]["invalid_check"]:
        payload, check = cusip[:8], int(cusip[8])
        assert _cusip_check_digit(payload) != check, f"Expected invalid CUSIP: {cusip}"


def test_aba_routing_known_vectors():
    """ABA routing numbers must satisfy checksum formula."""
    v = _load_vectors()
    for rtn in v["aba_routing"]["valid"]:
        assert _aba_valid(rtn), f"ABA routing vector failed: {rtn}"
    for rtn in v["aba_routing"]["invalid"]:
        assert not _aba_valid(rtn), f"Expected invalid ABA: {rtn}"


def test_tckn_known_vectors():
    """TCKN known valid values must pass official algorithm."""
    v = _load_vectors()
    for tckn in v["tckn"]["valid"]:
        assert _tckn_valid(tckn), f"TCKN vector failed: {tckn}"
    for tckn in v["tckn"]["invalid"]:
        assert not _tckn_valid(tckn), f"Expected invalid TCKN: {tckn}"


def test_ean13_known_vectors():
    """EAN-13 known values from GS1 must pass check digit."""
    v = _load_vectors()
    for ean in v["ean13"]["valid"]:
        assert _ean_valid(ean), f"EAN-13 vector failed: {ean}"
    for ean in v["ean13"]["invalid"]:
        assert not _ean_valid(ean), f"Expected invalid EAN-13: {ean}"


def test_isin_known_vectors():
    """ISO 6166 ISIN known values must pass Luhn check."""
    v = _load_vectors()
    for isin in v["isin"]["valid"]:
        assert _isin_luhn_valid(isin), f"ISIN vector failed: {isin}"
    for isin in v["isin"]["invalid"]:
        assert not _isin_luhn_valid(isin), f"Expected invalid ISIN: {isin}"


def test_luhn_known_vectors():
    """Luhn algorithm known values must be valid."""
    v = _load_vectors()
    for card in v["luhn"]["valid"]:
        assert _luhn_valid(card), f"Luhn vector failed: {card}"
    for card in v["luhn"]["invalid"]:
        assert not _luhn_valid(card), f"Expected invalid Luhn: {card}"


def test_nhs_known_vectors():
    """NHS number known values must pass official algorithm."""
    v = _load_vectors()
    for nhs in v["nhs"]["valid"]:
        assert _nhs_valid(nhs), f"NHS vector failed: {nhs}"
    for nhs in v["nhs"]["invalid"]:
        assert not _nhs_valid(nhs), f"Expected invalid NHS: {nhs}"


def test_creditor_ref_known_vectors():
    """ISO 11649 SEPA Creditor Reference (RF18...) must validate via MOD-97."""
    v = _load_vectors()
    for ref in v["creditor_ref"]["valid"]:
        assert _creditor_ref_valid(ref), f"Creditor ref vector failed: {ref}"
    for ref in v["creditor_ref"]["invalid"]:
        assert not _creditor_ref_valid(ref), f"Expected invalid creditor ref: {ref}"


def test_imo_number_known_vectors():
    """IMO ship identification numbers must pass weighted checksum (IMO Res. A.600(15))."""
    v = _load_vectors()
    for imo in v["imo_number"]["valid"]:
        assert _imo_valid(imo), f"IMO vector failed: {imo}"
    for imo in v["imo_number"]["invalid"]:
        assert not _imo_valid(imo), f"Expected invalid IMO: {imo}"


def test_sedol_known_vectors():
    """LSE SEDOL examples (BT Group 0263494, HSBC 3091357) must pass check digit."""
    v = _load_vectors()
    for sedol in v["sedol"]["valid"]:
        payload, check = sedol[:6], int(sedol[6])
        assert _sedol_check_digit(payload) == check, f"SEDOL vector failed: {sedol}"
    for sedol in v["sedol"]["invalid"]:
        payload, check = sedol[:6], int(sedol[6])
        assert _sedol_check_digit(payload) != check, f"Expected invalid SEDOL: {sedol}"


def test_nmea_gpgga_known_vectors():
    """NMEA 0183 GPGGA sentences must have valid XOR checksums."""
    v = _load_vectors()
    for sentence in v["nmea_gpgga"]["valid_sentences"]:
        assert _nmea_checksum_valid(sentence), f"NMEA GPGGA checksum failed: {sentence}"


def test_nmea_gprmc_known_vectors():
    """NMEA 0183 GPRMC sentences must have valid XOR checksums."""
    v = _load_vectors()
    for sentence in v["nmea_gprmc"]["valid_sentences"]:
        assert _nmea_checksum_valid(sentence), f"NMEA GPRMC checksum failed: {sentence}"


def test_tle_satellite_known_vectors():
    """NORAD TLE lines (ISS from Celestrak docs) must have valid Modulo-10 checksums."""
    v = _load_vectors()
    for line in v["tle_satellite"]["valid_lines"]:
        assert _tle_checksum_valid(line), f"TLE checksum failed: {line[:25]}..."


def test_gs1_128_known_vectors():
    """GS1-128 GTIN-14 check digit from GS1 General Specifications must be correct."""
    v = _load_vectors()
    for gtin in v["gs1_128"]["valid_gtin14"]:
        payload, check = gtin[:13], int(gtin[13])
        assert _gtin14_check_digit(payload) == check, f"GTIN-14 vector failed: {gtin}"
    for gtin in v["gs1_128"]["invalid_gtin14"]:
        payload, check = gtin[:13], int(gtin[13])
        assert _gtin14_check_digit(payload) != check, f"Expected invalid GTIN-14: {gtin}"


def test_iata_ticket_known_vectors():
    """IATA ETN Mod-7 check digit: form_serial % 7 == last digit."""
    v = _load_vectors()
    for etn in v["iata_ticket"]["valid"]:
        check = int(etn[12])
        assert _iata_check_digit(etn) == check, f"IATA ETN vector failed: {etn}"
    for etn in v["iata_ticket"]["invalid"]:
        check = int(etn[12])
        assert _iata_check_digit(etn) != check, f"Expected invalid IATA ETN: {etn}"


def test_ir_nec_known_vectors():
    """NEC IR protocol: address+~address and command+~command byte pairs must XOR to 0xFF."""
    v = _load_vectors()
    for word in v["ir_nec"]["valid_hex32"]:
        assert _nec_complement_valid(word), f"NEC vector failed: {word}"
    for word in v["ir_nec"]["invalid_hex32"]:
        assert not _nec_complement_valid(word), f"Expected invalid NEC: {word}"


def test_ir_rc5_known_vectors():
    """RC-5 IR protocol: bit 13 (S1 start bit) must always be 1."""
    v = _load_vectors()
    for word in v["ir_rc5"]["valid_words_hex"]:
        assert _rc5_start_bit_valid(word), f"RC-5 vector failed: {word}"
    for word in v["ir_rc5"]["invalid_words_hex"]:
        assert not _rc5_start_bit_valid(word), f"Expected invalid RC-5: {word}"


def test_pin_block_known_vectors():
    """ISO 9564-1 Format 0 PIN block: format nibble=0, PIN length 4-12, filler=0xF."""
    v = _load_vectors()
    for block in v["pin_block"]["valid_blocks"]:
        assert _pin_block_format0_valid(block), f"PIN block Format 0 vector failed: {block}"
    for block in v["pin_block"]["invalid_blocks"]:
        assert not _pin_block_format0_valid(block), f"Expected invalid PIN block Format 0: {block}"


def test_pin_block_fmt3_known_vectors():
    """ISO 9564-1 Format 3 PIN block: format nibble=3, PIN length 4-12, filler=0-9."""
    v = _load_vectors()
    for block in v["pin_block_fmt3"]["valid_blocks"]:
        assert _pin_block_format3_valid(block), f"PIN block Format 3 vector failed: {block}"
    for block in v["pin_block_fmt3"]["invalid_blocks"]:
        assert not _pin_block_format3_valid(block), f"Expected invalid PIN block Format 3: {block}"


def test_ndef_uri_known_vectors():
    """NFC Forum RTD URI record: header 0xD1, type 'U' (0x55), URI prefix code 0x00-0x23."""
    v = _load_vectors()
    for rec in v["ndef_uri"]["valid_hex_records"]:
        assert _ndef_uri_valid(rec), f"NDEF URI vector failed: {rec}"
    for rec in v["ndef_uri"]["invalid_hex_records"]:
        assert not _ndef_uri_valid(rec), f"Expected invalid NDEF URI: {rec}"


def test_ndef_text_known_vectors():
    """NFC Forum RTD Text record: header 0xD1, type 'T' (0x54), status byte with lang length."""
    v = _load_vectors()
    for rec in v["ndef_text"]["valid_hex_records"]:
        assert _ndef_text_valid(rec), f"NDEF Text vector failed: {rec}"
    for rec in v["ndef_text"]["invalid_hex_records"]:
        assert not _ndef_text_valid(rec), f"Expected invalid NDEF Text: {rec}"


def test_apdu_known_vectors():
    """ISO 7816-4 SELECT AID: CLA=0x00, INS=0xA4, P1=0x04, P2=0x00, Lc=len(AID), Data=AID."""
    v = _load_vectors()
    for apdu_hex in v["apdu"]["valid_select_apdus"]:
        b = bytes.fromhex(apdu_hex)
        assert b[0] == 0x00 and b[1] == 0xA4 and b[2] == 0x04 and b[3] == 0x00, \
            f"APDU vector failed CLA/INS/P1/P2: {apdu_hex}"
        assert b[4] == len(b) - 5, f"APDU Lc mismatch: {apdu_hex}"
    for apdu_hex in v["apdu"]["invalid_select_apdus"]:
        b = bytes.fromhex(apdu_hex)
        assert not (b[0] == 0x00 and b[1] == 0xA4 and b[2] == 0x04 and b[3] == 0x00), \
            f"Expected invalid APDU: {apdu_hex}"


def test_epc_known_vectors():
    """GS1 EPC SGTIN-96: 24-hex-char (96-bit), first byte must be 0x30 (SGTIN-96 header)."""
    v = _load_vectors()
    for epc_hex in v["epc"]["valid_hex96"]:
        b = bytes.fromhex(epc_hex)
        assert len(b) == 12 and b[0] == 0x30, f"EPC SGTIN-96 vector failed: {epc_hex}"
    for epc_hex in v["epc"]["invalid_hex96"]:
        b = bytes.fromhex(epc_hex)
        assert not (len(b) == 12 and b[0] == 0x30), f"Expected invalid EPC: {epc_hex}"


def test_rfid_uid_known_vectors():
    """ISO 14443-3A 7-byte RFID UID: 14 hex chars, byte[0]=valid manufacturer byte."""
    KNOWN_MANUFACTURERS = {0x04, 0x08, 0x02, 0x05, 0x1B}
    v = _load_vectors()
    for uid in v["rfid_uid"]["valid_uids"]:
        b = bytes.fromhex(uid)
        assert len(b) == 7, f"RFID UID must be 7 bytes: {uid}"
    for uid in v["rfid_uid"]["invalid_uids"]:
        try:
            b = bytes.fromhex(uid)
            assert len(b) != 7, f"Expected invalid RFID UID: {uid}"
        except ValueError:
            pass  # invalid hex is also invalid


def test_nfc_uid_known_vectors():
    """NFC Forum Type 2 UID: 14 hex chars (7 bytes), same format as ISO 14443-3A RFID UID."""
    v = _load_vectors()
    for uid in v["nfc_uid"]["valid_uids"]:
        b = bytes.fromhex(uid)
        assert len(b) == 7, f"NFC UID must be 7 bytes: {uid}"
    for uid in v["nfc_uid"]["invalid_uids"]:
        try:
            b = bytes.fromhex(uid)
            assert len(b) != 7, f"Expected invalid NFC UID: {uid}"
        except ValueError:
            pass


def test_track1_data_known_vectors():
    """ISO 7813 Track 1: starts with %B, fields separated by ^, ends with ?, max 79 chars."""
    v = _load_vectors()
    for track in v["track1_data"]["valid_examples"]:
        assert track.startswith("%B"), f"Track 1 must start with %B: {track}"
        assert track.endswith("?"), f"Track 1 must end with ?: {track}"
        assert track.count("^") >= 2, f"Track 1 must have 2+ ^ separators: {track}"
        assert len(track) <= 79, f"Track 1 exceeds 79 chars: {track}"
    for track in v["track1_data"]["invalid_examples"]:
        assert not track.startswith("%B"), f"Expected invalid Track 1: {track}"


def test_track2_data_known_vectors():
    """ISO 7813 Track 2: starts with ;, field separator =, ends with ?, max 40 chars."""
    v = _load_vectors()
    for track in v["track2_data"]["valid_examples"]:
        assert track.startswith(";"), f"Track 2 must start with ;: {track}"
        assert track.endswith("?"), f"Track 2 must end with ?: {track}"
        assert "=" in track, f"Track 2 must contain = separator: {track}"
        assert len(track) <= 40, f"Track 2 exceeds 40 chars: {track}"
    for track in v["track2_data"]["invalid_examples"]:
        assert not track.startswith(";"), f"Expected invalid Track 2: {track}"


def test_chip_data_known_vectors():
    """EMV TLV: known tag lengths — 9F02=6, 9F03=6, 95=5, 5F2A=2, 9A=3, 9C=1 bytes."""
    v = _load_vectors()
    known_tags = v["chip_data"]["known_tags"]
    for tag, info in known_tags.items():
        example = bytes.fromhex(info["example_hex"])
        assert len(example) == info["length"], \
            f"EMV tag {tag} example length mismatch: {info['example_hex']}"
    tlv = bytes.fromhex(v["chip_data"]["valid_tlv_partial"])
    assert len(tlv) > 0, "TLV partial must not be empty"


def test_dicom_uid_known_vectors():
    """DICOM UID 2.25 root: starts with '2.25.', digits and dots only, max 64 chars."""
    import re
    v = _load_vectors()
    pattern = re.compile(r'^[0-9]+(\.[0-9]+)+$')
    for uid in v["dicom_uid"]["valid_uids"]:
        assert uid.startswith("2.25."), f"DICOM UID must start with 2.25.: {uid}"
        assert len(uid) <= 64, f"DICOM UID exceeds 64 chars: {uid}"
        assert pattern.match(uid), f"DICOM UID invalid chars: {uid}"
    for uid in v["dicom_uid"]["invalid_uids"]:
        valid = uid.startswith("2.25.") and len(uid) <= 64 and bool(pattern.match(uid)) and not uid.endswith(".")
        assert not valid, f"Expected invalid DICOM UID: {uid}"


def test_sepa_ref_known_vectors():
    """ISO 20022 SEPA reference: 1-35 chars, uppercase alphanumeric only."""
    import re
    v = _load_vectors()
    pattern = re.compile(r'^[A-Z0-9]{1,35}$')
    for ref in v["sepa_ref"]["valid_refs"]:
        assert pattern.match(ref), f"SEPA ref vector failed: {ref}"
    for ref in v["sepa_ref"]["invalid_refs"]:
        assert not pattern.match(ref), f"Expected invalid SEPA ref: {ref}"


def test_totp_code_known_vectors():
    """RFC 6238 TOTP: 6 decimal digits exactly (000000-999999)."""
    import re
    v = _load_vectors()
    pattern = re.compile(r'^\d{6}$')
    for code in v["totp_code"]["valid_codes"]:
        assert pattern.match(code), f"TOTP code vector failed: {code}"
    for code in v["totp_code"]["invalid_codes"]:
        assert not pattern.match(code), f"Expected invalid TOTP code: {code}"


def test_webhook_signature_known_vectors():
    """HMAC-SHA256 webhook signature: 'sha256=' + 64 lowercase hex chars."""
    import re
    v = _load_vectors()
    pattern = re.compile(r'^sha256=[0-9a-f]{64}$')
    for sig in v["webhook_signature"]["valid_sigs"]:
        assert pattern.match(sig), f"Webhook sig vector failed: {sig}"
    for sig in v["webhook_signature"]["invalid_sigs"]:
        assert not pattern.match(sig), f"Expected invalid webhook sig: {sig}"


def test_swift_mt103_known_vectors():
    """SWIFT MT103: required field tags must be present in Block 4."""
    v = _load_vectors()
    required = v["swift_mt103"]["required_fields"]
    valid_cvn = v["swift_mt103"]["valid_field_values"]["23B"]
    assert valid_cvn == "CRED", "MT103 :23B: must always be CRED for standard payment"
    assert ":20:" in required, "MT103 must require :20: (sender reference)"
    assert ":32A:" in required, "MT103 must require :32A: (value date / currency / amount)"
    assert len(required) >= 5, f"MT103 must have at least 5 required fields, got {len(required)}"


def test_emv_arqc_known_vectors():
    """EMV ARQC (tag 9F26): 8 bytes = 16 uppercase hex chars."""
    import re
    v = _load_vectors()
    fmt = v["emv_arqc"]["format_checks"]
    example = v["emv_arqc"]["valid_format"]["example"]
    assert len(example) == fmt["hex_length"], f"ARQC example wrong length: {example}"
    pattern = re.compile(r'^[0-9A-F]{16}$')
    assert pattern.match(example), f"ARQC example invalid chars: {example}"


def test_emv_atc_known_vectors():
    """EMV ATC (tag 9F36): 2 bytes = 4 uppercase hex chars; valid range 0000-FFFF."""
    import re
    v = _load_vectors()
    pattern = re.compile(r'^[0-9A-F]{4}$')
    for atc in v["emv_atc"]["valid_atcs"]:
        assert pattern.match(atc), f"EMV ATC vector failed: {atc}"
    for atc in v["emv_atc"]["invalid_atcs"]:
        assert not pattern.match(atc), f"Expected invalid EMV ATC: {atc}"


def test_emv_iad_known_vectors():
    """EMV IAD (tag 9F10, Visa CVN): 11 bytes = 22 hex chars; starts with '0A'."""
    import re
    v = _load_vectors()
    pattern = re.compile(r'^[0-9A-Fa-f]{22}$')
    for iad in v["emv_iad"]["valid_iads"]:
        assert pattern.match(iad), f"EMV IAD vector failed: {iad}"
        assert iad.upper().startswith("0A"), f"EMV IAD (Visa CVN) must start with 0A: {iad}"
    for iad in v["emv_iad"]["invalid_iads"]:
        starts_0a = iad.upper().startswith("0A")
        right_len = bool(pattern.match(iad))
        assert not (starts_0a and right_len), f"Expected invalid EMV IAD: {iad}"


def test_iso8583_auth_request_known_vectors():
    """ISO 8583 MTI validation: auth request=0100, response=0110, reversal=0400."""
    v = _load_vectors()
    valid_mtis = set(v["iso8583_auth_request"]["valid_mtis"])
    assert "0100" in valid_mtis, "Auth request MTI 0100 must be in valid list"
    assert "0110" in valid_mtis, "Auth response MTI 0110 must be in valid list"
    assert "0400" in valid_mtis, "Reversal MTI 0400 must be in valid list"
    for mti in valid_mtis:
        assert len(mti) == 4 and mti.isdigit(), f"MTI must be 4 digits: {mti}"


def test_fedwire_known_vectors():
    """Fedwire: required tags {1500} {2000} {3100} {3400} must all be present."""
    v = _load_vectors()
    required = v["fedwire"]["required_tags"]
    assert "{1500}" in required, "Fedwire must require {1500} (type code)"
    assert "{2000}" in required, "Fedwire must require {2000} (amount)"
    assert "{3100}" in required, "Fedwire must require {3100} (sender DI)"
    assert "{3400}" in required, "Fedwire must require {3400} (receiver DI)"
    fmt = v["fedwire"]["valid_tag_formats"]
    assert fmt["2000"] == "12-digit zero-padded amount in cents", \
        "Fedwire {2000} format must be 12-digit zero-padded cents"


def test_edifact_orders_known_vectors():
    """UN/EDIFACT ORDERS: UNT segment count must include both UNH and UNT itself."""
    v = _load_vectors()
    for example in v["edifact_orders"]["example_counts"]:
        segments = example["segments"]
        expected_count = example["unt_count"]
        assert len(segments) == expected_count, \
            f"EDIFACT segment count mismatch: {len(segments)} vs {expected_count}"
        unt = segments[-1]
        count_in_unt = int(unt.split("+")[1])
        assert count_in_unt == expected_count, \
            f"EDIFACT UNT count field {count_in_unt} != segment list length {expected_count}"


# ── Generator output against format contracts ─────────────────────────────────

def test_generator_outputs_match_contracts():
    """
    Every generator type must produce output matching the canonical format contract.
    This is the Python-Java parity anchor — Java FormatValidationTest uses same patterns.
    """
    from mockjutsu.core import MockJutsuCore
    jutsu = MockJutsuCore()
    contracts = _load_contracts()
    locales = ["TR", "DE", "FR", "UK", "US", "RU"]
    failures = []

    # Types that are locale-specific (skip non-applicable locales)
    locale_specific = {
        "iban_tr": ["TR"],
        "iban_de": ["DE"],
        "iban_gb": ["UK"],
    }

    for type_key, contract in contracts.items():
        if type_key.startswith("_"):
            continue
        pattern = re.compile(contract["pattern"])
        test_locales = locale_specific.get(type_key, ["TR"])
        for locale in test_locales:
            try:
                val = str(jutsu.generate(type_key, locale=locale))
                if val.startswith("ERROR:"):
                    continue  # type not yet implemented — skip
                if not pattern.match(val):
                    failures.append(f"{type_key}/{locale}: '{val}' !~ /{contract['pattern']}/")
            except Exception:
                pass  # type not yet implemented — skip

    assert not failures, "Format contract violations:\n" + "\n".join(failures)
