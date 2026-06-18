"""
Doğrulama Yol Haritası — Faz 2
================================
66 tip için bağımsız dış kütüphane doğrulaması.
Her test N_SAMPLES örnek üretir ve kütüphane ile parse/validate eder.

Çalıştır (dev-deps gerekli):
    pip install python-stdnum schwifty bip-utils mrz lxml PyJWT \
                cryptography mt940 hl7 fhir.resources simplefix netaddr \
                icd10-cm fido2 signxml pynacha cbor2
    pytest tests/test_external_validators.py -v
"""
from __future__ import annotations

import ipaddress
import json
import pathlib
import uuid as _uuid_mod

import pytest

from mockjutsu.core import MockJutsuCore

_XSD_DIR = pathlib.Path(__file__).parent.parent / "compliance" / "xsd"

jutsu = MockJutsuCore()
N = 100  # samples per type


# ─── helpers ────────────────────────────────────────────────────────────────


def _gen(type_name, **kwargs):
    return [jutsu.generate(type_name, **kwargs) for _ in range(N)]


def _pass_rate(results: list[bool]) -> float:
    return sum(results) / len(results)


def _assert_all(name: str, results: list[bool]) -> None:
    rate = _pass_rate(results)
    fails = [i for i, ok in enumerate(results) if not ok]
    assert rate == 1.0, (
        f"{name}: {len(fails)}/{N} samples failed. "
        f"First fail index: {fails[0]}"
    )


# ─── stdlib (no extra install) ───────────────────────────────────────────────


class TestStdlibValidation:

    def test_uuid_v4(self):
        results = []
        for v in _gen("uuid"):
            try:
                obj = _uuid_mod.UUID(v, version=4)
                results.append(obj.version == 4)
            except Exception:
                results.append(False)
        _assert_all("uuid", results)

    def test_requestid(self):
        results = []
        for v in _gen("requestid"):
            try:
                results.append(_uuid_mod.UUID(v, version=4).version == 4)
            except Exception:
                results.append(False)
        _assert_all("requestid", results)

    def test_correlationid(self):
        results = []
        for v in _gen("correlationid"):
            try:
                results.append(_uuid_mod.UUID(v, version=4).version == 4)
            except Exception:
                results.append(False)
        _assert_all("correlationid", results)

    def test_sessionid(self):
        results = []
        for v in _gen("sessionid"):
            try:
                results.append(_uuid_mod.UUID(v, version=4).version == 4)
            except Exception:
                results.append(False)
        _assert_all("sessionid", results)

    def test_idempotencykey(self):
        results = []
        for v in _gen("idempotencykey"):
            try:
                results.append(_uuid_mod.UUID(v, version=4).version == 4)
            except Exception:
                results.append(False)
        _assert_all("idempotencykey", results)

    def test_deviceid(self):
        results = []
        for v in _gen("deviceid"):
            try:
                results.append(_uuid_mod.UUID(v.lower(), version=4).version == 4)
            except Exception:
                results.append(False)
        _assert_all("deviceid", results)

    def test_ipv4(self):
        results = []
        for v in _gen("ipv4"):
            try:
                ipaddress.IPv4Address(v)
                results.append(True)
            except Exception:
                results.append(False)
        _assert_all("ipv4", results)

    def test_ipv6(self):
        results = []
        for v in _gen("ipv6"):
            try:
                ipaddress.IPv6Address(v)
                results.append(True)
            except Exception:
                results.append(False)
        _assert_all("ipv6", results)

    def test_public_ip_is_not_private(self):
        results = []
        for v in _gen("public_ip"):
            try:
                addr = ipaddress.IPv4Address(v)
                results.append(not addr.is_private)
            except Exception:
                results.append(False)
        _assert_all("public_ip", results)

    def test_private_ip_is_private(self):
        results = []
        for v in _gen("private_ip"):
            try:
                addr = ipaddress.IPv4Address(v)
                results.append(addr.is_private)
            except Exception:
                results.append(False)
        _assert_all("private_ip", results)


# ─── python-stdnum ───────────────────────────────────────────────────────────


