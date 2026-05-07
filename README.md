<div align="center">

<!-- A placeholder for a future logo or GIF -->
<!-- <img src="https://raw.githubusercontent.com/altansayan/mock-jutsu-api/main/assets/mock-jutsu-banner.png" alt="mock-jutsu banner" width="100%"> -->

# 🥷 mock-jutsu

**Stop mocking with random strings. Start generating cryptographically valid test data.**

[![Tests](https://img.shields.io/badge/tests-1867%20passed-22c55e?style=for-the-badge&logo=pytest)](./tests)
[![Python](https://img.shields.io/badge/python-3.9%2B-3b82f6?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Data Types](https://img.shields.io/badge/Data%20Types-174-a855f7?style=for-the-badge)](./HOW-TO.html)
[![Locales](https://img.shields.io/badge/Locales-6-ec4899?style=for-the-badge)](#-6-locales-100-real-algorithms)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-0-ff69b4?style=for-the-badge)](#-features-that-will-blow-your-mind)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](./LICENSE)

*Traditional Mockers give you a random 16-digit string and call it a credit card number.<br>**mock-jutsu runs Luhn. Every. Single. Time.***

[**Installation**](#%EF%B8%8F-installation) • [**Why mock-jutsu?**](#-why-not-faker) • [**Usage Guide**](#-usage) • [**174 Types**](#-174-supported-data-types)

</div>

---

## 🚀 The Ultimate Algorithmic Mock Data Engine

QA engineers, Data Scientists, and Fintech developers are tired of test data failing at the validation layer. **mock-jutsu** is built differently. It treats every identifier as a strict technical specification. If an algorithm defines a checksum, `mock-jutsu` computes it. **No shortcuts.**

### 🔥 Features That Will Blow Your Mind
- **Zero External Dependencies**: The core data engine uses pure Python standard library for maximum speed, security, and zero bloat.
- **1867 Automated Tests**: We don't guess. We verify. Every single format and locale is rigorously tested against real-world algorithmic specifications.
- **Multi-Interface**: Use it as a rich Python SDK, a blazing-fast CLI, or a FastAPI REST endpoint.
- **Export Anywhere**: Directly export structured records as JSON, CSV, or SQL `INSERT` statements with thousands of rows in milliseconds.
- **Context-Aware Profiles**: Generate a person, and their email, phone, national ID, and IBAN will inherently match their locale and name.

---

## 🤔 Why Mock Jutsu?

| Capability | `mock-jutsu` 🥷 | Traditional Mockers 🤡 |
|:---|:---:|:---:|
| **Card Numbers (Luhn Valid)** | ✅ 9 Networks Validated | ❌ Random digits |
| **IBANs (MOD-97 Valid)** | ✅ Country-specific | ❌ Format-only |
| **National IDs** | ✅ Real algorithms (6 countries) | ⚠️ Partial / Random |
| **Telecom (IMEI, ICCID, IMSI)**| ✅ 3GPP / ITU-T Valid | ❌ None |
| **Securities (ISIN, LEI, SEDOL)**| ✅ Checksum Validated | ❌ None |
| **Crypto (BTC, ETH addresses)** | ✅ Base58Check / Keccak-256 | ❌ None |
| **Barcodes (EAN, ISBN, GS1)** | ✅ GS1 v24.0 Valid | ❌ None |
| **Tracking (USPS/UPS/FedEx)** | ✅ Pub.97 Luhn / Mod-11 | ❌ None |
| **Banking Routing Codes** | ✅ Valid ABA/Sort/BIC | ⚠️ Format-only |
| **RFID & NFC Data** | ✅ EPC SGTIN-96, NDEF URI/Text | ❌ None |
| **Context-Aware Profiles** | ✅ Linked Name ↔ Email ↔ Phone | ⚠️ Disconnected randoms |
| **SQL/CSV Direct Export** | ✅ Native Support | ❌ Manual generation |
| **Built-in CLI Tool** | ✅ Out-of-the-box (`mockjutsu generate`) | ❌ Requires custom scripts |
| **Built-in REST API** | ✅ 1 command (`mockjutsu start-api`) | ❌ Requires custom wrapper |
| **External Dependencies** | ✅ **Zero** (Pure Python) | ❌ Relies on external files |

---

## ⚙️ Installation

Requires **Python 3.9+**.

```bash
# Standard Installation
pip install git+https://github.com/altansayan/mock-jutsu-api.git#egg=mockjutsu

# For Developers (Editable Mode)
git clone https://github.com/altansayan/mock-jutsu-api.git
cd mock-jutsu-api
pip install -e .
```

---

## 💻 Usage

Whether you are writing automated tests, working in the terminal, or spinning up a mock API, `mock-jutsu` is ready.

### 🐍 1. Python SDK

```python
from mockjutsu.core import jutsu

# 1. Complete, internally-consistent profiles
person = jutsu.profile(locale='DE')
print(person['nationalid']) # -> "86094599602" (Steuer-ID: ISO 7064 MOD 11,10 ✅)
print(person['iban'])       # -> "DE89370400440532013000" (ISO 13616 MOD-97 ✅)

# 2. Individual precise data types
card = jutsu.generate('cardnum', network='amex') # -> "376956063521007" (Luhn ✅)
btc = jutsu.generate('btc_address')              # -> "1BvBMSEYstWet..." (Base58Check SHA256d ✅)

# 3. 🎯 Fully Customizable Templates
# Define your own schema and generate a list of dictionaries instantly
users = jutsu.template(
    {'user_id': 'uuid', 'name': 'fullname', 'wallet': 'crypto_address'},
    count=100, locale='UK'
)

# 4. Generate thousands of records & export directly to SQL
sql = jutsu.export(
    {'id': 'uuid', 'name': 'fullname', 'card': 'cardnum', 'bank_account': 'iban'},
    count=5000, format='sql', table='users', locale='TR'
)
```

### ⚡ 2. Beautiful CLI

Generate valid test data straight from your terminal.

```bash
# Get single values instantly
$ mockjutsu generate tckn
$ mockjutsu generate iban --locale FR
$ mockjutsu generate cardnum --network troy

# Need an array of valid US phone numbers?
$ mockjutsu bulk phone --count 500 --locale US

# Generate SQL seed files on the fly
$ mockjutsu export uuid fullname cardnum --count 10000 --format sql --table test_users > seed.sql
```

### 🌐 3. Built-in REST API

Spin up a local endpoint to serve mock data to your frontend, mobile app, or test frameworks.

```bash
$ mockjutsu start-api --port 8000
```
```http
GET http://localhost:8000/generate/cardnum?network=visa
GET http://localhost:8000/profile?locale=DE&count=3

# Interactive Swagger UI automatically available at http://localhost:8000/docs
```

---

## 🌍 6 Locales. 100% Real Algorithms.

We don't just localize names; we localize **mathematics**.

| Locale | Country | National ID | Internal Algorithm Executed |
|:---:|:---|:---|:---|
| 🇹🇷 | **TR** | TCKN | Dual MOD-10 checksum, 11 digits |
| 🇺🇸 | **US** | SSN / EIN | ABA Routing MOD-10 |
| 🇬🇧 | **UK** | NIN / UTR | HMRC prefix restrictions |
| 🇩🇪 | **DE** | Steuer-ID | ISO 7064 MOD 11,10 |
| 🇫🇷 | **FR** | SIREN / TVA | Luhn + MOD-97 |
| 🇷🇺 | **RU** | INN / SNILS | Weighted checksum arrays, MOD-101 |

---

## 📦 174 Supported Data Types

We cover everything from standard identities to complex financial market identifiers.

<details>
<summary><b>👤 Identity & Demographic (32 types)</b></summary>
<br>
<code>tckn</code> <code>ssn</code> <code>ein</code> <code>nin</code> <code>siren</code> <code>siret</code> <code>tva</code> <code>inn</code> <code>snils</code> <code>ogrn</code> <code>passport</code> <code>license</code> +20 more
</details>

<details>
<summary><b>💳 Financial & Banking (23 types)</b></summary>
<br>
<code>cardnum</code> <code>cardnetwork</code> <code>iban</code> <code>swift</code> <code>bic</code> <code>sort_code</code> <code>routing_number</code> <code>sepa_ref</code> +15 more
</details>

<details>
<summary><b>📡 Telecom & IoT (20 types)</b></summary>
<br>
<code>imei</code> <code>iccid</code> <code>imsi</code> <code>msisdn</code> <code>rfid_uid</code> <code>epc</code> <code>nfc_uid</code> <code>ndef_uri</code> <code>apdu</code> <code>ir_nec</code> +10 more
</details>

<details>
<summary><b>💹 Securities & Crypto (9 types)</b></summary>
<br>
<code>isin</code> <code>cusip</code> <code>sedol</code> <code>lei</code> <code>btc_address</code> <code>eth_address</code> <code>tx_hash</code> <code>block_hash</code>
</details>

<details>
<summary><b>📦 E-Commerce & Barcodes (12 types)</b></summary>
<br>
<code>ean13</code> <code>upca</code> <code>isbn13</code> <code>gs1_128</code> <code>tracking_number</code> <code>sku</code> <code>order_id</code> +5 more
</details>

*(See our interactive guides for the full list of 174 types:
[🇹🇷 TR](./HOW-TO-MockJutsu-TR.html) | [🇺🇸 EN](./HOW-TO-MockJutsu-EN.html) | [🇬🇧 UK](./HOW-TO-MockJutsu-UK.html) | [🇩🇪 DE](./HOW-TO-MockJutsu-DE.html) | [🇫🇷 FR](./HOW-TO-MockJutsu-FR.html) | [🇷🇺 RU](./HOW-TO-MockJutsu-RU.html))*

---

## 🤝 Contributing

`mock-jutsu` thrives on community contributions. Found a checksum we're not validating? A locale we're missing? We'd love your help!

**🚨 Strict TDD & Performance Mandate**
To maintain our enterprise-grade quality, this repository mechanically enforces **Test-Driven Development (TDD)**.
- Every new generator must be fully tested mathematically.
- Every new generator must pass the `< 1.5ms` performance baseline.
- **GitHub Actions will automatically block any Pull Request that lacks passing tests.**

Please read our full **[CONTRIBUTING.md](./CONTRIBUTING.md)** guide before starting your work.

### Quick Start for Contributors
1. Fork the Project & clone it locally.
2. Install the pre-push safety hook: `python scripts/setup-hooks.py`
3. Write your test first, then implement your algorithm.
4. Commit your changes and open a Pull Request!

---

## ⚖️ Legal Disclaimer

Generated data is **entirely synthetic and for development/testing environments only.**
- Do not submit to real financial, government, or telecom production systems.
- Generated IBANs, card numbers, and national IDs are mathematically valid but **do not belong to real entities**.

<br>

<div align="center">
  <h3>If mock-jutsu saved you from debugging a "valid-looking but broken" test ID, please leave a ⭐!</h3>
  <p>Released under the <a href="./LICENSE">MIT License</a> • Copyright © 2025 <a href="https://github.com/altansayan">Altan Sezer Ayan — A.S.A</a></p>
</div>
