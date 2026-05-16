"""
tests/test_hl7_fhir_dicom.py

God Mode #6 — HL7 v2.5 / FHIR R4 / DICOM UID

Standards:
  HL7 v2.5 §2.9 (segment structure), §2.3 (data types), §3.3.1 (ADT^A01)
  HL7 FHIR R4 (v4.0.1) §8.1 Patient resource
  NEMA DICOM PS3.5 §9.1 + ISO/IEC 9834-8 (UUID-based UID root 2.25)
"""

import json
import re
import pytest

from mockjutsu.generators.health import HealthGenerator
from mockjutsu.core import MockJutsuCore
from click.testing import CliRunner
from mockjutsu.cli import main

gen = HealthGenerator()
jutsu = MockJutsuCore(locale="TR")

# ─────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────

def _parse_hl7(msg: str) -> dict[str, list[str]]:
    """Returns {segment_name: [fields]} for each CR-terminated segment."""
    segments = {}
    for seg in msg.split("\r"):
        if not seg.strip():
            continue
        fields = seg.split("|")
        segments[fields[0]] = fields
    return segments


# ═════════════════════════════════════════════════════════════════
# HL7 v2.5 ADT^A01 Tests
# ═════════════════════════════════════════════════════════════════

class TestHL7Message:

    def _msg(self):
        return gen.generate_hl7_message()

    def test_returns_string(self):
        assert isinstance(self._msg(), str)

    def test_has_four_segments(self):
        segs = _parse_hl7(self._msg())
        assert set(segs.keys()) == {"MSH", "EVN", "PID", "PV1"}

    def test_msh_segment_type(self):
        segs = _parse_hl7(self._msg())
        assert segs["MSH"][0] == "MSH"

    def test_encoding_characters(self):
        segs = _parse_hl7(self._msg())
        # Array[1] = MSH.2 (encoding chars); MSH.1 is "|" itself — not a split element
        assert segs["MSH"][1] == r"^~\&"

    def test_message_type_adt_a01(self):
        segs = _parse_hl7(self._msg())
        # Array[8] = MSH.9 (message type)
        assert segs["MSH"][8] == "ADT^A01^ADT_A01"

    def test_processing_id_production(self):
        segs = _parse_hl7(self._msg())
        # Array[10] = MSH.11 (processing ID)
        assert segs["MSH"][10] == "P"

    def test_hl7_version(self):
        segs = _parse_hl7(self._msg())
        # Array[11] = MSH.12 (version ID)
        assert segs["MSH"][11] == "2.5"

    def test_datetime_format(self):
        segs = _parse_hl7(self._msg())
        # Array[6] = MSH.7 (date/time of message)
        ts = segs["MSH"][6]
        # YYYYMMDDHHMMSS — 14 digits
        assert re.fullmatch(r"\d{14}", ts), f"Bad datetime: {ts!r}"

    def test_message_control_id_format(self):
        segs = _parse_hl7(self._msg())
        # Array[9] = MSH.10 (message control ID)
        ctrl_id = segs["MSH"][9]
        assert ctrl_id.startswith("MSG")
        assert len(ctrl_id) == 11  # MSG + 8 hex chars

    def test_message_control_id_unique(self):
        # Array[9] = MSH.10
        ids = {_parse_hl7(gen.generate_hl7_message())["MSH"][9] for _ in range(100)}
        assert len(ids) == 100

    def test_evn_event_type(self):
        segs = _parse_hl7(self._msg())
        assert segs["EVN"][1] == "A01"

    def test_pid_mrn_present(self):
        segs = _parse_hl7(self._msg())
        # PID-3 contains MRN^^^FAC^MR
        pid3 = segs["PID"][3]
        assert "MRN" in pid3
        assert "MR" in pid3

    def test_pid_gender_valid(self):
        genders = set()
        for _ in range(30):
            segs = _parse_hl7(gen.generate_hl7_message())
            genders.add(segs["PID"][8])
        assert genders.issubset({"M", "F"})

    def test_pid_dob_format(self):
        segs = _parse_hl7(self._msg())
        dob = segs["PID"][7]
        assert re.fullmatch(r"\d{8}", dob), f"Bad DOB: {dob!r}"

    def test_pv1_patient_class_inpatient(self):
        segs = _parse_hl7(self._msg())
        assert segs["PV1"][2] == "I"

    def test_pv1_location_has_unit_room_bed(self):
        segs = _parse_hl7(self._msg())
        location = segs["PV1"][3]
        parts = location.split("^")
        assert len(parts) == 3
        assert parts[1].isdigit()
        assert parts[2] in {"A", "B", "C"}

    def test_cr_segment_terminator(self):
        msg = self._msg()
        assert "\r" in msg
        assert msg.endswith("\r")

    def test_via_core(self):
        result = jutsu.generate("hl7_message")
        assert "MSH" in result
        assert "ADT^A01" in result

    def test_via_cli(self):
        runner = CliRunner()
        result = runner.invoke(main, ["generate", "hl7_message"])
        assert result.exit_code == 0
        assert "MSH" in result.output


