"""
Faz 1 (Doğrulama Yol Haritası) — compliance/validation_matrix.json üretici.

Tüm 251 tipin mevcut test kalitesini ve hedef doğrulama yöntemini sınıflandırır.

Kategoriler:
  matematiksel_garanti  → dış kütüphane bağımsız parse/validate edebilir (~80 hedef)
  algoritmik_dogrulandi → resmi RFC/ISO/ICAO/NIST test vektörü mevcut veya bulunabilir (~50 hedef)
  yapisal_gecerlilik    → standart belgesi okunup format contract yazılır (~120 hedef)

Çalıştır:
    $env:PYTHONPATH='c:\\Users\\altan\\repos\\mock-jutsu-api\\src'
    python scripts/build_validation_matrix.py
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CLI_PY = ROOT / "src" / "mockjutsu" / "cli.py"
VECTORS_JSON = ROOT / "compliance" / "algorithm_vectors.json"
CONTRACTS_JSON = ROOT / "compliance" / "format_contracts.json"
OUTPUT = ROOT / "compliance" / "validation_matrix.json"


# Tipler bağımsız dış kütüphane ile doğrulanabilir → ✅ Matematiksel Garanti
# Format: type_name -> (library, validator_function_or_module)
EXTERNAL_VALIDATORS: dict[str, tuple[str, str]] = {
    # python-stdnum
    "tckn":            ("python-stdnum", "stdnum.tr.tckimlik.validate"),
    "vkn":             ("python-stdnum", "stdnum.tr.vkn.validate"),
    "ssn":             ("python-stdnum", "stdnum.us.ssn.validate"),
    "ein":             ("python-stdnum", "stdnum.us.ein.validate"),
    "nin":             ("python-stdnum", "stdnum.gb.nino.validate"),
    "utr":             ("python-stdnum", "stdnum.gb.utr.validate"),
    "ust_id":          ("python-stdnum", "stdnum.de.ustid.validate"),
    "ustid":           ("python-stdnum", "stdnum.de.ustid.validate"),
    "siren":           ("python-stdnum", "stdnum.fr.siren.validate"),
    "siret":           ("python-stdnum", "stdnum.fr.siret.validate"),
    "tva":             ("python-stdnum", "stdnum.fr.tva.validate"),
    "inn":             ("python-stdnum", "stdnum.ru.inn.validate"),
    "inn_individual":  ("python-stdnum", "stdnum.ru.inn.validate"),
    "snils":           ("python-stdnum", "stdnum.ru.snils.validate"),
    "ogrn":            ("python-stdnum", "stdnum.ru.ogrn.validate"),
    "kpp":             ("python-stdnum", "stdnum.ru.kpp.validate"),
    "vat_number":      ("python-stdnum", "stdnum.eu.vat.validate"),
    "isbn13":          ("python-stdnum", "stdnum.isbn.validate"),
    "isbn10":          ("python-stdnum", "stdnum.isbn.validate"),
    "ean13":           ("python-stdnum", "stdnum.ean.validate"),
    "ean8":            ("python-stdnum", "stdnum.ean.validate"),
    "upca":            ("python-stdnum", "stdnum.ean.validate"),
    "cusip":           ("python-stdnum", "stdnum.cusip.validate"),
    "isin":            ("python-stdnum", "stdnum.isin.validate"),
    "lei":             ("python-stdnum", "stdnum.lei.validate"),
    "imei":            ("python-stdnum", "stdnum.imei.validate"),
    "imei2":           ("python-stdnum", "stdnum.imei.validate"),
    "imsi":            ("python-stdnum", "stdnum.imsi.validate"),
    "iccid":           ("python-stdnum", "stdnum.iso7812.validate"),
    "iban":            ("python-stdnum", "stdnum.iban.validate"),
    "bic":             ("python-stdnum", "stdnum.bic.validate"),
    "swift":           ("python-stdnum", "stdnum.bic.validate"),
    "nhs_number":      ("python-stdnum", "stdnum.gb.nhs.validate"),
    "nhsnumber":       ("python-stdnum", "stdnum.gb.nhs.validate"),
    "vin":             ("python-stdnum", "stdnum.vatin.vin (community)"),
    # schwifty
    "iban_tr":         ("schwifty", "schwifty.IBAN"),
    "iban_de":         ("schwifty", "schwifty.IBAN"),
    "iban_gb":         ("schwifty", "schwifty.IBAN"),
    # Luhn-based (python-stdnum.luhn)
    "cardnum":         ("python-stdnum", "stdnum.luhn.validate"),
    "npi":             ("python-stdnum", "stdnum.luhn.validate"),
    "dhl_tracking":    ("python-stdnum", "stdnum.luhn.validate"),
    # bip-utils
    "mnemonic":        ("bip-utils", "bip_utils.Bip39MnemonicValidator"),
    "btc_address":     ("bip-utils", "bip_utils.P2PKHAddrDecoder"),
    "eth_address":     ("bip-utils", "bip_utils.EthAddrDecoder"),
    "eth_wallet":      ("bip-utils", "bip_utils.EthAddrEncoder"),
    "btc_wallet":      ("bip-utils", "bip_utils.WifDecoder + P2PKHAddrDecoder"),
    "sol_wallet":      ("solders / base58", "base58 + ed25519 verify"),
    # python-mrz
    "mrz_td3":         ("python-mrz", "mrz.TD3CodeChecker"),
    "mrz_td1":         ("python-mrz", "mrz.TD1CodeChecker"),
    # hl7 / fhir.resources
    "hl7_message":     ("hl7", "hl7.parse"),
    "fhir_patient":    ("fhir.resources", "fhir.resources.patient.Patient.parse_raw"),
    # lxml + XSD
    "ubl_invoice":     ("lxml + UBL-2.1 XSD", "lxml.etree.XMLSchema"),
    "xmldsig":         ("signxml", "signxml.XMLVerifier"),
    "pain001":         ("lxml + ISO 20022 XSD pain.001.001.09", "lxml.etree.XMLSchema"),
    "camt053":         ("lxml + ISO 20022 XSD camt.053.001.02", "lxml.etree.XMLSchema"),
    "sepa_mandate":    ("lxml + SEPA XSD", "lxml.etree.XMLSchema"),
    # PyCryptodome / cryptography
    "jwks":            ("cryptography / PyJWT", "jwt.algorithms.ECAlgorithm.from_jwk"),
    "oidc_token":      ("PyJWT", "jwt.decode"),
    "oidc_token_set":  ("PyJWT + cryptography", "jwt.decode (ES256)"),
    "fido2_assertion": ("python-fido2", "fido2.cose + cbor2"),
    "webauthn_credential": ("python-fido2 + cbor2", "fido2.webauthn.AttestationObject"),
    # cbor2
    # Routing / ABA
    "routing_number":  ("python-stdnum", "stdnum.us.rtn.validate"),
    # ICD-10
    "icd10":           ("icd10-cm", "icd10.find"),
    # UUID
    "uuid":            ("Python stdlib", "uuid.UUID(s, version=4)"),
    "requestid":       ("Python stdlib", "uuid.UUID(s, version=4)"),
    "correlationid":   ("Python stdlib", "uuid.UUID(s, version=4)"),
    "sessionid":       ("Python stdlib", "uuid.UUID(s, version=4)"),
    "idempotencykey":  ("Python stdlib", "uuid.UUID(s, version=4)"),
    "deviceid":        ("Python stdlib", "uuid.UUID(s, version=4)"),
    # IP
    "ipv4":            ("Python stdlib", "ipaddress.IPv4Address"),
    "ipv6":            ("Python stdlib", "ipaddress.IPv6Address"),
    "public_ip":       ("Python stdlib", "ipaddress.IPv4Address (not is_private)"),
    "private_ip":      ("Python stdlib", "ipaddress.IPv4Address (is_private)"),
    # MAC
    "mac_address":     ("netaddr", "netaddr.EUI"),
    # JSON
    "x509_cert":       ("cryptography", "x509.load_pem_x509_certificate"),
    # NACHA
    "nacha_ach":       ("ach-rfc / pynacha", "ach.AchFile.parse"),
    # FIX
    "fix_message":     ("simplefix", "simplefix.FixParser"),
    # SWIFT MT940
    "mt940":           ("mt-940", "mt940.models.Transactions"),
    # FedWire — not standard library; manual contract
    # ── Sprint 4-7 Uluslararası Kimlik Tipleri ──────────────────────────────
    # Güney Amerika
    "br_cpf":           ("python-stdnum", "stdnum.br.cpf.validate"),
    "br_cnpj":          ("python-stdnum", "stdnum.br.cnpj.validate"),
    "ar_cuit":          ("python-stdnum", "stdnum.ar.cuit.validate"),
    "ar_dni":           ("python-stdnum", "stdnum.ar.dni.validate"),
    "mx_rfc":           ("python-stdnum", "stdnum.mx.rfc.validate"),
    "mx_curp":          ("python-stdnum", "stdnum.mx.curp.validate"),
    "cl_rut":           ("python-stdnum", "stdnum.cl.rut.validate"),
    "co_nit":           ("python-stdnum", "stdnum.co.nit.validate"),
    # Asya-Pasifik
    "in_aadhaar":       ("python-stdnum", "stdnum.in_.aadhaar.validate"),
    "in_pan":           ("python-stdnum", "stdnum.in_.pan.validate"),
    "in_gstin":         ("python-stdnum", "stdnum.in_.gstin.validate"),
    "in_epic":          ("python-stdnum", "stdnum.in_.epic.validate"),
    "au_abn":           ("python-stdnum", "stdnum.au.abn.validate"),
    "au_acn":           ("python-stdnum", "stdnum.au.acn.validate"),
    "au_tfn":           ("python-stdnum", "stdnum.au.tfn.validate"),
    "nz_ird":           ("python-stdnum", "stdnum.nz.ird.validate"),
    "sg_uen":           ("python-stdnum", "stdnum.sg.uen.validate"),
    "kr_brn":           ("python-stdnum", "stdnum.kr.brn.validate"),
    "kr_rrn":           ("python-stdnum", "stdnum.kr.rrn.validate"),
    "jp_cn":            ("python-stdnum", "stdnum.jp.cn.validate"),
    "jp_in":            ("python-stdnum", "stdnum.jp.in_.validate"),
    "cn_ric":           ("python-stdnum", "stdnum.cn.ric.validate"),
    "th_pin":           ("python-stdnum", "stdnum.th.pin.validate"),
    "th_tin":           ("python-stdnum", "stdnum.th.tin.validate"),
    "pk_cnic":          ("python-stdnum", "stdnum.pk.cnic.validate"),
    # Avrupa (ek ülkeler)
    "fi_hetu":          ("python-stdnum", "stdnum.fi.hetu.validate"),
    "no_fodselsnummer": ("python-stdnum", "stdnum.no.fodselsnummer.validate"),
    "se_personnummer":  ("python-stdnum", "stdnum.se.personnummer.validate"),
    "dk_cpr":           ("python-stdnum", "stdnum.dk.cpr.validate"),
    "it_codicefiscale": ("python-stdnum", "stdnum.it.codicefiscale.validate"),
    "nl_bsn":           ("python-stdnum", "stdnum.nl.bsn.validate"),
    "pl_pesel":         ("python-stdnum", "stdnum.pl.pesel.validate"),
    "es_dni":           ("python-stdnum", "stdnum.es.dni.validate"),
    "es_nie":           ("python-stdnum", "stdnum.es.nie.validate"),
    "es_ccc":           ("python-stdnum", "stdnum.es.ccc.validate"),
    "de_idnr":          ("python-stdnum", "stdnum.de.idnr.validate"),
    "de_stnr":          ("python-stdnum", "stdnum.de.stnr.validate"),
    "hr_oib":           ("python-stdnum", "stdnum.hr.oib.validate"),
    "bg_egn":           ("python-stdnum", "stdnum.bg.egn.validate"),
    "ee_ik":            ("python-stdnum", "stdnum.ee.ik.validate"),
    "lt_asmens":        ("python-stdnum", "stdnum.lt.asmens.validate"),
    "ro_cnp":           ("python-stdnum", "stdnum.ro.cnp.validate"),
    "ro_cui":           ("python-stdnum", "stdnum.ro.cui.validate"),
    "pt_cc":            ("python-stdnum", "stdnum.pt.cc.validate"),
    # Afrika / Orta Doğu
    "za_idnr":          ("python-stdnum", "stdnum.za.idnr.validate"),
    "eg_tn":            ("python-stdnum", "stdnum.eg.tn.validate"),
    "il_idnr":          ("python-stdnum", "stdnum.il.idnr.validate"),
    # Kuzey Amerika
    "ca_bn":            ("python-stdnum", "stdnum.ca.bn.validate"),
    "wire_routing_number": ("python-stdnum", "stdnum.us.rtn.validate"),
    # Avrupa (stdnum'da bulunan, önceden atlanmış)
    "hrb":              ("python-stdnum", "stdnum.de.handelsregisternummer.validate"),
    # Güneydoğu Asya
    "my_nric":          ("python-stdnum", "stdnum.my.nric.validate"),
    # ── Python stdlib doğrulanabilir tipler ──────────────────────────────────
    # Tarih / Saat
    "timestamp":        ("Python stdlib", "datetime.datetime.fromtimestamp"),
    "timestamp_iso":    ("Python stdlib", "datetime.datetime.fromisoformat"),
    "time_only":        ("Python stdlib", "datetime.time.fromisoformat"),
    "future_date":      ("Python stdlib", "datetime.date.fromisoformat + > today"),
    "future_datetime":  ("Python stdlib", "datetime.datetime.fromisoformat + > now"),
    "past_date":        ("Python stdlib", "datetime.date.fromisoformat + < today"),
    "past_datetime":    ("Python stdlib", "datetime.datetime.fromisoformat + < now"),
    "date_between":     ("Python stdlib", "datetime.date.fromisoformat"),
    "date_this_month":  ("Python stdlib", "datetime.date.fromisoformat + same month"),
    "date_this_year":   ("Python stdlib", "datetime.date.fromisoformat + same year"),
    "settlement_date":  ("Python stdlib", "datetime.date.fromisoformat + Mon-Fri weekday"),
    "timezone":         ("Python stdlib", "zoneinfo.ZoneInfo(tz) no-throw"),
    # Ağ / URL
    "url":              ("Python stdlib", "urllib.parse.urlparse scheme+netloc"),
    "uri_path":         ("Python stdlib", "urllib.parse.urlparse path"),
    "hostname":         ("Python stdlib", "re.match RFC 1123 label format"),
    "domain":           ("Python stdlib", "re.match + known TLD"),
    "slug":             ("Python stdlib", "re.match ^[a-z0-9-]+$"),
    "tld":              ("Python stdlib", "str alpha-only len 2-6"),
    "port_number":      ("Python stdlib", "int 0-65535 range"),
    # Coğrafya
    "latitude":         ("Python stdlib", "float -90.0 to 90.0"),
    "longitude":        ("Python stdlib", "float -180.0 to 180.0"),
    "coordinates":      ("Python stdlib", "lat float -90/90, lon float -180/180"),
    "country_code":     ("Python stdlib", "ISO 3166-1 alpha-2 set (249 codes)"),
    # Demografik / Sağlık
    "blood_type":       ("Python stdlib", "enum {A+,A-,B+,B-,AB+,AB-,O+,O-}"),
    "bloodtype":        ("Python stdlib", "enum {A+,A-,B+,B-,AB+,AB-,O+,O-}"),
    "gender":           ("Python stdlib", "enum {M,F,Male,Female,Other,...}"),
    "age":              ("Python stdlib", "int 0-120 range"),
    "bmi":              ("Python stdlib", "float 10.0-60.0 range"),
    "credit_score":     ("Python stdlib", "int 300-850 FICO range"),
    # Kart / Ödeme
    "cvv3":             ("Python stdlib", "re.match ^[0-9]{3}$"),
    "cvv4":             ("Python stdlib", "re.match ^[0-9]{4}$"),
    "expiry":           ("Python stdlib", "re.match MM/YY + future date"),
    "expirymonth":      ("Python stdlib", "int or str 01-12"),
    "expiryyear":       ("Python stdlib", "int >= current year"),
    "3ds_cavv":         ("Python stdlib", "base64.b64decode + assert len==20"),
    "3ds_eci":          ("Python stdlib", "enum {00,01,02,05,06,07}"),
    # Kripto / Blockchain
    "tx_hash":          ("Python stdlib", "re.match (0x)?[0-9a-fA-F]{64}"),
    "block_hash":       ("Python stdlib", "re.match (0x)?[0-9a-fA-F]{64}"),
    "gas_limit":        ("Python stdlib", "int > 21000"),
    "gas_price":        ("Python stdlib", "int > 0"),
    "nft_token_id":     ("Python stdlib", "int 0 to 2**256-1"),
    "quaternion":       ("Python stdlib", "math.isclose(x²+y²+z²+w², 1.0, rel_tol=1e-6)"),
    # Hash / Güvenlik
    "hash":             ("Python stdlib", "re.match per algorithm: md5=32, sha256=64, sha512=128 hex"),
    "api_key":          ("Python stdlib", "re.match ^sk-[A-Za-z0-9]{48}$"),
    "pin":              ("Python stdlib", "re.match ^[0-9]{4,6}$"),
    # Türk özel tipleri (kendi Luhn/VKN impl.)
    "ykn":              ("Python stdlib", "Luhn MOD-10 check (kendi impl., 11-digit 99-prefix)"),
    "mersis":           ("Python stdlib", "VKN 10-digit checksum (kendi impl.) + 6-digit suffix = 16"),
    # Gözlemlenebilirlik (format spec, stdlib string check)
    "prometheus_metrics":    ("Python stdlib", "lines: # HELP, # TYPE, metric value; no trailing space"),
    "openmetrics_snapshot":  ("Python stdlib", "Prometheus format + mandatory # EOF last line"),
    "cef_log":               ("Python stdlib", "re.match ^CEF:0\\\\| + 7 pipe-delimited fields"),
    "mqtt_payload":          ("Python stdlib", "json.loads roundtrip"),
    # Renk
    "color":            ("Python stdlib", "re.match hex (#[0-9a-fA-F]{6}) or rgb/hsl/name"),
    # HTTP
    "http_status_code": ("Python stdlib", "int in http.HTTPStatus or known set"),
    "http_method":      ("Python stdlib", "enum {GET,POST,PUT,DELETE,PATCH,HEAD,OPTIONS,TRACE}"),
    # JWT (PyJWT zaten yüklü — oidc_token testleri var)
    "jwt":              ("PyJWT", "jwt.decode(token, options={'verify_signature':False})"),
    "bearertoken":      ("PyJWT", "jwt.decode(token, options={'verify_signature':False})"),
    "psd2_consent":     ("PyJWT", "jwt.decode(token, options={'verify_signature':False})"),
}


# Resmi RFC/ISO/ICAO/NIST test vektörü mevcut → ⚙️ Algoritmik Doğrulandı
# (test_known_vectors.py + test_bip39.py içinde kanıt var)
HAS_OFFICIAL_VECTORS_NOW: set[str] = {
    "cusip", "routing_number", "tckn", "ean13", "isin", "cardnum",
    "nhs_number", "nhsnumber", "mnemonic",
}

# Hardware/CardPhysics: ISO 9564, ISO 8583, ISO 7813 — kütüphane yok ama
# resmi spec PDF vektörleri eklenmeli (Faz 3 hedef)
NEEDS_VECTOR_EXTENSION: set[str] = {
    "iban", "iban_tr", "iban_de", "iban_gb",  # zaten python-stdnum yapacak
    "track1_data", "track2_data", "pin_block", "pin_block_fmt3",
    "iso8583_auth_request", "iso8583_auth_response", "iso8583_reversal",
    "emv_arqc", "emv_atc", "emv_iad",
    "chip_data",
    "creditor_ref",       # ISO 11649 MOD-97
    "iata_ticket",        # IATA MOD-7
    "imo_number",         # IMO MOD-10
    "fix_message",        # FIX 4.4 Tag 10 MOD-256
    "fedwire",            # Fedwire Tag format
    "sepa_ref",           # ISO 20022 SEPA
    "swift_mt103",        # SWIFT MT103
    "can_frame",          # CRC-15 over CAN frame
    "obd2_response",      # SAE J1979 PIDs
    "tle_satellite",      # NORAD MOD-10 on TLE lines
    "nmea_gpgga",         # XOR checksum
    "nmea_gprmc",         # XOR checksum
    "edi_850",            # X12 envelope counters
    "edifact_orders",     # EDIFACT counters
    "dicom_uid",          # ISO/IEC 9834-8
    "rfid_uid",           # ISO 14443-3A
    "epc",                # GS1 SGTIN-96
    "nfc_uid",            # ISO 14443-3A
    "ndef_uri",           # NFC Forum RTD URI
    "ndef_text",          # NFC Forum RTD Text
    "apdu",               # ISO 7816-4
    "ir_nec", "ir_rc5", "ir_pronto", "ir_raw",
    "gs1_128",            # GS1-128 AIs
    "msisdn",             # E.164
    "sedol",              # weighted check
    "lei",                # ISO 17442 MOD 97-10
    "totp_code",          # RFC 6238 (kütüphane var → matematiksel'e taşınabilir)
    "webhook_signature",  # HMAC-SHA256 RFC 2104
    "signature",          # HMAC test vektörleri (RFC 4231)
    # Sprint 4-7 yeni tipler — checksum algoritması var
    "figi",               # CUSIP-style per-character digit-sum (BBG000B9XRY4 doğrulandı)
    "nsin",               # CUSIP (US/CA) veya SEDOL (UK) checksum, locale-aware
    "ifsc_code",          # RBI IFSC format: 4-char bank + 0 + 6-char branch
    "bsb_code",           # AU BSB: bank-branch format, APCA directory
    "mic",                # ISO 10383 — 4-char exchange identifier
    # Phase 4'ten yükseltilen algoritmik tipler
    "emv_qr_p2p",         # EMVCo QR QRCPS: CRC-16/EMVCo (poly=0x1021, init=0xFFFF)
    "emv_qr_atm",         # EMVCo QR ATM: CRC-16/EMVCo checksum
    "emv_qr_pos",         # EMVCo QR POS: CRC-16/EMVCo checksum
    "sepa_qr",            # EPC QR: BCD header "BCD\n003\n1\nSCT" zorunlu
    "ohlcv_candles",      # OHLCV: H>=max(O,C), L<=min(O,C), Open[i]=Close[i-1]
    "rvn",                # DE Rentenversicherungsnummer: proprietary weighted checksum
    "sort_code",          # UK sort code: 6-digit NNN-NNN, Pay.UK Vocalink directory format
}


# CLI _REFERENCE listesini parse et
def parse_reference() -> list[dict[str, str]]:
    text = CLI_PY.read_text(encoding="utf-8")
    m = re.search(r"_REFERENCE = \[\s*(.*?)\n\]\s*\n", text, re.DOTALL)
    if not m:
        sys.exit("ERROR: _REFERENCE block not found in cli.py")
    block = m.group(1)
    rows: list[dict[str, str]] = []
    line_re = re.compile(
        r"\(\s*'([^']+)'\s*,\s*'([^']*)'\s*,\s*(True|False)\s*,\s*'([^']*)'\s*,\s*'([^']*)'\s*,\s*'([^']*)'",
    )
    for ln in block.splitlines():
        ln = ln.strip()
        if not ln.startswith("("):
            continue
        m2 = line_re.match(ln)
        if not m2:
            continue
        type_name = m2.group(1)
        category = m2.group(2)
        locale_aware = m2.group(3) == "True"
        if type_name.startswith("--") or category == "":
            continue
        rows.append({
            "type": type_name,
            "category_legacy": category,
            "locale_aware": locale_aware,
        })
    return rows


def classify(type_name: str) -> dict[str, Any]:
    """Bir tipi 3 doğrulama kategorisinden birine ata."""
    if type_name in EXTERNAL_VALIDATORS:
        lib, validator = EXTERNAL_VALIDATORS[type_name]
        has_now = type_name in HAS_OFFICIAL_VECTORS_NOW
        return {
            "validation_category": "matematiksel_garanti",
            "badge_target": "✅",
            "phase": 2 if not has_now else 1,
            "current_test_quality": "official_vector" if has_now else "circular_or_smoke",
            "target_validator": f"{lib}: {validator}",
            "test_vector_source": "test_known_vectors.py" if has_now else f"{lib} parse roundtrip",
        }
    if type_name in NEEDS_VECTOR_EXTENSION:
        return {
            "validation_category": "algoritmik_dogrulandi",
            "badge_target": "⚙️",
            "phase": 3,
            "current_test_quality": "circular",
            "target_validator": "spec PDF + hardcoded official vectors",
            "test_vector_source": "RFC/ISO/SWIFT/GS1/NMEA spec",
        }
    if type_name in HAS_OFFICIAL_VECTORS_NOW:
        return {
            "validation_category": "algoritmik_dogrulandi",
            "badge_target": "⚙️",
            "phase": 1,
            "current_test_quality": "official_vector",
            "target_validator": "tests/test_known_vectors.py",
            "test_vector_source": "compliance/algorithm_vectors.json",
        }
    return {
        "validation_category": "yapisal_gecerlilik",
        "badge_target": "📐",
        "phase": 4,
        "current_test_quality": "smoke_only",
        "target_validator": "format_contracts.json + spec belge okuma",
        "test_vector_source": "manual standards review",
    }


def build_matrix() -> dict[str, Any]:
    types = parse_reference()
    items: list[dict[str, Any]] = []
    for row in types:
        verdict = classify(row["type"])
        items.append({
            "type": row["type"],
            "category_legacy": row["category_legacy"],
            "locale_aware": row["locale_aware"],
            **verdict,
        })
    # Özet
    summary = {
        "total": len(items),
        "matematiksel_garanti": sum(1 for i in items if i["validation_category"] == "matematiksel_garanti"),
        "algoritmik_dogrulandi": sum(1 for i in items if i["validation_category"] == "algoritmik_dogrulandi"),
        "yapisal_gecerlilik": sum(1 for i in items if i["validation_category"] == "yapisal_gecerlilik"),
        "phase_1_already_done": sum(1 for i in items if i["phase"] == 1),
        "phase_2_external_lib": sum(1 for i in items if i["phase"] == 2),
        "phase_3_vector_extension": sum(1 for i in items if i["phase"] == 3),
        "phase_4_manual_spec": sum(1 for i in items if i["phase"] == 4),
    }
    return {
        "_comment": (
            "Validation Matrix — Faz 1 sınıflandırması. "
            "Her tipin mevcut test kalitesi ve hedef doğrulama yöntemi. "
            "Bkz. project_mockjutsu_validation_roadmap.md (memory)."
        ),
        "_version": "1.0",
        "_summary": summary,
        "types": items,
    }


def main() -> None:
    matrix = build_matrix()
    OUTPUT.write_text(json.dumps(matrix, indent=2, ensure_ascii=False), encoding="utf-8")
    s = matrix["_summary"]
    out = [
        f"Wrote {OUTPUT.relative_to(ROOT)}",
        f"  Total types                : {s['total']}",
        f"  [OK] Matematiksel Garanti  : {s['matematiksel_garanti']:>4} (lib parse/validate)",
        f"  [GR] Algoritmik Dogrulandi : {s['algoritmik_dogrulandi']:>4} (resmi vektor)",
        f"  [SQ] Yapisal Gecerlilik    : {s['yapisal_gecerlilik']:>4} (manuel spec)",
        "",
        f"  Faz 1 (zaten kanitlanmis)  : {s['phase_1_already_done']:>4}",
        f"  Faz 2 (dis kutuphane ekle) : {s['phase_2_external_lib']:>4}",
        f"  Faz 3 (vektor genisletme)  : {s['phase_3_vector_extension']:>4}",
        f"  Faz 4 (manuel spec)        : {s['phase_4_manual_spec']:>4}",
    ]
    sys.stdout.buffer.write(("\n".join(out) + "\n").encode("utf-8"))


if __name__ == "__main__":
    main()