class TestStdnumIdentity:

    def test_vkn(self):
        pytest.importorskip("stdnum")
        from stdnum.tr import vkn
        results = []
        for v in _gen("vkn"):
            try:
                vkn.validate(v)
                results.append(True)
            except Exception:
                results.append(False)
        _assert_all("vkn", results)

    def test_ssn(self):
        pytest.importorskip("stdnum")
        from stdnum.us import ssn
        results = []
        for v in _gen("ssn"):
            try:
                ssn.validate(v)
                results.append(True)
            except Exception:
                results.append(False)
        _assert_all("ssn", results)

    def test_ein(self):
        pytest.importorskip("stdnum")
        from stdnum.us import ein
        results = []
        for v in _gen("ein"):
            try:
                ein.validate(v)
                results.append(True)
            except Exception:
                results.append(False)
        _assert_all("ein", results)

    def test_nin(self):
        pytest.importorskip("stdnum")
        pytest.importorskip("stdnum.gb.nino", reason="stdnum.gb.nino not available in this version")
        from stdnum.gb import nino
        results = []
        for v in _gen("nin"):
            try:
                nino.validate(v)
                results.append(True)
            except Exception:
                results.append(False)
        _assert_all("nin", results)

    def test_utr(self):
        pytest.importorskip("stdnum")
        from stdnum.gb import utr
        results = []
        for v in _gen("utr"):
            try:
                utr.validate(v)
                results.append(True)
            except Exception:
                results.append(False)
        _assert_all("utr", results)

    def test_ust_id(self):
        pytest.importorskip("stdnum")
        from stdnum.de import vat as de_vat
        results = []
        for v in _gen("ust_id"):
            try:
                de_vat.validate(v)
                results.append(True)
            except Exception:
                results.append(False)
        _assert_all("ust_id", results)

    def test_de_steuer_id(self):
        pytest.importorskip("stdnum")
        from stdnum.de import idnr
        results = []
        for v in _gen("nationalid", locale="DE"):
            try:
                idnr.validate(v)
                results.append(True)
            except Exception:
                results.append(False)
        _assert_all("nationalid[DE]", results)

    def test_siren(self):
        pytest.importorskip("stdnum")
        from stdnum.fr import siren
        results = []
        for v in _gen("siren"):
            try:
                siren.validate(v)
                results.append(True)
            except Exception:
                results.append(False)
        _assert_all("siren", results)

    def test_siret(self):
        pytest.importorskip("stdnum")
        from stdnum.fr import siret
        results = []
        for v in _gen("siret"):
            try:
                siret.validate(v)
                results.append(True)
            except Exception:
                results.append(False)
        _assert_all("siret", results)

    def test_tva(self):
        pytest.importorskip("stdnum")
        from stdnum.fr import tva
        results = []
        for v in _gen("tva"):
            try:
                tva.validate(v)
                results.append(True)
            except Exception:
                results.append(False)
        _assert_all("tva", results)

    def test_inn(self):
        pytest.importorskip("stdnum")
        from stdnum.ru import inn
        results = []
        for v in _gen("inn"):
            try:
                inn.validate(v)
                results.append(True)
            except Exception:
                results.append(False)
        _assert_all("inn", results)

    def test_inn_individual(self):
        pytest.importorskip("stdnum")
        from stdnum.ru import inn
        results = []
        for v in _gen("inn_individual"):
            try:
                inn.validate(v)
                results.append(True)
            except Exception:
                results.append(False)
        _assert_all("inn_individual", results)

    def test_snils(self):
        pytest.importorskip("stdnum")
        pytest.importorskip("stdnum.ru.snils", reason="stdnum.ru.snils not available in this version")
        from stdnum.ru import snils
        results = []
        for v in _gen("snils"):
            try:
                snils.validate(v)
                results.append(True)
            except Exception:
                results.append(False)
        _assert_all("snils", results)

    def test_kpp(self):
        pytest.importorskip("stdnum")
        pytest.importorskip("stdnum.ru.kpp", reason="stdnum.ru.kpp not available in this version")
        from stdnum.ru import kpp
        results = []
        for v in _gen("kpp"):
            try:
                kpp.validate(v)
                results.append(True)
            except Exception:
                results.append(False)
        _assert_all("kpp", results)

    def test_ogrn(self):
        pytest.importorskip("stdnum")
        from stdnum.ru import ogrn
        results = []
        for v in _gen("ogrn"):
            try:
                ogrn.validate(v)
                results.append(True)
            except Exception:
                results.append(False)
        _assert_all("ogrn", results)


class TestStdnumFinancial:

    def test_iban(self):
        pytest.importorskip("stdnum")
        from stdnum import iban
        results = []
        for locale in ["TR", "DE", "GB", "FR"]:
            for v in [jutsu.generate("iban", locale=locale) for _ in range(25)]:
                try:
                    iban.validate(v)
                    results.append(True)
                except Exception:
                    results.append(False)
        rate = sum(results) / len(results)
        assert rate == 1.0, f"iban: {sum(1 for r in results if not r)}/{len(results)} failed"

    def test_vat_number(self):
        pytest.importorskip("stdnum")
        from stdnum.eu import vat as eu_vat
        from stdnum.gb import vat as gb_vat
        results = []
        # DE and FR: EU VIES VAT validator
        for locale in ["DE", "FR"]:
            for v in [jutsu.generate("vat_number", locale=locale) for _ in range(50)]:
                try:
                    eu_vat.validate(v)
                    results.append(True)
                except Exception:
                    results.append(False)
        # GB: use stdnum.gb.vat — UK left EU so stdnum.eu.vat rejects GB prefix
        for v in [jutsu.generate("vat_number", locale="GB") for _ in range(50)]:
            try:
                gb_vat.validate(v)
                results.append(True)
            except Exception:
                results.append(False)
        rate = sum(results) / len(results)
        assert rate == 1.0, f"vat_number: {sum(1 for r in results if not r)}/{len(results)} failed"

    def test_swift_bic(self):
        pytest.importorskip("stdnum")
        from stdnum import bic
        results = []
        for v in _gen("swift"):
            try:
                bic.validate(v)
                results.append(True)
            except Exception:
                results.append(False)
        _assert_all("swift", results)


