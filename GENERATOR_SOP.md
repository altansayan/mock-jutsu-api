# Mock Jutsu — Generator Development SOP

Her yeni generator eklemeden önce bu adımları uygula.
Bu kuralları atlamak = tekrar algoritma bug'ı demek.

## Zorunlu Kontrol Listesi

### 1. Standart Kaynağı Belirt
Her generator dosyasının başındaki docstring'e kaynak ekle:
```python
# Standard: ISO 13616 (IBAN), https://www.swift.com/standards/data-standards/iban
# Standard: ABA Routing, https://www.federalreserve.gov/
# Standard: T.C. Kimlik No, https://tckimlik.nvi.gov.tr/
```

### 2. Test Vektörü Ekle
`compliance/algorithm_vectors.json` dosyasına en az 2 gerçek-dünya değeri ekle:
- Checksum olan her algoritma için zorunlu
- Gerçek değer kullan (örn. IBM'in CUSIP'i, bilinen geçerli bir IBAN)
- Geçerli VE geçersiz değer ekle

### 3. Format Contract Ekle
`compliance/format_contracts.json` dosyasına regex ekle:
```json
"my_new_type": {"pattern": "^regex$", "example": "known_valid_value"}
```

### 4. Python Test Ekle
`tests/test_known_vectors.py` dosyasına:
- Vektörleri doğrulayan test
- Generator çıktısının format contract'ı karşıladığını doğrulayan test

### 5. Java Test Ekle
`KnownVectorTest.java` dosyasına:
- Aynı vektörlerle checksum doğrulaması
- Generated output format testi

### 6. Python–Java Parity
Her iki implementasyonun aynı formatta çıktı ürettiğini kontrol et.
`compliance/format_contracts.json` her iki taraf için tek kaynak.

## Algoritma Hata Kaçırma Kısıtlamaları

```
YANLIŞ: Sadece "doğru format üretiyor mu?" test et
DOĞRU:  Bilinen geçerli değerle checksum doğrula

YANLIŞ: Python'dan Java'ya elle çevir, test etme
DOĞRU:  compliance/ JSON'dan aynı regex'i oku

YANLIŞ: "çalışıyor gibi görünüyor" ile bırak
DOĞRU:  Gerçek-dünya değerini (IBM CUSIP, Apple ISIN) hardcode et
```

## Commit Mesajı Formatı

```
feat(generator): add XYZ generator

Standard: ISO XXXX / RFC XXXX / [ulusal kaynak]
Reference: https://...
Algorithm: [tek cümle özet]
Vectors: verified against [kaynak]
```

## Hangi Algoritmalar Test Vektörü Gerektirir?

Checksum olan her şey:
- Vergi numaraları (TCKN, VKN, INN, Steuer-ID, NIR...)
- Finansal (IBAN, CUSIP, ISIN, SEDOL, ABA Routing, Luhn...)
- Kimlik (NHS, NPI, SNILS...)
- Barkod (EAN-13, ISBN, UPC...)
- Telecom (IMEI, ICCID...)
