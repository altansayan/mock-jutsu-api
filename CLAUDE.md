# Mock Jutsu — AI Agent Development Guide

This document is the single source of truth for AI agents (Claude Code, Cursor, etc.)
working on this repository. Read it fully before touching any file.

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

## Mandatory SOP — Adding a New Data Type

Follow this exact order. **No shortcuts.**

### Step 1 — Legal Check
Is this type legal to mock? If it creates a real exploit vector or is illegal to simulate,
stop immediately.

### Step 2 — Write Tests First (TDD — Red Phase)
Create or extend a test file **before** writing any generator code.
Tests must reference real standards (ISO, IETF, RFC, industry spec).

```bash
# Run to confirm tests fail (expected at this stage)
pytest tests/test_<domain>.py -q --no-cov
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

**Add rows to `_REFERENCE`:**
```python
# Section header (visual separator in CLI list)
('--MyCategory--', '', False, '', '', '', ''),
# Type rows: (type_name, Category, locale_aware, example, cli_cmd, description, extra_param)
('type_a', 'MyCategory', False, 'example output', 'generate type_a', 'What it does.', '-'),
```

**If adding a new category**, also add it to:
```python
_CAT_ORDER = [..., 'MyCategory']          # display order
_CAT_COLORS = {'MyCategory': 'bright_red'}  # rich color
```

### Step 6 — Regenerate HTML Docs (MANDATORY)

```powershell
# PowerShell (Windows)
$env:PYTHONIOENCODING="utf-8"; python generate_locale_docs.py

# Bash/Linux
PYTHONIOENCODING=utf-8 python generate_locale_docs.py
```

This regenerates all 6 `HOW-TO-MockJutsu-*.html` files.
**Never manually edit the HTML files** — they will be overwritten.

### Step 7 — Run Full Test Suite

```bash
pytest tests/ -q --no-cov           # quick check
pytest tests/ --cov=mockjutsu       # with coverage report
```

All tests must pass. Coverage must stay ≥ 85%.

### Step 8 — Performance Check

```bash
pytest tests/test_performance.py -q --no-cov
```

Every type must complete 200 iterations in < 300ms (1.5ms/call).
If a new type is inherently slow (e.g., cryptographic), add it to `HEAVY_TYPES`
in `test_performance.py` to exempt it from the baseline.

### Step 9 — Push

```bash
git add <files>
git commit -m "feat(<domain>): add <type> generator"
git push origin main
```

The pre-push hook runs automatically:
1. `audit_compliance.py` — structural checks
2. `pytest --cov-fail-under=85` — full test suite with coverage

Push is blocked if either fails.

---

## Sync Guards (test_sync.py)

`test_sync.py` enforces three invariants on every push:

| Test | What it checks | What breaks it |
|------|---------------|----------------|
| `test_core_type_in_reference_table` | Every `core.py` type is in `cli.py _REFERENCE` | Adding a type to core but forgetting cli.py |
| `test_core_type_visible_in_html_tr` | Every `_REFERENCE` type has a `data-fn` row in TR HTML | Forgetting to run `generate_locale_docs.py` |
| `test_html_type_count_matches_core` | `data-fn` row count == `_REFERENCE` count (all 6 locales) | Forgetting to run `generate_locale_docs.py` |
| `test_no_orphan_types_in_reference` | No `_REFERENCE` type missing from `core.py` | Adding to cli.py without core.py |

**The HTML check is the generator enforcement mechanism.**
If `generate_locale_docs.py` is not run, `data-fn` rows are missing → test fails → push blocked.

---

## CI Pipeline

File: `.github/workflows/ci.yml`

```
Trigger: push / PR to main
Matrix: Python 3.10, 3.11, 3.12, 3.13 (fail-fast: false — all versions report independently)

Steps:
  1. actions/checkout@v4
  2. actions/setup-python@v5
  3. pip install -e ".[test]"
  4. playwright install chromium --with-deps
  5. pytest tests/ -v --cov=mockjutsu --cov-fail-under=85
```

**Python version policy:** Only active CPython releases. 3.9 reached EOL October 2025 — never re-add it.

---

## Category System

Categories are defined in `cli.py`:

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

- **Lazy imports inside functions** → performance regression in tight loops. Always import at module top.
- **Hardcoding the current year** in tests → breaks next year (use `datetime.now().year`).
- **Manually editing HTML files** → overwritten by generator. Always run `generate_locale_docs.py`.
- **Adding to core.py but not cli.py** → `test_sync.py` catches it, push blocked.
- **Using external libraries** → zero-dependency rule, push blocked by compliance audit.
- **Running generator with wrong encoding on Windows** → use `$env:PYTHONIOENCODING="utf-8"` in PowerShell.

---

## 🌍 Global Ecosystem Strategy (Fan-out)

Mock Jutsu aims to be the standard testing tool for all platforms:
- **PyPI (Python):** `pip install mockjutsu` (Active)
- **Homebrew (macOS/Linux):** `brew install mockjutsu`
- **NPM (JavaScript):** `npx mockjutsu` wrapper
- **NuGet (.NET):** Standalone `.exe` via PyInstaller
- **Maven (Java/Kotlin):** JNI/ProcessBuilder wrapper
- **VS Code Marketplace:** Extension for direct IBAN/QR/UUID injection

---

## ⚠️ Mandatory Rules & Gotchas

- **NO UNAUTHORIZED CHANGES:** Do NOT change any file without asking the user first. Always ask for permission.
- **GITHUB MANDATE:** Every project produced by ASA Intelligence MUST be uploaded to GitHub.
- **PYTHONPATH:** Always run tests with `$env:PYTHONPATH='src'` (PowerShell) or `export PYTHONPATH=src` (Bash).
- **Zero-Dependency:** Strict adherence. No external libraries in generators.
- **Compliance:** Run `python scripts/audit_compliance.py` before every push.
- **Coverage:** `pytest --cov-fail-under=85` — never drop below 85%.