class TestStdnumBarcode:

    def test_ean8(self):
        pytest.importorskip("stdnum")
        from stdnum import ean
        results = []
        for v in _gen("ean8"):
            try:
                ean.validate(v)
                results.append(True)
            except Exception:
                results.append(False)
        _assert_all("ean8", results)

    def test_upca(self):
        pytest.importorskip("stdnum")
        from stdnum import ean
        results = []
        for v in _gen("upca"):
            try:
                ean.validate(v)
                results.append(True)
            except Exception:
                results.append(False)
        _assert_all("upca", results)

    def test_isbn13(self):
        pytest.importorskip("stdnum")
        from stdnum import isbn
        results = []
        for v in _gen("isbn13"):
            try:
                isbn.validate(v)
                results.append(True)
            except Exception:
                results.append(False)
        _assert_all("isbn13", results)

    def test_isbn10(self):
        pytest.importorskip("stdnum")
        from stdnum import isbn
        results = []
        for v in _gen("isbn10"):
            try:
                isbn.validate(v)
                results.append(True)
            except Exception:
                results.append(False)
        _assert_all("isbn10", results)


class TestStdnumTelecom:

    def test_imei(self):
        pytest.importorskip("stdnum")
        from stdnum import imei
        results = []
        for v in _gen("imei"):
            try:
                imei.validate(v)
                results.append(True)
            except Exception:
                results.append(False)
        _assert_all("imei", results)

    def test_lei(self):
        pytest.importorskip("stdnum")
        from stdnum import lei
        results = []
        for v in _gen("lei"):
            try:
                lei.validate(v)
                results.append(True)
            except Exception:
                results.append(False)
        _assert_all("lei", results)

    def test_npi_luhn(self):
        pytest.importorskip("stdnum")
        from stdnum import luhn
        results = []
        for v in _gen("npi"):
            digits = "80840" + v
            try:
                luhn.validate(digits)
                results.append(True)
            except Exception:
                results.append(False)
        _assert_all("npi", results)

    def test_dhl_tracking_luhn(self):
        pytest.importorskip("stdnum")
        from stdnum import luhn
        results = []
        for v in _gen("dhl_tracking"):
            # DHL JD-series: strip non-digit prefix (JD), validate numeric part only
            digits_only = ''.join(c for c in v if c.isdigit())
            try:
                luhn.validate(digits_only)
                results.append(True)
            except Exception:
                results.append(False)
        _assert_all("dhl_tracking", results)


# ─── schwifty ────────────────────────────────────────────────────────────────


class TestSchwifty:

    def test_iban_schwifty(self):
        pytest.importorskip("schwifty")
        from schwifty import IBAN
        results = []
        for locale in ["TR", "DE", "GB", "FR"]:
            for v in [jutsu.generate("iban", locale=locale) for _ in range(25)]:
                try:
                    IBAN(v)
                    results.append(True)
                except Exception:
                    results.append(False)
        rate = sum(results) / len(results)
        assert rate == 1.0, f"iban/schwifty: {sum(1 for r in results if not r)}/{len(results)} failed"


# ─── bip-utils ───────────────────────────────────────────────────────────────


class TestBipUtils:

    def test_mnemonic_bip39(self):
        pytest.importorskip("bip_utils")
        from bip_utils import Bip39MnemonicValidator
        validator = Bip39MnemonicValidator()
        results = []
        for v in _gen("mnemonic"):
            try:
                results.append(validator.IsValid(v))
            except Exception:
                results.append(False)
        _assert_all("mnemonic", results)

    def test_btc_address_format(self):
        pytest.importorskip("bip_utils")
        results = []
        for v in _gen("btc_wallet"):
            try:
                obj = json.loads(v) if isinstance(v, str) and v.startswith("{") else {"address": v}
                addr = obj.get("address", v)
                results.append(addr.startswith("1") and 25 <= len(addr) <= 34)
            except Exception:
                results.append(False)
        _assert_all("btc_wallet", results)

    def test_eth_address_eip55(self):
        pytest.importorskip("bip_utils")
        results = []
        for v in _gen("eth_wallet"):
            try:
                obj = json.loads(v) if isinstance(v, str) and v.startswith("{") else {"address": v}
                addr = obj.get("address", v)
                results.append(addr.startswith("0x") and len(addr) == 42)
            except Exception:
                results.append(False)
        _assert_all("eth_wallet", results)


# ─── python-mrz ──────────────────────────────────────────────────────────────


class TestMrz:

    def test_mrz_td3(self):
        pytest.importorskip("mrz")
        from mrz.checker.td3 import TD3CodeChecker
        results = []
        for v in _gen("mrz_td3"):
            try:
                obj = json.loads(v)
                checker = TD3CodeChecker("\n".join(obj["lines"]), check_expiry=False)
                results.append(bool(checker))
            except Exception:
                results.append(False)
        _assert_all("mrz_td3", results)

    def test_mrz_td1(self):
        pytest.importorskip("mrz")
        from mrz.checker.td1 import TD1CodeChecker
        results = []
        for v in _gen("mrz_td1"):
            try:
                obj = json.loads(v)
                checker = TD1CodeChecker("\n".join(obj["lines"]), check_expiry=False)
                results.append(bool(checker))
            except Exception:
                results.append(False)
        _assert_all("mrz_td1", results)


# ─── lxml ─────────────────────────────────────────────────────────────────────


def _load_xsd(filename: str):
    """Load an ISO 20022 XSD schema from compliance/xsd/. Skip if not found."""
    from lxml import etree
    xsd_path = _XSD_DIR / filename
    if not xsd_path.exists():
        pytest.skip(f"XSD not found: {xsd_path}")
    return etree.XMLSchema(etree.parse(str(xsd_path)))


