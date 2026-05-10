# Contributing to Mock Jutsu

Mock Jutsu is a zero-dependency, pure-Python algorithmic mock data engine.
192 data types, 6 locales, real checksums and ISO-compliant formats.
This guide gets you from zero to your first merged contribution.

**Developer:** Altan Sezer Ayan  
**GitHub:** https://github.com/altansayan  
**LinkedIn:** https://www.linkedin.com/in/altansezerayan/  
**Repository:** https://github.com/altansayan/mock-jutsu-api

---

## Quick Setup

```bash
git clone https://github.com/altansayan/mock-jutsu-api.git
cd mock-jutsu-api
pip install -e ".[test]"
playwright install chromium
pytest tests/ -q --no-cov    # should be ~2875 passed
```

---

## How the Codebase Works

### Data flow

```
mockjutsu generate <type>
        ↓
   cli.py (Click)
        ↓
   core.py MockJutsuCore.generate()
        ↓
   generators/<domain>.py
        ↓
   string output
```

### core.py — the dispatcher

Every data type is registered in two places in `core.py`:

1. A **type set** (e.g. `_HEALTH_TYPES = {'nhs_number', 'icd10', ...}`)
2. A dispatch branch in `generate()`:
   ```python
   elif dt in _HEALTH_TYPES:
       result = self.health.generate(dt, **kwargs)
   ```

### cli.py — the reference table

`_REFERENCE` is a list of tuples that drives:
- `mockjutsu list` output
- All 6 multilingual HTML documentation files (via `generate_locale_docs.py`)
- Sync guard tests (`test_sync.py`)

```python
# (type_name, Category, locale_aware, example_output, cli_cmd, description, extra_param)
('nhs_number', 'Health', False, '943 476 5919', 'generate nhs_number', 'UK NHS Number (Modulo 11).', '-'),
```

---

## Adding a New Data Type — Step by Step

### 1. Write tests first (TDD)

Create `tests/test_<domain>.py` or extend an existing one.
Reference the real standard (ISO, RFC, NHS spec, etc.).

```python
class TestMyNewType:
    def test_format(self):
        val = jutsu.generate('my_type')
        assert re.match(r'^[A-Z]{2}\d{10}$', val)

    def test_bulk_unique(self):
        results = jutsu.bulk('my_type', 20)
        assert len(set(results)) > 1
```

Run to confirm they **fail** (red phase):
```bash
pytest tests/test_<domain>.py -q --no-cov
```

### 2. Implement the generator

Edit or create `src/mockjutsu/generators/<domain>.py`.

Rules:
- **Zero external dependencies** — pure Python stdlib only
- **Module-level imports** — never `import x` inside a function (performance)
- Generator class must implement `def generate(self, data_type, **kwargs) -> str`
- Return `f"ERROR: Unknown type '{data_type}'"` for unknown types

```python
import random
import secrets

class MyDomainGenerator:
    def generate(self, data_type, **kwargs):
        if data_type == 'my_type':
            return _generate_my_type()
        return f"ERROR: Unknown type '{data_type}'"

def _generate_my_type():
    ...
```

Run tests to confirm they **pass** (green phase):
```bash
pytest tests/test_<domain>.py -q --no-cov
```

### 3. Register in core.py

```python
# Add type set (top of file, with other _*_TYPES)
_MYDOMAIN_TYPES = {'my_type', 'my_other_type'}

# Import the generator (with other imports)
from .generators.mydomain import MyDomainGenerator

# Instantiate in __init__
self.mydomain = MyDomainGenerator()

# Add dispatch in generate()
elif dt in _MYDOMAIN_TYPES:
    result = self.mydomain.generate(dt, **kwargs)
```

### 4. Register in cli.py _REFERENCE

```python
# Optional section header (visual separator in CLI list output)
('--MyCategory--', '', False, '', '', '', ''),
# Type row
('my_type', 'MyCategory', False, 'ABC1234567890', 'generate my_type', 'What this generates.', '-'),
```

If using a **new category**, also add it to `_CAT_ORDER` and `_CAT_COLORS`:
```python
_CAT_ORDER = [..., 'MyCategory']
_CAT_COLORS = {'MyCategory': 'bright_magenta'}
```

### 5. Regenerate HTML documentation (MANDATORY)

The 6 multilingual HTML files are auto-generated — never edit them manually.

```powershell
# Windows PowerShell
$env:PYTHONIOENCODING="utf-8"; python generate_locale_docs.py

# Linux / macOS
PYTHONIOENCODING=utf-8 python generate_locale_docs.py
```