# ═════════════════════════════════════════════════════════════════
# FHIR R4 Patient Resource Tests
# ═════════════════════════════════════════════════════════════════

class TestFhirPatient:

    def _patient(self, locale="TR") -> dict:
        raw = gen.generate_fhir_patient(locale=locale)
        return json.loads(raw)

    def test_returns_string(self):
        assert isinstance(gen.generate_fhir_patient(), str)

    def test_valid_json(self):
        raw = gen.generate_fhir_patient()
        data = json.loads(raw)
        assert isinstance(data, dict)

    def test_resource_type(self):
        assert self._patient()["resourceType"] == "Patient"

    def test_id_is_uuid_format(self):
        pat = self._patient()
        uuid_re = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")
        assert uuid_re.match(pat["id"]), f"Bad UUID: {pat['id']}"

    def test_unique_ids(self):
        ids = {json.loads(gen.generate_fhir_patient())["id"] for _ in range(50)}
        assert len(ids) == 50

    def test_name_has_family_and_given(self):
        pat = self._patient()
        name = pat["name"][0]
        assert "family" in name
        assert "given" in name
        assert isinstance(name["given"], list)
        assert len(name["given"]) >= 1

    def test_gender_valid(self):
        genders = {json.loads(gen.generate_fhir_patient())["gender"] for _ in range(30)}
        assert genders.issubset({"male", "female", "other", "unknown"})

    def test_birth_date_format(self):
        pat = self._patient()
        bd = pat["birthDate"]
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", bd), f"Bad birthDate: {bd}"

    def test_identifier_list(self):
        pat = self._patient()
        assert isinstance(pat.get("identifier"), list)
        assert len(pat["identifier"]) >= 1

    def test_telecom_list(self):
        pat = self._patient()
        assert isinstance(pat.get("telecom"), list)
        assert len(pat["telecom"]) >= 1

    def test_telecom_system_valid(self):
        pat = self._patient()
        systems = {t["system"] for t in pat["telecom"]}
        assert systems.issubset({"phone", "email"})

    def test_address_list(self):
        pat = self._patient()
        assert isinstance(pat.get("address"), list)
        addr = pat["address"][0]
        assert "city" in addr
        assert "country" in addr

    def test_meta_version_id(self):
        pat = self._patient()
        assert pat["meta"]["versionId"] == "1"

    def test_active_flag(self):
        pat = self._patient()
        assert pat["active"] is True

    def test_locale_uk_country(self):
        pat = self._patient(locale="UK")
        country = pat["address"][0]["country"]
        assert country == "GB"

    def test_locale_us_country(self):
        pat = self._patient(locale="US")
        country = pat["address"][0]["country"]
        assert country == "US"

    def test_locale_tr_country(self):
        pat = self._patient(locale="TR")
        country = pat["address"][0]["country"]
        assert country == "TR"

    def test_locale_de_country(self):
        pat = self._patient(locale="DE")
        country = pat["address"][0]["country"]
        assert country == "DE"

    def test_via_core(self):
        raw = jutsu.generate("fhir_patient")
        data = json.loads(raw)
        assert data["resourceType"] == "Patient"

    def test_via_cli(self):
        runner = CliRunner()
        result = runner.invoke(main, ["generate", "fhir_patient"])
        assert result.exit_code == 0
        data = json.loads(result.output.strip())
        assert data["resourceType"] == "Patient"

    def test_via_cli_with_locale(self):
        runner = CliRunner()
        result = runner.invoke(main, ["generate", "fhir_patient", "--locale", "US"])
        assert result.exit_code == 0
        data = json.loads(result.output.strip())
        assert data["address"][0]["country"] == "US"

    def test_telecom_e164_country_code_per_locale(self):
        """FHIR patient phone must use correct E.164 country code per locale."""
        expected = {"TR": "90", "US": "1", "UK": "44", "DE": "49", "FR": "33", "RU": "7"}
        for locale, cc in expected.items():
            for _ in range(10):
                pat = self._patient(locale=locale)
                phones = [t["value"] for t in pat["telecom"] if t["system"] == "phone"]
                for phone in phones:
                    assert phone.startswith(f"+{cc}-"), \
                        f"FHIR {locale} phone must start with +{cc}-, got: {phone}"


