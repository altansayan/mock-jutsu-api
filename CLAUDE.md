# Mock Jutsu — AI Development Guide

This document provides strict rules and patterns for AI agents (Claude, Cursor, etc.) working on the Mock Jutsu ecosystem.

**Developer:** Altan Sezer Ayan  
**GitHub:** https://github.com/altansayan  
**LinkedIn:** https://www.linkedin.com/in/altansezerayan/  
**Repository:** https://github.com/altansayan/mock-jutsu-api  
**License:** MIT — https://github.com/altansayan/mock-jutsu-api/blob/main/LICENSE

## 🛡️ STRICT DEVELOPMENT PROTOCOL (SOP)
The following 11-step lifecycle MUST be followed for every module. **No shortcuts allowed.**

1.  **Legal Check:** Ensure the data type is legal to mock. If it creates a real security vulnerability or is illegal, cancel the module immediately.
2.  **Unit Test (TDD) First:** Write unit tests in `tests/test_generators.py` based on real standards (ISO, IETF, etc.) BEFORE implementation.
3.  **Zero-Dependency Principle:** Use ONLY the Python Standard Library. Mathematical/cryptographic logic must be built from scratch in pure Python.
4.  **Code Development:** Implement the generator logic to pass the unit tests.
5.  **Integration (API) Tests:** Verify the data via the main API (`jutsu.generate()`) to ensure algorithmic compliance.
6.  **CLI & UI Tests:** Implement/test the CLI command and verify the new type appears in `mockjutsu list`.
7.  **Documentation Sync:** Run `generate_locale_docs.py` to regenerate all 6 multilingual HTML files. Never edit HTML manually.
8.  **README.md Update:** Update the supported type counts, test counts, and UI badges in the main README.
9.  **Performance & Profiling:** Ensure latency is **< 1.5ms**. Test for CPU/RAM bottlenecks. Refactor if needed.
10. **Clean Code & DRY:** High readability, detailed docstrings, and modular architecture. Avoid spaghetti code.
11. **GitHub Push:** Only push to `main` after all 10 stages are successfully completed.

## 🌍 GLOBAL ECOSYSTEM STRATEGY (Fan-out)
Mock Jutsu aims to be the standard testing tool for all platforms:
- **PyPI (Python):** `pip install mockjutsu` (Active)
- **Homebrew (macOS/Linux):** `brew install mockjutsu`
- **NPM (JavaScript):** `npx mockjutsu` wrapper.
- **NuGet (.NET):** Standalone `.exe` via PyInstaller.
- **Maven (Java/Kotlin):** JNI/ProcessBuilder wrapper.
- **VS Code Marketplace:** Extension for direct IBAN/QR/UUID injection.

## ⚠️ MANDATORY RULES & GOTCHAS
- **NO UNAUTHORIZED CHANGES:** DO NOT change any file without asking the user first. Always ask for permission.
- **GITHUB MANDATE:** Every project produced by Altan Sezer Ayan MUST be uploaded to GitHub.
- **PYTHONPATH:** Always run tests with `$env:PYTHONPATH='src'` (PowerShell) or `export PYTHONPATH=src` (Bash).
- **Zero-Dependency:** Strict adherence. No external libraries.
- **Compliance:** Run `python scripts/audit_compliance.py` and `pytest --cov-fail-under=85` before every push.

---

## Project Overview

Mock Jutsu is a **zero-dependency, pure-Python** algorithmic mock data engine.
- **192 data types**, 6 locales (TR / US / UK / DE / FR / RU)
- All values are algorithmically generated (real checksums, ISO-compliant formats)
- Ships as a CLI tool (`mockjutsu`) and a Python API (`jutsu.generate()`)
- Python support: **3.10, 3.11, 3.12, 3.13** (3.9 is EOL — never add it back)
- Test coverage: **≥ 85%** enforced (currently ~97%)
- Performance: **< 1.5ms per call** (300ms for 200 iterations)

---

## Repository Layout

