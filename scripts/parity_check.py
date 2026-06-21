"""
Parity checker: Python generator vs Java (JMeter) generator.

For every type, generates N samples from both sides and compares structure:
  - JSON types   : top-level key sets must match
  - String types : length range sanity check
  - Error values : "ERROR:" prefix detected

Usage:
  cd mock-jutsu-api
  python scripts/parity_check.py                          # all 300 types, locale TR, 20 samples
  python scripts/parity_check.py --locale DE --count 30
  python scripts/parity_check.py --type tckn br_cpf event_stream
  python scripts/parity_check.py --no-java                # Python-only error check
  python scripts/parity_check.py --out results.json       # save full output
"""

import sys, os, json, re, subprocess, argparse
from pathlib import Path

REPO_ROOT  = Path(__file__).parent.parent
JMETER_POM = REPO_ROOT.parent / "mock-jutsu-jmeter" / "jmeter-plugin" / "pom.xml"
MVN        = r"C:\tools\apache-maven-3.9.16\bin\mvn.cmd"
SEP        = "\x1f"  # unit separator used by MockJutsuCLI

sys.path.insert(0, str(REPO_ROOT / "src"))
from mockjutsu.core import jutsu as _engine

def _py_gen(type_: str, locale: str) -> str:
    result = _engine.generate(type_, locale=locale)
    if isinstance(result, (dict, list)):
        return json.dumps(result, ensure_ascii=False)
    return str(result) if result is not None else "ERROR: None returned"

# ── All 300 types ─────────────────────────────────────────────────────────────

ALL_TYPES = [
    "tckn","ykn","taxid","vkn","nationalid","ssn","nin","inn","inn_individual",
    "snils","sgk","mersis","ein","utr","crn","paye","ust_id","ustid","hrb","rvn",
    "siren","siret","tva","ogrn","kpp","employer_id","insurance_id",
    "firstname","lastname","fullname","patronymic","passport","license",
    "age","gender","birthdate","tckn_masked","ssn_masked","nationality","vat_number","cardowner",
    "cardnum","cardnetwork","cardtype","cardstatus","cvv3","cvv4",
    "issuer","expiry","expirymonth","expiryyear","pin","balance",
    "iban","cardcategory","credit_score","sepa_qr","emv_qr_p2p",
    "emv_qr_atm","emv_qr_pos","3ds_cavv","3ds_eci",
    "phone","phone_country","phone_area","phone_local",
    "address_city","address_street","address_full","postalcode","plate","email",
    "uuid","requestid","correlationid","sessionid","idempotencykey",
    "deviceid","ipv4","ipv6","browser_name","browser_version","browser_engine",
    "useragent","timestamp","timestamp_iso","clientversion","bearertoken",
    "signature","apppassword","jwt","hash","mac_address","domain","url","color",
    "api_key","totp_code","webhook_signature","transaction_id","public_ip","private_ip",
    "swift","bic","sort_code","routing_number","bik_code",
    "transaction","bank_name","sepa_ref","creditor_ref",
    "company_name","job_title","occupation","jobtitle",
    "blood_type","bloodtype","nhs_number","nhsnumber","icd10",
    "height","weight","npi","bmi","hl7_message","fhir_patient","dicom_uid",
    "currency","tax_rate","taxrate","invoice_number","invoicenumber","vin","vehicle",
    "rfid_uid","epc","rfid_tag","nfc_uid","nfc_atqa","nfc_sak",
    "ndef_uri","ndef_text","apdu","nfc_tag",
    "ir_nec","ir_rc5","ir_pronto","ir_raw","mqtt_payload","lora_packet",
    "ean13","ean8","upca","isbn13","isbn10","gs1_128",
    "imei","imei2","iccid","imsi","msisdn",
    "isin","cusip","sedol","lei","fix_message","psd2_consent",
    "btc_address","eth_address","crypto_address","tx_hash","block_hash","mnemonic",
    "product_name","sku","order_id","tracking_number","category","rating","dhl_tracking",
    "latitude","longitude","timezone","country_code","coordinates",
    "username","hashtag","bio","handle","follower_count",
    "track1_data","track2_data","chip_data","pin_block","pin_block_fmt3",
    "emv_arqc","emv_atc","emv_iad",
    "iso8583_auth_request","iso8583_auth_response","iso8583_reversal",
    "atm_session","pos_receipt",
    "cef_log","x509_cert","pcap_hex",
    "iata_ticket","imo_number","pnr_code",
    "webauthn_credential","fido2_assertion",
    "eth_wallet","btc_wallet","sol_wallet",
    "ai_embedding","ai_vector","ai_sparse_vector",
    "oidc_token_set","jwks","oidc_token",
    "mt940","camt053",
    "edi_850","edifact_orders",
    "event_stream","cdc_event",
    "fdr_record","drone_telemetry",
    "jwt_attack","asn1_fuzz",
    "mrz_td3","mrz_td1",
    "ohlcv_candles","market_tick",
    "nmea_gpgga","nmea_gprmc",
    "prometheus_metrics","openmetrics_snapshot",
    "quaternion","navmesh_path",
    "ubl_invoice","xmldsig",
    "can_frame","obd2_response",
    "tle_satellite",
    "swift_mt103","pain001","nacha_ach","sepa_mandate","fedwire",
    "reverse_regex",
    "br_cpf","br_cnpj",
    "in_pan","in_aadhaar","in_gstin","in_epic",
    "cn_ric","mx_curp","mx_rfc","it_codicefiscale",
    "es_dni","es_nie","es_ccc","de_idnr","de_stnr","pk_cnic",
    "jp_cn","jp_in","kr_rrn","kr_brn",
    "nl_bsn","pl_pesel","se_personnummer","dk_cpr","fi_hetu","no_fodselsnummer",
    "au_abn","au_tfn","au_acn","my_nric","th_pin","th_tin","sg_uen","za_idnr",
    "ca_bn","nz_ird","ar_cuit","ar_dni","cl_rut","co_nit","il_idnr",
    "ro_cnp","ro_cui","hr_oib","bg_egn","lt_asmens","ee_ik","pt_cc","eg_tn",
]

