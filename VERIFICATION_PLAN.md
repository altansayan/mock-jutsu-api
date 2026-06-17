# Mock-Jutsu Generator Doğrulama Planı

## Mevcut Durum

| Kategori | Tip Sayısı | Güven Durumu |
|----------|-----------|--------------|
| Dış kütüphane doğrulandı | 50 | Güvenilir |
| Algoritmik (doğrulama yok) | 40 | Bilinmiyor |
| Yapısal (format-only) | 139 | Bilinmiyor |
| validation_matrix'e hiç girmemiş | ~25 | Tamamen bilinmiyor |
| **Toplam** | **~254** | |

**Temel sorun:** Testlerin büyük çoğunluğu circular — generator'ın kendi formülünü
kendi testiyle denetliyor. Bu oturumda UTR'nin %93, VAT GB'nin %100 hatalı olduğunu
ancak dış kütüphaneyle anlayabildik.

---

## Doğrulama Metodolojisi

Her fonksiyon için şu 4 adım:

1. **Kod oku** — generator implementasyonunu anla
2. **Standart karşılaştır** — RFC/ISO/SWIFT/GS1 belgesiyle adım adım eşleştir
3. **Bug varsa düzelt** — kütüphane otorite, bizim kod değil
4. **Resmi vektör ekle** — standarttaki tüm örnekleri `test_known_vectors.py`'ye yaz

---

## Sprint Planı

### Sprint 0 — Haritalama (Önce Yap)
**Hedef:** Tüm [???] fonksiyonları tespit et, validation_matrix'e ekle.

Şu an `[???]` görünen ~25 fonksiyon var:
- `generate_tr_id`, `generate_ykn`, `generate_uk_ni`
- `generate_ru_snils`, `generate_ru_kpp`, `generate_ru_inn_*`
- `generate_de_steuer_id`, `generate_tr_sgk`, `generate_tr_mersis`
- `generate_bik`, `generate_edifact_orders`
- `generate_card_number`, `generate_bank_account`
- vs.

Çıktı: Güncellenmiş `compliance/validation_matrix.json`, sıfır [???].

---

### Sprint 1 — hardware.py (En Yüksek Risk)
**Dosya:** `src/mockjutsu/generators/hardware.py`
**Tipler:** 5 algoritmik tip

| Tip | Standart | Risk |
|-----|---------|------|
| `track1_data` | ISO/IEC 7813 — LRC checksum | YÜKSEK |
| `track2_data` | ISO/IEC 7813 — LRC checksum | YÜKSEK |
| `chip_data` | EMV Book 2/3 | YÜKSEK |
| `pin_block` | ISO 9564-1 Format 0 | YÜKSEK |
| `pin_block_fmt3` | ISO 9564-1 Format 3 | YÜKSEK |

Tüm bunlar finansal kart verisi — yanlış üretilirse test sistemleri yanlış sonuç verir.

---

### Sprint 2 — identity.py Tamamlama
**Dosya:** `src/mockjutsu/generators/identity.py`
**Durum:** 27 fonksiyon var, çoğu [???]

| Tip | Standart | Durum |
|-----|---------|-------|
| `nin` / `uk_ni` | HMRC NI format | Dış validator yok |
| `snils` | PFR Rusya checksum | Dış validator yok |
| `kpp` | FTS Rusya format | Dış validator yok |
| `de_steuer_id` | BZSt MOD 11 | Bilinmiyor |
| `tr_sgk` | SGK format | Bilinmiyor |
| `de_rvn` | Deutsche Rentenversicherung | Sprint 2'de doğrulandı |

---

### Sprint 3 — banking.py (Mesaj Protokolleri)
**Dosya:** `src/mockjutsu/generators/banking.py`
**Tipler:**

| Tip | Standart | Risk |
|-----|---------|------|
| `swift_mt103` | SWIFT User Handbook | YÜKSEK |
| `fedwire` | Fedwire Funds Service | YÜKSEK |
| `sepa_ref` | ISO 11649 MOD-97 | ORTA |
| `creditor_ref` | ISO 11649 MOD-97 | ORTA |
| `sort_code` | UK BACS format | DÜŞÜK |

---

### Sprint 4 — automotive.py + nmea.py (Checksum Tipleri)
**Tipler:**

| Tip | Standart | Durum |
|-----|---------|-------|
| `can_frame` | ISO 11898-1 CRC-15 | Zaten implement var |
| `obd2_response` | SAE J1979 | CAN frame bazlı |
| `nmea_gpgga` | NMEA 0183 XOR checksum | Kontrol gerek |
| `nmea_gprmc` | NMEA 0183 XOR checksum | Kontrol gerek |

---

### Sprint 5 — barcode.py + telecom.py + tle.py
**Tipler:**

| Tip | Standart | Durum |
|-----|---------|-------|
| `gs1_128` | GS1 General Spec | Bilinmiyor |
| `msisdn` | ITU-T E.164 | Format kontrolü |
| `tle_satellite` | NORAD Modulo-10 | Implement var |
| `epc` | GS1 EPC | Bilinmiyor |

---

### Sprint 6 — edi.py + payments.py
**Tipler:**

| Tip | Standart | Risk |
|-----|---------|------|
| `edi_850` | ANSI X12 (ISA/GS/SE count) | ORTA |
| `edifact_orders` | UN/EDIFACT D96A | ORTA |
| `iso8583_*` (3 tip) | ISO 8583 bitmap | YÜKSEK |

---

### Sprint 7 — health.py
**Tipler:**

| Tip | Standart | Durum |
|-----|---------|-------|
| `dicom_uid` | DICOM PS 3.5 UUID-based | Bilinmiyor |
| `nhs_number` | NHS Modulo-11 | Zaten dış lib doğrulayamıyor — vektör ekle |

---

### Sprint 8 — Yapısal Tiplerin Gizli Algoritmalarını Bul
**Hedef:** 139 "yapısal" tipten gerçekten algoritmik olanları ayıkla.

Şüphelenilen tipler (format-only değil, algoritma var):
- `totp_code` — RFC 6238 TOTP (HMAC-SHA1 tabanlı)
- `webhook_signature` — HMAC-SHA256
- `signature` — imza formatı
- `bik_code` — Rusya banka kodu
- `sedol` — LSE check digit
- `3ds_cavv` — Base64 kriptografik değer

---

### Sprint 9 — Son Kontrol & README Güncelleme
- Tüm kategoriler güncellendi mi?
- `test_known_vectors.py` yeterince zengin mi?
- README rozet tablosu gerçeği yansıtıyor mu?
- PyPI için hazır mıyız?

---

## Hedef Tablo (Plan Tamamlandığında)

| Kategori | Hedef Tip Sayısı |
|----------|-----------------|
| Dış kütüphane doğrulandı | ~55 |
| Resmi vektörle doğrulandı | ~80 |
| Yapısal (dürüstçe etiketlenmiş) | ~120 |
| Bilinmiyor | 0 |

---

## Kural

> Her sprint sonunda: testler yeşil, validation_matrix güncel, push yapılmış.
> "Doğrulanmamış" tipi "doğrulandı" olarak etiketlemek test vektörü olmadan yasak.
