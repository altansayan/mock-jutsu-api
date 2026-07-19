# Changelog

All notable changes to Mock Jutsu are documented here.

## [1.1.4] - 2026-07-20

### Fixed
- **Docker image REST API was completely non-functional since Docker support was added (2026-06-22, v1.1.0+).** The builder stage installed the bare package plus `granian` only, never `fastapi`/`httpx` — every worker crashed on startup with `ModuleNotFoundError: No module named 'fastapi'` in an infinite respawn loop, and `/health` never came up. Fixed by installing the `[server]` extra (`pip install ".[server]"`), which pulls in `fastapi`, `granian`, and `httpx` together. Verified locally: built the image, ran it, confirmed `/health` responds and `/generate/tckn` returns valid data with all 4 workers stable.

## [1.1.3] - 2026-07-20

### Fixed
- Pin `click!=8.3.*` — click 8.3.0/8.3.1 have a regression in `CliRunner.invoke()` where the `finally` block's `sys.stdout.flush()` runs on an already-closed stream, raising `ValueError: I/O operation on closed file.` This broke essentially every CLI test (1287 failures) for anyone installing during that version window. Fixed upstream in click 8.4; excluding the whole 8.3.x line here since it's the narrowest safe fix without needing an exact good/bad patch boundary.

## [1.1.2] - 2026-07-20

### Added
- `jutsu.masker(type, value)` API — validates then masks a value per PCI DSS / GDPR / KVKK rules, returning `"No Valid Data"` on invalid input
- `cardnum_bin8` type and `--bin8` CLI flag (ISO/IEC 7812:2017 8-digit BIN masking)

### Fixed
- `ubl_invoice`: customer TCKN and supplier VKN now pass real checksum validation (previously random digits with no checksum — always invalid)
- `mt940` / `camt053`: account IBAN now uses real ISO 13616 MOD-97 check digits (previously randomized per its own "checksum approximate" note — invalid almost every time)

### Changed
- Centralized checksum algorithms (Luhn, IBAN MOD-97, ISIN/CUSIP, ABA routing, etc.) into a shared `algorithms` module and added a `validators` module — consolidates several previously duplicated/drifted implementations

## [1.1.1] - 2026-06-24

### Added
- 15 masked variant types (account_number_masked, micr_line_masked, etc.) plus Wave B/C security generators (password, password_hash, cve_id) — 390 total types

### Security
- Upgrade pip in Docker builder stage to fix CVE-2025-8869 and CVE-2026-8643

## [1.1.0] - 2026-06-22

### Added
- Full query parameter support for all API endpoints
- Postman collection with all 390 API endpoints
- Python API widget example in HOW-TO pages
- JMeter plugin section in Installation docs
- Docker Hub installation section in README

### Fixed
- Removed hardcoded locale/network defaults from API

## [1.0.2] - 2026-06-18

### Fixed
- Correct Granian CLI flags (removed uvicorn-specific options)

## [1.0.1] - 2026-06-15

### Fixed
- Performance test: add liquidity_pool_id to HEAVY_TYPES

## [1.0.0] - 2026-06-01

### Initial Release
- 390+ format-valid mock data types across 49 categories
- 6 locales: TR, UK, US, DE, FR, RU
- Real checksums: IBAN, TCKN, Luhn, VIN, NHS, SWIFT, MRZ and more
- CLI tool (`mockjutsu generate`)
- REST API (`mockjutsu start-api`)
- Python package (PyPI: `pip install mockjutsu`)
- JMeter plugin support
- Regulation-aware masking: PCI DSS, GDPR, KVKK, HIPAA
- Zero external dependencies
- 5955 tests passed
