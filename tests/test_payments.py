"""
mock-jutsu — Payment Messaging Standards Tests (Wave 8-A)
TDD Red Phase: SWIFT MT103, ISO 20022 Pain.001, NACHA ACH, SEPA Mandate, Fedwire
"""
import re
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import mockjutsu.core as mc

jutsu = mc.MockJutsuCore()


# ─────────────────────────────────────────────────────────────
# G29. SWIFT MT103
# ─────────────────────────────────────────────────────────────
class TestSwiftMT103:
    def test_returns_string(self):
        val = jutsu.generate("swift_mt103")
        assert isinstance(val, str)

    def test_has_mandatory_field_tags(self):
        val = jutsu.generate("swift_mt103")
        # Mandatory fields per MT103 spec
        assert ":20:" in val   # Sender's Reference
        assert ":23B:" in val  # Bank Operation Code
        assert ":32A:" in val  # Value Date / Currency / Amount
        assert ":50K:" in val  # Ordering Customer
        assert ":59:" in val   # Beneficiary Customer
        assert ":71A:" in val  # Details of Charges

    def test_field_20_max_16_chars(self):
        val = jutsu.generate("swift_mt103")
        ref = re.search(r":20:(.+)", val).group(1).strip()
        assert 1 <= len(ref) <= 16

    def test_field_23b_valid_code(self):
        val = jutsu.generate("swift_mt103")
        code = re.search(r":23B:(.+)", val).group(1).strip()
        assert code in ("CRED", "CRTS", "SPAY", "SPRI", "SSTD")

    def test_field_32a_format(self):
        # Format: YYMMDDCCCAMOUNT  e.g. 261231EUR1234,56
        val = jutsu.generate("swift_mt103")
        f32 = re.search(r":32A:(.+)", val).group(1).strip()
        assert re.match(r"^\d{6}[A-Z]{3}[\d,]+$", f32), f"Invalid :32A: format: {f32}"

    def test_field_71a_charges_code(self):
        val = jutsu.generate("swift_mt103")
        charges = re.search(r":71A:(.+)", val).group(1).strip()
        assert charges in ("OUR", "SHA", "BEN")

    def test_bulk_unique(self):
        results = [jutsu.generate("swift_mt103") for _ in range(10)]
        refs = [re.search(r":20:(.+)", r).group(1).strip() for r in results]
        assert len(set(refs)) > 1

    def test_locale_aware(self):
        tr = jutsu.generate("swift_mt103", locale="TR")
        de = jutsu.generate("swift_mt103", locale="DE")
        # Currency should reflect locale
        tr_ccy = re.search(r":32A:\d{6}([A-Z]{3})", tr).group(1)
        de_ccy = re.search(r":32A:\d{6}([A-Z]{3})", de).group(1)
        assert tr_ccy == "TRY"
        assert de_ccy == "EUR"