Expected output:
```
✅ System synced: 195 types, 2900 tests.
Generated: HOW-TO-MockJutsu-TR.html
Generated: HOW-TO-MockJutsu-EN.html
...
```

### 6. Run the full test suite

```bash
pytest tests/ -q --no-cov          # fast check
pytest tests/ --cov=mockjutsu      # with coverage (must be ≥ 85%)
```

### 7. Performance check

Every type must complete 200 iterations in under 300ms (1.5ms per call).

```bash
pytest tests/test_performance.py -q --no-cov
```

If your type is inherently slow (e.g. involves many random bytes), add it to `HEAVY_TYPES`
in `test_performance.py` to exempt it from the latency baseline.

### 8. Commit and push

```bash
git add <files>
git commit -m "feat(<domain>): add <type_name> generator"
git push origin main
```

The pre-push hook runs automatically before upload:
- `scripts/audit_compliance.py` — checks zero-dependency, structural rules
- `pytest --cov-fail-under=85` — full test suite with coverage enforcement

**Push is blocked if any check fails.**

---

## Sync Guard — What Keeps Everything Consistent

`tests/test_sync.py` runs on every push and enforces:

| Check | Rule |
|-------|------|
| `test_core_type_in_reference_table` | Every type in `core.py` must be in `cli.py _REFERENCE` |
| `test_core_type_visible_in_html_tr` | Every `_REFERENCE` type must have a `data-fn` row in TR HTML |
| `test_html_type_count_matches_core` | `data-fn` count in all 6 HTML files must equal `_REFERENCE` count |
| `test_no_orphan_types_in_reference` | No `_REFERENCE` type may be missing from `core.py` |

**If you forget to run `generate_locale_docs.py`**, the HTML won't have the new `data-fn` rows,
the count test fails, and push is blocked. This is by design.

---

## CI Pipeline

GitHub Actions runs on every push and PR to `main`:

- **Matrix:** Python 3.10, 3.11, 3.12, 3.13
- **fail-fast: false** — all Python versions report independently
- **Steps:** checkout → setup-python → `pip install -e ".[test]"` → playwright install → pytest

Python version policy: only active CPython releases.
Python 3.9 reached EOL October 2025 and has been removed permanently.

---

## Project Constraints

| Rule | Detail |
|------|--------|
| Zero dependencies | Only Python stdlib. `import requests` → rejected. |
| No lazy imports | Imports inside functions hurt performance at 200 iter/call. |
| No hardcoded years | Use `datetime.now().year` — hardcoded years break next January. |
| No manual HTML edits | Always run `generate_locale_docs.py` — HTML is generated. |
| Test coverage ≥ 85% | Enforced by pyproject.toml and CI. Currently ~97%. |
| Latency < 1.5ms/call | Enforced by `test_performance.py`. |

---

## Category Reference

| Category | Contains |
|----------|----------|
| Identity | TCKN, SSN, NIN, INN, SNILS, passports... |
| Financial | Cards (Luhn), IBAN, EMV, 3DS, credit score... |
| Banking | SWIFT, sort code, routing number, BIK... |
| CapMarkets(Trading) | ISIN, CUSIP, SEDOL, LEI, FIX protocol, PSD2... |
| Health | HL7, FHIR, DICOM, NHS, NPI, ICD-10, BMI... |
| Security | API key, JWT, TOTP, CEF log, X.509, pcap hex... |
| IoT (RFID/NFC/IR) | EPC, NDEF, APDU, NEC/RC5/Pronto IR codes... |
| Hardware | Track2, EMV chip TLV, ISO 9564 PIN block... |

---

## 🌍 Global Ecosystem Strategy

We are expanding Mock Jutsu to all major platforms. If you are building a wrapper,
ensure it follows the same algorithmic integrity as the core engine.

- **PyPI (Python):** `pip install mockjutsu` (Active)
- **Homebrew (macOS/Linux):** `brew install mockjutsu`
- **NPM (JavaScript):** `npx mockjutsu` wrapper
- **NuGet (.NET):** Standalone `.exe` via PyInstaller
- **Maven (Java/Kotlin):** JNI/ProcessBuilder wrapper
- **VS Code Marketplace:** Extension for direct IBAN/QR/UUID injection

---

## Getting Help

- Open an issue: https://github.com/altansayan/mock-jutsu-api/issues
- Read the type reference: `mockjutsu list`
- Browse the interactive docs: `HOW-TO-MockJutsu-EN.html`

---

Stay professional, code with precision. ⚔️
