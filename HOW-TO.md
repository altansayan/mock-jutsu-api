# mock-jutsu — Kullanım Kılavuzu (How-To)

> **mock-jutsu** — 6 locale (TR/US/UK/DE/FR/RU), 152+ parametre tipi, yasal algoritmalarla mock veri üretimi.
> Developer: Altan Sezer Ayan - A.S.A · [github.com/altansayan](https://github.com/altansayan)

---

## İçindekiler

1. [Hızlı Başlangıç](#1-hızlı-başlangıç)
2. [API İmzası](#2-api-i̇mzası)
3. [Kimlik Fonksiyonları](#3-kimlik-fonksiyonları)
4. [Finansal Fonksiyonlar](#4-finansal-fonksiyonlar)
5. [İletişim & Adres Fonksiyonları](#5-i̇letişim--adres-fonksiyonları)
6. [Meta & Sistem Fonksiyonları](#6-meta--sistem-fonksiyonları)
7. [Dil Bazlı Fonksiyon Listesi](#7-dil-bazlı-fonksiyon-listesi)
8. [Locale-Aware Fonksiyonlar](#8-locale-aware-fonksiyonlar)
9. [Tam Parametre Tablosu](#9-tam-parametre-tablosu)
10. [Barkod Fonksiyonları](#10-barkod-fonksiyonları)
11. [Telekomünikasyon Fonksiyonları](#11-telekomünikasyon-fonksiyonları)
12. [Finansal Piyasalar (Menkul Kıymet)](#12-finansal-piyasalar-menkul-kıymet)
13. [Kripto Para & Web3](#13-kripto-para--web3)
14. [E-Ticaret](#14-e-ticaret)
15. [Konum & Coğrafya](#15-konum--coğrafya)
16. [Sosyal Medya](#16-sosyal-medya)
17. [CLI Komutları — Profile, Company, Bulk, Export](#17-cli-komutları--profile-company-bulk-export)

---

## 1. Hızlı Başlangıç

```python
from mockjutsu.core import jutsu

# Tek değer üret
jutsu.generate('tckn')                        # → '45678901234'
jutsu.generate('firstname', locale='DE')      # → 'Maximilian'
jutsu.generate('cardnum', network='amex')     # → '378282246310005'

# Locale varsayılanı değiştir
from mockjutsu.core import MockJutsuCore
tr = MockJutsuCore(locale='TR')
tr.generate('phone')                          # → '+905325551234'
```

---

## 2. API İmzası

```python
jutsu.generate(data_type: str, locale: str = 'TR', **kwargs) -> str | int | float
```

| Parametre | Tip | Varsayılan | Açıklama |
|-----------|-----|-----------|---------|
| `data_type` | `str` | zorunlu | Üretilecek veri tipi (büyük/küçük harf fark etmez) |
| `locale` | `str` | `'TR'` | Ülke kodu: `TR` `US` `UK` `DE` `FR` `RU` |
| `**kwargs` | — | — | Tipe özgü ek parametreler (aşağıda açıklanmıştır) |

**Dönüş tipi:** Çoğu tip `str` döner. `age` → `int`, `balance` → `float`.

---

## 3. Kimlik Fonksiyonları

### 3.1 Türkiye'ye Özgü

#### `tckn` — T.C. Kimlik Numarası
Resmi algoritma: d[9] = (Σtekli×7 − Σçiftli) % 10 · d[10] = Σ[:10] % 10 · ilk hane: 2,4,5,6,7,8
```python
jutsu.generate('tckn')
# → '45678901234'   (11 hane, locale parametresi dikkate alınmaz)
```

#### `ykn` — Yabancı Kimlik Numarası
99 ile başlar, 11 hane, Luhn (MOD-10) checksum.
```python
jutsu.generate('ykn')
# → '99012345678'
```

#### `vkn` — Vergi Kimlik Numarası
10 hane, proprietary checksum algoritması.
```python
jutsu.generate('vkn')
# → '1234567890'
```

#### `sgk` — SGK İşyeri Sicil Numarası
Format: `il(2)-sıra(7)-birim(1).şube(2)-alt(2)`
```python
jutsu.generate('sgk')
# → '34-0012345-1.01-02'
```

#### `mersis` — MERSİS Şirket Numarası
16 hane, VKN tabanlı.
```python
jutsu.generate('mersis')
# → '1234567890012345'
```

---

### 3.2 Amerika Birleşik Devletleri

#### `ssn` — Social Security Number
Format: `NNN-NN-NNNN`
```python
jutsu.generate('ssn')
# → '234-56-7890'
```

#### `ein` — Employer Identification Number
Format: `XX-XXXXXXX`
```python
jutsu.generate('ein')
# → '12-3456789'
```

---

### 3.3 Birleşik Krallık

#### `nin` — National Insurance Number
Format: `AA 99 99 99 A` · HMRC prefix kısıtlamaları uygulanır.
```python
jutsu.generate('nin')
# → 'AB 12 34 56 C'
```

#### `utr` — Unique Taxpayer Reference
10 hane, kamuya açık checksum yok.
```python
jutsu.generate('utr')
# → '1234567890'
```

#### `crn` — Company Registration Number
8 hane (İngiltere/Galler) veya SC/NI + 6 hane (İskoçya/Kuzey İrlanda).
```python
jutsu.generate('crn')
# → '12345678'  veya  'SC123456'
```

#### `paye` — PAYE Employer Reference
Format: `XXX/XXXXXX`
```python
jutsu.generate('paye')
# → '123/AB4567'
```

---

### 3.4 Almanya

#### `ust_id` — Umsatzsteuer-Identifikationsnummer (VAT)
`DE` + 9 hane, ISO 7064 MOD 11,10 checksum.
```python
jutsu.generate('ust_id')
# → 'DE123456789'
```

#### `hrb` — Handelsregisternummer
HRB (GmbH/AG) veya HRA (OHG/KG).
```python
jutsu.generate('hrb')
# → 'HRB 123456'  veya  'HRA 78901'
```

#### `rvn` — Rentenversicherungsnummer
Format: `BB TTMMJJ A SSSC` · Resmi check digit algoritması.
```python
jutsu.generate('rvn')
# → '65 070892 W 1235'
```

---

### 3.5 Fransa

#### `siren` — SIREN
9 hane, Luhn checksum.
```python
jutsu.generate('siren')
# → '732829320'
```

#### `siret` — SIRET
14 hane (SIREN 9 + NIC 4 + check 1), tüm sayı ve SIREN prefix Luhn-valid.
```python
jutsu.generate('siret')
# → '73282932000074'
```

#### `tva` — TVA (Numéro de TVA Intracommunautaire)
`FR` + 2 haneli mod-97 anahtar + SIREN.
```python
jutsu.generate('tva')
# → 'FR73732829320'
```

---

### 3.6 Rusya

#### `inn` — ИНН (Bireysel Vergi No)
10 hane, ağırlıklı checksum [2,4,10,3,5,9,4,6,8].
```python
jutsu.generate('inn')
# → '7707083893'
```

#### `snils` — СНИЛС (Emeklilik Sigorta No)
Format: `XXX-XXX-XXX XX` · Resmi checksum.
```python
jutsu.generate('snils')
# → '112-233-445 95'
```

#### `ogrn` — ОГРН (Şirket Tescil No)
13 hane, mod-11 checksum.
```python
jutsu.generate('ogrn')
# → '1027700132195'
```

#### `kpp` — КПП (Vergi Kayıt Nedeni Kodu)
9 hane.
```python
jutsu.generate('kpp')
# → '770701001'
```

---

### 3.7 Locale-Aware Kimlik Fonksiyonları

#### `nationalid` — Ulusal Kimlik (locale'e göre değişir)
```python
jutsu.generate('nationalid', locale='TR')  # → TCKN '45678901234'
jutsu.generate('nationalid', locale='US')  # → SSN  '234-56-7890'
jutsu.generate('nationalid', locale='UK')  # → NI   'AB 12 34 56 C'
jutsu.generate('nationalid', locale='DE')  # → Steuer-ID '12345678901' (11 hane, MOD 11,10)
jutsu.generate('nationalid', locale='FR')  # → INSEE/NIR '1850175123456789' (15+2 hane)
jutsu.generate('nationalid', locale='RU')  # → Pasaport seri/no '1234 567890'
```

#### `taxid` — Vergi Kimliği (locale'e göre değişir)
```python
jutsu.generate('taxid', locale='TR')  # → VKN       '1234567890'
jutsu.generate('taxid', locale='US')  # → EIN        '12-3456789'
jutsu.generate('taxid', locale='UK')  # → UTR        '1234567890'
jutsu.generate('taxid', locale='DE')  # → USt-IdNr   'DE123456789'
jutsu.generate('taxid', locale='FR')  # → SIREN      '732829320'
jutsu.generate('taxid', locale='RU')  # → INN        '7707083893'
```

#### `employer_id` — Şirket/İşveren No (locale'e göre değişir)
```python
jutsu.generate('employer_id', locale='TR')  # → MERSİS  '1234567890012345'
jutsu.generate('employer_id', locale='US')  # → EIN      '12-3456789'
jutsu.generate('employer_id', locale='UK')  # → CRN      '12345678'
jutsu.generate('employer_id', locale='DE')  # → HRB/HRA  'HRB 123456'
jutsu.generate('employer_id', locale='FR')  # → SIRET    '73282932000074'
jutsu.generate('employer_id', locale='RU')  # → OGRN     '1027700132195'
```

#### `insurance_id` — Sosyal Sigorta No (locale'e göre değişir)
```python
jutsu.generate('insurance_id', locale='TR')  # → SGK      '34-0012345-1.01-02'
jutsu.generate('insurance_id', locale='US')  # → SSN      '234-56-7890'
jutsu.generate('insurance_id', locale='UK')  # → PAYE     '123/AB4567'
jutsu.generate('insurance_id', locale='DE')  # → RVN      '65 070892 W 1235'
jutsu.generate('insurance_id', locale='FR')  # → INSEE    '1850175123456789'
jutsu.generate('insurance_id', locale='RU')  # → SNILS    '112-233-445 95'
```

---

### 3.8 Demografik Bilgiler

#### `firstname` / `lastname` / `fullname`
```python
jutsu.generate('firstname', locale='TR')               # → 'Emre'
jutsu.generate('firstname', locale='TR', gender='f')   # → 'Merve'
jutsu.generate('lastname',  locale='DE')               # → 'Müller'
jutsu.generate('fullname',  locale='RU')               # → 'Иван Андреевич Петров'  (3 parça)
jutsu.generate('fullname',  locale='US')               # → 'James Smith'             (2 parça)
```
`gender` parametresi: `'m'` / `'male'` / `'erkek'` — `'f'` / `'female'` / `'kadın'`

#### `patronymic` — Rusça baba adı
```python
jutsu.generate('patronymic', locale='RU')  # → 'Иванович'  (erkek) veya 'Ивановна' (kadın)
jutsu.generate('patronymic', locale='TR')  # → ''           (Türkçede bu kavram yoktur)
```

#### `passport`
```python
jutsu.generate('passport')  # → 'P1234567'  (P + 7 rakam)
```

#### `license`
```python
jutsu.generate('license')   # → '654321'  (6 hane)
```

#### `age`
```python
jutsu.generate('age')       # → 34  (int, 18–80 arası)
```

#### `gender`
```python
jutsu.generate('gender')    # → 'Male' veya 'Female'
```

#### `birthdate`
```python
jutsu.generate('birthdate') # → '1990-05-14'  (YYYY-MM-DD, 18–80 yaş)
```

---

## 4. Finansal Fonksiyonlar

### 4.1 Kart Numarası

#### `cardnum` — Kart Numarası
Tüm ağlar için Luhn-valid.

```python
jutsu.generate('cardnum')                    # → Visa (varsayılan)
jutsu.generate('cardnum', network='visa')    # → '4532015112830366'  (16 hane, 4 ile başlar)
jutsu.generate('cardnum', network='mc')      # → '5412345678901234'  (16 hane, 51-55)
jutsu.generate('cardnum', network='amex')    # → '378282246310005'   (15 hane, 34/37)
jutsu.generate('cardnum', network='troy')    # → '9792123456789012'  (16 hane, 9792)
jutsu.generate('cardnum', network='jcb')     # → '3528123456789012'  (16 hane)
jutsu.generate('cardnum', network='discover')# → '6011123456789012'  (16 hane)
jutsu.generate('cardnum', network='unionpay')# → '6212123456789012'  (16 hane)
jutsu.generate('cardnum', network='mir')     # → '2200123456789012'  (16 hane)
jutsu.generate('cardnum', network='maestro') # → '6304123456789012'  (16 hane)
```

| Ağ | Prefix | Uzunluk |
|----|--------|---------|
| `visa` | 4 | 16 |
| `mc` | 51–55 | 16 |
| `amex` | 34, 37 | 15 |
| `troy` | 9792 | 16 |
| `jcb` | 352, 358 | 16 |
| `discover` | 6011, 65 | 16 |
| `unionpay` | 62 | 16 |
| `mir` | 2200–2202 | 16 |
| `maestro` | 6304, 6759 | 16 |

### 4.2 Kart Bilgileri

```python
jutsu.generate('cardnetwork')   # → 'VISA' / 'MC' / 'AMEX' / ...
jutsu.generate('cardtype')      # → 'Credit' veya 'Debit'
jutsu.generate('cardstatus')    # → 'Active' / 'Blocked' / 'Expired'
jutsu.generate('cardcategory')  # → 'Classic' / 'Gold' / 'Platinum' / 'Business'
jutsu.generate('cardowner')     # → 'JOHN SMITH'  (fullname büyük harf, locale-aware)
jutsu.generate('issuer', locale='TR')  # → 'BosphorusBank'
jutsu.generate('issuer', locale='DE')  # → 'Volksbank Nord'
```

### 4.3 Güvenlik & Son Kullanma

```python
jutsu.generate('cvv3')          # → '847'    (3 hane)
jutsu.generate('cvv4')          # → '1234'   (4 hane, Amex için)
jutsu.generate('pin')           # → '7291'   (4 hane)
jutsu.generate('expiry')        # → '09/27'  (MM/YY)
jutsu.generate('expirymonth')   # → '09'     (01–12)
jutsu.generate('expiryyear')    # → '27'     (25–30)
```

### 4.4 Bakiye

```python
jutsu.generate('balance')                    # → 12450.75   (10–50000 arası)
jutsu.generate('balance', min=100, max=500)  # → 234.80     (özel aralık)
```

### 4.5 Banka Hesabı (IBAN / Routing)

```python
jutsu.generate('iban', locale='TR')  # → 'TR330006100519786457841326'   (IBAN, 26 hane)
jutsu.generate('iban', locale='UK')  # → 'GB82WEST12345698765432'        (IBAN, 22 hane)
jutsu.generate('iban', locale='DE')  # → 'DE89370400440532013000'        (IBAN, 22 hane)
jutsu.generate('iban', locale='FR')  # → 'FR7630006000011234567890189'   (IBAN, 27 hane)
jutsu.generate('iban', locale='US')  # → 'RT:123456789 ACC:123456789012' (Routing + Account)
jutsu.generate('iban', locale='RU')  # → 'BIK:044525225 ACC:408170000001234567890' (BIK)
```

---

## 5. İletişim & Adres Fonksiyonları

### 5.1 Telefon

```python
jutsu.generate('phone', locale='TR')         # → '+905325551234'   (tam numara)
jutsu.generate('phone', locale='US')         # → '+15552121234'
jutsu.generate('phone_country', locale='TR') # → '+90'             (ülke kodu)
jutsu.generate('phone_area',    locale='TR') # → '532'             (alan/operatör kodu)
jutsu.generate('phone_local',   locale='TR') # → '5551234'         (yerel numara)
```

| Locale | Ülke Kodu |
|--------|-----------|
| TR | +90 |
| US | +1 |
| UK | +44 |
| DE | +49 |
| FR | +33 |
| RU | +7 |

### 5.2 Adres

```python
jutsu.generate('address_full',   locale='TR')  # → 'İstanbul, Bağdat Caddesi No:42'
jutsu.generate('address_city',   locale='DE')  # → 'München'
jutsu.generate('address_street', locale='FR')  # → 'Avenue des Champs-Élysées'
```

### 5.3 Posta Kodu

```python
jutsu.generate('postalcode', locale='TR')  # → '34500'      (5 hane)
jutsu.generate('postalcode', locale='US')  # → '90210'      (5 hane)
jutsu.generate('postalcode', locale='UK')  # → 'SW1 2AB'    (alfasayısal)
jutsu.generate('postalcode', locale='DE')  # → '10115'      (5 hane)
jutsu.generate('postalcode', locale='FR')  # → '75008'      (5 hane)
jutsu.generate('postalcode', locale='RU')  # → '101000'     (6 hane)
```

### 5.4 Plaka

```python
jutsu.generate('plate', locale='TR')  # → '34 ABC 123'
jutsu.generate('plate', locale='UK')  # → 'AB23 XYZ'
jutsu.generate('plate', locale='DE')  # → 'B-AB 1234'
jutsu.generate('plate', locale='FR')  # → 'AB-123-CD'
jutsu.generate('plate', locale='RU')  # → 'A123BC 77'
jutsu.generate('plate', locale='US')  # → '3ABC456'
```

### 5.5 E-posta

```python
jutsu.generate('email')
# → 'samuraijack_012345678901@mockjutsu.test'
# Format: samuraijack_ + 12 rakam + @mockjutsu.test (locale parametresi yok)
```

---

## 6. Meta & Sistem Fonksiyonları

### 6.1 Tanımlayıcılar (UUID tabanlı)

```python
jutsu.generate('uuid')            # → '550e8400-e29b-41d4-a716-446655440000'
jutsu.generate('requestid')       # → '550e8400-e29b-41d4-a716-446655440000'
jutsu.generate('correlationid')   # → '550e8400-e29b-41d4-a716-446655440000'
jutsu.generate('sessionid')       # → '550e8400-e29b-41d4-a716-446655440000'
jutsu.generate('idempotencykey')  # → '550e8400-e29b-41d4-a716-446655440000'
jutsu.generate('deviceid')        # → '550E8400-E29B-41D4-A716-446655440000'  (büyük harf)
```

### 6.2 Zaman Damgaları

```python
jutsu.generate('timestamp')      # → '1714900000'       (Unix epoch, saniye)
jutsu.generate('timestamp_iso')  # → '2024-05-05T14:30:00.123456'  (ISO 8601)
```

### 6.3 Ağ

```python
jutsu.generate('ipv4')   # → '192.168.1.42'          (0–255 aralığı)
jutsu.generate('ipv6')   # → 'fe80:0000:0000:0000:0202:b3ff:fe1e:8329'  (8 grup, 4 hex)
```

### 6.4 Tarayıcı & Kullanıcı Ajanı

```python
jutsu.generate('browser_name')     # → 'Chrome' / 'Firefox' / 'Safari' / 'Edge' / 'Opera'
jutsu.generate('browser_engine')   # → 'Blink' / 'Gecko' / 'WebKit'
jutsu.generate('browser_version')  # → '124.0.6367.78'
jutsu.generate('useragent')
# → 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.78 Safari/537.36'
```

### 6.5 Güvenlik Token'ları

```python
jutsu.generate('bearertoken')
# → 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ...}.signature'
# Format: Bearer header.payload.signature (JWT yapısı)

jutsu.generate('clientversion')   # → '2.4.1'

jutsu.generate('signature')
# → 'a1b2c3d4e5f6...'  (HMAC-SHA256, hex 64 karakter)
jutsu.generate('signature', secret='mykey', payload='data')  # özel key/payload
```

### 6.6 Uygulama Şifresi

```python
jutsu.generate('apppassword')
# → '481302'  (6 hane)
# Kurallar: aynı ardışık rakam YOK · 3+ artan/azalan seri YOK
# Örnekler:  '123456' ❌  '112345' ❌  '481302' ✅
```

---

## 7. Dil Bazlı Fonksiyon Listesi

### 7.1 Yalnızca Belirli Bir Dile Özgü Fonksiyonlar

Bu fonksiyonlar sabit bir ülkenin formatını döner; `locale` parametresi **görmezden gelinir**.

| Fonksiyon | Ülke | Sistem Adı | Algoritma |
|-----------|------|-----------|-----------|
| `tckn` | 🇹🇷 TR | T.C. Kimlik No | d[9]=(Σtekli×7−Σçiftli)%10 · d[10]=Σ%10 |
| `ykn` | 🇹🇷 TR | Yabancı Kimlik No | 99 prefix + Luhn (MOD-10) |
| `vkn` | 🇹🇷 TR | Vergi Kimlik No | Proprietary 10-hane checksum |
| `sgk` | 🇹🇷 TR | SGK İşyeri Sicil No | il-seq-birim.şube-alt format |
| `mersis` | 🇹🇷 TR | MERSİS Şirket No | VKN + 0 + 5 hane = 16 |
| `ssn` | 🇺🇸 US | Social Security Number | NNN-NN-NNNN format |
| `ein` | 🇺🇸 US | Employer ID Number | XX-XXXXXXX format |
| `nin` | 🇬🇧 UK | National Insurance No | AA 99 99 99 A + HMRC kısıtlamaları |
| `utr` | 🇬🇧 UK | Unique Taxpayer Reference | 10 hane |
| `crn` | 🇬🇧 UK | Company Registration No | 8 hane / SC·NI prefix + 6 hane |
| `paye` | 🇬🇧 UK | PAYE Employer Reference | XXX/XXXXXX |
| `ust_id` | 🇩🇪 DE | Umsatzsteuer-IdNr (VAT) | DE + 9 hane, ISO 7064 MOD 11,10 |
| `hrb` | 🇩🇪 DE | Handelsregisternummer | HRB/HRA + sayı |
| `rvn` | 🇩🇪 DE | Rentenversicherungsnummer | BB TTMMJJ A SSSC + resmi check |
| `siren` | 🇫🇷 FR | SIREN | 9 hane, Luhn |
| `siret` | 🇫🇷 FR | SIRET | 14 hane, Luhn (SIREN prefix de valid) |
| `tva` | 🇫🇷 FR | TVA Numarası | FR + mod-97 key + SIREN |
| `inn` | 🇷🇺 RU | ИНН Vergi No | 10 hane, ağırlıklı checksum |
| `snils` | 🇷🇺 RU | СНИЛС Sigorta No | XXX-XXX-XXX XX + resmi checksum |
| `ogrn` | 🇷🇺 RU | ОГРН Şirket Tescil No | 13 hane, mod-11 checksum |
| `kpp` | 🇷🇺 RU | КПП Vergi Kayıt Kodu | 9 hane format |

### 7.2 Tüm Dillerde Çalışan Evrensel Fonksiyonlar

`locale` parametresi bu fonksiyonlarda **etkisizdir** — her locale için aynı format döner.

**Kart & Finansal:**
`cardnum` · `cardnetwork` · `cardtype` · `cardstatus` · `cardcategory` · `cvv3` · `cvv4` · `pin` · `expiry` · `expirymonth` · `expiryyear` · `balance`

**Belgeler & Demografik:**
`passport` · `license` · `age` · `gender` · `birthdate`

**İletişim:**
`email`

**Meta & Sistem:**
`uuid` · `requestid` · `correlationid` · `sessionid` · `idempotencykey` · `deviceid` · `timestamp` · `timestamp_iso` · `ipv4` · `ipv6` · `browser_name` · `browser_version` · `browser_engine` · `useragent` · `bearertoken` · `clientversion` · `signature` · `apppassword`

---

## 8. Locale-Aware Fonksiyonlar

Bu fonksiyonlar `locale` parametresine göre **farklı ülkenin formatını ve algoritmasını** uygular.

| Fonksiyon | TR | US | UK | DE | FR | RU |
|-----------|----|----|----|----|----|----|
| `nationalid` | TCKN | SSN | NI No | Steuer-ID | INSEE/NIR | Pasaport seri/no |
| `taxid` | VKN | EIN | UTR | USt-IdNr | SIREN | INN |
| `employer_id` | MERSİS | EIN | CRN | HRB/HRA | SIRET | OGRN |
| `insurance_id` | SGK Sicil | SSN | PAYE | RVN | INSEE/NIR | SNILS |
| `firstname` | Türkçe isim | İngilizce | İngilizce | Almanca | Fransızca | Rusça (Kiril) |
| `lastname` | Türkçe soyad | İngilizce | İngilizce | Almanca | Fransızca | Rusça (çekim) |
| `fullname` | Ad Soyad (2) | Ad Soyad (2) | Ad Soyad (2) | Ad Soyad (2) | Ad Soyad (2) | Ad Baba Soyad (3) |
| `patronymic` | `''` (boş) | `''` (boş) | `''` (boş) | `''` (boş) | `''` (boş) | Отчество |
| `issuer` | TR banka | US banka | UK banka | DE banka | FR banka | RU banka |
| `iban` | TR IBAN (26) | RT: routing | GB IBAN (22) | DE IBAN (22) | FR IBAN (27) | BIK: format |
| `cardowner` | Büyük harf TR ad | US ad | UK ad | DE ad | FR ad | RU ad |
| `phone` | +90 … | +1 … | +44 … | +49 … | +33 … | +7 … |
| `phone_country` | +90 | +1 | +44 | +49 | +33 | +7 |
| `phone_area` | 532/542/… | 555/212/… | 7911/7700/… | 151/160/… | 06/07 | 916/999/… |
| `phone_local` | 7 hane | 7 hane | 7 hane | 7 hane | 8 hane | 7 hane |
| `address_city` | İstanbul/Ankara/… | New York/LA/… | London/Birmingham/… | Berlin/Hamburg/… | Paris/Lyon/… | Москва/… |
| `address_street` | Atatürk Cad./… | Main Street/… | High Street/… | Hauptstraße/… | Rue de la Paix/… | Ул. Ленина/… |
| `address_full` | Şehir, Sokak No:X | Şehir, Sokak No:X | Şehir, Sokak No:X | Şehir, Sokak No:X | Şehir, Sokak No:X | Şehir, Sokak No:X |
| `postalcode` | 5 hane | 5 hane | Alfasayısal | 5 hane | 5 hane | 6 hane |
| `plate` | 34 ABC 123 | 3ABC456 | AB23 XYZ | B-AB 1234 | AB-123-CD | A123BC 77 |

---

## 9. Tam Parametre Tablosu

> **CLI sözdizimi:** `mockjutsu generate <type> [--locale XX] [--network XX]`
> `¹` işareti olan parametreler (`min`, `max`, `secret`, `payload`, `gender`) yalnızca Python API'de desteklenir; CLI'de kullanılamaz.

| Fonksiyon | Kategori | Locale Etkisi | Ek Param | Örnek Çıktı | CLI Komutu |
|-----------|----------|---------------|----------|-------------|-----------|
| `tckn` | Kimlik | Yok | — | `45678901234` | `mockjutsu generate tckn` |
| `ykn` | Kimlik | Yok | — | `99012345678` | `mockjutsu generate ykn` |
| `nationalid` | Kimlik | ✅ Var | — | locale'e göre | `mockjutsu generate nationalid --locale US` |
| `vkn` | Kimlik/Vergi | Yok | — | `1234567890` | `mockjutsu generate vkn` |
| `taxid` | Kimlik/Vergi | ✅ Var | — | locale'e göre | `mockjutsu generate taxid --locale DE` |
| `employer_id` | İşveren | ✅ Var | — | locale'e göre | `mockjutsu generate employer_id --locale FR` |
| `insurance_id` | Sigorta | ✅ Var | — | locale'e göre | `mockjutsu generate insurance_id --locale RU` |
| `sgk` | Kimlik/TR | Yok | — | `34-0012345-1.01-02` | `mockjutsu generate sgk` |
| `mersis` | Kimlik/TR | Yok | — | `1234567890012345` | `mockjutsu generate mersis` |
| `ssn` | Kimlik/US | Yok | — | `234-56-7890` | `mockjutsu generate ssn` |
| `ein` | Kimlik/US | Yok | — | `12-3456789` | `mockjutsu generate ein` |
| `nin` | Kimlik/UK | Yok | — | `AB 12 34 56 C` | `mockjutsu generate nin` |
| `utr` | Kimlik/UK | Yok | — | `1234567890` | `mockjutsu generate utr` |
| `crn` | Kimlik/UK | Yok | — | `12345678` | `mockjutsu generate crn` |
| `paye` | Kimlik/UK | Yok | — | `123/AB4567` | `mockjutsu generate paye` |
| `ust_id` | Kimlik/DE | Yok | — | `DE123456789` | `mockjutsu generate ust_id` |
| `hrb` | Kimlik/DE | Yok | — | `HRB 123456` | `mockjutsu generate hrb` |
| `rvn` | Kimlik/DE | Yok | — | `65 070892 W 1235` | `mockjutsu generate rvn` |
| `siren` | Kimlik/FR | Yok | — | `732829320` | `mockjutsu generate siren` |
| `siret` | Kimlik/FR | Yok | — | `73282932000074` | `mockjutsu generate siret` |
| `tva` | Kimlik/FR | Yok | — | `FR73732829320` | `mockjutsu generate tva` |
| `inn` | Kimlik/RU | Yok | — | `7707083893` | `mockjutsu generate inn` |
| `snils` | Kimlik/RU | Yok | — | `112-233-445 95` | `mockjutsu generate snils` |
| `ogrn` | Kimlik/RU | Yok | — | `1027700132195` | `mockjutsu generate ogrn` |
| `kpp` | Kimlik/RU | Yok | — | `770701001` | `mockjutsu generate kpp` |
| `firstname` | İsim | ✅ Var | `gender`¹ | `Emre` | `mockjutsu generate firstname --locale TR` |
| `lastname` | İsim | ✅ Var | `gender`¹ (RU) | `Yılmaz` | `mockjutsu generate lastname --locale DE` |
| `fullname` | İsim | ✅ Var | `gender`¹ | `Emre Kaya` | `mockjutsu generate fullname --locale RU` |
| `patronymic` | İsim | ✅ Var (sadece RU) | `gender`¹ | `Иванович` | `mockjutsu generate patronymic --locale RU` |
| `passport` | Belge | Yok | — | `P1234567` | `mockjutsu generate passport` |
| `license` | Belge | Yok | — | `654321` | `mockjutsu generate license` |
| `age` | Demografik | Yok | — | `34` | `mockjutsu generate age` |
| `gender` | Demografik | Yok | — | `Male` | `mockjutsu generate gender` |
| `birthdate` | Demografik | Yok | — | `1990-05-14` | `mockjutsu generate birthdate` |
| `cardnum` | Finansal | Yok | `--network` | `4532015112830366` | `mockjutsu generate cardnum --network amex` |
| `cardnetwork` | Finansal | Yok | — | `VISA` | `mockjutsu generate cardnetwork` |
| `cardtype` | Finansal | Yok | — | `Credit` | `mockjutsu generate cardtype` |
| `cardstatus` | Finansal | Yok | — | `Active` | `mockjutsu generate cardstatus` |
| `cardcategory` | Finansal | Yok | — | `Gold` | `mockjutsu generate cardcategory` |
| `cardowner` | Finansal | ✅ Var | `gender`¹ | `JOHN SMITH` | `mockjutsu generate cardowner --locale US` |
| `cvv3` | Finansal | Yok | — | `847` | `mockjutsu generate cvv3` |
| `cvv4` | Finansal | Yok | — | `1234` | `mockjutsu generate cvv4` |
| `pin` | Finansal | Yok | — | `7291` | `mockjutsu generate pin` |
| `expiry` | Finansal | Yok | — | `09/27` | `mockjutsu generate expiry` |
| `expirymonth` | Finansal | Yok | — | `09` | `mockjutsu generate expirymonth` |
| `expiryyear` | Finansal | Yok | — | `27` | `mockjutsu generate expiryyear` |
| `issuer` | Finansal | ✅ Var | — | `BosphorusBank` | `mockjutsu generate issuer --locale TR` |
| `balance` | Finansal | Yok | `min` `max`¹ | `12450.75` | `mockjutsu generate balance` |
| `iban` | Finansal | ✅ Var | — | `TR330006100519786457841326` | `mockjutsu generate iban --locale TR` |
| `phone` | İletişim | ✅ Var | — | `+905325551234` | `mockjutsu generate phone --locale TR` |
| `phone_country` | İletişim | ✅ Var | — | `+90` | `mockjutsu generate phone_country --locale TR` |
| `phone_area` | İletişim | ✅ Var | — | `532` | `mockjutsu generate phone_area --locale TR` |
| `phone_local` | İletişim | ✅ Var | — | `5551234` | `mockjutsu generate phone_local --locale TR` |
| `address_city` | İletişim | ✅ Var | — | `İstanbul` | `mockjutsu generate address_city --locale TR` |
| `address_street` | İletişim | ✅ Var | — | `Bağdat Caddesi` | `mockjutsu generate address_street --locale FR` |
| `address_full` | İletişim | ✅ Var | — | `İstanbul, Bağdat Caddesi No:42` | `mockjutsu generate address_full --locale TR` |
| `postalcode` | İletişim | ✅ Var | — | `34500` | `mockjutsu generate postalcode --locale UK` |
| `plate` | İletişim | ✅ Var | — | `34 ABC 123` | `mockjutsu generate plate --locale TR` |
| `email` | İletişim | Yok | — | `samuraijack_012345678901@mockjutsu.test` | `mockjutsu generate email` |
| `uuid` | Meta | Yok | — | `550e8400-e29b-41d4-a716-446655440000` | `mockjutsu generate uuid` |
| `requestid` | Meta | Yok | — | `550e8400-…` | `mockjutsu generate requestid` |
| `correlationid` | Meta | Yok | — | `550e8400-…` | `mockjutsu generate correlationid` |
| `sessionid` | Meta | Yok | — | `550e8400-…` | `mockjutsu generate sessionid` |
| `idempotencykey` | Meta | Yok | — | `550e8400-…` | `mockjutsu generate idempotencykey` |
| `deviceid` | Meta | Yok | — | `550E8400-…` | `mockjutsu generate deviceid` |
| `timestamp` | Meta | Yok | — | `1714900000` | `mockjutsu generate timestamp` |
| `timestamp_iso` | Meta | Yok | — | `2024-05-05T14:30:00.123456` | `mockjutsu generate timestamp_iso` |
| `ipv4` | Meta | Yok | — | `192.168.1.42` | `mockjutsu generate ipv4` |
| `ipv6` | Meta | Yok | — | `fe80:0000:0000:0000:…` | `mockjutsu generate ipv6` |
| `browser_name` | Meta | Yok | — | `Chrome` | `mockjutsu generate browser_name` |
| `browser_version` | Meta | Yok | — | `124.0.6367.78` | `mockjutsu generate browser_version` |
| `browser_engine` | Meta | Yok | — | `Blink` | `mockjutsu generate browser_engine` |
| `useragent` | Meta | Yok | — | `Mozilla/5.0 …` | `mockjutsu generate useragent` |
| `bearertoken` | Meta | Yok | — | `Bearer eyJ….eyJ….sig` | `mockjutsu generate bearertoken` |
| `clientversion` | Meta | Yok | — | `2.4.1` | `mockjutsu generate clientversion` |
| `signature` | Meta | Yok | `secret` `payload`¹ | `a1b2c3d4…` (hex 64) | `mockjutsu generate signature` |
| `apppassword` | Meta | Yok | — | `481302` | `mockjutsu generate apppassword` |
| `ean13` | Barkod | ✅ Var | — | `8680001234567` | `mockjutsu generate ean13 --locale TR` |
| `ean8` | Barkod | ✅ Var | — | `86812340` | `mockjutsu generate ean8 --locale TR` |
| `upca` | Barkod | Yok | — | `036000291452` | `mockjutsu generate upca` |
| `isbn13` | Barkod | Yok | — | `9780306406157` | `mockjutsu generate isbn13` |
| `isbn10` | Barkod | Yok | — | `0306406152` | `mockjutsu generate isbn10` |
| `gs1_128` | Barkod | Yok | — | `(01)01234...(17)250506...(10)AB1C2D` | `mockjutsu generate gs1_128` |
| `imei` | Telecom | Yok | — | `490154203237518` | `mockjutsu generate imei` |
| `imei2` | Telecom | Yok | — | `49-015420-323751-8` | `mockjutsu generate imei2` |
| `iccid` | Telecom | ✅ Var | — | `8990053412345678901` | `mockjutsu generate iccid --locale TR` |
| `imsi` | Telecom | ✅ Var | — | `286011234567890` | `mockjutsu generate imsi --locale TR` |
| `msisdn` | Telecom | ✅ Var | — | `+905321234567` | `mockjutsu generate msisdn --locale TR` |
| `isin` | Securities | ✅ Var | — | `US0378331005` | `mockjutsu generate isin --locale US` |
| `cusip` | Securities | Yok | — | `037833100` | `mockjutsu generate cusip` |
| `sedol` | Securities | Yok | — | `0263494` | `mockjutsu generate sedol` |
| `lei` | Securities | Yok | — | `529900T8BM49AURSDO55` | `mockjutsu generate lei` |
| `btc_address` | Crypto | Yok | — | `1A1zP1eP5QGefi2D...` | `mockjutsu generate btc_address` |
| `eth_address` | Crypto | Yok | — | `0x5aAeb6053F3E9...` | `mockjutsu generate eth_address` |
| `crypto_address` | Crypto | Yok | `--currency btc\|eth` | `(btc veya eth)` | `mockjutsu generate crypto_address --currency eth` |
| `tx_hash` | Crypto | Yok | `--currency btc\|eth` | `a1b2c3...64hex` | `mockjutsu generate tx_hash --currency btc` |
| `block_hash` | Crypto | Yok | `--currency btc\|eth` | `0x+64hex` | `mockjutsu generate block_hash --currency eth` |
| `product_name` | E-Commerce | Yok | — | `Wireless Headphones` | `mockjutsu generate product_name` |
| `sku` | E-Commerce | Yok | — | `AB-123456` | `mockjutsu generate sku` |
| `order_id` | E-Commerce | Yok | — | `ORD-A1B2C3D4E5` | `mockjutsu generate order_id` |
| `tracking_number` | E-Commerce | Yok | `--carrier usps\|ups\|fedex` | `9400111...22digit` | `mockjutsu generate tracking_number --carrier ups` |
| `category` | E-Commerce | Yok | — | `Electronics` | `mockjutsu generate category` |
| `rating` | E-Commerce | Yok | — | `4.5` | `mockjutsu generate rating` |
| `latitude` | Location | ✅ Var | — | `39.925533` | `mockjutsu generate latitude --locale TR` |
| `longitude` | Location | ✅ Var | — | `32.866287` | `mockjutsu generate longitude --locale TR` |
| `timezone` | Location | ✅ Var | — | `Europe/Istanbul` | `mockjutsu generate timezone --locale TR` |
| `country_code` | Location | ✅ Var | — | `TR` | `mockjutsu generate country_code --locale TR` |
| `coordinates` | Location | ✅ Var | — | `39.925533,32.866287` | `mockjutsu generate coordinates --locale TR` |
| `username` | Social | Yok | — | `cooldev42` | `mockjutsu generate username` |
| `handle` | Social | Yok | — | `@cooldev42` | `mockjutsu generate handle` |
| `hashtag` | Social | Yok | — | `#TechNews2024` | `mockjutsu generate hashtag` |
| `bio` | Social | Yok | — | `Building the future...` | `mockjutsu generate bio` |
| `follower_count` | Social | Yok | — | `14273` | `mockjutsu generate follower_count` |

---

## 10. Barkod Fonksiyonları

Standart: **GS1 General Specifications v24.0** · **ISO 2108:2017**

### `ean13` — EAN-13 Barkod
GS1 MOD-10 check digit. 3 haneli ülke prefix + 9 rastgele + 1 check = 13 hane. Locale-aware.
```python
jutsu.generate('ean13')             # → '8680001234567'  (TR varsayılan)
jutsu.generate('ean13', locale='DE')# → '4001234567893'
jutsu.generate('ean13', locale='US')# → '0031234567892'
# Test vektörü: 590123412345 → check=7 ✓
```

### `ean8` — EAN-8 Barkod
GS1 MOD-10 check digit. 3 haneli prefix + 4 rastgele + 1 check = 8 hane. Locale-aware.
```python
jutsu.generate('ean8')             # → '86812340'
jutsu.generate('ean8', locale='UK')# → '50112340'
```

### `upca` — UPC-A Barkod
GS1 MOD-10 check digit. ABD/Kanada standardı. 1 haneli sistem kodu + 10 rastgele + 1 check = 12 hane.
```python
jutsu.generate('upca')  # → '036000291452'
# Test vektörü: 03600029145 → check=2 ✓
```

### `isbn13` — ISBN-13
EAN-13 format + 978/979 Bookland prefix. GS1 MOD-10 check. ISO 2108:2017.
```python
jutsu.generate('isbn13')  # → '9780306406157'
```

### `isbn10` — ISBN-10
ISO 2108:2017 MOD-11 check. 9 hane + check ('0'-'9' veya 'X').
```python
jutsu.generate('isbn10')  # → '0306406152'
# Test vektörü: 030640615 → check=2 ✓
```

### `gs1_128` — GS1-128 Barkod İçeriği
GS1 General Specifications v24.0 §5.4. AI(01) GTIN-14 + AI(17) son kullanma + AI(10) lot numarası.
```python
jutsu.generate('gs1_128')
# → '(01)01234567890128(17)250506(10)AB1C2D'
# GTIN-14 içindeki check digit GS1 MOD-10 ile hesaplanır.
```

---

## 11. Telekomünikasyon Fonksiyonları

Standart: **3GPP TS 23.003 v17.5.0** · **ITU-T E.118 / E.164 / E.212**

### `imei` — IMEI
3GPP TS 23.003 §6.2. TAC(8) + SNR(6) + Luhn check(1) = 15 hane.
TAC = GSMA kamuya açık RBI kodu(2) + sentetik model kodu(6).
```python
jutsu.generate('imei')  # → '490154203237518'
# Test vektörü: payload 49015420323751 → check=8 ✓
```

### `imei2` — IMEI (Tire Formatı)
IMEI'nin `AA-BBBBBB-CCCCCC-D` görüntü formatı. 3GPP TS 23.003 §6.2.
```python
jutsu.generate('imei2')  # → '49-015420-323751-8'
```

### `iccid` — ICCID
ITU-T E.118 §3.2. 89 + CC(1-2 hane) + issuer(4) + seri + Luhn check = 19 hane. Locale-aware.
```python
jutsu.generate('iccid')             # → '8990053412345678901'  (TR varsayılan)
jutsu.generate('iccid', locale='UK')# → '8944790012345678901'
jutsu.generate('iccid', locale='US')# → '8911234512345678901'
```

### `imsi` — IMSI
3GPP TS 23.003 §2.2. MCC(3) + MNC(2-3) + MSIN = maks. 15 hane. Check digit yok. Locale-aware.

| Locale | MCC | MNC örnekleri |
|--------|-----|---------------|
| TR | 286 | 01 (Turkcell), 02 (Vodafone TR), 03 (Türk Telekom) |
| US | 310 | 010 (AT&T), 260 (T-Mobile), 030 |
| UK | 234 | 10 (O2), 20 (Vodafone), 30 (EE) |
| DE | 262 | 01 (T-Mobile DE), 02 (Vodafone DE), 03 (Telefónica) |
| FR | 208 | 01 (Orange), 10 (SFR), 20 (Bouygues) |
| RU | 250 | 01 (MTS), 02 (MegaFon), 20 (Tele2) |

```python
jutsu.generate('imsi')              # → '286011234567890'  (TR varsayılan)
jutsu.generate('imsi', locale='US') # → '310010123456789'
```

### `msisdn` — MSISDN (E.164)
ITU-T E.164 §6 / 3GPP TS 23.003 §3.3. Locale-aware telefon numarası, tam E.164 formatında.
```python
jutsu.generate('msisdn')              # → '+905321234567'  (TR)
jutsu.generate('msisdn', locale='US') # → '+11234567890'
jutsu.generate('msisdn', locale='UK') # → '+447912345678'
jutsu.generate('msisdn', locale='DE') # → '+491512345678'
jutsu.generate('msisdn', locale='FR') # → '+33612345678'
jutsu.generate('msisdn', locale='RU') # → '+79161234567'
```

---

## 12. Finansal Piyasalar (Menkul Kıymet)

Standart: **ISO 6166:2021 (ISIN)** · **ABA CUSIP** · **London Stock Exchange SEDOL** · **ISO 17442 / ISO 7064 (LEI)**

### `isin` — International Securities Identification Number
ISO 6166:2021. CC(2) + NSIN(9 alfasayısal) + Luhn check(1) = 12 karakter. Locale-aware ülke kodu.
```python
jutsu.generate('isin')              # → 'TRB680001234X'  (TR varsayılan)
jutsu.generate('isin', locale='US') # → 'US0378331005'
jutsu.generate('isin', locale='UK') # → 'GB0002634946'  (GB prefix — ISO 3166-1 kodu)
jutsu.generate('isin', locale='DE') # → 'DE000XXXX0001'
# Test vektörleri (ISO 6166:2021):
#   Apple   US0378331005 → "30280378331005" → sum=50 ✓
#   Amazon  US0231351067 → "30280231351067" → sum=50 ✓
#   Vodafone GB0002634946 → "16110002634946" → sum=50 ✓
```

**Locale → ISIN Ülke Kodu:**

| Locale | ISIN Prefix | ISO 3166-1 |
|--------|------------|------------|
| TR | `TR` | Türkiye |
| US | `US` | Amerika Birleşik Devletleri |
| UK | `GB` | Birleşik Krallık |
| DE | `DE` | Almanya |
| FR | `FR` | Fransa |
| RU | `RU` | Rusya |

### `cusip` — Committee on Uniform Securities Identification Procedures
ABA CUSIP. 6 char issuer + 2 char issue + 1 check = 9 karakter (A-Z/0-9). Locale-independent.
```python
jutsu.generate('cusip')  # → '037833100'
# Algoritma: tek (1-indexed) pozisyonlar ×2, dijit toplamı
# Test vektörleri:
#   Apple  037833100 → sum=30 → check=0 ✓
#   Amazon 023135106 → sum=14 → check=6 ✓
```

### `sedol` — Stock Exchange Daily Official List
LSE SEDOL. 6 karakter (rakam + ünsüzler, ÜNLÜsüz: A,E,I,O,U yasak) + 1 check = 7 karakter. Ağırlıklar: [1,3,1,7,3,9].
```python
jutsu.generate('sedol')  # → '0263494'
# Test vektörleri:
#   Vodafone 0263494: 0×1+2×3+6×1+3×7+4×3+9×9 = 126 → check=4 ✓
#   Barclays 0798059: 0+21+9+56+0+45 = 131 → check=9 ✓
#   BT Group 3134865: 3+3+3+28+24+54 = 115 → check=5 ✓
```

### `lei` — Legal Entity Identifier
ISO 17442 / ISO 7064 MOD 97-10. 4 char LOU + 14 char entity + 2 check = 20 karakter.
```python
jutsu.generate('lei')  # → '529900T8BM49AURSDO55'  (örnek)
# Algoritma: tüm karakterler sayısala çevrilir (A=10...Z=35),
# birleştirilir, int(string) % 97 = 1 olmalı.
# Test vektörü: GLEIF kendi LEI'si 529900T8BM49AURSDO55 → 1 ✓
```

---

## 13. Kripto Para & Web3

Standart: **BTC P2PKH Base58Check** · **EIP-55 Ethereum Checksum Address** · **32-byte tx/block hash**

### `btc_address` — Bitcoin P2PKH Adresi

Base58Check kodlaması: `version(0x00)` + 20 byte random pubkey hash + SHA256d 4-byte checksum.
```python
jutsu.generate('btc_address')
# → '1A1zP1eP5QGefi2DMPTfTL5SLmv7Divf'  (genesis block coinbase — format örneği)
# Kural: 25–34 karakter, her zaman '1' ile başlar, sadece Base58 alfabesi (0,O,I,l hariç)
```

**Algoritma:**
- `payload = 0x00 || random_20_bytes`
- `checksum = SHA256(SHA256(payload))[:4]`
- `address = Base58Encode(payload + checksum)`

### `eth_address` — Ethereum EIP-55 Adresi

20 byte random hash + Keccak-256 mixed-case checksum (EIP-55).
```python
jutsu.generate('eth_address')
# → '0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed'
# Kural: '0x' + 40 hex karakter, Keccak-256 nibble >= 8 → büyük harf

# Bilinen test vektörleri (EIP-55 spec):
# 0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed
# 0xfB6916095ca1df60bB79Ce92cE3Ea74c37c5d359
# 0xdbF03B407c01E7cD3CBea99509d93f8DDDC8C6FB
# 0xD1220A0cf47c7B9Be7A2E6BA89F429762e7b9aDb
```

**Not:** Keccak-256, SHA3-256'dan sadece padding byte'ta farklıdır (Keccak: `0x01`, SHA3: `0x06`).

### `crypto_address` — BTC veya ETH Seçimli

```python
jutsu.generate('crypto_address')               # → BTC (varsayılan)
jutsu.generate('crypto_address', currency='btc')  # → BTC P2PKH
jutsu.generate('crypto_address', currency='eth')  # → ETH EIP-55
```

### `tx_hash` — İşlem Hash'i

```python
jutsu.generate('tx_hash')                   # → 64 hex (BTC varsayılan)
jutsu.generate('tx_hash', currency='btc')   # → 'a1b2c3d4...64hex'   (lowercase)
jutsu.generate('tx_hash', currency='eth')   # → '0xa1b2c3d4...64hex' (0x prefix)
```

### `block_hash` — Blok Hash'i

```python
jutsu.generate('block_hash')                   # → 64 hex (BTC varsayılan)
jutsu.generate('block_hash', currency='btc')   # → 64 char lowercase hex
jutsu.generate('block_hash', currency='eth')   # → '0x' + 64 char lowercase hex
```

---

## 14. E-Ticaret

Standart: **USPS Luhn MOD-10 (Publication 97)** · **UPS weighted check digit** · **FedEx Mod-11**

### `tracking_number` — Kargo Takip Numarası

```python
jutsu.generate('tracking_number')                    # USPS 22-digit (varsayılan)
jutsu.generate('tracking_number', carrier='usps')   # → '9400111899223397522384'
jutsu.generate('tracking_number', carrier='ups')    # → '1ZXS6O6M01YKTERUO2'
jutsu.generate('tracking_number', carrier='fedex')  # → '927385968731'
```

- **USPS**: prefix(92/94/70...) + 19 rastgele rakam + Luhn check = 22 rakam
- **UPS**: `1Z` + 6 alfasayısal + 2 servis kodu + 7 alfasayısal + 1 check = 18 karakter
- **FedEx**: 11 rakam + Mod-11 check = 12 rakam

### `sku` — Stok Kodu

```python
jutsu.generate('sku')       # → 'AB-048291'
# Format: 2-4 büyük harf + tire + 4-8 rakam (GS1'den ilham)
```

### `order_id` — Sipariş Numarası

```python
jutsu.generate('order_id')  # → 'ORD-K3M7P2Q9R1X5'
# Format: ORD- + 8-12 büyük alfasayısal (CSPRNG)
```

### `product_name`, `category`, `rating`

```python
jutsu.generate('product_name')  # → 'Wireless Headphones'
jutsu.generate('category')      # → 'Electronics'
jutsu.generate('rating')        # → '4.5'  (1.0–5.0, gerçekçi dağılım)
```

---

## 15. Konum & Coğrafya

Standart: **WGS 84 (ISO 6709)** · **IANA Time Zone Database** · **ISO 3166-1 alpha-2**

### Koordinatlar — locale-aware sınır kutuları

| Locale | Enlem (lat) | Boylam (lon) |
|---|---|---|
| TR | 36.0–42.0°N | 26.0–45.0°E |
| US | 25.0–49.0°N | -125.0 – -66.0°W |
| UK | 50.0–59.0°N | -8.0 – 2.0°E |
| DE | 47.0–55.0°N | 6.0–15.0°E |
| FR | 42.0–51.0°N | -5.0 – 8.0°E |
| RU | 41.0–82.0°N | 27.0–170.0°E |

```python
jutsu.generate('latitude',    locale='TR')   # → 39.925533
jutsu.generate('longitude',   locale='US')   # → -95.324812
jutsu.generate('timezone',    locale='RU')   # → 'Asia/Vladivostok'
jutsu.generate('country_code',locale='UK')   # → 'GB'  (ISO 3166-1)
jutsu.generate('coordinates', locale='DE')   # → '51.234567,9.876543'
```

---

## 16. Sosyal Medya

Format kuralı: **Twitter/X spec** — 4-15 karakter, `[a-z0-9_]`, baş/son alt çizgi yok.

```python
jutsu.generate('username')        # → 'probuilder99'
jutsu.generate('handle')          # → '@probuilder99'
jutsu.generate('hashtag')         # → '#AI2025'
jutsu.generate('bio')             # → 'Full-stack developer by day, gamer by night.'
jutsu.generate('follower_count')  # → '14273'
```

**Dağılım (follower_count):**
- %40 → 0–499 (mikro hesap)
- %25 → 500–4.999
- %15 → 5k–49k
- %12 → 50k–499k
- %6  → 500k–4.99M
- %2  → 5M–49M

---

## 17. CLI Komutları — Profile, Company, Bulk, Export

### `mockjutsu profile` — Kişi Profili

```bash
mockjutsu profile                    # TR locale, 1 profil
mockjutsu profile --locale DE        # Alman profili
mockjutsu profile --locale TR --count 3  # 3 profil, JSON array
```

### `mockjutsu company` — Şirket Profili

```bash
mockjutsu company                    # TR locale
mockjutsu company --locale US        # Amerikan şirketi
mockjutsu company --count 2          # 2 şirket
```

### `mockjutsu bulk` — Toplu Üretim

```bash
mockjutsu bulk tckn --count 5        # 5 TCKN
mockjutsu bulk iban --locale TR --count 10  # 10 TR IBAN
```

### `mockjutsu export` — Şablon & Dışa Aktarım

```bash
# JSON (varsayılan)
mockjutsu export fullname tckn phone --count 5 --locale TR

# CSV
mockjutsu export fullname iban --count 10 --format csv

# SQL INSERT
mockjutsu export fullname tckn iban --count 3 --format sql --table users
```

### `generate` — Ek Parametreler

```bash
# Kripto — --currency
mockjutsu generate tx_hash --currency eth
mockjutsu generate crypto_address --currency btc

# Kargo — --carrier
mockjutsu generate tracking_number --carrier ups
mockjutsu generate tracking_number --carrier fedex
```

---

*mock-jutsu-api · Altan Sezer Ayan - A.S.A · [github.com/altansayan/mock-jutsu-api](https://github.com/altansayan/mock-jutsu-api)*