# ═════════════════════════════════════════════════════════════════
# DICOM UID Tests
# ═════════════════════════════════════════════════════════════════

class TestDicomUid:

    def _uid(self):
        return gen.generate_dicom_uid()

    def test_returns_string(self):
        assert isinstance(self._uid(), str)

    def test_only_digits_and_dots(self):
        uid = self._uid()
        assert re.fullmatch(r"[\d.]+", uid), f"Invalid chars in UID: {uid!r}"

    def test_max_64_chars(self):
        for _ in range(100):
            uid = gen.generate_dicom_uid()
            assert len(uid) <= 64, f"UID too long ({len(uid)}): {uid}"

    def test_starts_with_root_2_25(self):
        uid = self._uid()
        assert uid.startswith("2.25.")

    def test_suffix_is_numeric(self):
        uid = self._uid()
        suffix = uid[len("2.25."):]
        assert suffix.isdigit()

    def test_suffix_max_39_digits(self):
        # 2^128 has 39 digits → UUID-derived decimal fits in 39 chars
        uid = self._uid()
        suffix = uid[len("2.25."):]
        assert len(suffix) <= 39

    def test_no_component_starts_with_zero_unless_zero_itself(self):
        for _ in range(50):
            uid = gen.generate_dicom_uid()
            for component in uid.split("."):
                if len(component) > 1:
                    assert not component.startswith("0"), \
                        f"Component {component!r} starts with 0 in UID {uid!r}"

    def test_no_empty_components(self):
        uid = self._uid()
        for comp in uid.split("."):
            assert comp != "", f"Empty component in UID: {uid!r}"

    def test_does_not_start_or_end_with_dot(self):
        uid = self._uid()
        assert not uid.startswith(".")
        assert not uid.endswith(".")

    def test_unique(self):
        uids = {gen.generate_dicom_uid() for _ in range(100)}
        assert len(uids) == 100

    def test_via_core(self):
        uid = jutsu.generate("dicom_uid")
        assert uid.startswith("2.25.")
        assert re.fullmatch(r"[\d.]+", uid)

    def test_via_cli(self):
        runner = CliRunner()
        result = runner.invoke(main, ["generate", "dicom_uid"])
        assert result.exit_code == 0
        uid = result.output.strip()
        assert uid.startswith("2.25.")
        assert re.fullmatch(r"[\d.]+", uid)
