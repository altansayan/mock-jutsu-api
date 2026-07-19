# Changelog

All notable changes to Mock Jutsu are documented here.

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
