# Contributing to Mock Jutsu

Mock Jutsu is not just a library; it's a high-performance standard for the fintech and testing ecosystem. To maintain this, we follow a rigorous 11-step development lifecycle.

## 🏗️ Standard Operating Procedure (SOP)

Every contribution must pass through these stages:

1.  **Legal Awareness:** Only mock data types that are legal and safe to simulate are accepted.
2.  **Strict TDD:** Write unit tests based on ISO/IETF/Industry standards BEFORE writing logic.
3.  **Zero-Dependency:** Pure Python only. No external packages.
4.  **Implementation:** Pass the unit tests with clean, modular code.
5.  **Integration (API):** Verify functionality via the core `jutsu.generate()` engine.
6.  **CLI/UI Validation:** Ensure the new type works in the terminal and appears in `mockjutsu list`.
7.  **Multilingual Docs:** Update the HTML documentation in all 6 supported languages.
8.  **README Maintenance:** Update badges and counts in the main README.md.
9.  **Profiling:** Latency must be **< 1.5ms**. No exceptions.
10. **Clean Architecture:** Use detailed docstrings and follow DRY/SOLID principles.
11. **Final Audit:** Pass `python scripts/audit_compliance.py` and achieve **100% test coverage**.

## 🌍 Global Ecosystem Strategy
We are expanding Mock Jutsu to Python (PyPI), macOS (Homebrew), Node.js (NPM), .NET (NuGet), and Java (Maven). If you are building a wrapper, ensure it follows the same algorithmic integrity as the core engine.

## ⚠️ Important Guidelines
- **Always Ask:** Before modifying existing files or starting a major feature, please discuss it with the maintainers.
- **PythonPath:** Run tests using: `export PYTHONPATH=src` (or PowerShell equivalent).
- **Compliance:** We use a pre-push hook. If your code isn't tested or synchronized, you won't be able to push/submit.

Stay professional, code with precision. ⚔️