# ─────────────────────────────────────────────────────────────
# G30. ISO 20022 Pain.001
# ─────────────────────────────────────────────────────────────
class TestPain001:
    def test_returns_string(self):
        val = jutsu.generate("pain001")
        assert isinstance(val, str)

    def test_valid_xml_structure(self):
        val = jutsu.generate("pain001")
        assert val.startswith("<?xml")
        assert "pain.001" in val
        assert "<GrpHdr>" in val
        assert "<PmtInf>" in val
        assert "<CdtTrfTxInf>" in val

    def test_has_msg_id(self):
        val = jutsu.generate("pain001")
        assert re.search(r"<MsgId>[^<]+</MsgId>", val)

    def test_has_creation_datetime(self):
        val = jutsu.generate("pain001")
        # ISO 8601: 2026-05-14T12:00:00
        assert re.search(r"<CreDtTm>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}</CreDtTm>", val)

    def test_has_debtor_iban(self):
        val = jutsu.generate("pain001")
        iban = re.search(r"<DbtrAcct>.*?<Id>.*?<IBAN>([A-Z]{2}\d{2}[A-Z0-9]+)</IBAN>", val, re.DOTALL)
        assert iban, "No debtor IBAN found"

    def test_has_creditor_iban(self):
        val = jutsu.generate("pain001")
        iban = re.search(r"<CdtrAcct>.*?<Id>.*?<IBAN>([A-Z]{2}\d{2}[A-Z0-9]+)</IBAN>", val, re.DOTALL)
        assert iban, "No creditor IBAN found"

    def test_has_bic_codes(self):
        val = jutsu.generate("pain001")
        # Debtor and Creditor agent BICs
        bics = re.findall(r"<BICFI>([A-Z]{6}[A-Z0-9]{2,5})</BICFI>", val)
        assert len(bics) >= 2

    def test_amount_positive(self):
        val = jutsu.generate("pain001")
        amount = re.search(r"<InstdAmt Ccy=\"[A-Z]{3}\">([\d.]+)</InstdAmt>", val)
        assert amount
        assert float(amount.group(1)) > 0

    def test_end_to_end_id_present(self):
        val = jutsu.generate("pain001")
        assert re.search(r"<EndToEndId>[^<]+</EndToEndId>", val)

    def test_bulk_unique_msg_id(self):
        ids = []
        for _ in range(5):
            v = jutsu.generate("pain001")
            ids.append(re.search(r"<MsgId>([^<]+)</MsgId>", v).group(1))
        assert len(set(ids)) == 5


# ─────────────────────────────────────────────────────────────
# G31. NACHA ACH
# ─────────────────────────────────────────────────────────────
class TestNachaAch:
    def test_returns_string(self):
        val = jutsu.generate("nacha_ach")
        assert isinstance(val, str)

    def test_has_all_record_types(self):
        val = jutsu.generate("nacha_ach")
        lines = val.strip().splitlines()
        type_codes = {l[0] for l in lines if l}
        assert "1" in type_codes  # File Header
        assert "5" in type_codes  # Batch Header
        assert "6" in type_codes  # Entry Detail
        assert "8" in type_codes  # Batch Control
        assert "9" in type_codes  # File Control

    def test_record_length_94(self):
        val = jutsu.generate("nacha_ach")
        for line in val.strip().splitlines():
            assert len(line) == 94, f"Line not 94 chars: {repr(line)}"

    def test_file_header_format(self):
        val = jutsu.generate("nacha_ach")
        header = next(l for l in val.splitlines() if l.startswith("1"))
        assert header[1:3] == "01"   # Priority Code
        assert header[9:23].strip()  # Immediate Destination (routing)

    def test_entry_detail_routing_9_digits(self):
        val = jutsu.generate("nacha_ach")
        entry = next(l for l in val.splitlines() if l.startswith("6"))
        routing = entry[3:12]
        assert routing.isdigit() and len(routing) == 9

    def test_batch_control_hash_total(self):
        # Hash = sum of all Entry Detail routing numbers, last 10 digits
        val = jutsu.generate("nacha_ach")
        lines = val.strip().splitlines()
        entries = [l for l in lines if l.startswith("6")]
        routing_sum = sum(int(e[3:11]) for e in entries)
        hash_total = str(routing_sum % 10**10).zfill(10)
        batch_ctrl = next(l for l in lines if l.startswith("8"))
        # NACHA spec: Entry Hash at 1-indexed positions 11-20 = Python [10:20]
        assert batch_ctrl[10:20] == hash_total

    def test_sec_code_valid(self):
        val = jutsu.generate("nacha_ach")
        batch_hdr = next(l for l in val.splitlines() if l.startswith("5"))
        sec = batch_hdr[50:53]
        assert sec in ("PPD", "CCD", "CTX", "WEB", "TEL")

    def test_bulk_unique(self):
        vals = [jutsu.generate("nacha_ach") for _ in range(5)]
        # File header trace numbers differ
        assert len(set(v[:94] for v in vals)) > 1


