# 🥷 mock-jutsu-api

**The Algorithmic Mock Data Engine for Fintech & Cross-Border Testing.**  
*Developed by [Altan Sezer Ayan](https://github.com/altansayan)*

`mock-jutsu-api` generates legally-structured fake data for 6 countries with real regulatory algorithms — TCKN checksums, Luhn-valid cards, VIN check digits, NHS numbers, ABA routing validation, barcode check digits, IMEI Luhn, financial market identifiers (ISIN, CUSIP, SEDOL, LEI), crypto addresses (BTC P2PKH, ETH EIP-55), e-commerce tracking numbers (USPS/UPS/FedEx/DHL), locale-aware coordinates, security tokens (API keys, TOTP, webhook signatures), and social media types. **1091 tests. Zero false positives.**

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
| Barcode: EAN-13/8, UPC-A, ISBN, GS1-128 (GS1 MOD-10) | ✅ | ❌ |
| Telecom: IMEI, ICCID, IMSI, MSISDN (3GPP/ITU-T) | ✅ | ❌ |
| Securities: ISIN (ISO 6166), CUSIP, SEDOL, LEI (ISO 17442) | ✅ | ❌ |
| Crypto: BTC P2PKH Base58Check, ETH EIP-55 Keccak-256 | ✅ | ❌ |
| E-Commerce: USPS/UPS/FedEx tracking checksums, SKU, Order ID | ✅ | ❌ |
| Location: WGS-84 locale-aware lat/lon, IANA timezone, ISO 3166-1 | ✅ | ❌ |
| Social Media: Twitter/X spec username, handle, hashtag, bio | ✅ | Partial |

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

## 📋 All 167+ Data Types

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
| `tckn_masked` | `***123456**` | KVKK uyumlu maskeleme |
| `ssn_masked` | `***-**-6789` | PCI-DSS son 4 hane gösterimi |
| `nationality` | `TUR` | ISO 3166-1 alpha-3, 40 ülke havuzu |

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
| `inn` | `7707083893` | RU — Kurumsal (10 hane) |
| `inn_individual` | `123456789012` | RU — Bireysel (12 hane, dual checksum) |
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
| `credit_score` | `720` | FICO scale 300–850 |

### 🏦 Banking

| Type | Output | Notes |
|:---|:---|:---|
| `swift` / `bic` | `DEUTDEDB` | real public BIC codes |
| `routing_number` | `021000021` | US ABA — MOD-10 checksum |
| `sort_code` | `20-00-00` | UK — Pay.UK published |
| `bik_code` | `044525225` | RU — Central Bank published |
| `bank_name` | `Berliner Finanzbank AG` | fictional names |
| `transaction` | `{ref, iban×2, amount, currency, ...}` | FAST/SEPA/ACH/SWIFT channels; micro/normal/large tiers |
| `sepa_ref` | `SEPAENDTOEND20240501XY7Z` | ISO 20022 — 20–35 char uppercase alphanumeric |

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
| `npi` | `1234567893` | US NPI — Luhn (80840 prefix, 10 digits) |
| `bmi` | `24.7` | BMI 18.5–35.0, one decimal |

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

### 🏷️ Barcode

Standard: **GS1 General Specifications v24.0**, **ISO 2108:2017**

| Type | Output | Algorithm |
|:---|:---|:---|
| `ean13` | `8680001234567` | GS1 MOD-10 — 3-digit locale prefix + 9 random digits + check; locale-aware (TR→868/869) |
| `ean8` | `86812340` | GS1 MOD-10 — 3-digit prefix + 4 random digits + check; locale-aware |
| `upca` | `036000291452` | GS1 MOD-10 — US/Canada, 1-digit system code + 10 digits + check |
| `isbn13` | `9780306406157` | EAN-13 with 978/979 Bookland prefix — ISO 2108:2017 + GS1 MOD-10 |
| `isbn10` | `0306406152` | ISO 2108:2017 MOD-11 — 9 digits + check (0–9 or 'X' for remainder 10) |
| `gs1_128` | `(01)01234567890128(17)250506(10)AB1C2D` | AI(01) GTIN-14 + AI(17) expiry YYMMDD + AI(10) lot; GS1 v24.0 §5.4 |

```python
jutsu.generate('ean13', locale='TR')   # "8680001234567"
jutsu.generate('ean8',  locale='DE')   # "40012340"
jutsu.generate('upca')                  # "036000291452"
jutsu.generate('isbn13')                # "9780306406157"
jutsu.generate('isbn10')                # "0306406152"
jutsu.generate('gs1_128')               # "(01)01234567890128(17)250506(10)AB1C2D"
```

### 📡 Telecom

Standard: **3GPP TS 23.003 v17.5.0**, **ITU-T E.118 / E.164 / E.212**

| Type | Output | Algorithm |
|:---|:---|:---|
| `imei` | `490154203237518` | 3GPP TS 23.003 §6.2 — TAC(8: public RBI codes) + SNR(6) + Luhn check(1) |
| `imei2` | `49-015420-323751-8` | Same as `imei` — hyphenated display format AA-BBBBBB-CCCCCC-D |
| `iccid` | `8990053412345678901` | ITU-T E.118 §3.2 — 89+CC(1-2)+issuer(4)+serial+Luhn; 19 digits; locale-aware |
| `imsi` | `286011234567890` | 3GPP TS 23.003 §2.2 — MCC(3)+MNC(2-3)+MSIN; ≤15 digits; no check digit; locale-aware |
| `msisdn` | `+905321234567` | ITU-T E.164 §6 — +CC+subscriber; locale-aware (TR→+905, US→+1, UK→+447) |

```python
jutsu.generate('imei')                  # "490154203237518"   (Luhn valid)
jutsu.generate('imei2')                 # "49-015420-323751-8"
jutsu.generate('iccid', locale='TR')    # "8990053412345678901"  (19 digits, Luhn valid)
jutsu.generate('imsi',  locale='DE')    # "26201123456789"
jutsu.generate('msisdn', locale='TR')   # "+905321234567"
```

### 💹 Financial Markets (Securities)

Standards: **ISO 6166:2021 (ISIN)**, **ABA CUSIP**, **LSE SEDOL**, **ISO 17442 / ISO 7064 (LEI)**

| Type | Output | Algorithm |
|:---|:---|:---|
| `isin` | `US0378331005` | ISO 6166:2021 — CC(2) + NSIN(9) + Luhn check(1) on numeric expansion; locale-aware country prefix |
| `cusip` | `037833100` | ABA — 8 chars (issuer+issue, A-Z/0-9) + check; odd positions ×2 with digit-sum |
| `sedol` | `0263494` | LSE — 6 consonant/digit chars (no vowels A,E,I,O,U) + check; weights [1,3,1,7,3,9] |
| `lei` | `529900T8BM49AURSDO55` | ISO 17442 — 4-char LOU + 14-char entity + 2 MOD 97-10 check digits |

```python
jutsu.generate('isin', locale='TR')    # "TR8680001234567X"  — TR prefix, Luhn valid
jutsu.generate('isin', locale='US')    # "US0378331005"      — US prefix, Luhn valid
jutsu.generate('cusip')                # "037833100"         — ABA check valid
jutsu.generate('sedol')                # "0263494"           — LSE check valid
jutsu.generate('lei')                  # "5299000T8BM49AURS11" — MOD 97-10 valid
```

---

### ₿ Crypto / Web3

Standards: **BTC P2PKH Base58Check (SHA256d)**, **EIP-55 Keccak-256 mixed-case checksum**

| Type | Output | Algorithm |
|:---|:---|:---|
| `btc_address` | `1A1zP1eP5QGefi2DMPTfTL5SLmv7Divf` | P2PKH: v0x00 + 20-byte hash + SHA256d checksum → Base58 |
| `eth_address` | `0x5aAeb6053F3E94C9b9A09f...` | EIP-55: 20-byte hex + Keccak-256 mixed-case |
| `crypto_address` | `(btc or eth)` | `currency='btc'` (default) or `currency='eth'` |
| `tx_hash` | `a1b2c3...` (64 hex) | BTC: plain 64-char hex; ETH: `0x` + 64-char hex |
| `block_hash` | `0x+64 hex` | Same format as tx_hash per chain |

```python
jutsu.generate('btc_address')                       # "1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2"
jutsu.generate('eth_address')                       # "0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed"
jutsu.generate('crypto_address', currency='eth')    # ETH EIP-55 address
jutsu.generate('tx_hash', currency='btc')           # "a1b2c3d4...64hex"
jutsu.generate('tx_hash', currency='eth')           # "0xa1b2c3d4...64hex"
jutsu.generate('block_hash', currency='btc')        # "00000000...64hex"
```

---

### 🛒 E-Commerce

Standards: **USPS Luhn MOD-10 (Pub.97)**, **UPS weighted check digit**, **FedEx Mod-11**

| Type | Output | Algorithm |
|:---|:---|:---|
| `product_name` | `Wireless Headphones` | — |
| `sku` | `AB-123456` | GS1-inspired: 2-4 letters + dash + 4-8 digits |
| `order_id` | `ORD-A1B2C3D4E5` | ORD- prefix + CSPRNG alphanumeric |
| `tracking_number` | `9400111899223397522384` | USPS (default), UPS (`--carrier ups`), FedEx (`--carrier fedex`) |
| `dhl_tracking` | `JD123456789` | DHL JD-series — JD + 8 digits + Luhn (11 chars total) |
| `category` | `Electronics` | — |
| `rating` | `4.5` | 1.0–5.0, one decimal place, realistic distribution |

```python
jutsu.generate('tracking_number')                    # USPS 22-digit, Luhn valid
jutsu.generate('tracking_number', carrier='ups')     # 1Z... 18-char, check digit valid
jutsu.generate('tracking_number', carrier='fedex')   # 12-digit, Mod-11 valid
jutsu.generate('sku')                                # "ABC-048291"
jutsu.generate('order_id')                           # "ORD-K3M7P2Q9R1X5"
jutsu.generate('rating')                             # "4.5"
```

---

### 🌍 Location / Geo

Standards: **WGS 84 (ISO 6709)**, **IANA Time Zone Database**, **ISO 3166-1 alpha-2**

| Type | Output | Notes |
|:---|:---|:---|
| `latitude` | `39.925533` | Locale-aware bounding box (TR: 36–42°N) |
| `longitude` | `32.866287` | Locale-aware bounding box (TR: 26–45°E) |
| `timezone` | `Europe/Istanbul` | IANA timezone, locale-aware |
| `country_code` | `TR` | ISO 3166-1 alpha-2 (UK→GB) |
| `coordinates` | `39.925533,32.866287` | `lat,lon` comma-separated |

```python
jutsu.generate('latitude',  locale='TR')   # 36.0–42.0
jutsu.generate('longitude', locale='US')   # -125.0 to -66.0
jutsu.generate('timezone',  locale='RU')   # e.g. "Asia/Vladivostok"
jutsu.generate('country_code', locale='UK') # "GB"
jutsu.generate('coordinates',  locale='DE') # "51.234567,9.876543"
```

---

### 📱 Social Media

Format rules: **Twitter/X spec** (4-15 chars, `[a-z0-9_]`, no leading/trailing underscore)

| Type | Output | Notes |
|:---|:---|:---|
| `username` | `cooldev42` | 4-15 chars, `[a-z0-9_]` |
| `handle` | `@cooldev42` | `@` + username |
| `hashtag` | `#TechNews2024` | `#` + `[a-zA-Z][a-zA-Z0-9]*` |
| `bio` | `Building the future...` | max 160 chars (Twitter bio limit) |
| `follower_count` | `14273` | Power-law distribution (0–50M) |

```python
jutsu.generate('username')        # "probuilder99"
jutsu.generate('handle')          # "@probuilder99"
jutsu.generate('hashtag')         # "#AI2025"
jutsu.generate('bio')             # "Full-stack developer by day, gamer by night."
jutsu.generate('follower_count')  # "14273"
```

---

### ⚙️ Tech / System

| Type | Output | Notes |
|:---|:---|:---|
| `uuid` / `requestid` / `correlationid` / `sessionid` / `idempotencykey` | RFC 4122 v4 | — |
| `deviceid` | `B3D9F2A1-...` | IDFA/GAID format |
| `ipv4` / `ipv6` | `185.46.212.33` / `2001:0db8:...` | `ipv4` → globally routable public only |
| `public_ip` | `185.46.212.33` | Public IPv4 only — RFC 1918 / loopback / multicast excluded |
| `private_ip` | `192.168.1.42` | RFC 1918 only: 10.x / 172.16-31.x / 192.168.x |
| `jwt` | `eyJhbGci...` | real base64url, no "Bearer" prefix |
| `bearertoken` | `Bearer eyJhbGci...` | with prefix |
| `hash` | `e3b0c44298fc...` | md5/sha1/sha256/sha512 via `algorithm=` |
| `mac_address` | `A4:C3:F0:3D:8E:21` | 30 real OUI prefixes (expanded) |
| `url` | `https://mockapi-42.co.uk/api/v1/users` | locale TLD |
| `domain` | `test-77.com.tr` | locale TLD |
| `color` | `#3A7BF0` | hex/rgb/hsl/name via `format=` |
| `useragent` | `Mozilla/5.0 (Windows NT...)` | realistic Chrome/Firefox/Safari |
| `browser_name` / `browser_version` / `browser_engine` | `Chrome` / `124.0` / `Blink` | — |
| `timestamp` / `timestamp_iso` | `1748000000` / `2025-01-15T14:32:07` | — |
| `clientversion` | `3.2.7` | semver |
| `apppassword` | `483716` | no repeats, no sequential runs |
| `signature` | `a3f9b2c1...` | HMAC-SHA256 via `secret=` + `payload=` |
| `api_key` | `sk-aBcDe...` (51 chars) | `sk-` + 48 CSPRNG alphanumeric |
| `totp_code` | `482931` | 6-digit RFC 6238 format test data |
| `webhook_signature` | `sha256=e3b0c...` | SHA-256 hex (Stripe/GitHub style, 71 chars) |
| `transaction_id` | `TXN1A2B3C4D5E6F7G8` | TXN + 16 uppercase hex |

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
│       ├── iot.py               # RFID (EPC SGTIN-96), NFC (NDEF/APDU), IR (NEC/RC-5/Pronto)
│       ├── barcode.py           # EAN-13/8, UPC-A, ISBN-13/10, GS1-128 (GS1 v24.0)
│       ├── telecom.py           # IMEI, ICCID, IMSI, MSISDN (3GPP TS 23.003 / ITU-T)
│       ├── financial_markets.py # ISIN, CUSIP, SEDOL, LEI (ISO 6166 / ISO 17442)
│       ├── crypto.py            # BTC P2PKH, ETH EIP-55, tx_hash, block_hash
│       ├── ecommerce.py         # USPS/UPS/FedEx tracking, SKU, Order ID, rating
│       ├── location.py          # WGS-84 lat/lon, IANA timezone, ISO 3166-1
│       └── social.py            # Username, handle, hashtag, bio, follower_count
├── tests/test_generators.py     # 1091 tests
└── reports/
    ├── test_report.html
    └── test_results.json
```

---

## ✅ Test Coverage

```
1091 passed

146 types × 6 locales = 876 matrix scenarios
+ algorithmic validation tests

Algorithms verified:
  TCKN (dual MOD-10) · YKN (Luhn) · TR VKN (proprietary)
  DE Steuer-ID (ISO 7064 MOD 11,10) · DE USt-IdNr (ISO 7064)
  UK NI (HMRC prefix rules) · FR SIREN/SIRET (Luhn)
  FR TVA (MOD-97) · RU OGRN (MOD-11) · RU INN corporate (weighted)
  RU INN individual (12-digit, dual checksum weights [7,2,4...] / [3,7,2,4...])
  RU SNILS (MOD-101) · VIN (ISO 3779) · NHS (weighted MOD-11)
  ABA Routing (MOD-10 weights 3,7,1) · Luhn (card networks)
  IBAN ISO 13616 MOD-97 (TR/UK/DE/FR) · SEPA ISO 20022 ref
  NPI Luhn (80840 prefix, 10 digits) · DHL JD Luhn (8+1 digits)
  EPC SGTIN-96 (GS1 96-bit) · NFC NDEF URI/Text (RTD v1.0)
  NEC IR (32-bit checksum) · RC-5 (14-bit Manchester frame)
  Pronto Hex CCF (38 kHz NEC) · RFID UID entropy (CSPRNG)
  EAN-13/8 GS1 MOD-10 · UPC-A GS1 MOD-10 · ISBN-10 MOD-11
  ISBN-13 Bookland · GS1-128 GTIN-14 · IMEI Luhn (3GPP)
  ICCID Luhn (ITU-T E.118) · IMSI MCC/MNC (ITU-T E.212)
  MSISDN E.164 (ITU-T) · IMEI2 hyphenated display
  ISIN Luhn MOD-10 (ISO 6166:2021) · CUSIP check (ABA)
  SEDOL weighted check (LSE) · LEI MOD 97-10 (ISO 17442)
  BTC P2PKH Base58Check (SHA256d) · ETH EIP-55 (Keccak-256)
  Keccak-256 pure Python (vector: keccak256('')=c5d2460...)
  USPS Luhn MOD-10 (Pub.97) · UPS weighted check (mod 10)
  FedEx Mod-11 (weights [3,1,7,3,1,7,3,1,7,3,1])
  WGS-84 locale bounding boxes · IANA timezone · ISO 3166-1
  Twitter/X username spec (4-15 chars, [a-z0-9_])
  IPv4 public routing (RFC 1918 / loopback / multicast excluded)
  API key format (sk- prefix + 48 alphanumeric CSPRNG)
  TOTP code 6-digit format · Webhook signature sha256= prefix
  FICO credit score range (300–850) · BMI range (18.5–35.0)
  TCKN masked format · SSN masked format · Nationality alpha-3
  Vehicle year range 2000–2026 · FR postal code range 01000–97999
```

---

## Legal Disclaimer

This library generates **synthetic data** for software development and testing purposes only.

- Generated data must **not** be submitted to real financial, government, or telecom systems.
- Generated identifiers (IBAN, card numbers, national IDs, IMEI, etc.) are algorithmically valid in format but are **not real** and do not belong to any person or entity.
- Must **not** be used for fraud, identity theft, or any unlawful activity.
- CUSIP® and SEDOL® reference formats governed by ABA / London Stock Exchange. Synthetic generation for testing is permitted; use in real securities systems requires proper licensing.

Licensed under the [MIT License](./LICENSE) · Copyright (c) 2025 Altan Sezer Ayan - A.S.A

*Ninja Way: Precision in every digit.* 🥷
