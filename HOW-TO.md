# mock-jutsu — Kullanım Kılavuzu (How-To)

> **mock-jutsu** — 6 locale (TR/US/UK/DE/FR/RU), 57 parametre tipi, yasal algoritmalarla mock veri üretimi.
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

---

*mock-jutsu-api · Altan Sezer Ayan - A.S.A · [github.com/altansayan/mock-jutsu-api](https://github.com/altansayan/mock-jutsu-api)*