# ── Generators ────────────────────────────────────────────────────────────────

def run_python(types: list, locale: str, count: int) -> dict:
    result = {}
    for t in types:
        samples = []
        for _ in range(count):
            try:
                v = _py_gen(t, locale)
                samples.append(v if isinstance(v, str) else str(v))
            except Exception as e:
                samples.append(f"ERROR: {e}")
        result[t] = samples
    return result

def run_java(locale: str, count: int) -> dict:
    """Run MockJutsuCLI via mvn exec:java. Returns {type: [samples]}."""
    cmd = [
        MVN, "-f", str(JMETER_POM),
        "exec:java",
        "-Dexec.mainClass=com.mockjutsu.jmeter.MockJutsuCLI",
        f"-Dexec.args=--all --count {count} --locale {locale}",
        "-q", "--no-transfer-progress",
    ]
    print("  [java] running MockJutsuCLI (this takes ~10s)...", flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        raise RuntimeError(f"mvn exec:java failed:\n{r.stderr[-800:]}")

    result: dict = {}
    for line in r.stdout.splitlines():
        if SEP not in line:
            continue
        type_, val = line.split(SEP, 1)
        val = val.replace("\\n", "\n")
        result.setdefault(type_, []).append(val)
    return result

# ── Structure extraction ──────────────────────────────────────────────────────

def is_json(s: str) -> bool:
    s = s.strip()
    return s.startswith("{") or s.startswith("[")

def json_keys(samples: list) -> set:
    keys: set = set()
    for s in samples:
        try:
            obj = json.loads(s)
            if isinstance(obj, dict):
                keys.update(obj.keys())
            elif isinstance(obj, list) and obj and isinstance(obj[0], dict):
                keys.update(obj[0].keys())
        except Exception:
            pass
    return keys

def sig(samples: list) -> dict:
    valid = [s for s in samples if not s.startswith("ERROR:")]
    if not valid:
        return {"kind": "error"}
    first = valid[0].strip()
    if is_json(first):
        return {"kind": "json", "keys": sorted(json_keys(valid))}
    lengths = [len(s) for s in valid]
    return {"kind": "str", "min": min(lengths), "max": max(lengths), "sample": first[:80]}

# ── Comparison ────────────────────────────────────────────────────────────────

OK   = "OK  "
DIFF = "DIFF"
WARN = "WARN"

def compare(t: str, py: list, java: list) -> dict:
    py_errs   = sum(1 for s in py   if s.startswith("ERROR:"))
    java_errs = sum(1 for s in java if s.startswith("ERROR:"))

    if java_errs:
        return {"status": WARN, "issue": f"Java {java_errs}/{len(java)} errors",
                "java_sample": java[0]}
    if py_errs:
        return {"status": WARN, "issue": f"Python {py_errs}/{len(py)} errors",
                "py_sample": py[0]}

    ps, js = sig(py), sig(java)

    if ps["kind"] != js["kind"]:
        return {"status": DIFF,
                "issue": f"kind mismatch py={ps['kind']} java={js['kind']}",
                "py_sample": py[0][:80], "java_sample": java[0][:80]}

    if ps["kind"] == "json":
        pk, jk = set(ps["keys"]), set(js["keys"])
        only_py   = sorted(pk - jk)
        only_java = sorted(jk - pk)
        if only_py or only_java:
            return {"status": DIFF, "issue": "JSON key mismatch",
                    "only_in_python": only_py, "only_in_java": only_java}
        return {"status": OK, "keys": ps["keys"]}

    # String: allow wide variance for inherently variable types
    if ps["kind"] == "str":
        py_max, java_max = ps["max"], js["max"]
        py_min, java_min = ps["min"], js["min"]
        # flag only extreme divergence (>5x)
        if java_max > py_max * 5 or (py_min > 0 and java_max < py_min // 5):
            return {"status": DIFF,
                    "issue": f"length divergence py={py_min}-{py_max} java={java_min}-{java_max}",
                    "py_sample": py[0][:80], "java_sample": java[0][:80]}
        return {"status": OK, "len": f"{py_min}-{py_max}", "sample": py[0][:60]}

    return {"status": OK}

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--locale",  default="TR")
    ap.add_argument("--count",   type=int, default=20)
    ap.add_argument("--type",    nargs="*", dest="types")
    ap.add_argument("--no-java", action="store_true")
    ap.add_argument("--out",     default=None)
    args = ap.parse_args()

    types  = args.types or ALL_TYPES
    count  = args.count
    locale = args.locale

    print(f"\n{'='*72}")
    print(f"  mock-jutsu Parity Check | {len(types)} types | locale={locale} | n={count}")
    print(f"{'='*72}\n")

    print("[1/2] Python samples...")
    py_data = run_python(types, locale, count)

    java_data = {}
    if not args.no_java:
        print("[2/2] Java samples...")
        try:
            java_data = run_java(locale, count)
        except Exception as e:
            print(f"  ⚠️  Java failed: {e}\n  Continuing in Python-only mode.")
            args.no_java = True

    results = {}
    ok = diff = warn = 0
    diff_list = []

    col = max(len(t) for t in types) + 2

    print(f"\n{'TYPE':<{col}}  STATUS  DETAIL")
    print("-" * 90)

    for t in types:
        py_s   = py_data.get(t, [])
        java_s = java_data.get(t, []) if not args.no_java else []

        if args.no_java or not java_s:
            py_errs = sum(1 for s in py_s if s.startswith("ERROR:"))
            if py_errs:
                r = {"status": WARN, "issue": f"Python {py_errs} errors: {py_s[0]}"}
                warn += 1
            else:
                r = {"status": OK, "sample": py_s[0][:60] if py_s else ""}
                ok += 1
        else:
            r = compare(t, py_s, java_s)
            if   r["status"] == OK:   ok   += 1
            elif r["status"] == WARN: warn += 1
            else:
                diff += 1
                diff_list.append(t)

        results[t] = r
        status = r["status"]
        detail = ""
        if status != OK:
            detail = r.get("issue","")
            if "only_in_python" in r: detail += f" | +py:{r['only_in_python']}"
            if "only_in_java"   in r: detail += f" | +java:{r['only_in_java']}"
        else:
            v = r.get("sample", r.get("keys", r.get("len","")))
            detail = str(v)[:80] if isinstance(v, list) else str(v)[:80]
        print(f"  {t:<{col}}  {status}  {detail}")

    print(f"\n{'='*72}")
    print(f"  RESULT: {ok} OK  |  {diff} DIFF  |  {warn} WARN  |  total {len(types)}")
    if diff_list:
        print(f"\n  [DIFF] Fix needed ({diff} types):")
        for t in diff_list:
            r = results[t]
            print(f"    {t}: {r.get('issue','')}")
            if "only_in_python" in r: print(f"      only in Python : {r['only_in_python']}")
            if "only_in_java"   in r: print(f"      only in Java   : {r['only_in_java']}")
    print(f"{'='*72}\n")

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump({"results": results,
                       "summary": {"ok": ok, "diff": diff, "warn": warn}}, f, indent=2)
        print(f"Saved -> {args.out}")

    return 0 if (diff + warn) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