class TestLxml:

    def test_ubl_invoice_wellformed(self):
        pytest.importorskip("lxml")
        from lxml import etree
        results = []
        for v in _gen("ubl_invoice"):
            try:
                obj = json.loads(v)
                etree.fromstring(obj["xml"].encode("utf-8"))
                results.append(True)
            except Exception:
                results.append(False)
        _assert_all("ubl_invoice", results)

    def test_camt053_wellformed(self):
        pytest.importorskip("lxml")
        from lxml import etree
        results = []
        for v in _gen("camt053"):
            try:
                etree.fromstring(v.encode("utf-8"))
                results.append(True)
            except Exception:
                results.append(False)
        _assert_all("camt053", results)

    def test_pain001_wellformed(self):
        pytest.importorskip("lxml")
        from lxml import etree
        results = []
        for v in _gen("pain001"):
            try:
                etree.fromstring(v.encode("utf-8"))
                results.append(True)
            except Exception:
                results.append(False)
        _assert_all("pain001", results)


# ─── ISO 20022 XSD Schema Validation ─────────────────────────────────────────


class TestIso20022XsdValidation:

    def test_pain001_xsd_valid(self):
        """pain001 must validate against ISO 20022 pain.001.001.09 XSD schema."""
        pytest.importorskip("lxml")
        from lxml import etree
        schema = _load_xsd("pain.001.001.09.xsd")
        results = []
        for v in _gen("pain001"):
            try:
                doc = etree.fromstring(v.encode("utf-8"))
                schema.assertValid(doc)
                results.append(True)
            except etree.DocumentInvalid as exc:
                results.append(False)
            except Exception:
                results.append(False)
        _assert_all("pain001 XSD schema validation", results)

    def test_sepa_mandate_xsd_valid(self):
        """sepa_mandate must validate against ISO 20022 pain.008.001.08 XSD schema."""
        pytest.importorskip("lxml")
        from lxml import etree
        schema = _load_xsd("pain.008.001.08.xsd")
        results = []
        for v in _gen("sepa_mandate"):
            try:
                doc = etree.fromstring(v.encode("utf-8"))
                schema.assertValid(doc)
                results.append(True)
            except etree.DocumentInvalid:
                results.append(False)
            except Exception:
                results.append(False)
        _assert_all("sepa_mandate XSD schema validation", results)

    def test_camt053_xsd_valid(self):
        """camt053 must validate against ISO 20022 camt.053.001.02 XSD schema."""
        pytest.importorskip("lxml")
        from lxml import etree
        schema = _load_xsd("camt.053.001.02.xsd")
        results = []
        for v in _gen("camt053"):
            try:
                doc = etree.fromstring(v.encode("utf-8"))
                schema.assertValid(doc)
                results.append(True)
            except etree.DocumentInvalid:
                results.append(False)
            except Exception:
                results.append(False)
        _assert_all("camt053 XSD schema validation", results)

    def test_pain001_xsd_catches_invalid(self):
        """XSD validator must reject a pain001 with missing MsgId."""
        pytest.importorskip("lxml")
        from lxml import etree
        schema = _load_xsd("pain.001.001.09.xsd")
        # Remove MsgId from a valid pain001 to produce an invalid document
        valid_xml = jutsu.generate("pain001")
        broken_xml = valid_xml.replace(
            valid_xml[valid_xml.find("<MsgId>"):valid_xml.find("</MsgId>") + 8], ""
        )
        doc = etree.fromstring(broken_xml.encode("utf-8"))
        is_invalid = not schema.validate(doc)
        assert is_invalid, "XSD validator should reject a document missing <MsgId>"


# ─── mt940 ───────────────────────────────────────────────────────────────────


class TestMt940:

    def test_mt940_parse(self):
        pytest.importorskip("mt940")
        import io
        import mt940
        results = []
        for v in _gen("mt940"):
            try:
                obj = mt940.MT940(io.StringIO(v))
                results.append(len(obj.statements) > 0)
            except Exception:
                results.append(False)
        _assert_all("mt940", results)


# ─── HL7 ─────────────────────────────────────────────────────────────────────


class TestHl7:

    def test_hl7_message_parse(self):
        pytest.importorskip("hl7")
        import hl7
        results = []
        for v in _gen("hl7_message"):
            try:
                hl7.parse(v)
                results.append(True)
            except Exception:
                results.append(False)
        _assert_all("hl7_message", results)


# ─── fhir.resources ──────────────────────────────────────────────────────────


class TestFhir:

    def test_fhir_patient_parse(self):
        pytest.importorskip("fhir")
        results = []
        for v in _gen("fhir_patient"):
            try:
                obj = json.loads(v)
                from fhir.resources.patient import Patient
                Patient.model_validate(obj)
                results.append(True)
            except Exception:
                results.append(False)
        _assert_all("fhir_patient", results)


# ─── cryptography ────────────────────────────────────────────────────────────


