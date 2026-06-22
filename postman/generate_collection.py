"""
Generates mock-jutsu.postman_collection.json from _REFERENCE.
Run from the repo root: python postman/generate_collection.py
"""

import json, sys, uuid
sys.path.insert(0, "src")
from mockjutsu.cli import _REFERENCE

BASE = "{{baseUrl}}"

# ── Type → extra query params ────────────────────────────────────────────────
# Maps type name → list of (key, value) tuples to add as query params.
# Types not listed here get only `locale` by default.

LOCALE_TYPES = {
    # identity / name / demographic / document
    "tckn","ykn","nationalid","vkn","taxid","employer_id","insurance_id",
    "sgk","mersis","ssn","ein","nin","utr","crn","paye","ust_id","ustid",
    "hrb","rvn","siren","siret","tva","inn","inn_individual","snils","kpp",
    "ogrn","vat_number","tckn_masked","ssn_masked","nationality",
    "firstname","lastname","fullname","patronymic",
    "age","gender","birthdate","passport","license",
    # financial
    "iban","sepa_qr","emv_qr_p2p","emv_qr_atm","emv_qr_pos",
    "cardowner","issuer","credit_score",
    "cardtype","cardstatus","cardcategory","cardnetwork",
    "3ds_cavv","3ds_eci",
    # financial ext
    "credit_score_model","credit_score_tier","credit_limit","credit_utilization",
    "credit_card_issuer_name","apr","loan_type","mortgage_rate","mortgage_term",
    "premium_amount","deductible","coverage_limit","claim_status",
    "credit_limit_masked","mortgage_rate_masked","premium_amount_masked",
    # banking
    "swift","bic","bank_name","transaction","transaction_description",
    "transaction_description_masked",
    # payments
    "swift_mt103","pain001","nacha_ach","sepa_mandate","fedwire",
    # card physics
    "iso8583_auth_request","iso8583_auth_response","iso8583_reversal","atm_session","pos_receipt",
    # hardware
    "chip_data",
    # compliance
    "kyc_document_type","onboarding_method","tpp_id",
    # contact
    "phone","phone_country","phone_area","phone_local",
    "address_city","address_street","address_full","postalcode","plate","email",
    # corporate
    "company_name","job_title","jobtitle","occupation",
    # commerce
    "currency","tax_rate","taxrate","invoice_number","invoicenumber","vehicle",
    # health
    "height","weight","fhir_patient","hl7_message",
    # location
    "latitude","longitude","timezone","country_code","coordinates",
    # social
    "username","handle","hashtag","bio","follower_count",
    # e-commerce
    "product_name","sku","category","rating",
    # cap markets
    "isin","cusip","sedol","lei","fix_message","psd2_consent",
    "stock_ticker","figi","forex_pair","ric","mic","stock_exchange",
    "option_contract","bond_yield","coupon_rate","settlement_date",
    "portfolio_id","portfolio_id_masked","nsin",
    # barcode
    "ean13","ean8","upca","isbn13","isbn10","gs1_128",
    # telecom
    "imei","imei2","iccid","imsi","msisdn",
    # iot / nfc
    "ndef_text",
    # bank statement
    "mt940","camt053",
    # edi
    "edi_850","edifact_orders",
    # aviation
    "iata_ticket","pnr_code",
    # metadata
    "url","domain",
}

NETWORK_TYPES = {"cardnum","cvv3","cvv4","pin","expiry","expirymonth","expiryyear"}
CURRENCY_TYPES = {"btc_address","eth_address","crypto_address","tx_hash"}
CARRIER_TYPES = {"tracking_number","dhl_tracking"}
ALGORITHM_TYPES = {"hash"}
MASK_TYPES = {
    "tckn","ssn","nin","passport","license","iban","cardnum","cvv3","cvv4","pin",
    "expiry","balance","email","phone","address_full","fullname","birthdate",
    "imei","iccid","credit_limit","mortgage_rate","premium_amount",
    "blood_type","bloodtype","bmi","npi","icd10","dicom_uid","hl7_message",
    "mrz_td3","mrz_td1","mnemonic","oidc_token","webauthn_credential",
    "track1_data","track2_data","pin_block","pin_block_fmt3",
    "emv_arqc","emv_atc","emv_iad",
    "sessionid","deviceid","ipv4","mac_address",
    "password","password_hash","public_ip",
    "order_id","tracking_number",
    "handle","username",
    "pep_status","sar_number","policy_number","claim_number","consent_id",
}