# ─────────────────────────────────────────────────────────────
# G32. SEPA Direct Debit Mandate
# ─────────────────────────────────────────────────────────────
class TestSepaMandate:
    def test_returns_string(self):
        val = jutsu.generate("sepa_mandate")
        assert isinstance(val, str)

    def test_has_mandate_reference(self):
        val = jutsu.generate("sepa_mandate")
        assert "MandateRef" in val or "mandate_ref" in val or "UMR" in val

    def test_creditor_id_format(self):
        # Format: CC + 2 check digits + 3 char business code + up to 28 national ID
        val = jutsu.generate("sepa_mandate")
        cid = re.search(r"[A-Z]{2}\d{2}[A-Z]{3}[A-Z0-9]+", val)
        assert cid, f"No Creditor ID found in: {val}"

    def test_creditor_id_check_digits(self):
        # Check digits: same MOD-97 as IBAN
        val = jutsu.generate("sepa_mandate")
        cid = re.search(r"([A-Z]{2})(\d{2})([A-Z]{3}[A-Z0-9]+)", val).group(0)
        country = cid[:2]
        check = int(cid[2:4])
        rest = cid[4:]
        # Rearrange: rest + country + check digits → numeric → MOD 97 = 1
        rearranged = rest + country + cid[2:4]
        numeric = "".join(str(ord(c) - 55) if c.isalpha() else c for c in rearranged)
        assert int(numeric) % 97 == 1

    def test_debtor_iban_present(self):
        val = jutsu.generate("sepa_mandate")
        assert re.search(r"[A-Z]{2}\d{2}[A-Z0-9]{4,}", val)

    def test_sequence_type_valid(self):
        val = jutsu.generate("sepa_mandate")
        assert any(seq in val for seq in ("FRST", "RCUR", "FNAL", "OOFF"))

    def test_signing_date_format(self):
        val = jutsu.generate("sepa_mandate")
        assert re.search(r"\d{4}-\d{2}-\d{2}", val)

    def test_bulk_unique_mandate_ref(self):
        vals = [jutsu.generate("sepa_mandate") for _ in range(10)]
        assert len(set(vals)) > 1


# ─────────────────────────────────────────────────────────────
# G33. Fedwire Funds Transfer
# ─────────────────────────────────────────────────────────────
class TestFedwire:
    def test_returns_string(self):
        val = jutsu.generate("fedwire")
        assert isinstance(val, str)

    def test_has_mandatory_tags(self):
        val = jutsu.generate("fedwire")
        assert "{1500}" in val  # Sender Reference
        assert "{2000}" in val  # Amount
        assert "{3100}" in val  # Sender DI
        assert "{3400}" in val  # Receiver DI

    def test_amount_format(self):
        # {2000} amount: 12-digit zero-padded cents, e.g. 000000100000 = $1000.00
        val = jutsu.generate("fedwire")
        amount_str = re.search(r"\{2000\}(\d+)", val).group(1)
        assert len(amount_str) == 12
        assert int(amount_str) > 0

    def test_sender_routing_9_digits(self):
        val = jutsu.generate("fedwire")
        routing = re.search(r"\{3100\}(\d{9})", val).group(1)
        assert routing.isdigit() and len(routing) == 9

    def test_receiver_routing_9_digits(self):
        val = jutsu.generate("fedwire")
        routing = re.search(r"\{3400\}(\d{9})", val).group(1)
        assert routing.isdigit() and len(routing) == 9

    def test_type_subtype_code(self):
        val = jutsu.generate("fedwire")
        # {1510} TypeCode: 10=Transfer, 15=Book, 16=Settlement
        tsc = re.search(r"\{1510\}(\d{4})", val)
        assert tsc
        type_code = tsc.group(1)[:2]
        assert type_code in ("10", "15", "16")

    def test_sender_reference_format(self):
        val = jutsu.generate("fedwire")
        ref = re.search(r"\{1500\}(\S+)", val).group(1)
        assert 1 <= len(ref) <= 16

    def test_bulk_unique(self):
        refs = []
        for _ in range(10):
            v = jutsu.generate("fedwire")
            refs.append(re.search(r"\{1500\}(\S+)", v).group(1))
        assert len(set(refs)) > 1
