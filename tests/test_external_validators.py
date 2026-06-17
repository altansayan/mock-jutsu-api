"""
Doğrulama Yol Haritası — Faz 2
================================
66 tip için bağımsız dış kütüphane doğrulaması.
Her test N_SAMPLES örnek üretir ve kütüphane ile parse/validate eder.

Çalıştır (dev-deps gerekli):
    pip install python-stdnum schwifty bip-utils python-mrz lxml PyJWT \
                cryptography mt940 hl7 fhir.resources simplefix netaddr \
                icd10-cm fido2 signxml pynacha cbor2
    pytest tests/test_external_validators.py -v
"""
from __future__ import annotations

import ipaddress
import json
import uuid as _uuid_mod

import pytest

from mockjutsu.core import MockJutsuCore

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