EXTRA_PARAMS = {
    "reverse_regex":  [("pattern", "[A-Z]{3}\\d{4}")],
    "color":          [("format", "hex")],
    "hash":           [("algorithm", "sha256")],
    "mnemonic":       [("words", "12")],
    "ai_embedding":   [("dims", "1536")],
    "ai_vector":      [("dims", "384")],
    "ai_sparse_vector": [("dims", "10000"), ("nnz", "128")],
    "signature":      [("secret", "ninja"), ("payload", "mock")],
    "date_between":   [("start", "2020-01-01"), ("end", "2025-12-31")],
    "forex_rate":     [("pair", "EURUSD")],
    "balance":        [("min", "100"), ("max", "50000")],
    "age":            [("min", "18"), ("max", "65")],
    "cardnum":        [("network", "visa")],
    "cvv3":           [("network", "visa")],
    "cvv4":           [("network", "amex")],
    "pin":            [("network", "visa")],
    "expiry":         [("network", "visa")],
    "expirymonth":    [("network", "visa")],
    "expiryyear":     [("network", "visa")],
    "btc_address":    [("currency", "btc")],
    "eth_address":    [("currency", "eth")],
    "tracking_number":[("carrier", "fedex")],
    "dhl_tracking":   [("carrier", "dhl")],
    "firstname":      [("gender", "male")],
    "lastname":       [("gender", "female")],
    "fullname":       [("gender", "male")],
    "patronymic":     [("gender", "male")],
    "emv_qr_pos":     [("amount", "250.00"), ("merchant", "MOCK STORE"), ("city", "ISTANBUL")],
    "emv_qr_p2p":     [("amount", "150.00")],
    "emv_qr_atm":     [("amount", "500.00")],
    "sepa_qr":        [("amount", "99.90")],
}

LOCALE_DEFAULT = {
    "Identity": "TR", "Name": "TR", "Demographic": "TR", "Document": "TR",
    "Financial": "TR", "FinancialExt": "TR", "Banking": "TR", "Payments": "TR",
    "CardPhysics": "TR", "Hardware": "TR", "BankStatement": "TR",
    "Compliance": "TR", "Contact": "TR", "Corporate": "TR", "Commerce": "TR",
    "Health": "TR", "Location": "TR", "Social": "TR",
    "CapMarkets(Trading)": "TR", "E-Commerce": "TR",
    "IntlIDs": "TR",
}

def make_request(name: str, cat: str) -> dict:
    clean = name.strip()
    url_path = f"generate/{clean}"

    params = []

    # locale
    if clean in LOCALE_TYPES or cat in LOCALE_DEFAULT:
        params.append({"key": "locale", "value": LOCALE_DEFAULT.get(cat, "TR")})

    # type-specific extra params
    if clean in EXTRA_PARAMS:
        for k, v in EXTRA_PARAMS[clean]:
            params.append({"key": k, "value": str(v)})
    elif clean in NETWORK_TYPES:
        params.append({"key": "network", "value": "visa"})
    elif clean in CURRENCY_TYPES:
        params.append({"key": "currency", "value": "btc"})
    elif clean in CARRIER_TYPES:
        params.append({"key": "carrier", "value": "usps"})
    elif clean in ALGORITHM_TYPES:
        params.append({"key": "algorithm", "value": "sha256"})

    # mask variant — add disabled mask param so user can enable easily
    if clean in MASK_TYPES:
        params.append({"key": "mask", "value": "true", "disabled": True})

    return {
        "name": clean,
        "request": {
            "method": "GET",
            "url": {
                "raw": f"{BASE}/{url_path}" + (
                    "?" + "&".join(f"{p['key']}={p['value']}" for p in params if not p.get("disabled"))
                    if any(not p.get("disabled") for p in params) else ""
                ),
                "host": [BASE],
                "path": url_path.split("/"),
                "query": [
                    {"key": p["key"], "value": p["value"],
                     **({"disabled": True} if p.get("disabled") else {})}
                    for p in params
                ],
            },
        },
    }

# ── Build collection ─────────────────────────────────────────────────────────
from collections import defaultdict

CAT_ORDER = [
    "Identity","Name","Demographic","Document","IntlIDs",
    "Financial","FinancialExt","Banking","Payments","CardPhysics","Hardware","BankStatement","CapMarkets(Trading)",
    "Compliance",
    "Contact","Location","Corporate","Commerce","E-Commerce","EInvoice","EDI",
    "Health",
    "Meta","Security","Datetime","Web","PenTest",
    "Crypto","Wallet","OIDC","WebAuthn",
    "Telecom","NFC","RFID","IR","Wireless",
    "Social","Barcode",
    "Automotive","Aviation","MRZ","NMEA","TLE","Telemetry","EventSourcing",
    "AI Vector","OHLCV","GameDev","Prometheus",
]

groups = defaultdict(list)
for row in _REFERENCE:
    t = row[0].strip()
    cat = row[1] if len(row) > 1 else "Other"
    if not t or t.startswith("--") or cat == "Commands":
        continue
    groups[cat].append((t, cat))