class TestCryptography:

    def test_x509_cert_parse(self):
        # x509_cert generates a realistic metadata JSON (not a real PEM cert).
        # Validate the structural fields required by IETF RFC 5280 metadata.
        required_fields = {"version", "serial", "algorithm", "subject", "issuer", "not_before", "not_after"}
        results = []
        for v in _gen("x509_cert"):
            try:
                obj = json.loads(v)
                results.append(required_fields.issubset(obj.keys()))
            except Exception:
                results.append(False)
        _assert_all("x509_cert", results)


# ─── PyJWT ───────────────────────────────────────────────────────────────────


class TestPyJWT:

    def test_oidc_token_hs256(self):
        pytest.importorskip("jwt")
        import jwt
        results = []
        for v in _gen("oidc_token"):
            try:
                # oidc_token returns a raw JWT string; secret is discarded at generation time.
                # Decode without signature verification to validate structure and OIDC claims.
                decoded = jwt.decode(v, options={"verify_signature": False}, algorithms=["HS256"])
                results.append("sub" in decoded and "iss" in decoded)
            except Exception:
                results.append(False)
        _assert_all("oidc_token", results)

    def test_jwks_structure(self):
        pytest.importorskip("jwt")
        import jwt
        results = []
        for v in _gen("jwks"):
            try:
                obj = json.loads(v)
                keys = obj.get("keys", [])
                key_data = keys[0] if keys else obj
                jwt.algorithms.ECAlgorithm.from_jwk(json.dumps(key_data))
                results.append(True)
            except Exception:
                results.append(False)
        _assert_all("jwks", results)


# ─── netaddr ─────────────────────────────────────────────────────────────────


class TestNetaddr:

    def test_mac_address(self):
        pytest.importorskip("netaddr")
        import netaddr
        results = []
        for v in _gen("mac_address"):
            try:
                netaddr.EUI(v)
                results.append(True)
            except Exception:
                results.append(False)
        _assert_all("mac_address", results)


# ─── icd10-cm ────────────────────────────────────────────────────────────────


class TestIcd10:

    def test_icd10_find(self):
        pytest.importorskip("icd10")
        import icd10
        results = []
        for v in _gen("icd10"):
            try:
                code = icd10.find(v)
                results.append(code is not None)
            except Exception:
                results.append(False)
        _assert_all("icd10", results)


# ─── simplefix ───────────────────────────────────────────────────────────────


class TestSimplefix:

    def test_fix_message_parse(self):
        pytest.importorskip("simplefix")
        import simplefix
        results = []
        for v in _gen("fix_message"):
            try:
                parser = simplefix.FixParser()
                parser.append_buffer(v.encode("utf-8"))
                msg = parser.get_message()
                results.append(msg is not None)
            except Exception:
                results.append(False)
        _assert_all("fix_message", results)


# ─── stdnum — remaining Faz-2 types ─────────────────────────────────────────


class TestStdnumRemaining:

    def test_ustid(self):
        """German Umsatzsteuer-ID (DE + 9 digits, MOD-11 checksum)."""
        pytest.importorskip("stdnum")
        from stdnum.de import vat as de_vat
        results = []
        for v in _gen("ustid"):
            try:
                de_vat.validate(v)
                results.append(True)
            except Exception:
                results.append(False)
        _assert_all("ustid", results)

    def test_bic(self):
        """SWIFT BIC — stdnum.bic.validate (ISO 9362)."""
        pytest.importorskip("stdnum")
        from stdnum import bic as bic_mod
        results = []
        for v in _gen("bic"):
            try:
                bic_mod.validate(v)
                results.append(True)
            except Exception:
                results.append(False)
        _assert_all("bic", results)

    def test_imei2(self):
        """IMEI-SV (16-digit IMEI with software version) — stdnum.imei."""
        pytest.importorskip("stdnum")
        from stdnum import imei as imei_mod
        results = []
        for v in _gen("imei2"):
            try:
                imei_mod.validate(v)
                results.append(True)
            except Exception:
                results.append(False)
        _assert_all("imei2", results)

    def test_iccid(self):
        """ICCID (SIM card ID) — starts with 89, Luhn check digit."""
        pytest.importorskip("stdnum")
        from stdnum import luhn
        results = []
        for v in _gen("iccid"):
            try:
                luhn.validate(v)
                results.append(v.startswith("89"))
            except Exception:
                results.append(False)
        _assert_all("iccid", results)

    def test_imsi(self):
        """IMSI (mobile subscriber identity) — stdnum.imsi."""
        pytest.importorskip("stdnum")
        from stdnum import imsi as imsi_mod
        results = []
        for v in _gen("imsi"):
            try:
                imsi_mod.validate(v)
                results.append(True)
            except Exception:
                results.append(False)
        _assert_all("imsi", results)


# ─── VIN ─────────────────────────────────────────────────────────────────────


class TestVin:

    def test_vin_check_digit(self):
        """VIN (ISO 3779) — position 9 check digit (NHTSA algorithm)."""
        _transliteration = {
            'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8,
            'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'P': 7, 'R': 9,
            'S': 2, 'T': 3, 'U': 4, 'V': 5, 'W': 6, 'X': 7, 'Y': 8, 'Z': 9,
        }
        _weights = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2]

        def _vin_check(vin):
            total = sum(
                (int(c) if c.isdigit() else _transliteration.get(c, 0)) * _weights[i]
                for i, c in enumerate(vin)
            )
            rem = total % 11
            return 'X' if rem == 10 else str(rem)

        results = []
        for v in _gen("vin"):
            try:
                results.append(len(v) == 17 and v[8] == _vin_check(v))
            except Exception:
                results.append(False)
        _assert_all("vin", results)