```
mock-jutsu-api/
├── src/mockjutsu/
│   ├── core.py                  # Master orchestrator — dispatches to generators
│   ├── cli.py                   # CLI commands + _REFERENCE table + _CAT_ORDER
│   ├── generators/
│   │   ├── identity.py          # TCKN, SSN, NIN, INN, SNILS...
│   │   ├── financial.py         # Cards (Luhn), IBAN, EMV QR, 3DS...
│   │   ├── banking.py           # SWIFT, SORT, routing, BIK...
│   │   ├── communication.py     # Phone, address, email, plate...
│   │   ├── meta.py              # UUID, JWT, IP, URL, API key, TOTP...
│   │   ├── corporate.py         # Company name, job title...
│   │   ├── health.py            # HL7, FHIR, DICOM, NHS, NPI, ICD-10...
│   │   ├── commerce.py          # VIN, vehicle, currency, invoice...
│   │   ├── iot.py               # RFID, NFC, NDEF, APDU, IR (NEC/RC5/Pronto)...
│   │   ├── barcode.py           # EAN-13, EAN-8, UPC-A, ISBN, GS1-128...
│   │   ├── telecom.py           # IMEI, ICCID, IMSI, MSISDN...
│   │   ├── financial_markets.py # ISIN, CUSIP, SEDOL, LEI, FIX, PSD2...
│   │   ├── crypto.py            # BTC/ETH addresses, tx hash, mnemonic...
│   │   ├── ecommerce.py         # SKU, order ID, tracking, DHL...
│   │   ├── location.py          # Lat/lon, timezone, country code...
│   │   ├── social.py            # Username, hashtag, bio, follower count...
│   │   ├── hardware.py          # Track2, EMV chip TLV, PIN block...
│   │   └── security.py          # CEF log, X.509 cert, pcap hex...
│   └── api/main.py              # FastAPI server (omitted from coverage)
│
├── tests/
│   ├── test_generators.py       # Main generator tests
│   ├── test_cli.py              # CLI command tests
│   ├── test_sync.py             # SYNC GUARD — enforces HTML/CLI/core consistency
│   ├── test_performance.py      # Latency baseline (< 300ms / 200 iter per type)
│   ├── test_security.py         # CEF / X.509 / pcap tests
│   ├── test_hl7_fhir_dicom.py   # HL7 / FHIR / DICOM tests
│   └── ...                      # Other domain-specific test files
│
├── generate_locale_docs.py      # HTML doc generator — MUST run before every push
├── scripts/
│   ├── audit_compliance.py      # Pre-push compliance auditor
│   └── run_all_checks.py        # Pre-push hook entry point
├── HOW-TO-MockJutsu-{TR,EN,UK,DE,FR,RU}.html  # Generated — do not edit manually
├── pyproject.toml               # Build config, test config, coverage config
└── .github/workflows/ci.yml     # CI: Python 3.10-3.13, fail-fast: false
```

---

## Detailed SOP — Adding a New Data Type

### Step 1 — Legal Check
Is this type legal to mock? If it creates a real exploit vector or is illegal to simulate, stop immediately.

### Step 2 — Write Tests First (TDD — Red Phase)
Create or extend a test file **before** writing any generator code.
Tests must reference real standards (ISO, IETF, RFC, industry spec).

```bash
pytest tests/test_<domain>.py -q --no-cov   # must FAIL at this stage
```

### Step 3 — Implement the Generator (Green Phase)

**If adding to an existing generator:** edit `src/mockjutsu/generators/<domain>.py`

**If creating a new generator:**
1. Create `src/mockjutsu/generators/<name>.py` with a `<Name>Generator` class
2. Add module-level imports (never lazy imports inside functions — hurts performance)
3. Class must expose: `def generate(self, data_type, **kwargs) -> str`

**Zero-Dependency rule:** only Python standard library. No `pip install` anything.

### Step 4 — Register in core.py

```python
# 1. Add a type set at the top of core.py
_MYNEW_TYPES = {'type_a', 'type_b'}

# 2. Import the generator
from .generators.mynew import MyNewGenerator

# 3. Instantiate in MockJutsuCore.__init__
self.mynew = MyNewGenerator()

# 4. Add dispatch in generate()
elif dt in _MYNEW_TYPES:
    result = self.mynew.generate(dt, **kwargs)
```

### Step 5 — Register in cli.py