# deduplicate within category
seen_global = set()
folders = []
for cat in CAT_ORDER + sorted(set(groups.keys()) - set(CAT_ORDER)):
    if cat not in groups:
        continue
    items = []
    for (t, c) in groups[cat]:
        if t in seen_global:
            continue
        seen_global.add(t)
        items.append(make_request(t, c))
    if items:
        folders.append({"name": f"{cat} ({len(items)})", "item": items})

# Static folders first
STATIC_FOLDERS = [
    {
        "name": "🔍 Core",
        "item": [
            {"name": "Health Check", "request": {"method": "GET", "url": {"raw": f"{BASE}/health", "host": [BASE], "path": ["health"]}}},
            {"name": "Root", "request": {"method": "GET", "url": {"raw": f"{BASE}/", "host": [BASE], "path": [""]}}},
            {"name": "List All Types", "request": {"method": "GET", "url": {"raw": f"{BASE}/list", "host": [BASE], "path": ["list"]}}},
            {"name": "List by Category", "request": {"method": "GET", "url": {"raw": f"{BASE}/list?cat=financial", "host": [BASE], "path": ["list"], "query": [{"key": "cat", "value": "financial"}]}}},
        ],
    },
    {
        "name": "⚡ Generate — by Type",
        "item": folders,
    },
    {
        "name": "📦 Bulk",
        "item": [
            {"name": "Bulk tckn ×20", "request": {"method": "GET", "url": {"raw": f"{BASE}/bulk/tckn?count=20&locale=TR", "host": [BASE], "path": ["bulk","tckn"], "query": [{"key":"count","value":"20"},{"key":"locale","value":"TR"}]}}},
            {"name": "Bulk iban ×10 (DE)", "request": {"method": "GET", "url": {"raw": f"{BASE}/bulk/iban?count=10&locale=DE", "host": [BASE], "path": ["bulk","iban"], "query": [{"key":"count","value":"10"},{"key":"locale","value":"DE"}]}}},
            {"name": "Bulk cardnum ×50", "request": {"method": "GET", "url": {"raw": f"{BASE}/bulk/cardnum?count=50&locale=TR", "host": [BASE], "path": ["bulk","cardnum"], "query": [{"key":"count","value":"50"},{"key":"locale","value":"TR"}]}}},
            {"name": "Bulk email ×100", "request": {"method": "GET", "url": {"raw": f"{BASE}/bulk/email?count=100&locale=TR", "host": [BASE], "path": ["bulk","email"], "query": [{"key":"count","value":"100"},{"key":"locale","value":"TR"}]}}},
            {"name": "Bulk uuid ×1000", "request": {"method": "GET", "url": {"raw": f"{BASE}/bulk/uuid?count=1000", "host": [BASE], "path": ["bulk","uuid"], "query": [{"key":"count","value":"1000"}]}}},
        ],
    },
    {
        "name": "🧩 Template",
        "item": [
            {
                "name": "KYC Record (TR)",
                "request": {
                    "method": "POST",
                    "url": {"raw": f"{BASE}/template", "host": [BASE], "path": ["template"]},
                    "header": [{"key": "Content-Type", "value": "application/json"}],
                    "body": {"mode": "raw", "raw": json.dumps({"types": ["tckn","fullname","birthdate","phone","email","address_full"], "count": 1, "locale": "TR"}, indent=2)},
                },
            },
            {
                "name": "Financial Transaction ×5",
                "request": {
                    "method": "POST",
                    "url": {"raw": f"{BASE}/template", "host": [BASE], "path": ["template"]},
                    "header": [{"key": "Content-Type", "value": "application/json"}],
                    "body": {"mode": "raw", "raw": json.dumps({"types": ["iban","cardnum","swift","balance","uuid","timestamp"], "count": 5, "locale": "TR"}, indent=2)},
                },
            },
            {
                "name": "Health Record (TR)",
                "request": {
                    "method": "POST",
                    "url": {"raw": f"{BASE}/template", "host": [BASE], "path": ["template"]},
                    "header": [{"key": "Content-Type", "value": "application/json"}],
                    "body": {"mode": "raw", "raw": json.dumps({"types": ["tckn","fullname","birthdate","blood_type","bmi","height","weight"], "count": 1, "locale": "TR"}, indent=2)},
                },
            },
            {
                "name": "E-Commerce Order ×3",
                "request": {
                    "method": "POST",
                    "url": {"raw": f"{BASE}/template", "host": [BASE], "path": ["template"]},
                    "header": [{"key": "Content-Type", "value": "application/json"}],
                    "body": {"mode": "raw", "raw": json.dumps({"types": ["order_id","fullname","email","phone","address_full","cardnum","tracking_number"], "count": 3, "locale": "TR"}, indent=2)},
                },
            },
            {
                "name": "Corporate DE ×5",
                "request": {
                    "method": "POST",
                    "url": {"raw": f"{BASE}/template", "host": [BASE], "path": ["template"]},
                    "header": [{"key": "Content-Type", "value": "application/json"}],
                    "body": {"mode": "raw", "raw": json.dumps({"types": ["company_name","vat_number","iban","bic","email","phone"], "count": 5, "locale": "DE"}, indent=2)},
                },
            },
        ],
    },
    {
        "name": "👤 Profile & Company",
        "item": [
            {"name": "Profile TR", "request": {"method": "GET", "url": {"raw": f"{BASE}/profile?locale=TR&count=1", "host": [BASE], "path": ["profile"], "query": [{"key":"locale","value":"TR"},{"key":"count","value":"1"}]}}},
            {"name": "Profile DE", "request": {"method": "GET", "url": {"raw": f"{BASE}/profile?locale=DE&count=1", "host": [BASE], "path": ["profile"], "query": [{"key":"locale","value":"DE"},{"key":"count","value":"1"}]}}},
            {"name": "Profile US", "request": {"method": "GET", "url": {"raw": f"{BASE}/profile?locale=US&count=1", "host": [BASE], "path": ["profile"], "query": [{"key":"locale","value":"US"},{"key":"count","value":"1"}]}}},
            {"name": "Bulk Profiles ×10 (TR)", "request": {"method": "GET", "url": {"raw": f"{BASE}/profile?locale=TR&count=10", "host": [BASE], "path": ["profile"], "query": [{"key":"locale","value":"TR"},{"key":"count","value":"10"}]}}},
            {"name": "Company TR", "request": {"method": "GET", "url": {"raw": f"{BASE}/company?locale=TR&count=1", "host": [BASE], "path": ["company"], "query": [{"key":"locale","value":"TR"},{"key":"count","value":"1"}]}}},
            {"name": "Company DE", "request": {"method": "GET", "url": {"raw": f"{BASE}/company?locale=DE&count=1", "host": [BASE], "path": ["company"], "query": [{"key":"locale","value":"DE"},{"key":"count","value":"1"}]}}},
            {"name": "Bulk Companies ×5", "request": {"method": "GET", "url": {"raw": f"{BASE}/company?locale=TR&count=5", "host": [BASE], "path": ["company"], "query": [{"key":"locale","value":"TR"},{"key":"count","value":"5"}]}}},
        ],
    },
    {
        "name": "📤 Export",
        "item": [
            {
                "name": "Export JSON — customers ×10",
                "request": {
                    "method": "POST",
                    "url": {"raw": f"{BASE}/export", "host": [BASE], "path": ["export"]},
                    "header": [{"key": "Content-Type", "value": "application/json"}],
                    "body": {"mode": "raw", "raw": json.dumps({"schema_map": {"citizen_id":"tckn","full_name":"fullname","email":"email","phone":"phone","iban":"iban","card_number":"cardnum"}, "count": 10, "locale": "TR", "format": "json", "table": "customers"}, indent=2)},
                },
            },
            {
                "name": "Export CSV — transactions ×50",
                "request": {
                    "method": "POST",
                    "url": {"raw": f"{BASE}/export", "host": [BASE], "path": ["export"]},
                    "header": [{"key": "Content-Type", "value": "application/json"}],
                    "body": {"mode": "raw", "raw": json.dumps({"schema_map": {"tx_id":"uuid","iban":"iban","amount":"balance","swift":"swift","ts":"timestamp"}, "count": 50, "locale": "TR", "format": "csv", "table": "transactions"}, indent=2)},
                },
            },
            {
                "name": "Export SQL — users ×100",
                "request": {
                    "method": "POST",
                    "url": {"raw": f"{BASE}/export", "host": [BASE], "path": ["export"]},
                    "header": [{"key": "Content-Type", "value": "application/json"}],
                    "body": {"mode": "raw", "raw": json.dumps({"schema_map": {"id":"uuid","username":"username","email":"email","phone":"phone","created_at":"timestamp"}, "count": 100, "locale": "TR", "format": "sql", "table": "users"}, indent=2)},
                },
            },
        ],
    },
]

total = sum(len(f["item"]) for f in folders)

collection = {
    "info": {
        "name": "mock-jutsu API",
        "description": (
            f"Algorithmic mock data engine — {total} types, 6 locales.\n\n"
            "Import one of the environment files (local.json or docker.json), "
            "select it, and run any request.\n\n"
            "Generate folder is organized by category. Each request includes\n"
            "the correct default parameters for that type. Disabled params\n"
            "(e.g. mask=true) can be enabled per request."
        ),
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
    },
    "variable": [{"key": "baseUrl", "value": "http://localhost:8000", "type": "string"}],
    "item": STATIC_FOLDERS,
}

out = "postman/mock-jutsu.postman_collection.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(collection, f, indent=2, ensure_ascii=False)

print(f"OK: {out} generated - {total} types across {len(folders)} category folders")