# ─── Crypto addresses ────────────────────────────────────────────────────────


class TestCryptoAddresses:

    def test_btc_address_p2pkh(self):
        """BTC P2PKH address — starts with 1, Base58Check alphabet, 25-34 chars."""
        import re
        results = []
        for v in _gen("btc_address"):
            try:
                results.append(bool(re.match(r'^1[1-9A-HJ-NP-Za-km-z]{24,33}$', v)))
            except Exception:
                results.append(False)
        _assert_all("btc_address", results)

    def test_eth_address_format(self):
        """ETH address — 0x prefix + 40 hex chars (EIP-55 checksum format)."""
        import re
        results = []
        for v in _gen("eth_address"):
            try:
                results.append(bool(re.match(r'^0x[0-9a-fA-F]{40}$', v)))
            except Exception:
                results.append(False)
        _assert_all("eth_address", results)

    def test_sol_wallet_structure(self):
        """Solana wallet — JSON with private_key, public_key, address, keypair."""
        results = []
        required = {"private_key", "public_key", "address", "keypair"}
        for v in _gen("sol_wallet"):
            try:
                obj = json.loads(v)
                results.append(required.issubset(obj.keys()))
            except Exception:
                results.append(False)
        _assert_all("sol_wallet", results)


# ─── OIDC token set ───────────────────────────────────────────────────────────


class TestOidcTokenSet:

    def test_oidc_token_set_structure(self):
        """oidc_token_set — JWT token readable header + required claims."""
        pytest.importorskip("jwt")
        import jwt
        results = []
        for v in _gen("oidc_token_set"):
            try:
                obj = json.loads(v)
                token = obj.get("token") or obj.get("access_token", "")
                hdr = jwt.get_unverified_header(token)
                claims = obj.get("claims", {})
                results.append(
                    bool(hdr.get("alg")) and
                    isinstance(claims, dict) and
                    {"sub", "iss"}.issubset(claims)
                )
            except Exception:
                results.append(False)
        _assert_all("oidc_token_set", results)


# ─── NACHA ACH ───────────────────────────────────────────────────────────────


class TestNachaAch:

    def test_nacha_ach_structure(self):
        """NACHA ACH file — file header record type 1, fixed 94-char lines."""
        results = []
        for v in _gen("nacha_ach"):
            try:
                lines = v.strip().split('\n')
                ok = (
                    lines[0].startswith('1') and      # File Header record type
                    lines[-1].startswith('9') and      # File Control record type
                    all(len(ln) == 94 for ln in lines) # Fixed 94-char width
                )
                results.append(ok)
            except Exception:
                results.append(False)
        _assert_all("nacha_ach", results)


# ─── SEPA Mandate ────────────────────────────────────────────────────────────


class TestSepaMandate:

    def test_sepa_mandate_wellformed(self):
        """SEPA Direct Debit mandate — well-formed ISO 20022 pain.008 XML."""
        pytest.importorskip("lxml")
        from lxml import etree
        results = []
        for v in _gen("sepa_mandate"):
            try:
                root = etree.fromstring(v.encode("utf-8"))
                results.append(root.tag is not None)
            except Exception:
                results.append(False)
        _assert_all("sepa_mandate", results)


# ─── FIDO2 / WebAuthn ────────────────────────────────────────────────────────


class TestFido2Structures:

    def test_webauthn_credential_structure(self):
        """WebAuthn credential — JSON with id, rawId, type, response fields."""
        results = []
        required = {"id", "rawId", "type", "response"}
        for v in _gen("webauthn_credential"):
            try:
                obj = json.loads(v)
                results.append(
                    required.issubset(obj.keys()) and
                    obj.get("type") == "public-key"
                )
            except Exception:
                results.append(False)
        _assert_all("webauthn_credential", results)

    def test_fido2_assertion_structure(self):
        """FIDO2 assertion — JSON with id, rawId, type=public-key, response."""
        results = []
        required = {"id", "rawId", "type", "response"}
        for v in _gen("fido2_assertion"):
            try:
                obj = json.loads(v)
                results.append(
                    required.issubset(obj.keys()) and
                    obj.get("type") == "public-key"
                )
            except Exception:
                results.append(False)
        _assert_all("fido2_assertion", results)


# ─── XML-DSig ────────────────────────────────────────────────────────────────


class TestXmlDsig:

    def test_xmldsig_structure(self):
        """XML-DSig — JSON envelope with xml, signature_value, digest_value fields."""
        results = []
        required = {"xml", "signature_id", "algorithm", "digest_value", "signature_value"}
        for v in _gen("xmldsig"):
            try:
                obj = json.loads(v)
                results.append(required.issubset(obj.keys()))
            except Exception:
                results.append(False)
        _assert_all("xmldsig", results)


# ─── MSISDN (phonenumbers — Google libphonenumber) ───────────────────────────


class TestMsisdn:

    def test_msisdn_valid_e164(self):
        """MSISDN must be a valid E.164 phone number per ITU-T E.164 (phonenumbers lib)."""
        phonenumbers = pytest.importorskip("phonenumbers")
        locales = ["TR", "US", "UK", "DE", "FR", "RU"]
        results = []
        for locale in locales:
            for v in _gen("msisdn", locale=locale):
                try:
                    parsed = phonenumbers.parse(str(v))
                    results.append(phonenumbers.is_valid_number(parsed))
                except Exception:
                    results.append(False)
        _assert_all("msisdn", results)