```python
# Section header (visual separator in CLI list)
('--MyCategory--', '', False, '', '', '', ''),
# (type_name, Category, locale_aware, example, cli_cmd, description, extra_param)
('type_a', 'MyCategory', False, 'example output', 'generate type_a', 'What it does.', '-'),
```

If adding a **new category**, also add to `_CAT_ORDER` and `_CAT_COLORS` in cli.py.

### Step 6 — Regenerate HTML Docs (MANDATORY)

```powershell
# Windows PowerShell
$env:PYTHONIOENCODING="utf-8"; python generate_locale_docs.py

# Linux / macOS
PYTHONIOENCODING=utf-8 python generate_locale_docs.py
```

**Never manually edit the HTML files** — they will be overwritten by the generator.

### Step 7 — Run Full Test Suite

```bash
pytest tests/ -q --no-cov           # quick check
pytest tests/ --cov=mockjutsu       # with coverage (must be ≥ 85%)
```

### Step 8 — Performance Check

```bash
pytest tests/test_performance.py -q --no-cov
```

Every type must complete 200 iterations in < 300ms (1.5ms/call).
Inherently slow types go into `HEAVY_TYPES` in `test_performance.py`.

### Step 9 — Push

The pre-push hook runs automatically:
1. `audit_compliance.py` — structural checks
2. `pytest --cov-fail-under=85` — full test suite with coverage

Push is blocked if either fails.

---

## Sync Guards (test_sync.py)

`test_sync.py` enforces these invariants on every push:

| Test | What it checks | What breaks it |
|------|---------------|----------------|
| `test_core_type_in_reference_table` | Every `core.py` type is in `cli.py _REFERENCE` | Adding to core but forgetting cli.py |
| `test_core_type_visible_in_html_tr` | Every `_REFERENCE` type has a `data-fn` row in TR HTML | Forgetting to run `generate_locale_docs.py` |
| `test_html_type_count_matches_core` | `data-fn` count == `_REFERENCE` count (all 6 locales) | Forgetting to run `generate_locale_docs.py` |
| `test_no_orphan_types_in_reference` | No `_REFERENCE` type missing from `core.py` | Adding to cli.py without core.py |

---

## CI Pipeline

```
Trigger: push / PR to main
Matrix: Python 3.10, 3.11, 3.12, 3.13 (fail-fast: false)

Steps:
  1. actions/checkout@v4
  2. actions/setup-python@v5
  3. pip install -e ".[test]"
  4. playwright install chromium --with-deps
  5. pytest tests/ -v --cov=mockjutsu --cov-fail-under=85
```

Python 3.9 reached EOL October 2025 — never re-add it.

---

## Category System

```python
_CAT_ORDER = [
    "Identity", "Name", "Document", "Demographic",
    "Financial", "Contact", "Banking", "Corporate",
    "Health", "Commerce", "Meta", "Security", "RFID", "NFC", "IR",
    "Barcode", "Telecom", "CapMarkets(Trading)", "Crypto",
    "E-Commerce", "Location", "Social", "Hardware",
]
```

| Category | Domain |
|----------|--------|
| Financial | Payment cards, IBAN, EMV, 3DS — retail banking |
| Banking | SWIFT/BIC, routing, sort code — interbank |
| CapMarkets(Trading) | ISIN, CUSIP, FIX protocol, LEI — capital markets |
| Security | API keys, JWT, TOTP, CEF log, X.509, pcap |
| Health | HL7, FHIR, DICOM, NHS, NPI — medical |
| IoT (RFID/NFC/IR) | Hardware protocol data |

---

## Common Mistakes to Avoid

- **Lazy imports inside functions** → performance regression. Always import at module top.
- **Hardcoding the current year** in tests → breaks next year (use `datetime.now().year`).
- **Manually editing HTML files** → overwritten by generator. Always run `generate_locale_docs.py`.
- **Adding to core.py but not cli.py** → `test_sync.py` catches it, push blocked.
- **Using external libraries** → zero-dependency rule, push blocked by compliance audit.
- **Running generator with wrong encoding on Windows** → use `$env:PYTHONIOENCODING="utf-8"` in PowerShell.
