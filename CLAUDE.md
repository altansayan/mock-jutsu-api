# Mock Jutsu — AI Development Guide

This document provides strict rules and patterns for AI agents (Claude, Cursor, etc.) working on the Mock Jutsu ecosystem.

## 🛡️ STRICT DEVELOPMENT PROTOCOL (SOP)
The following 11-step lifecycle MUST be followed for every module. **No shortcuts allowed.**

1.  **Legal Check:** Ensure the data type is legal to mock. If it creates a real security vulnerability or is illegal, cancel the module immediately.
2.  **Unit Test (TDD) First:** Write unit tests in `tests/test_generators.py` based on real standards (ISO, IETF, etc.) BEFORE implementation.
3.  **Zero-Dependency Principle:** Use ONLY the Python Standard Library. Mathematical/cryptographic logic must be built from scratch in pure Python.
4.  **Code Development:** Implement the generator logic to pass the unit tests.
5.  **Integration (API) Tests:** Verify the data via the main API (`jutsu.generate()`) to ensure algorithmic compliance.
6.  **CLI & UI Tests:** Implement/test the CLI command and verify the new type appears in `mockjutsu list`.
7.  **Documentation Sync:** Update multilingual (TR, EN, DE, FR, RU, UK) `HOW-TO-MockJutsu-*.html` files with Regex and command references.
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
- **GITHUB MANDATE:** Every project produced by Asa Intelligence MUST be uploaded to GitHub.
- **PYTHONPATH:** Always run tests with `$env:PYTHONPATH='c:\Users\altan\repos\mock-jutsu-api\src'`.
- **Zero-Dependency:** Strict adherence. No external libraries.
- **Compliance:** Run `python scripts/audit_compliance.py` and `pytest --cov-fail-under=100` before every push.
