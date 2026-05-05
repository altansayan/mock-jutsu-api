# 🥷 mock-jutsu-api

**The Algorithmic Mock Data Engine for Fintech & Cross-Border Testing.**  
*Developed by [Altan Sezer Ayan](https://github.com/altansayan)*

`mock-jutsu-api` generates legally-structured fake data for 6 countries with real regulatory algorithms — TCKN checksums, Luhn-valid cards, VIN check digits, NHS numbers, ABA routing validation, and more. **689 tests. Zero false positives.**

---

## ✨ Why mock-jutsu?

| Feature | mock-jutsu | Faker |
|:---|:---:|:---:|
| Real checksum algorithms | ✅ | ❌ |
| 6-country national ID compliance | ✅ | Partial |
| Fintech-grade: IBAN, BIC, SWIFT, Routing | ✅ | ❌ |
| VIN (ISO 3779) check digit | ✅ | ❌ |
| NHS number weighted checksum | ✅ | ❌ |
| Bulk + Template + Profile + Export | ✅ | Partial |
| `profile()` — one call, all fields consistent | ✅ | ❌ |
| RFID/NFC: EPC SGTIN-96, NDEF, APDU | ✅ | ❌ |
| IR: NEC/RC-5 checksums, Pronto Hex | ✅ | ❌ |

---

## 🌍 6 Locales

| Code | Country | National ID Algorithm |
|:---:|:---|:---|
| `TR` | Turkey | TCKN — dual MOD-10 checksum |
| `US` | United States | SSN — ABA routing MOD-10 |
| `UK` | United Kingdom | NIN — HMRC prefix restrictions |
| `DE` | Germany | Steuer-ID — ISO 7064 MOD 11,10 |
| `FR` | France | NIR/INSEE — MOD-97 checksum |
| `RU` | Russia | INN — weighted [2,4,10,3,5,9,4,6,8] |

---

## 📦 Install

```bash
git clone https://github.com/altansayan/mock-jutsu-api
cd mock-jutsu-api
pip install -e .
```

---

## 🚀 Quick Start

### Python API

```python
from mockjutsu.core import jutsu

# Single value
jutsu.generate('tckn')                         # "34521876543"
jutsu.generate('cardnum', network='troy')      # "9792483716250934"
jutsu.generate('iban', locale='DE')            # "DE89370400440532013000"

# Complete person profile — all fields consistent
jutsu.profile(locale='TR')
# {
#   "id": "f47ac10b-...", "firstname": "Mert", "lastname": "Yılmaz",
#   "fullname": "Mert Yılmaz", "gender": "M", "birthdate": "1990-04-12",
#   "nationalid": "34521876543", "phone": "+905321234567",
#   "email": "mert.yilmaz42@gmail.com", "iban": "TR330006100519..."
# }

# Company profile
jutsu.company(locale='DE')
# {
#   "name": "Fischer Technologien GmbH", "hrb": "HRB 48291",
#   "ust_id": "DE273815499", "iban": "DE89370400440532013000",
#   "bic": "DEUTDEDB", ...
# }

# Bulk
jutsu.bulk('tckn', count=1000)                 # ["34521...", "67890...", ...]

# Template → structured records
jutsu.template({
    'id':      'uuid',
    'name':    'fullname',
    'card':    'cardnum',
    'amount':  'balance',
    'iban':    'iban',
}, count=100, locale='TR')

# Export as SQL seed
jutsu.export({'id':'uuid','name':'fullname','card':'cardnum'},
             count=500, format='sql', table='users', locale='TR')
```

### CLI

```bash
mockjutsu generate tckn
mockjutsu generate cardnum --network amex
mockjutsu generate iban --locale DE
mockjutsu generate fullname --locale RU
mockjutsu generate swift --locale UK
```

---

## 📋 All 80+ Data Types

### 👤 Identity

| Type | Output | Algorithm |
|:---|:---|:---|
| `tckn` | `34521876543` | 11-digit dual MOD-10 |
| `ykn` | `99341827461` | 11-digit Luhn |
| `nationalid` | locale-aware | TCKN / SSN / NIN / Steuer-ID / NIR / INN |
| `ssn` | `234-56-7890` | US format |
| `nin` | `AB 12 34 56 C` | HMRC prefix rules |
| `firstname` / `lastname` / `fullname` | `Emre Yılmaz` | locale name pools |
| `patronymic` | `Иванович` | RU only |
| `passport` / `license` | `P4827361` | — |
| `age` / `gender` / `birthdate` | `34` / `Male` / `1990-04-12` | — |

### 🏛️ Tax & Business IDs

| Type | Output | Country |
|:---|:---|:---|
| `taxid` | locale-aware | TR→VKN, US→EIN, UK→UTR, DE→USt-IdNr, FR→SIREN, RU→INN |
| `vkn` | `3847261095` | TR — proprietary 10-digit checksum |
| `ein` | `82-4739261` | US |
| `utr` | `1234567890` | UK |
| `ust_id` / `ustid` | `DE273815499` | DE — ISO 7064 MOD 11,10 |
| `hrb` | `HRB 48291` | DE |
| `siren` | `732829320` | FR — Luhn |
| `siret` | `73282932000074` | FR — double Luhn |
| `tva` | `FR58732829320` | FR — MOD-97 key |
| `inn` | `7707083893` | RU |
| `ogrn` | `1024700218114` | RU — 13-digit MOD-11 |
| `kpp` | `770701001` | RU |
| `mersis` | `3847261095012345` | TR — 16 digits |
| `employer_id` | locale-aware | TR→MERSIS, US→EIN, UK→CRN, DE→HRB, FR→SIRET, RU→OGRN |

### 🏥 Insurance & Social IDs

| Type | Output | Country |
|:---|:---|:---|
| `insurance_id` | locale-aware | TR→SGK, US→SSN, UK→PAYE, DE→RVN, FR→INSEE, RU→SNILS |
| `sgk` | `34-0012345-1.03-01` | TR |
| `paye` | `123/AB1234` | UK |
| `rvn` | `12 140382 A 0041` | DE |
| `snils` | `112-233-445 95` | RU — MOD-101 |

### 💳 Financial

| Type | Output | Notes |
|:---|:---|:---|
| `cardnum` | `4532015112830366` | 9 networks, Luhn valid |
| `iban` | `TR330006100519...` | locale-aware prefix + length |
| `cardnetwork` / `cardtype` / `cardstatus` / `cardcategory` | `VISA` / `Credit` | — |
| `cardowner` | `EMRE KAYA` | uppercase fullname |
| `cvv3` / `cvv4` / `pin` | `847` / `2938` / `4728` | — |
| `expiry` / `expirymonth` / `expiryyear` | `09/27` | — |
| `issuer` | `AnadoluFinans A.Ş.` | fictional bank names |
| `balance` | `4827.50` | `min` / `max` kwargs |

### 🏦 Banking

| Type | Output | Notes |
|:---|:---|:---|
| `swift` / `bic` | `DEUTDEDB` | real public BIC codes |
| `routing_number` | `021000021` | US ABA — MOD-10 checksum |
| `sort_code` | `20-00-00` | UK — Pay.UK published |
| `bik_code` | `044525225` | RU — Central Bank published |
| `bank_name` | `Berliner Finanzbank AG` | fictional names |
| `transaction` | `{ref, iban×2, amount, currency, ...}` | FAST/SEPA/ACH/SWIFT channels |

### 🏢 Corporate

| Type | Output | Notes |
|:---|:---|:---|
| `company_name` | `Fischer Technologien GmbH` | locale-aware legal suffix |
| `job_title` | `Yazılım Mühendisi` | locale-aware, 15 titles each |

### 🏥 Health

| Type | Output | Notes |
|:---|:---|:---|
| `blood_type` | `A+` / `O-` | 8 types |
| `nhs_number` | `943 476 5919` | UK — weighted MOD-11 checksum |
| `icd10` | `J18.9` | WHO ICD-10 codes |
| `height` | `178 cm` / `5'10"` | locale-aware units |
| `weight` | `74 kg` / `163 lbs` | locale-aware units |

### 🚗 Commerce & Vehicle

| Type | Output | Notes |
|:---|:---|:---|
| `currency` | `{"code":"TRY","symbol":"₺",...}` | locale-aware |
| `tax_rate` | `{"name":"KDV","standard":20,...}` | locale-aware rates |
| `invoice_number` | `INV-2024-001234` | locale-aware prefix |
| `vin` | `WBA3A5C5XMD123456` | ISO 3779 — check digit at pos 9 |
| `vehicle` | `{make, model, year, vin, color, fuel}` | locale-aware brands |

### 📍 Communication

| Type | Output | Notes |
|:---|:---|:---|
| `phone` / `phone_country` / `phone_area` / `phone_local` | `+905321234567` | locale E.164 |
| `address_full` / `address_city` / `address_street` | `İstanbul, Bağdat Caddesi No:47` | — |
| `postalcode` | `34820` / `SW1 3AB` | locale format |
| `plate` | `34 BCK 447` / `SW23 KTR` | 6-locale formats |
| `email` | `user492@gmail.com` | locale domain |

### 📡 IoT / Protocol

#### RFID

| Type | Output | Algorithm |
|:---|:---|:---|
| `rfid_uid` | `A4:B2:3C:D1` / `04:A3:B2:C1:D0:E5:F6` | ISO 14443-3A — 4-byte or 7-byte UID, OS-CSPRNG body |
| `epc` | `3034257BF400B71800004000` | GS1 SGTIN-96 (ISO 18000-6C) — 96-bit: Header(0x30)+Filter+Partition+CompanyPrefix+ItemRef+Serial(38b) |
| `rfid_tag` | `{uid, standard, frequency_mhz, memory_bytes, epc?}` | Profile-matched: ISO 14443-A/B, ISO 15693, ISO 18000-6C, EM4100, HID Prox |

#### NFC

| Type | Output | Algorithm |
|:---|:---|:---|
| `nfc_uid` | `04:A3:B2:C1:D0:E5:F6` | ISO 14443-3A 7-byte — IC manufacturer byte + 48-bit CSPRNG |
| `nfc_atqa` | `00:44` | 2-byte Answer To reQuest — real NTAG/MIFARE profiles |
| `nfc_sak` | `20` | 1-byte Select AcKnowledge — matched to tag profile |
| `ndef_uri` | `{raw_hex, decoded, tnf, type, prefix_code}` | NFC Forum RTD v1.0 — header 0xD1, URI prefix table, 32-bit random path |
| `ndef_text` | `{raw_hex, decoded, lang, encoding}` | NFC Forum Text RTD — status byte, lang code, UTF-8 payload; locale-aware |
| `apdu` | `{cla, ins, p1, p2, hex, description}` | ISO 7816-4 — real EMVCo AIDs (Visa/MC/Amex/JCB/UnionPay) |
| `nfc_tag` | `{uid, atqa, sak, type, capacity_bytes, ndef_message}` | Complete NFC tag record — profile-matched + embedded NDEF |

#### IR (Infrared)

| Type | Output | Algorithm |
|:---|:---|:---|
| `ir_nec` | `{address, command, hex, checksum_valid}` | NEC 32-bit — address+~address+command+~command; XOR checksum guaranteed |
| `ir_rc5` | `{system, command, toggle, frame_bits}` | Philips RC-5 — 14-bit Manchester; Start+Field+Toggle+System(5b)+Cmd(6b) |
| `ir_pronto` | `"0000 006D 0022 0000 0156 00AB ..."` | Pronto Hex (CCF) — 38 kHz NEC frame; compatible with Home Assistant, Broadlink, Harmony |
| `ir_raw` | `{carrier_hz, address, command, pulses}` | Raw µs pulse/space — NEC LSB-first; direct ESPHome/MQTT IR blaster input |

---

### ⚙️ Tech / System

| Type | Output | Notes |
|:---|:---|:---|
| `uuid` / `requestid` / `correlationid` / `sessionid` / `idempotencykey` | RFC 4122 v4 | — |
| `deviceid` | `B3D9F2A1-...` | IDFA/GAID format |
| `ipv4` / `ipv6` | `192.168.1.1` / `2001:0db8:...` | — |
| `jwt` | `eyJhbGci...` | real base64url, no "Bearer" prefix |
| `bearertoken` | `Bearer eyJhbGci...` | with prefix |
| `hash` | `e3b0c44298fc...` | md5/sha1/sha256/sha512 via `algorithm=` |
| `mac_address` | `A4:C3:F0:3D:8E:21` | real OUI prefixes |
| `url` | `https://mockapi-42.co.uk/api/v1/users` | locale TLD |
| `domain` | `test-77.com.tr` | locale TLD |
| `color` | `#3A7BF0` | hex/rgb/hsl/name via `format=` |
| `useragent` | `Mozilla/5.0 (Windows NT...)` | realistic Chrome/Firefox/Safari |
| `browser_name` / `browser_version` / `browser_engine` | `Chrome` / `124.0` / `Blink` | — |
| `timestamp` / `timestamp_iso` | `1748000000` / `2025-01-15T14:32:07` | — |
| `clientversion` | `3.2.7` | semver |
| `apppassword` | `483716` | no repeats, no sequential runs |
| `signature` | `a3f9b2c1...` | HMAC-SHA256 via `secret=` + `payload=` |

---

## 🧩 Power Features

### `profile()` — Complete Person in One Call

```python
p = jutsu.profile(locale='DE')
# {
#   "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
#   "firstname": "Felix", "lastname": "Müller",
#   "fullname": "Felix Müller", "gender": "M",
#   "birthdate": "1988-09-23",
#   "nationalid": "86094599602",    ← Steuer-ID (ISO 7064 valid)
#   "phone": "+4917612345678",
#   "email": "felix.mueller@web.de",
#   "address": "München, Schillerstraße No:12",
#   "iban": "DE89370400440532013000"
# }
```

### `company()` — Full Company Record

```python
c = jutsu.company(locale='FR')
# {
#   "id": "3e4a1b2c-...", "name": "Martin Finance SAS",
#   "employer_id": "73282932000074",  ← SIRET (double Luhn valid)
#   "tax_id": "732829320",            ← SIREN (Luhn valid)
#   "iban": "FR7614508590013xxxxxxxx",
#   "bic": "BNPAFRPP",
#   "phone": "+33612345678",
#   "address": "Paris, Rue de la Paix No:8"
# }
```

### `bulk()` — Thousands in Milliseconds

```python
# 1000 valid Turkish ID numbers
ids = jutsu.bulk('tckn', count=1000)

# 500 Luhn-valid Visa cards
cards = jutsu.bulk('cardnum', count=500, network='visa')
```

### `template()` — Structured Test Records

```python
records = jutsu.template({
    'user_id':   'uuid',
    'name':      'fullname',
    'card':      'cardnum',
    'amount':    'balance',
    'currency':  'currency',
    'timestamp': 'timestamp_iso',
}, count=100, locale='TR')
# → list of 100 dicts, each with all 6 fields
```

### `export()` — Direct DB Seed

```python
# SQL INSERT for Postgres/MySQL
sql = jutsu.export(
    {'id':'uuid', 'name':'fullname', 'card':'cardnum', 'balance':'balance'},
    count=500, format='sql', table='test_users', locale='TR'
)
# INSERT INTO test_users (id, name, card, balance) VALUES
#   ('f47ac10b-...', 'Emre Yılmaz', '4532015112830366', 12840.50),
#   ...

# CSV
csv = jutsu.export(schema, count=1000, format='csv')

# JSON
json_data = jutsu.export(schema, count=50, format='json')
```

---

## 🗂️ Supported Card Networks

| `network=` | Name | Prefix | Length |
|:---:|:---|:---|:---:|
| `visa` | Visa | `4` | 16 |
| `mc` | Mastercard | `51–55` | 16 |
| `amex` | American Express | `34`, `37` | 15 |
| `troy` | Troy (Turkey) | `9792` | 16 |
| `jcb` | JCB | `352–358` | 16 |
| `discover` | Discover | `6011`, `65` | 16 |
| `unionpay` | UnionPay | `62` | 16 |
| `mir` | Mir (Russia) | `2200–2202` | 16 |
| `maestro` | Maestro | `6304`, `6759` | 16 |

---

## 🏗️ Project Structure

```
mock-jutsu-api/
├── api/main.py                  # FastAPI REST server
├── src/mockjutsu/
│   ├── core.py                  # MockJutsuCore — bulk/template/profile/company/export
│   ├── cli.py                   # CLI (Click)
│   └── generators/
│       ├── identity.py          # National IDs — TCKN, SSN, NIN, Steuer-ID, NIR, INN
│       ├── financial.py         # Cards (Luhn), IBAN, balance
│       ├── communication.py     # Phone, address, plate, email
│       ├── meta.py              # UUID, JWT, hash, MAC, IP, color, URL
│       ├── banking.py           # BIC/SWIFT, routing, sort code, transaction
│       ├── corporate.py         # Company names, job titles
│       ├── health.py            # NHS, blood type, ICD-10, height/weight
│       ├── commerce.py          # Currency, VIN, vehicle, invoice, tax rate
│       └── iot.py               # RFID (EPC SGTIN-96), NFC (NDEF/APDU), IR (NEC/RC-5/Pronto)
├── tests/test_generators.py     # 689 tests
└── reports/
    ├── test_report.html
    └── test_results.json
```

---

## ✅ Test Coverage

```
689 passed in 1.7s

95 types × 6 locales = 570 matrix scenarios
+ 119 algorithmic validation tests

Algorithms verified:
  TCKN (dual MOD-10) · YKN (Luhn) · TR VKN (proprietary)
  DE Steuer-ID (ISO 7064 MOD 11,10) · DE USt-IdNr (ISO 7064)
  UK NI (HMRC prefix rules) · FR SIREN/SIRET (Luhn)
  FR TVA (MOD-97) · RU OGRN (MOD-11) · RU INN (weighted)
  RU SNILS (MOD-101) · VIN (ISO 3779) · NHS (weighted MOD-11)
  ABA Routing (MOD-10 weights 3,7,1) · Luhn (card networks)
  EPC SGTIN-96 (GS1 96-bit) · NFC NDEF URI/Text (RTD v1.0)
  NEC IR (32-bit checksum) · RC-5 (14-bit Manchester frame)
  Pronto Hex CCF (38 kHz NEC) · RFID UID entropy (CSPRNG)
```

---

*Ninja Way: Precision in every digit.* 🥷