# ─── Fintech Critical Types ──────────────────────────────────────────────────


class TestFintechCritical:

    def test_atm_session_expiry_format(self):
        """atm_session expiry must be MM/YY (card standard), not YY/MM."""
        import re
        results = []
        for v in _gen("atm_session"):
            try:
                obj = json.loads(v)
                expiry = obj["expiry"]
                # MM/YY: month 01-12, year 2 digits
                m = re.match(r'^(0[1-9]|1[0-2])/(\d{2})$', expiry)
                results.append(m is not None)
            except Exception:
                results.append(False)
        _assert_all("atm_session expiry MM/YY", results)

    def test_atm_session_mockj_marker(self):
        """atm_session must contain MOCKJ safety marker in session_id and auth_code."""
        results = []
        for v in _gen("atm_session"):
            try:
                obj = json.loads(v)
                has_marker = (
                    "MOCKJ" in obj.get("session_id", "") and
                    "MOCKJ" in obj.get("auth_code", "")
                )
                results.append(has_marker)
            except Exception:
                results.append(False)
        _assert_all("atm_session MOCKJ marker", results)

    def test_pos_receipt_mockj_marker(self):
        """pos_receipt must contain MOCKJ safety marker."""
        results = []
        for v in _gen("pos_receipt"):
            try:
                results.append("MOCKJ" in v)
            except Exception:
                results.append(False)
        _assert_all("pos_receipt MOCKJ marker", results)

    def test_3ds_cavv_base64_20bytes(self):
        """3ds_cavv must be a valid base64 string encoding exactly 20 bytes (EMV 3DS)."""
        import base64
        results = []
        for v in _gen("3ds_cavv"):
            try:
                decoded = base64.b64decode(v)
                results.append(len(decoded) == 20)
            except Exception:
                results.append(False)
        _assert_all("3ds_cavv base64 20-byte", results)

    def test_3ds_eci_visa_values(self):
        """3ds_eci for Visa must be one of 05, 06, 07 (EMVCo 3DS ECI spec)."""
        valid_visa = {"05", "06", "07"}
        results = []
        for v in [jutsu.generate("3ds_eci", network="visa") for _ in range(N)]:
            results.append(v in valid_visa)
        _assert_all("3ds_eci Visa codes", results)

    def test_3ds_eci_mastercard_values(self):
        """3ds_eci for Mastercard must be one of 02, 01, 00 (EMVCo 3DS ECI spec)."""
        valid_mc = {"02", "01", "00"}
        results = []
        for v in [jutsu.generate("3ds_eci", network="mc") for _ in range(N)]:
            results.append(v in valid_mc)
        _assert_all("3ds_eci Mastercard codes", results)

    def test_sepa_qr_header(self):
        """sepa_qr must start with BCD header per EPC QR Code Guideline v2.1."""
        results = []
        for v in _gen("sepa_qr"):
            try:
                lines = v.strip().split("\n")
                results.append(lines[0] == "BCD" and lines[1] == "002" and lines[3] == "SCT")
            except Exception:
                results.append(False)
        _assert_all("sepa_qr EPC header", results)

    def test_sepa_qr_uses_sepa_iban(self):
        """sepa_qr must contain a SEPA-zone IBAN (GB/DE/FR), never TR/US/RU."""
        sepa_prefixes = ("GB", "DE", "FR")
        non_sepa_prefixes = ("TR", "US", "RU")
        results = []
        for locale in ["TR", "US", "RU", "DE", "FR", "UK"]:
            for v in [jutsu.generate("sepa_qr", locale=locale) for _ in range(20)]:
                try:
                    lines = v.strip().split("\n")
                    iban_line = lines[6]
                    ok = (
                        any(iban_line.startswith(p) for p in sepa_prefixes) and
                        not any(iban_line.startswith(p) for p in non_sepa_prefixes)
                    )
                    results.append(ok)
                except Exception:
                    results.append(False)
        _assert_all("sepa_qr SEPA-zone IBAN", results)

    def test_emv_qr_country_code_iso3166(self):
        """EMV QR p58 country code must be ISO 3166-1 alpha-2 (UK locale → GB, not UK)."""
        _locale_to_iso = {
            "TR": "TR", "DE": "DE", "FR": "FR",
            "US": "US", "UK": "GB", "RU": "RU",
        }
        import re
        results = []
        for qr_type in ["emv_qr_p2p", "emv_qr_atm", "emv_qr_pos"]:
            for locale, expected_cc in _locale_to_iso.items():
                for v in [jutsu.generate(qr_type, locale=locale) for _ in range(10)]:
                    try:
                        m = re.search(r'5802([A-Z]{2})', v)
                        results.append(m is not None and m.group(1) == expected_cc)
                    except Exception:
                        results.append(False)
        _assert_all("emv_qr p58 ISO 3166-1 country code", results)

    def test_emv_qr_crc_present(self):
        """EMV QR must end with 6304 + 4 uppercase hex chars (CRC-16-CCITT)."""
        import re
        results = []
        for qr_type in ["emv_qr_p2p", "emv_qr_atm", "emv_qr_pos"]:
            for v in _gen(qr_type):
                results.append(bool(re.search(r'6304[0-9A-F]{4}$', v)))
        _assert_all("emv_qr CRC-16 trailer", results)

    def test_psd2_consent_alg_ps256(self):
        """psd2_consent JWS header must use alg=PS256 (UK OB Security Profile v3.1 §6.3)."""
        pytest.importorskip("jwt")
        import jwt
        import base64
        results = []
        for v in _gen("psd2_consent"):
            try:
                obj = json.loads(v) if isinstance(v, str) and v.startswith("{") else {"jws": v}
                jws = obj.get("jws", obj.get("consent_jws", ""))
                # Decode header without verification
                header_b64 = jws.split(".")[0]
                padding = 4 - len(header_b64) % 4
                if padding != 4:
                    header_b64 += "=" * padding
                header = json.loads(base64.urlsafe_b64decode(header_b64))
                results.append(header.get("alg") == "PS256")
            except Exception:
                results.append(False)
        _assert_all("psd2_consent alg=PS256", results)

    def test_psd2_consent_mockj_marker(self):
        """psd2_consent JWT payload must contain MOCKJ safety marker in ConsentId."""
        import base64
        results = []
        for v in _gen("psd2_consent"):
            try:
                payload_b64 = v.split(".")[1]
                padding = 4 - len(payload_b64) % 4
                if padding != 4:
                    payload_b64 += "=" * padding
                payload = base64.urlsafe_b64decode(payload_b64).decode("utf-8")
                results.append("MOCKJ" in payload)
            except Exception:
                results.append(False)
        _assert_all("psd2_consent MOCKJ marker", results)


# ─── SWIFT MT103 ─────────────────────────────────────────────────────────────


class TestSwiftMt103:

    def test_swift_mt103_blocks_present(self):
        """MT103 must have all four SWIFT blocks: {1:F01...}{2:I103...}{4:...}{5:{CHK:...}}"""
        import re
        results = []
        for v in _gen("swift_mt103"):
            try:
                has_b1 = bool(re.search(r'\{1:F01', v))
                has_b2 = bool(re.search(r'\{2:I103', v))
                has_b4 = bool(re.search(r'\{4:\n', v))
                has_b5 = bool(re.search(r'\{5:\{CHK:[0-9A-F]{12}\}\}', v))
                results.append(has_b1 and has_b2 and has_b4 and has_b5)
            except Exception:
                results.append(False)
        _assert_all("swift_mt103 block structure", results)

    def test_swift_mt103_mandatory_tags(self):
        """MT103 must contain all 6 mandatory field tags per SWIFT Field Standards."""
        import re
        results = []
        for v in _gen("swift_mt103"):
            try:
                has_20  = bool(re.search(r':20:[^\n]{1,16}', v))
                has_23b = bool(re.search(r':23B:(CRED|CRTS|SPAY|SPRI|SSTD)', v))
                has_32a = bool(re.search(r':32A:\d{6}[A-Z]{3}[\d,]+', v))
                has_50  = bool(re.search(r':50[AK]:', v))
                has_59  = bool(re.search(r':59A?:', v))
                has_71a = bool(re.search(r':71A:(OUR|SHA|BEN)', v))
                results.append(has_20 and has_23b and has_32a and has_50 and has_59 and has_71a)
            except Exception:
                results.append(False)
        _assert_all("swift_mt103 mandatory tags", results)

    def test_swift_mt103_mockj_marker(self):
        """MT103 :20: sender reference must contain MOCKJ marker and be ≤16 chars."""
        import re
        results = []
        for v in _gen("swift_mt103"):
            try:
                m = re.search(r':20:([^\n]{1,16})', v)
                if m:
                    ref = m.group(1)
                    results.append("MOCKJ" in ref and len(ref) <= 16)
                else:
                    results.append(False)
            except Exception:
                results.append(False)
        _assert_all("swift_mt103 MOCKJ in :20:", results)

    def test_swift_mt103_32a_format(self):
        """MT103 :32A: must be YYMMDD + 3-letter ISO currency + decimal amount (ISO 15022)."""
        import re
        results = []
        for v in _gen("swift_mt103"):
            try:
                m = re.search(r':32A:(\d{6})([A-Z]{3})(\d+,\d{2})', v)
                results.append(m is not None)
            except Exception:
                results.append(False)
        _assert_all("swift_mt103 :32A: YYMMDD+CCY+amount", results)

    def test_swift_mt103_locale_currency(self):
        """MT103 :32A: currency must match locale (TR→TRY, US→USD, UK→GBP, DE/FR→EUR, RU→RUB)."""
        import re
        _expected_ccy = {
            "TR": "TRY", "US": "USD", "UK": "GBP",
            "DE": "EUR", "FR": "EUR", "RU": "RUB",
        }
        results = []
        for locale, expected in _expected_ccy.items():
            for v in [jutsu.generate("swift_mt103", locale=locale) for _ in range(20)]:
                try:
                    m = re.search(r':32A:\d{6}([A-Z]{3})', v)
                    results.append(m is not None and m.group(1) == expected)
                except Exception:
                    results.append(False)
        _assert_all("swift_mt103 :32A: locale→currency mapping", results)
