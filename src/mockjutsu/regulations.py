"""
Mock Jutsu — Regulation Reference Map
======================================
Maps every generator type to the data-protection regulations that govern it,
together with the masking format required by each regulation.

IMPORTANT: Mock Jutsu generates *synthetic* test data — no real PII.
           This file exists so the --mask flag can produce output whose
           format matches what real systems are permitted to display.

══════════════════════════════════════════════════════════════════════════
  REGULATION TEXTS
══════════════════════════════════════════════════════════════════════════

── PCI DSS v4.0.1 ────────────────────────────────────────────────────────

  Requirement 3.3.1 (Sensitive Authentication Data — SAD):
    "SAD must not be retained after authorization, even if encrypted.
     SAD includes: full track data (magnetic stripe or chip equivalent),
     card verification codes/values (CVV2, CVC2, CAV2, CID), and PINs/PIN blocks."

  Requirement 3.4.1 (PAN Display Masking):
    "The PAN is masked when displayed (the BIN and last four digits are the
     maximum number of digits to be displayed), such that only personnel with
     a legitimate business need can see more than the BIN/last four digits
     of the PAN."
    → BIN = first 6 digits (or first 8 for extended BIN networks).
    → Masked format: 453201** **** 9012  (first 6 + ****** + last 4)

  Requirement 3.5.1 (PAN Storage):
    "PAN is secured with strong cryptography if stored."

  Requirement 3.3.2 (SAD in pre-authorisation):
    "All SAD collected prior to completion of authorisation is encrypted
     using strong cryptography."

── KVKK (Kişisel Verilerin Korunması Kanunu) — Law No. 6698 ─────────────

  Madde 12 — Veri güvenliğine ilişkin yükümlülükler:
    "Veri sorumlusu; kişisel verilerin hukuka aykırı olarak işlenmesini
     önlemek, kişisel verilere hukuka aykırı olarak erişilmesini önlemek,
     kişisel verilerin muhafazasını sağlamak amacıyla uygun güvenlik
     düzeyini temin etmeye yönelik gerekli her türlü teknik ve idari
     tedbirleri almak zorundadır."

  KVKK Kişisel Veri Güvenliği Rehberi — Maskeleme Örneği:
    TCKN maskesi: "25*******10"  (ilk 2 hane + son 2 hane görünür)
    Telefon:      "+90 532 *** ** 34"
    E-posta:      "al***@gmail.com"

  Özel nitelikli kişisel veriler (Madde 6):
    Sağlık, biyometrik, cezai sicil, din, siyasi görüş, etnik köken,
    sendika üyeliği, cinsel yaşam verisi — işlenmesi kural olarak yasaktır.

── GDPR (EU General Data Protection Regulation — 2016/679) ──────────────

  Article 4(1) — Personal Data Definition:
    "'personal data' means any information relating to an identified or
     identifiable natural person; an identifiable natural person is one who
     can be identified, directly or indirectly, in particular by reference to
     an identifier such as a name, an identification number, location data,
     an online identifier or to one or more factors specific to the physical,
     physiological, genetic, mental, economic, cultural or social identity
     of that natural person."

  Article 9(1) — Special Categories (prohibited without explicit consent):
    "Processing of personal data revealing racial or ethnic origin, political
     opinions, religious or philosophical beliefs, or trade union membership,
     and the processing of genetic data, biometric data for the purpose of
     uniquely identifying a natural person, data concerning health or data
     concerning a natural person's sex life or sexual orientation
     shall be prohibited."

  Article 25 — Data Protection by Design and by Default:
    Controllers must implement pseudonymisation and data minimisation.

  Recital 26 — Pseudonymisation:
    "Personal data which have undergone pseudonymisation, which could be
     attributed to a natural person by the use of additional information
     should be considered to be information on an identifiable natural person."

── UK GDPR + Data Protection Act 2018 (DPA 2018) ───────────────────────

  UK GDPR mirrors EU GDPR post-Brexit.
  DPA 2018 Schedule 1 Part 1 — additional lawful bases for special categories.

  NIN (National Insurance Number):
    HM Revenue & Customs — must not be shared beyond tax/benefits purposes.
    Guidance: "You must keep your NIN secure."

  NHS Number:
    NHS Data Security and Protection Toolkit (DSPT) mandates
    masking in non-clinical contexts (e.g., NHS 943 476 5919 → 943 *** ****)

── US Laws ────────────────────────────────────────────────────────────────

  Privacy Act of 1974 (5 U.S.C. § 552a):
    Federal agencies must safeguard SSN and other personally identifiable
    information (PII) held in systems of records.

  IRS Revenue Procedure 2007-40 / Publication 1075:
    SSN truncation on official documents:
    "Truncated SSN (TSSN): ***-**-1234 (last four visible)"

  GLBA (Gramm-Leach-Bliley Act, 15 U.S.C. § 6801):
    Financial institutions must protect customers' nonpublic personal
    information including bank account numbers, routing numbers, and
    credit card numbers.

  HIPAA Privacy Rule (45 CFR §164.514):
    Protected Health Information (PHI) — 18 identifiers must be de-identified.
    Includes: names, geographic data, dates (except year), phone, fax,
    email, SSN, medical record numbers, health plan numbers, account numbers,
    certificate/license numbers, biometric identifiers, NPI.

── LGPD (Lei Geral de Proteção de Dados — Brazil, Law No. 13.709/2018) ──

  Art. 46: Controllers must adopt technical and administrative measures
    to protect personal data from unauthorized access.
  CPF and CNPJ are treated as personal/business identifiers.
  Sensitive data (Art. 11) includes: racial/ethnic origin, religious beliefs,
    health data, genetic/biometric data, political opinions.

── PDPA / Aadhaar Act (India) ────────────────────────────────────────────

  Aadhaar (Targeted Delivery...) Act 2016, Section 29:
    "No Aadhaar number or biometric information collected shall be used
     for any purpose other than the purposes specified in this Act."
  UIDAI guidelines: Aadhaar must be masked as "XXXX XXXX 1234" (last 4 visible).

  Personal Data Protection Bill (PDPB) — draft, under review as of 2025.

── PIPL (Personal Information Protection Law — China, 2021) ─────────────

  Article 28 — Sensitive Personal Information:
    Includes biometrics, religious beliefs, special identity, medical health,
    financial accounts, location tracking, and minors' personal information.
  RIC (Resident Identity Card) — considered sensitive; processing requires
    separate consent.

── LFPDPPP (Ley Federal de Protección de Datos Personales — Mexico, 2010) ─

  Article 16 — Privacy Notice:
    Data subjects must be informed of data collection via privacy notice.
  CURP and RFC are national identifiers — treated as personal data.

══════════════════════════════════════════════════════════════════════════
"""

# ── Regulation constants ──────────────────────────────────────────────────
PCI_DSS    = "PCI_DSS_4.0.1"
KVKK       = "KVKK_6698"
GDPR       = "GDPR_2016_679"
GDPR_ART9  = "GDPR_Art9_SpecialCategory"
UK_GDPR    = "UK_GDPR_DPA2018"
US_PRIVACY = "US_Privacy_Act"
US_GLBA    = "US_GLBA"
US_HIPAA   = "US_HIPAA"
LGPD       = "LGPD_Brazil"
PDPA_IN    = "Aadhaar_Act_India"
PIPL       = "PIPL_China"
LFPDPPP    = "LFPDPPP_Mexico"

# ── REGULATION_TAGS ───────────────────────────────────────────────────────
# Schema per entry:
#   regs        : list[str]  — applicable regulation constants (may be empty)
#   req         : str        — specific article / requirement reference
#   mask        : str        — masked display example ("" if not applicable)
#   never_store : bool       — True = must NEVER be stored even in encrypted form (PCI SAD)
#   notes       : str        — brief note on why this type is regulated
#
REGULATION_TAGS: dict[str, dict] = {

    # ══════════════════════════════════════════════════════════════════════
    # IDENTITY — Turkish
    # ══════════════════════════════════════════════════════════════════════
    "tckn": {
        "regs": [KVKK],
        "req": "KVKK Madde 12 / KVKK Rehberi",
        "mask": "25*******10",
        "never_store": False,
        "notes": "Türk Cumhuriyeti Kimlik Numarası — kişisel veri (KVKK Madde 6 kapsamında değil ama Madde 12 güvenlik yükümlülüğü var)",
    },
    "tckn_masked": {
        "regs": [KVKK],
        "req": "KVKK Madde 12 / KVKK Rehberi",
        "mask": "***123456**",
        "never_store": False,
        "notes": "Zaten maskeli TCKN — privacy-safe display format",
    },
    "ykn": {
        "regs": [KVKK],
        "req": "KVKK Madde 12",
        "mask": "99*******78",
        "never_store": False,
        "notes": "Yabancı Kimlik Numarası — yabancı uyruklu kişisel veri",
    },
    "vkn": {
        "regs": [KVKK],
        "req": "KVKK Madde 12",
        "mask": "123****890",
        "never_store": False,
        "notes": "Vergi Kimlik Numarası — tüzel veya gerçek kişi tanımlayıcı",
    },
    "sgk": {
        "regs": [KVKK],
        "req": "KVKK Madde 12",
        "mask": "34-*******-1.01-02",
        "never_store": False,
        "notes": "SGK Sicil Numarası — çalışan kişisel verisi",
    },
    "mersis": {
        "regs": [KVKK],
        "req": "KVKK Madde 12",
        "mask": "",
        "never_store": False,
        "notes": "MERSIS — tüzel kişi tanımlayıcı; bireysel gizlilik riski düşük",
    },

    # ── Generic / locale-based identity ──────────────────────────────────
    "nationalid": {
        "regs": [KVKK, GDPR],
        "req": "KVKK Madde 12 (TR) / GDPR Art 4(1) (EU)",
        "mask": "**...**XX",
        "never_store": False,
        "notes": "Locale-specific national ID — governed by the country's own data-protection law",
    },
    "taxid": {
        "regs": [KVKK, GDPR],
        "req": "KVKK Madde 12 (TR) / GDPR Art 4(1) (EU)",
        "mask": "***...***",
        "never_store": False,
        "notes": "Generic tax ID — personal identifier; mask in non-tax contexts",
    },
    "employer_id": {
        "regs": [KVKK, GDPR],
        "req": "KVKK Madde 12 (TR) / GDPR Art 4(1) (EU)",
        "mask": "",
        "never_store": False,
        "notes": "Employer registration — usually business identifier; low individual privacy risk",
    },
    "insurance_id": {
        "regs": [KVKK, GDPR, GDPR_ART9],
        "req": "KVKK Madde 6 (TR) / GDPR Art 9(1) (EU)",
        "mask": "**...**XX",
        "never_store": False,
        "notes": "Social insurance ID can link to health/disability data — special category risk",
    },

    # ── US Identity ───────────────────────────────────────────────────────
    "ssn": {
        "regs": [US_PRIVACY],
        "req": "Privacy Act 1974 / IRS Rev. Proc. 2007-40 (truncation: ***-**-1234)",
        "mask": "***-**-6789",
        "never_store": False,
        "notes": "US Social Security Number — must be masked to last 4 digits on documents",
    },
    "ssn_masked": {
        "regs": [US_PRIVACY],
        "req": "Privacy Act 1974 / IRS Rev. Proc. 2007-40",
        "mask": "***-**-6789",
        "never_store": False,
        "notes": "Already-masked SSN — privacy-safe display format",
    },
    "ein": {
        "regs": [US_PRIVACY, US_GLBA],
        "req": "GLBA / IRS guidelines",
        "mask": "**-*456789",
        "never_store": False,
        "notes": "Employer ID Number — business identifier but also used for identity theft",
    },

    # ── UK Identity ───────────────────────────────────────────────────────
    "nin": {
        "regs": [UK_GDPR],
        "req": "UK GDPR Art 4(1) / HMRC NIN Security Guidance",
        "mask": "AB ** ** ** C",
        "never_store": False,
        "notes": "UK National Insurance Number — must be kept secure; share only for tax/benefits",
    },
    "utr": {
        "regs": [UK_GDPR],
        "req": "UK GDPR Art 4(1) / HMRC guidelines",
        "mask": "12345*****",
        "never_store": False,
        "notes": "Unique Taxpayer Reference — personal identifier, HMRC confidential",
    },
    "crn": {
        "regs": [UK_GDPR],
        "req": "UK GDPR Art 4(1)",
        "mask": "",
        "never_store": False,
        "notes": "Company Registration Number — public register data; low privacy risk",
    },
    "paye": {
        "regs": [UK_GDPR],
        "req": "UK GDPR Art 4(1) / HMRC PAYE guidelines",
        "mask": "123/**4567",
        "never_store": False,
        "notes": "UK PAYE reference — employer/employee tax reference; keep confidential",
    },

    # ── German Identity ───────────────────────────────────────────────────
    "ust_id": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1)",
        "mask": "",
        "never_store": False,
        "notes": "German VAT ID — business identifier; publicly verifiable via VIES",
    },
    "ustid": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1)",
        "mask": "",
        "never_store": False,
        "notes": "Alias for ust_id",
    },
    "hrb": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1)",
        "mask": "",
        "never_store": False,
        "notes": "German Handelsregister — public commercial register entry",
    },
    "rvn": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) — personal identifier in German pension system",
        "mask": "65 ****92 W ****",
        "never_store": False,
        "notes": "Rentenversicherungsnummer — personal pension ID; keep confidential",
    },

    # ── French Identity ───────────────────────────────────────────────────
    "siren": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1)",
        "mask": "",
        "never_store": False,
        "notes": "French SIREN — business entity; public INSEE registry",
    },
    "siret": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1)",
        "mask": "",
        "never_store": False,
        "notes": "French SIRET — establishment code; public INSEE registry",
    },
    "tva": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1)",
        "mask": "",
        "never_store": False,
        "notes": "French VAT number — business identifier; publicly verifiable",
    },

    # ── Russian Identity ──────────────────────────────────────────────────
    "inn": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) (if EU data subjects involved)",
        "mask": "770*****93",
        "never_store": False,
        "notes": "Russian INN — personal/business tax identifier",
    },
    "inn_individual": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1)",
        "mask": "770*****93",
        "never_store": False,
        "notes": "Russian individual INN — personal tax ID",
    },
    "snils": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1)",
        "mask": "112-***-445 **",
        "never_store": False,
        "notes": "Russian SNILS — pension insurance personal account number",
    },
    "kpp": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1)",
        "mask": "",
        "never_store": False,
        "notes": "KPP — reason code for tax registration; business/entity identifier",
    },
    "ogrn": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1)",
        "mask": "",
        "never_store": False,
        "notes": "OGRN — Russian primary state registration number; legal entity",
    },

    # ── VAT Number ────────────────────────────────────────────────────────
    "vat_number": {
        "regs": [GDPR, KVKK],
        "req": "GDPR Art 4(1) (EU) / KVKK Madde 12 (TR)",
        "mask": "",
        "never_store": False,
        "notes": "EU/Global VAT number — business identifier; publicly verifiable via VIES",
    },

    # ══════════════════════════════════════════════════════════════════════
    # NAME
    # ══════════════════════════════════════════════════════════════════════
    "firstname": {
        "regs": [KVKK, GDPR],
        "req": "KVKK Madde 12 (TR) / GDPR Art 4(1) (EU)",
        "mask": "E***",
        "never_store": False,
        "notes": "Personal name — direct identifier",
    },
    "lastname": {
        "regs": [KVKK, GDPR],
        "req": "KVKK Madde 12 (TR) / GDPR Art 4(1) (EU)",
        "mask": "Y***az",
        "never_store": False,
        "notes": "Personal surname — direct identifier",
    },
    "fullname": {
        "regs": [KVKK, GDPR],
        "req": "KVKK Madde 12 (TR) / GDPR Art 4(1) (EU)",
        "mask": "E*** K***",
        "never_store": False,
        "notes": "Full name — direct personal identifier",
    },
    "patronymic": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1)",
        "mask": "I***vich",
        "never_store": False,
        "notes": "Russian-style patronymic — personal identifier",
    },

    # ══════════════════════════════════════════════════════════════════════
    # DOCUMENT
    # ══════════════════════════════════════════════════════════════════════
    "passport": {
        "regs": [KVKK, GDPR],
        "req": "KVKK Madde 12 / GDPR Art 4(1)",
        "mask": "P1****67",
        "never_store": False,
        "notes": "Passport number — travel document; direct personal identifier",
    },
    "license": {
        "regs": [KVKK, GDPR],
        "req": "KVKK Madde 12 / GDPR Art 4(1)",
        "mask": "6****1",
        "never_store": False,
        "notes": "Driver's license number — government-issued personal identifier",
    },

    # ══════════════════════════════════════════════════════════════════════
    # DEMOGRAPHIC
    # ══════════════════════════════════════════════════════════════════════
    "age": {
        "regs": [KVKK, GDPR],
        "req": "KVKK Madde 12 / GDPR Art 4(1)",
        "mask": "",
        "never_store": False,
        "notes": "Age alone rarely identifies a person but combined with other data does (quasi-identifier)",
    },
    "gender": {
        "regs": [KVKK, GDPR],
        "req": "KVKK Madde 12 / GDPR Art 4(1)",
        "mask": "",
        "never_store": False,
        "notes": "Gender — personal attribute; quasi-identifier",
    },
    "birthdate": {
        "regs": [KVKK, GDPR],
        "req": "KVKK Madde 12 / GDPR Art 4(1)",
        "mask": "1990-**-**",
        "never_store": False,
        "notes": "Date of birth — strong quasi-identifier; combined with name or ZIP uniquely identifies most people",
    },
    "nationality": {
        "regs": [KVKK, GDPR],
        "req": "KVKK Madde 12 / GDPR Art 4(1)",
        "mask": "",
        "never_store": False,
        "notes": "Nationality — can reveal ethnic/national origin (GDPR quasi-Art9 risk)",
    },

    # ══════════════════════════════════════════════════════════════════════
    # FINANCIAL — Payment Cards (PCI DSS Scope)
    # ══════════════════════════════════════════════════════════════════════
    "cardnum": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1 Req 3.4.1",
        "mask": "4532 01** **** 9012",
        "never_store": False,
        "notes": "Primary Account Number (PAN) — mask all but first 6 (BIN) and last 4 digits",
    },
    "cvv3": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1 Req 3.3.1 — SAD",
        "mask": "***",
        "never_store": True,
        "notes": "CVV/CVC — Sensitive Authentication Data; MUST NOT be stored after authorization under any circumstances",
    },
    "cvv4": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1 Req 3.3.1 — SAD",
        "mask": "****",
        "never_store": True,
        "notes": "4-digit CVV (Amex CID) — SAD; same prohibition as cvv3",
    },
    "pin": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1 Req 3.3.1 — SAD",
        "mask": "****",
        "never_store": True,
        "notes": "PIN — SAD; must never be stored, logged, or displayed after authorization",
    },
    "cardtype": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "Card type (Credit/Debit) — not PII alone; no direct regulation",
    },
    "cardstatus": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "Card status flag — not PII alone",
    },
    "cardcategory": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "Card level/category — not PII alone",
    },
    "cardowner": {
        "regs": [PCI_DSS, KVKK, GDPR],
        "req": "PCI DSS 4.0.1 Req 3.4.1 (cardholder name on card) / GDPR Art 4(1)",
        "mask": "J*** S***",
        "never_store": False,
        "notes": "Cardholder name — PAN-linked personal data; mask when displaying card details",
    },
    "expiry": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1 Req 3.4 — PAN-linked data",
        "mask": "**/**",
        "never_store": False,
        "notes": "Card expiry — PAN-linked; mask in non-payment contexts",
    },
    "expirymonth": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1 Req 3.4",
        "mask": "**",
        "never_store": False,
        "notes": "Expiry month — PAN-linked data",
    },
    "expiryyear": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1 Req 3.4",
        "mask": "**",
        "never_store": False,
        "notes": "Expiry year — PAN-linked data",
    },
    "cardnetwork": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "Card network name — not PII",
    },
    "issuer": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "Simulated issuing bank name — not real PII",
    },

    # ── Financial — Account / Banking ─────────────────────────────────────
    "balance": {
        "regs": [KVKK, GDPR, US_GLBA],
        "req": "KVKK Madde 12 / GDPR Art 4(1) / GLBA",
        "mask": "****75",
        "never_store": False,
        "notes": "Account balance — financial personal data; restrict access",
    },
    "iban": {
        "regs": [KVKK, GDPR],
        "req": "KVKK Madde 12 (TR) / GDPR Art 4(1) (EU)",
        "mask": "TR33 0006 **** **** **** **00 26",
        "never_store": False,
        "notes": "IBAN — bank account identifier; personal financial data",
    },
    "credit_score": {
        "regs": [KVKK, GDPR, US_GLBA],
        "req": "KVKK Madde 12 / GDPR Art 4(1) / GLBA",
        "mask": "7**",
        "never_store": False,
        "notes": "Credit score — financial profiling data; restrict access",
    },

    # ── Financial — QR / 3DS / EMV ───────────────────────────────────────
    "sepa_qr": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) — contains IBAN and beneficiary name",
        "mask": "",
        "never_store": False,
        "notes": "SEPA QR code contains IBAN + payee name — personal financial data",
    },
    "emv_qr_p2p": {
        "regs": [PCI_DSS, KVKK],
        "req": "PCI DSS 4.0.1 Req 3.4 / KVKK Madde 12",
        "mask": "",
        "never_store": False,
        "notes": "P2P payment QR can contain masked PAN data",
    },
    "emv_qr_atm": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1 Req 3.4",
        "mask": "",
        "never_store": False,
        "notes": "ATM cash-out QR — PCI DSS in-scope",
    },
    "emv_qr_pos": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1 Req 3.4",
        "mask": "",
        "never_store": False,
        "notes": "POS merchant QR — PCI DSS in-scope",
    },
    "3ds_cavv": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1 Req 3.3.1 — SAD",
        "mask": "****",
        "never_store": True,
        "notes": "3DS CAVV — cardholder authentication value; SAD, must not be stored post-auth",
    },
    "3ds_eci": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1 Req 3.3",
        "mask": "",
        "never_store": False,
        "notes": "ECI flag — transaction outcome indicator; not sensitive on its own",
    },

    # ══════════════════════════════════════════════════════════════════════
    # HARDWARE — Magnetic Stripe / Chip / PIN Block (PCI DSS SAD)
    # ══════════════════════════════════════════════════════════════════════
    "track1_data": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1 Req 3.3.1 — SAD (full track data)",
        "mask": "%B4532 01** **** 9012^MOCKJ***^28120...?",
        "never_store": True,
        "notes": "ISO 7813 Track 1 — full track data is SAD; must NEVER be stored after authorization",
    },
    "track2_data": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1 Req 3.3.1 — SAD (full track data)",
        "mask": ";4532 01** **** 9012=2812...?",
        "never_store": True,
        "notes": "ISO 7813 Track 2 — full track data is SAD; must NEVER be stored after authorization",
    },
    "chip_data": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1 Req 3.3.1 — SAD (chip equivalent data)",
        "mask": "",
        "never_store": True,
        "notes": "EMV chip TLV — equivalent of track data; SAD, must not be stored post-auth",
    },
    "pin_block": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1 Req 3.3.1 — SAD (PIN block)",
        "mask": "0*FFFFFFFFFFFF",
        "never_store": True,
        "notes": "ISO 9564-1 Format 0 PIN block — SAD; never store",
    },
    "pin_block_fmt3": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1 Req 3.3.1 — SAD (PIN block)",
        "mask": "3***************",
        "never_store": True,
        "notes": "ISO 9564-1 Format 3 PIN block — SAD; never store",
    },

    # ══════════════════════════════════════════════════════════════════════
    # SECURITY — technical data, low PII risk
    # ══════════════════════════════════════════════════════════════════════
    "cef_log": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "Security log format — may contain IP addresses (GDPR quasi-PII if linked to person)",
    },
    "x509_cert": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "X.509 certificate fields — subject/SAN may contain personal email/domain",
    },
    "pcap_hex": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "Network capture hex — mock data; real pcaps may contain PII under GDPR",
    },

    # ══════════════════════════════════════════════════════════════════════
    # BANKING
    # ══════════════════════════════════════════════════════════════════════
    "creditor_ref": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "ISO 11649 creditor reference — payment metadata, no direct PII",
    },
    "swift": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "BIC/SWIFT code — bank identifier, public information",
    },
    "bic": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "Alias for SWIFT BIC — public information",
    },
    "sort_code": {
        "regs": [UK_GDPR, US_GLBA],
        "req": "UK GDPR Art 4(1) — when linked to account holder",
        "mask": "20-**-**",
        "never_store": False,
        "notes": "UK sort code — bank routing identifier; personal when combined with account number",
    },
    "routing_number": {
        "regs": [US_GLBA],
        "req": "GLBA — bank routing identifier",
        "mask": "021***021",
        "never_store": False,
        "notes": "US ABA routing number — identifies the bank; restricted under GLBA when linked to account",
    },
    "bik_code": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "Russian BIK — bank identifier code; public information",
    },
    "bank_name": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "Simulated bank name — fictitious; no PII",
    },
    "transaction": {
        "regs": [KVKK, GDPR, US_GLBA],
        "req": "KVKK Madde 12 / GDPR Art 4(1) / GLBA",
        "mask": "",
        "never_store": False,
        "notes": "Banking transaction record — contains IBAN, amounts, references; financial personal data",
    },
    "sepa_ref": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1)",
        "mask": "",
        "never_store": False,
        "notes": "SEPA end-to-end reference — payment metadata; low PII risk alone",
    },

    # ══════════════════════════════════════════════════════════════════════
    # AVIATION
    # ══════════════════════════════════════════════════════════════════════
    "iata_ticket": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) — EU PNR Directive 2016/681",
        "mask": "001234****902",
        "never_store": False,
        "notes": "IATA ticket number — links to passenger travel record (PNR); GDPR PNR Directive applies",
    },
    "imo_number": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "IMO ship registration — public marine registry; no personal data",
    },
    "pnr_code": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) / EU PNR Directive 2016/681",
        "mask": "K7****",
        "never_store": False,
        "notes": "Passenger Name Record locator — links to full travel itinerary and personal data",
    },

    # ══════════════════════════════════════════════════════════════════════
    # WEBAUTHN — technical credentials, no PII
    # ══════════════════════════════════════════════════════════════════════
    "webauthn_credential": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "FIDO2 credential — cryptographic key material; not personal data by itself",
    },
    "fido2_assertion": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "FIDO2 authentication response — cryptographic; no PII",
    },

    # ══════════════════════════════════════════════════════════════════════
    # WALLET — Crypto (no standard PII regulation yet)
    # ══════════════════════════════════════════════════════════════════════
    "eth_wallet": {
        "regs": [],
        "req": "No binding regulation (pseudo-anonymous by design)",
        "mask": "",
        "never_store": False,
        "notes": "ETH wallet — private key must be protected as secret; address is pseudo-anonymous",
    },
    "btc_wallet": {
        "regs": [],
        "req": "No binding regulation (pseudo-anonymous by design)",
        "mask": "",
        "never_store": False,
        "notes": "BTC wallet — private key / WIF must be secret; address pseudo-anonymous",
    },
    "sol_wallet": {
        "regs": [],
        "req": "No binding regulation",
        "mask": "",
        "never_store": False,
        "notes": "Solana wallet — same as ETH/BTC wallet",
    },

    # ══════════════════════════════════════════════════════════════════════
    # AI VECTOR — pure numeric, no PII
    # ══════════════════════════════════════════════════════════════════════
    "ai_embedding":     {"regs": [], "req": "", "mask": "", "never_store": False, "notes": ""},
    "ai_vector":        {"regs": [], "req": "", "mask": "", "never_store": False, "notes": ""},
    "ai_sparse_vector": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": ""},

    # ══════════════════════════════════════════════════════════════════════
    # OIDC — authentication tokens (security-sensitive but not PII regs)
    # ══════════════════════════════════════════════════════════════════════
    "oidc_token_set": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) — JWT sub/email claims are personal data",
        "mask": "eyJ***...",
        "never_store": False,
        "notes": "OIDC token contains sub (user ID) and email — personal data under GDPR",
    },
    "jwks": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "JWK Set — public key material; no PII",
    },
    "oidc_token": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1)",
        "mask": "eyJ***...",
        "never_store": False,
        "notes": "JWT with OIDC claims — sub/email are personal data",
    },

    # ══════════════════════════════════════════════════════════════════════
    # BANK STATEMENT
    # ══════════════════════════════════════════════════════════════════════
    "mt940": {
        "regs": [KVKK, GDPR, US_GLBA],
        "req": "KVKK Madde 12 / GDPR Art 4(1) / GLBA",
        "mask": "",
        "never_store": False,
        "notes": "MT940 bank statement — contains IBAN, balances, transaction details; financial personal data",
    },
    "camt053": {
        "regs": [KVKK, GDPR, US_GLBA],
        "req": "KVKK Madde 12 / GDPR Art 4(1) / GLBA",
        "mask": "",
        "never_store": False,
        "notes": "ISO 20022 CAMT.053 statement — same as MT940; financial personal data",
    },

    # ══════════════════════════════════════════════════════════════════════
    # EDI — business documents, no direct personal PII
    # ══════════════════════════════════════════════════════════════════════
    "edi_850":        {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "EDI 850 Purchase Order — B2B; may contain company names but typically no personal PII"},
    "edifact_orders": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "UN/EDIFACT ORDERS — B2B; same as edi_850"},

    # ══════════════════════════════════════════════════════════════════════
    # EVENT SOURCING — technical, no direct PII
    # ══════════════════════════════════════════════════════════════════════
    "event_stream": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "Event stream — contains user_id (UUID); if linked to real person, GDPR Art 4 applies",
    },
    "cdc_event": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "CDC event — reflects DB changes; if table contains personal data, inherit those regulations",
    },

    # ══════════════════════════════════════════════════════════════════════
    # TELEMETRY — no PII (device/sensor data)
    # ══════════════════════════════════════════════════════════════════════
    "fdr_record":      {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Flight Data Recorder — aircraft sensor telemetry; no personal data"},
    "drone_telemetry": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Drone telemetry — device data; location data could link to operator under GDPR"},

    # ══════════════════════════════════════════════════════════════════════
    # OHLCV / MARKET DATA — no PII
    # ══════════════════════════════════════════════════════════════════════
    "ohlcv_candles": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Market candlestick data — financial instrument; no PII"},
    "market_tick":   {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Exchange trade tick — instrument price data; no PII"},

    # ══════════════════════════════════════════════════════════════════════
    # MRZ — travel document data
    # ══════════════════════════════════════════════════════════════════════
    "mrz_td3": {
        "regs": [KVKK, GDPR],
        "req": "KVKK Madde 12 / GDPR Art 4(1) — contains name, DOB, nationality, passport number",
        "mask": "P<TUR E*** <<... / ABCD1*****<...",
        "never_store": False,
        "notes": "ICAO 9303 TD3 MRZ — combines passport number, name, DOB, nationality; strong personal data",
    },
    "mrz_td1": {
        "regs": [KVKK, GDPR],
        "req": "KVKK Madde 12 / GDPR Art 4(1)",
        "mask": "",
        "never_store": False,
        "notes": "ICAO 9303 TD1 MRZ (ID card) — same as TD3 with 3-line format",
    },

    # ══════════════════════════════════════════════════════════════════════
    # TLE — satellite data, no PII
    # ══════════════════════════════════════════════════════════════════════
    "tle_satellite": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Two-Line Element — orbital parameters; no PII"},

    # ══════════════════════════════════════════════════════════════════════
    # AUTOMOTIVE — technical, no PII (VIN is in Commerce)
    # ══════════════════════════════════════════════════════════════════════
    "can_frame":     {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "CAN bus frame — vehicle network data; no PII"},
    "obd2_response": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "OBD-II response — vehicle diagnostics; no PII in isolation"},

    # ══════════════════════════════════════════════════════════════════════
    # E-INVOICE — business documents
    # ══════════════════════════════════════════════════════════════════════
    "ubl_invoice": {
        "regs": [KVKK, GDPR],
        "req": "KVKK Madde 12 (TR GIB e-fatura) / GDPR Art 4(1) (EU)",
        "mask": "",
        "never_store": False,
        "notes": "UBL invoice — may contain individual customer name and address",
    },
    "xmldsig": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "XML Digital Signature — cryptographic; no PII",
    },

    # ══════════════════════════════════════════════════════════════════════
    # GAMEDEV — no PII
    # ══════════════════════════════════════════════════════════════════════
    "quaternion":   {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "3D rotation quaternion — mathematical; no PII"},
    "navmesh_path": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "NavMesh waypoints — game AI path; no PII"},

    # ══════════════════════════════════════════════════════════════════════
    # PROMETHEUS — metrics, no PII
    # ══════════════════════════════════════════════════════════════════════
    "prometheus_metrics":   {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Prometheus metrics — system monitoring; no PII"},
    "openmetrics_snapshot": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "OpenMetrics — same as Prometheus; no PII"},

    # ══════════════════════════════════════════════════════════════════════
    # NMEA — GPS coordinates (quasi-PII when linked to person)
    # ══════════════════════════════════════════════════════════════════════
    "nmea_gpgga": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) — location data is personal data when linked to a person",
        "mask": "$GPGGA,...,**07.****,N,...",
        "never_store": False,
        "notes": "GPS fix data — location is personal data under GDPR when device owner is identifiable",
    },
    "nmea_gprmc": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) — location data",
        "mask": "",
        "never_store": False,
        "notes": "GPS recommended minimum — location data; same as nmea_gpgga",
    },

    # ══════════════════════════════════════════════════════════════════════
    # PENTEST — attack payloads (no PII by design)
    # ══════════════════════════════════════════════════════════════════════
    "jwt_attack":  {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "JWT attack payload — security testing tool; no real PII"},
    "asn1_fuzz":   {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "ASN.1 fuzz payload — security testing; no PII"},
    "reverse_regex": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Regex-generated string — pattern testing; no PII"},

    # ══════════════════════════════════════════════════════════════════════
    # CONTACT
    # ══════════════════════════════════════════════════════════════════════
    "phone": {
        "regs": [KVKK, GDPR],
        "req": "KVKK Madde 12 / GDPR Art 4(1)",
        "mask": "+90 532 *** ** 34",
        "never_store": False,
        "notes": "Phone number — direct personal identifier",
    },
    "phone_country": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "Country dial code — public information, no PII",
    },
    "phone_area": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "Area/operator code — partial phone; quasi-identifier",
    },
    "phone_local": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "Local phone number part — partial; quasi-identifier",
    },
    "email": {
        "regs": [KVKK, GDPR],
        "req": "KVKK Madde 12 / GDPR Art 4(1)",
        "mask": "al***@gmail.com",
        "never_store": False,
        "notes": "Email address — direct personal identifier",
    },
    "address_city": {
        "regs": [KVKK, GDPR],
        "req": "KVKK Madde 12 / GDPR Art 4(1)",
        "mask": "",
        "never_store": False,
        "notes": "City alone is not personal data; combined with name/DOB it becomes quasi-identifier",
    },
    "address_street": {
        "regs": [KVKK, GDPR],
        "req": "KVKK Madde 12 / GDPR Art 4(1)",
        "mask": "B***t C***esi",
        "never_store": False,
        "notes": "Street address — personal data (location identifier)",
    },
    "address_full": {
        "regs": [KVKK, GDPR],
        "req": "KVKK Madde 12 / GDPR Art 4(1)",
        "mask": "Istanbul, B*** C***.",
        "never_store": False,
        "notes": "Full address — strong personal location data",
    },
    "postalcode": {
        "regs": [KVKK, GDPR],
        "req": "KVKK Madde 12 / GDPR Art 4(1)",
        "mask": "",
        "never_store": False,
        "notes": "Postal code — location quasi-identifier; HIPAA considers ZIP ≤3 digits re-identifying",
    },
    "plate": {
        "regs": [KVKK, GDPR],
        "req": "KVKK Madde 12 / GDPR Art 4(1)",
        "mask": "34 A** 123",
        "never_store": False,
        "notes": "Vehicle license plate — links to registered owner; personal data",
    },

    # ══════════════════════════════════════════════════════════════════════
    # CORPORATE — mostly business data, low personal PII
    # ══════════════════════════════════════════════════════════════════════
    "company_name": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Company name — business entity; no personal PII unless sole trader"},
    "job_title":    {"regs": [GDPR], "req": "GDPR Art 4(1) — when linked to named employee", "mask": "", "never_store": False, "notes": "Job title alone is not PII; combined with name it is"},
    "jobtitle":     {"regs": [GDPR], "req": "GDPR Art 4(1)", "mask": "", "never_store": False, "notes": "Alias for job_title"},
    "occupation":   {"regs": [GDPR], "req": "GDPR Art 4(1)", "mask": "", "never_store": False, "notes": "Occupation — same as job_title; quasi-identifier when combined"},

    # ══════════════════════════════════════════════════════════════════════
    # HEALTH — GDPR Art 9 Special Category + HIPAA + KVKK Madde 6
    # ══════════════════════════════════════════════════════════════════════
    "bloodtype": {
        "regs": [GDPR_ART9, KVKK, US_HIPAA],
        "req": "GDPR Art 9(1) (health data) / KVKK Madde 6 (sağlık verisi) / HIPAA PHI",
        "mask": "",
        "never_store": False,
        "notes": "Blood type — health/biometric data; special category under GDPR Art 9 and KVKK Madde 6",
    },
    "blood_type": {
        "regs": [GDPR_ART9, KVKK, US_HIPAA],
        "req": "GDPR Art 9(1) / KVKK Madde 6 / HIPAA PHI",
        "mask": "",
        "never_store": False,
        "notes": "Alias for bloodtype — same regulation",
    },
    "nhs_number": {
        "regs": [UK_GDPR, US_HIPAA],
        "req": "UK GDPR Art 4(1) / NHS DSPT — NHS Number must be kept confidential",
        "mask": "943 *** ***9",
        "never_store": False,
        "notes": "NHS Number — links to patient health record; UK GDPR + NHS Data Security Policy",
    },
    "nhsnumber": {
        "regs": [UK_GDPR, US_HIPAA],
        "req": "UK GDPR Art 4(1) / NHS DSPT",
        "mask": "943 *** ***9",
        "never_store": False,
        "notes": "Alias for nhs_number",
    },
    "icd10": {
        "regs": [GDPR_ART9, KVKK, US_HIPAA],
        "req": "GDPR Art 9(1) / KVKK Madde 6 / HIPAA PHI (diagnosis code)",
        "mask": "J**.***",
        "never_store": False,
        "notes": "ICD-10 diagnosis code — health data; special category",
    },
    "bmi": {
        "regs": [GDPR_ART9, KVKK, US_HIPAA],
        "req": "GDPR Art 9(1) / KVKK Madde 6 / HIPAA PHI",
        "mask": "**.5",
        "never_store": False,
        "notes": "BMI — derived health metric; special category data",
    },
    "height": {
        "regs": [GDPR_ART9, KVKK, US_HIPAA],
        "req": "GDPR Art 9(1) / KVKK Madde 6 / HIPAA PHI (physical characteristic)",
        "mask": "*** cm",
        "never_store": False,
        "notes": "Height — biometric physical characteristic; health special category",
    },
    "weight": {
        "regs": [GDPR_ART9, KVKK, US_HIPAA],
        "req": "GDPR Art 9(1) / KVKK Madde 6 / HIPAA PHI",
        "mask": "** kg",
        "never_store": False,
        "notes": "Weight — biometric physical characteristic; health special category",
    },
    "npi": {
        "regs": [US_HIPAA],
        "req": "HIPAA — NPI is a healthcare provider identifier (not patient PII but regulated)",
        "mask": "123456****",
        "never_store": False,
        "notes": "US National Provider Identifier — HIPAA-mandated provider ID; public but regulated",
    },
    "hl7_message": {
        "regs": [GDPR_ART9, KVKK, US_HIPAA],
        "req": "GDPR Art 9(1) / KVKK Madde 6 / HIPAA PHI (HL7 patient record)",
        "mask": "",
        "never_store": False,
        "notes": "HL7 v2.5 ADT message — contains patient name, DOB, MRN; full PHI under HIPAA",
    },
    "fhir_patient": {
        "regs": [GDPR_ART9, KVKK, US_HIPAA],
        "req": "GDPR Art 9(1) / KVKK Madde 6 / HIPAA PHI (FHIR Patient resource)",
        "mask": "",
        "never_store": False,
        "notes": "FHIR R4 Patient — name, gender, birthDate, address; full PHI",
    },
    "dicom_uid": {
        "regs": [GDPR_ART9, US_HIPAA],
        "req": "GDPR Art 9(1) / HIPAA PHI (medical imaging study UID)",
        "mask": "2.25.****...",
        "never_store": False,
        "notes": "DICOM Study UID — links to medical imaging data; PHI under HIPAA",
    },

    # ══════════════════════════════════════════════════════════════════════
    # COMMERCE
    # ══════════════════════════════════════════════════════════════════════
    "currency":       {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Currency metadata — no PII"},
    "tax_rate":       {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Tax rate — no PII"},
    "taxrate":        {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Alias for tax_rate"},
    "invoice_number": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Invoice number — business metadata; no direct PII"},
    "invoicenumber":  {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Alias for invoice_number"},
    "vin": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) — VIN can identify vehicle owner via registration records",
        "mask": "WBA3A5C5X****3456",
        "never_store": False,
        "notes": "Vehicle Identification Number — can be cross-referenced to identify owner",
    },
    "vehicle": {
        "regs": [GDPR, KVKK],
        "req": "GDPR Art 4(1) / KVKK Madde 12",
        "mask": "",
        "never_store": False,
        "notes": "Vehicle record with VIN — same as VIN, plus make/model/year",
    },

    # ══════════════════════════════════════════════════════════════════════
    # META — UUIDs, tokens, technical identifiers
    # ══════════════════════════════════════════════════════════════════════
    "uuid":           {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "UUID v4 — random; no PII (but may link to user record)"},
    "requestid":      {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Request ID — technical tracing; no direct PII"},
    "correlationid":  {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Correlation ID — distributed tracing; no direct PII"},
    "sessionid":      {"regs": [GDPR], "req": "GDPR Art 4(1) — session ID can identify user", "mask": "550e***...", "never_store": False, "notes": "Session ID — online identifier; personal data under GDPR if linked to user"},
    "idempotencykey": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Idempotency key — API safety token; no direct PII"},
    "deviceid":       {"regs": [GDPR], "req": "GDPR Art 4(1) — device ID is online identifier", "mask": "550E***...", "never_store": False, "notes": "Device ID — GDPR considers device identifiers personal data"},
    "timestamp":      {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Unix timestamp — no PII"},
    "timestamp_iso":  {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "ISO timestamp — no PII"},
    "ipv4": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) / CJEU Case C-582/14 (Breyer) — dynamic IP is personal data",
        "mask": "192.168.***.***",
        "never_store": False,
        "notes": "IPv4 — CJEU ruled that dynamic IP addresses are personal data under GDPR",
    },
    "ipv6": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1)",
        "mask": "fe80:***:***:...",
        "never_store": False,
        "notes": "IPv6 — same as IPv4; often embeds MAC address (EUI-64) making it more identifying",
    },
    "browser_name":    {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Browser name — no PII alone"},
    "browser_version": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Browser version — no PII alone"},
    "browser_engine":  {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Browser engine — no PII alone"},
    "useragent": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) — user agent combined with IP is personal data",
        "mask": "",
        "never_store": False,
        "notes": "User-Agent string — fingerprinting risk; GDPR personal data when combined with IP",
    },
    "jwt":         {"regs": [GDPR], "req": "GDPR Art 4(1) — if sub/email claims are present", "mask": "eyJ***...", "never_store": False, "notes": "JWT — may contain personal claims (sub, email); treat as personal data"},
    "bearertoken": {"regs": [], "req": "", "mask": "Bearer eyJ***...", "never_store": False, "notes": "Bearer token — security credential; mask in logs"},
    "hash":        {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Hash value — no PII (but hashing PII doesn't always anonymize it)"},
    "mac_address": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) — MAC address is a device identifier (personal data)",
        "mask": "A4:C3:F0:**:**:**",
        "never_store": False,
        "notes": "MAC address — hardware identifier; GDPR considers it personal data",
    },
    "url":          {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "URL — no PII (unless contains personal parameters)"},
    "domain":       {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Domain name — no PII"},
    "color":        {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Color value — no PII"},
    "clientversion": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Software version — no PII"},
    "signature":    {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "HMAC signature — cryptographic; no PII"},
    "apppassword":  {"regs": [], "req": "", "mask": "******", "never_store": False, "notes": "One-time password — secret credential; mask in logs"},
    "transaction_id": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Transaction ID — reference number; no direct PII"},
    "public_ip":    {"regs": [GDPR], "req": "GDPR Art 4(1) — Breyer ruling", "mask": "185.***.***.**", "never_store": False, "notes": "Public IP — personal data under GDPR (Breyer)"},
    "private_ip":   {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Private IP — RFC1918 range; not routable, minimal PII risk"},
    "api_key":      {"regs": [], "req": "", "mask": "sk-***...***", "never_store": False, "notes": "API key — secret credential; mask in logs and UI"},
    "totp_code":    {"regs": [], "req": "", "mask": "******", "never_store": False, "notes": "TOTP code — time-limited OTP; secret but not personal data"},
    "webhook_signature": {"regs": [], "req": "", "mask": "sha256=****...", "never_store": False, "notes": "HMAC webhook signature — security; no PII"},

    # ══════════════════════════════════════════════════════════════════════
    # RFID / NFC / IR / WIRELESS — technical identifiers
    # ══════════════════════════════════════════════════════════════════════
    "rfid_uid": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) — RFID UID can identify card holder",
        "mask": "04:**:**:**:**:**:**",
        "never_store": False,
        "notes": "RFID UID — if linked to a person (access card), it is personal data under GDPR",
    },
    "epc":       {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "EPC — product identifier; no PII"},
    "rfid_tag":  {"regs": [GDPR], "req": "GDPR Art 4(1) — if linked to person", "mask": "", "never_store": False, "notes": "RFID tag — same as rfid_uid; personal if linked to person"},
    "nfc_uid":   {"regs": [GDPR], "req": "GDPR Art 4(1)", "mask": "04:**:**:**:**:**:**", "never_store": False, "notes": "NFC UID — same as RFID; personal if access/payment card linked to person"},
    "nfc_atqa":  {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "NFC ATQA — card type code; no PII"},
    "nfc_sak":   {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "NFC SAK — card capability byte; no PII"},
    "ndef_uri":  {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "NDEF URI — URL encoded in NFC tag; no PII unless URL contains personal data"},
    "ndef_text": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "NDEF text — arbitrary text; no PII"},
    "apdu":      {"regs": [PCI_DSS], "req": "PCI DSS — APDU may carry PAN in payment cards", "mask": "", "never_store": False, "notes": "APDU command — smart card protocol; may carry PAN if payment card"},
    "nfc_tag":   {"regs": [GDPR], "req": "GDPR Art 4(1)", "mask": "", "never_store": False, "notes": "Full NFC tag — includes UID; personal if linked to person"},
    "ir_nec":    {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "IR NEC signal — remote control; no PII"},
    "ir_rc5":    {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "IR RC5 signal — no PII"},
    "ir_pronto": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "IR Pronto hex — no PII"},
    "ir_raw":    {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "IR raw timing — no PII"},
    "mqtt_payload": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "MQTT IoT payload — device_id could link to owner under GDPR"},
    "lora_packet":  {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "LoRaWAN frame — device data; DevAddr could link to owner"},

    # ══════════════════════════════════════════════════════════════════════
    # BARCODE — product data, no PII
    # ══════════════════════════════════════════════════════════════════════
    "ean13":   {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "EAN-13 barcode — product identifier; no PII"},
    "ean8":    {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "EAN-8 barcode — product identifier; no PII"},
    "upca":    {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "UPC-A barcode — product identifier; no PII"},
    "isbn13":  {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "ISBN-13 — book identifier; no PII"},
    "isbn10":  {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "ISBN-10 — book identifier; no PII"},
    "gs1_128": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "GS1-128 — supply chain barcode; no direct PII"},

    # ══════════════════════════════════════════════════════════════════════
    # TELECOM
    # ══════════════════════════════════════════════════════════════════════
    "imei": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) / ePrivacy Directive — IMEI identifies a device (and through it, a person)",
        "mask": "490154******518",
        "never_store": False,
        "notes": "IMEI — unique device identifier; personal data under GDPR (links to subscriber)",
    },
    "imei2": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) / ePrivacy Directive",
        "mask": "49-0154-******-8",
        "never_store": False,
        "notes": "IMEI hyphenated format — same as imei",
    },
    "iccid": {
        "regs": [GDPR, KVKK],
        "req": "GDPR Art 4(1) / KVKK Madde 12 — SIM card identifier links to subscriber",
        "mask": "8990053412****8901",
        "never_store": False,
        "notes": "ICCID — SIM serial number; identifies subscriber, personal data",
    },
    "imsi": {
        "regs": [GDPR, KVKK],
        "req": "GDPR Art 4(1) / ePrivacy Directive / KVKK Madde 12",
        "mask": "2860112*****890",
        "never_store": False,
        "notes": "IMSI — subscriber identity; directly identifies a mobile subscriber",
    },
    "msisdn": {
        "regs": [GDPR, KVKK],
        "req": "GDPR Art 4(1) / KVKK Madde 12 — phone number is direct personal identifier",
        "mask": "+90 532 *** ** 67",
        "never_store": False,
        "notes": "MSISDN — international mobile phone number; direct personal identifier",
    },

    # ══════════════════════════════════════════════════════════════════════
    # CAPITAL MARKETS
    # ══════════════════════════════════════════════════════════════════════
    "isin":       {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "ISIN — financial instrument identifier; no PII"},
    "cusip":      {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "CUSIP — US security identifier; no PII"},
    "sedol":      {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "SEDOL — UK stock identifier; no PII"},
    "lei":        {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "LEI — legal entity identifier (ISO 17442); company, not personal data"},
    "fix_message": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "FIX protocol message — trading; no direct PII in mock data"},
    "psd2_consent": {
        "regs": [GDPR, UK_GDPR],
        "req": "GDPR Art 4(1) / PSD2 (EU 2015/2366) / UK Open Banking v3.1",
        "mask": "",
        "never_store": False,
        "notes": "PSD2 payment consent JWS — may contain account holder info; GDPR + PSD2 apply",
    },

    # ══════════════════════════════════════════════════════════════════════
    # CRYPTO (blockchain addresses — pseudo-anonymous)
    # ══════════════════════════════════════════════════════════════════════
    "btc_address":    {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Bitcoin address — pseudo-anonymous; may become PII if linked to identity via KYC"},
    "eth_address":    {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Ethereum address — pseudo-anonymous"},
    "crypto_address": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Generic crypto address — pseudo-anonymous"},
    "tx_hash":        {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Blockchain tx hash — public ledger data; pseudo-anonymous"},
    "block_hash":     {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Block hash — public; no PII"},
    "mnemonic": {
        "regs": [],
        "req": "No PII regulation — but treat as SECRET (controls wallet funds)",
        "mask": "abandon *** *** ... ***",
        "never_store": False,
        "notes": "BIP-39 mnemonic — not PII but controls crypto funds; treat as highest-sensitivity secret",
    },

    # ══════════════════════════════════════════════════════════════════════
    # E-COMMERCE
    # ══════════════════════════════════════════════════════════════════════
    "product_name":    {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Product name — no PII"},
    "sku":             {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "SKU — product code; no PII"},
    "order_id":        {"regs": [GDPR], "req": "GDPR Art 4(1) — order links to customer identity", "mask": "ORD-A1B2****5F6", "never_store": False, "notes": "Order ID — links to customer; personal data in e-commerce context"},
    "tracking_number": {"regs": [GDPR], "req": "GDPR Art 4(1) — tracking links to recipient address", "mask": "9400111*****7522384", "never_store": False, "notes": "Shipment tracking — links to recipient name and address; personal data"},
    "dhl_tracking":    {"regs": [GDPR], "req": "GDPR Art 4(1)", "mask": "JD12345****", "never_store": False, "notes": "DHL tracking — same as tracking_number"},
    "category":        {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Product category — no PII"},
    "rating":          {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Rating score — no PII alone"},

    # ══════════════════════════════════════════════════════════════════════
    # LOCATION
    # ══════════════════════════════════════════════════════════════════════
    "latitude": {
        "regs": [GDPR, KVKK],
        "req": "GDPR Art 4(1) — location data is personal when linked to a person",
        "mask": "39.9*****",
        "never_store": False,
        "notes": "Latitude — personal data when linked to device/person; precision-reduce for privacy",
    },
    "longitude": {
        "regs": [GDPR, KVKK],
        "req": "GDPR Art 4(1)",
        "mask": "32.8*****",
        "never_store": False,
        "notes": "Longitude — same as latitude",
    },
    "timezone":     {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Timezone — public information; no PII alone"},
    "country_code": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Country code — public; no PII alone"},
    "coordinates": {
        "regs": [GDPR, KVKK],
        "req": "GDPR Art 4(1)",
        "mask": "39.9*****,32.8*****",
        "never_store": False,
        "notes": "Lat+Lon pair — location personal data when linked to person",
    },

    # ══════════════════════════════════════════════════════════════════════
    # SOCIAL
    # ══════════════════════════════════════════════════════════════════════
    "username": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) — username is an online identifier",
        "mask": "c***ev42",
        "never_store": False,
        "notes": "Username — online identifier; personal data under GDPR",
    },
    "handle": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1)",
        "mask": "@c***ev42",
        "never_store": False,
        "notes": "Social media handle — online identifier; personal data",
    },
    "hashtag":       {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Hashtag — topic tag; no PII"},
    "bio":           {"regs": [GDPR], "req": "GDPR Art 4(1) — may contain personal information", "mask": "", "never_store": False, "notes": "Profile bio — may contain name, location, personal facts"},
    "follower_count": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Follower count — public metric; no PII"},

    # ══════════════════════════════════════════════════════════════════════
    # PAYMENTS
    # ══════════════════════════════════════════════════════════════════════
    "swift_mt103": {
        "regs": [KVKK, GDPR, US_GLBA, PCI_DSS],
        "req": "KVKK Madde 12 / GDPR Art 4(1) / GLBA / PCI DSS if card data present",
        "mask": "",
        "never_store": False,
        "notes": "MT103 transfer message — contains sender/beneficiary name, IBAN, amount; financial PII",
    },
    "pain001": {
        "regs": [GDPR, KVKK, US_GLBA],
        "req": "GDPR Art 4(1) / KVKK Madde 12 / GLBA",
        "mask": "",
        "never_store": False,
        "notes": "ISO 20022 PAIN.001 — credit transfer initiation; contains debtor/creditor personal data",
    },
    "nacha_ach": {
        "regs": [US_GLBA, US_PRIVACY],
        "req": "GLBA / Privacy Act — ACH file contains account numbers and names",
        "mask": "",
        "never_store": False,
        "notes": "NACHA ACH file — bank account numbers + names; regulated under GLBA",
    },
    "sepa_mandate": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) — mandate contains debtor name and IBAN",
        "mask": "",
        "never_store": False,
        "notes": "SEPA Direct Debit Mandate — creditor ID + debtor IBAN; personal financial data",
    },
    "fedwire": {
        "regs": [US_GLBA],
        "req": "GLBA — Fedwire message contains account and routing numbers",
        "mask": "",
        "never_store": False,
        "notes": "Fedwire transfer message — routing + account numbers; GLBA regulated",
    },

    # ══════════════════════════════════════════════════════════════════════
    # CARD PHYSICS — PCI DSS Scope
    # ══════════════════════════════════════════════════════════════════════
    "iso8583_auth_request": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1 Req 3.3.1 / Req 3.4.1 — contains PAN (DE002)",
        "mask": "DE002: 4532 01** **** 9012",
        "never_store": False,
        "notes": "ISO 8583 0100 — PAN in DE002 must be masked per Req 3.4.1; in-flight data in-scope",
    },
    "iso8583_auth_response": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1 Req 3.4.1",
        "mask": "DE002: 4532 01** **** 9012",
        "never_store": False,
        "notes": "ISO 8583 0110 — contains PAN in DE002; mask for display",
    },
    "iso8583_reversal": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1 Req 3.4.1",
        "mask": "DE002: 4532 01** **** 9012",
        "never_store": False,
        "notes": "ISO 8583 0400 reversal — contains PAN; PCI scope",
    },
    "emv_arqc": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1 — EMV cryptogram (derived from PAN/session data)",
        "mask": "A1B2C3D4****0718",
        "never_store": False,
        "notes": "EMV ARQC — cryptogram derived from card data; PCI in-scope",
    },
    "emv_atc": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1",
        "mask": "00**",
        "never_store": False,
        "notes": "EMV ATC — application transaction counter; PCI in-scope",
    },
    "emv_iad": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1",
        "mask": "0A02102B****ABCD1234",
        "never_store": False,
        "notes": "EMV IAD — issuer application data; PCI in-scope",
    },
    "atm_session": {
        "regs": [PCI_DSS, KVKK, GDPR],
        "req": "PCI DSS 4.0.1 Req 3.4.1 / KVKK Madde 12 / GDPR Art 4(1)",
        "mask": "masked_pan: 4532 **** **** 9012",
        "never_store": False,
        "notes": "ATM session JSON — already contains masked_pan; PCI + KVKK/GDPR apply",
    },
    "pos_receipt": {
        "regs": [PCI_DSS, KVKK, GDPR],
        "req": "PCI DSS 4.0.1 Req 3.4.1 — receipt must show only last 4 digits",
        "mask": "Card: **** **** **** 9012",
        "never_store": False,
        "notes": "POS receipt — cardholder copy shows last 4 only per PCI DSS Req 3.4.1",
    },

    # ══════════════════════════════════════════════════════════════════════
    # IntlIDs — country-specific
    # ══════════════════════════════════════════════════════════════════════

    # Brazil
    "br_cpf": {
        "regs": [LGPD],
        "req": "LGPD (Lei 13.709/2018) Art 46 — CPF is personal identifier",
        "mask": "123.***.***-09",
        "never_store": False,
        "notes": "Brazilian CPF — national personal identifier; LGPD applies",
    },
    "br_cnpj": {
        "regs": [LGPD],
        "req": "LGPD Art 46 — CNPJ is business identifier (personal if sole trader)",
        "mask": "11.222.***/**01-81",
        "never_store": False,
        "notes": "Brazilian CNPJ — company identifier; personal data if sole proprietor",
    },

    # India
    "in_pan": {
        "regs": [PDPA_IN],
        "req": "Income Tax Act 1961 + PDPB draft — PAN is personal financial identifier",
        "mask": "ABCDE****F",
        "never_store": False,
        "notes": "Indian PAN — tax identifier; personal data; PDPB will regulate",
    },
    "in_aadhaar": {
        "regs": [PDPA_IN],
        "req": "Aadhaar Act 2016 Sec 29 — must be masked as XXXX XXXX 1234",
        "mask": "XXXX XXXX 2346",
        "never_store": False,
        "notes": "Indian Aadhaar — biometric-linked; UIDAI requires masking to last 4 digits",
    },
    "in_gstin": {
        "regs": [PDPA_IN],
        "req": "PDPB draft — GSTIN links business to PAN (personal identifier chain)",
        "mask": "29ABCDE****1Z5",
        "never_store": False,
        "notes": "Indian GSTIN — GST registration; embeds PAN; personal data chain",
    },
    "in_epic": {
        "regs": [PDPA_IN],
        "req": "PDPB draft — Voter ID is personal identifier",
        "mask": "ABC*******",
        "never_store": False,
        "notes": "Indian Voter ID (EPIC) — personal government identifier",
    },

    # China
    "cn_ric": {
        "regs": [PIPL],
        "req": "PIPL (2021) Art 28 — RIC is sensitive personal information",
        "mask": "110000******1234",
        "never_store": False,
        "notes": "Chinese Resident ID — contains DOB and gender; PIPL sensitive personal data",
    },

    # Mexico
    "mx_curp": {
        "regs": [LFPDPPP],
        "req": "LFPDPPP (2010) Art 16 — CURP is personal identifier",
        "mask": "BOXW******HNERXN09",
        "never_store": False,
        "notes": "Mexican CURP — national personal identifier with encoded DOB and gender",
    },
    "mx_rfc": {
        "regs": [LFPDPPP],
        "req": "LFPDPPP Art 16",
        "mask": "ABCD82****ABC",
        "never_store": False,
        "notes": "Mexican RFC — tax registration; personal or business identifier",
    },

    # Italy
    "it_codicefiscale": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) — Codice Fiscale is personal identifier with encoded DOB",
        "mask": "RSSM**80A01H501U",
        "never_store": False,
        "notes": "Italian Codice Fiscale — encodes surname, name, DOB, birthplace; strong personal data",
    },

    # Spain
    "es_dni": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) — DNI is national ID; Spain Organic Law 3/2018",
        "mask": "12****78Z",
        "never_store": False,
        "notes": "Spanish DNI — national personal identifier; GDPR + Spain LOPDGDD",
    },
    "es_nie": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) / Spain LOPDGDD",
        "mask": "X12****7L",
        "never_store": False,
        "notes": "Spanish NIE — foreigner ID; same as DNI for personal data",
    },
    "es_ccc": {
        "regs": [GDPR, US_GLBA],
        "req": "GDPR Art 4(1) — Spanish bank account number",
        "mask": "2100-0418-**-**0051332",
        "never_store": False,
        "notes": "Spanish CCC — bank account; personal financial data",
    },

    # Germany
    "de_idnr": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) / German BDSG §12 — IdNr is unique personal tax ID",
        "mask": "024762****8",
        "never_store": False,
        "notes": "German Steuerliche Identifikationsnummer — permanent personal tax ID",
    },
    "de_stnr": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) / German BDSG",
        "mask": "21/815/****5",
        "never_store": False,
        "notes": "German Steuernummer — tax authority assigned; personal identifier",
    },

    # Pakistan
    "pk_cnic": {
        "regs": [],
        "req": "Pakistan PECA 2016 / proposed PDPB",
        "mask": "35202-123****-1",
        "never_store": False,
        "notes": "Pakistani CNIC — national ID; Pakistan data protection under PECA/PDPB",
    },

    # Japan
    "jp_cn": {
        "regs": [],
        "req": "Japan APPI (Act on the Protection of Personal Information)",
        "mask": "1234567****23",
        "never_store": False,
        "notes": "Japanese Corporate Number — public company ID; low individual PII risk",
    },
    "jp_in": {
        "regs": [],
        "req": "Japan My Number Act (Act No. 27 of 2013) — special care required",
        "mask": "123456******",
        "never_store": False,
        "notes": "Japanese My Number — individual number; My Number Act strictly limits use",
    },

    # South Korea
    "kr_rrn": {
        "regs": [],
        "req": "Korea PIPA (Personal Information Protection Act) — RRN restricted since 2014",
        "mask": "700101-1*****9",
        "never_store": False,
        "notes": "Korean RRN — encodes DOB and gender; PIPA restricts collection/use",
    },
    "kr_brn": {
        "regs": [],
        "req": "Korea PIPA",
        "mask": "123-45-*****0",
        "never_store": False,
        "notes": "Korean Business Registration Number — company identifier",
    },

    # Netherlands
    "nl_bsn": {
        "regs": [GDPR],
        "req": "GDPR Art 87 / Dutch Wbp successor (AVG) — BSN highly protected",
        "mask": "12345****2",
        "never_store": False,
        "notes": "Dutch BSN — citizen service number; GDPR Art 87 requires specific authorisation to process",
    },

    # Poland
    "pl_pesel": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) / Poland UODO — PESEL encodes DOB and gender",
        "mask": "700101****5",
        "never_store": False,
        "notes": "Polish PESEL — national ID with encoded DOB; strong personal identifier",
    },

    # Sweden
    "se_personnummer": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) / Sweden DPIA guidelines",
        "mask": "19700101-****",
        "never_store": False,
        "notes": "Swedish Personnummer — national ID; DOB embedded; personal data",
    },

    # Denmark
    "dk_cpr": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) / Danish Dataprotektionsloven §11",
        "mask": "010170-****",
        "never_store": False,
        "notes": "Danish CPR — encodes DOB; §11 restricts processing",
    },

    # Finland
    "fi_hetu": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) / Finnish Data Protection Act",
        "mask": "010170-***A",
        "never_store": False,
        "notes": "Finnish HETU — national ID with DOB; personal data",
    },

    # Norway
    "no_fodselsnummer": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) / Norway Personopplysningsloven",
        "mask": "010170*****",
        "never_store": False,
        "notes": "Norwegian Fødselsnummer — national ID with DOB; personal data",
    },

    # Australia
    "au_abn": {
        "regs": [],
        "req": "Australia Privacy Act 1988 — ABN is business identifier (personal for sole traders)",
        "mask": "51824*****6",
        "never_store": False,
        "notes": "Australian ABN — business number; personal if sole trader",
    },
    "au_tfn": {
        "regs": [],
        "req": "Australia Privacy Act 1988 Part IIIA — TFN is sensitive personal data",
        "mask": "123*****2",
        "never_store": False,
        "notes": "Australian TFN — Tax File Number; Privacy Act Part IIIA gives extra protection",
    },
    "au_acn": {
        "regs": [],
        "req": "Australia Privacy Act 1988",
        "mask": "004*****6",
        "never_store": False,
        "notes": "Australian ACN — company number; public ASIC register",
    },

    # Malaysia
    "my_nric": {
        "regs": [],
        "req": "Malaysia PDPA 2010 — NRIC encodes DOB and birth state",
        "mask": "701231-**-5678",
        "never_store": False,
        "notes": "Malaysian NRIC — national ID with encoded DOB and birth state; PDPA regulated",
    },

    # Thailand
    "th_pin": {
        "regs": [],
        "req": "Thailand PDPA 2019 (B.E. 2562)",
        "mask": "123456****234",
        "never_store": False,
        "notes": "Thai personal ID — 13-digit national ID; Thailand PDPA applies",
    },
    "th_tin": {
        "regs": [],
        "req": "Thailand PDPA 2019",
        "mask": "123456****234",
        "never_store": False,
        "notes": "Thai TIN — same format as personal ID; business or personal",
    },

    # Singapore
    "sg_uen": {
        "regs": [],
        "req": "Singapore PDPA 2012",
        "mask": "12345***X",
        "never_store": False,
        "notes": "Singapore UEN — business entity number; PDPA applies if linked to individual",
    },

    # South Africa
    "za_idnr": {
        "regs": [],
        "req": "South Africa POPIA 2013 — ID embeds DOB and gender",
        "mask": "700101****081",
        "never_store": False,
        "notes": "South African ID — contains DOB and gender; POPIA regulated",
    },

    # Canada
    "ca_bn": {
        "regs": [],
        "req": "Canada PIPEDA — business number; personal if sole proprietor",
        "mask": "12345****2",
        "never_store": False,
        "notes": "Canadian Business Number — PIPEDA applies for individual proprietors",
    },

    # New Zealand
    "nz_ird": {
        "regs": [],
        "req": "New Zealand Privacy Act 2020 — IRD is personal tax identifier",
        "mask": "490***268",
        "never_store": False,
        "notes": "New Zealand IRD number — tax identifier; Privacy Act 2020",
    },

    # Argentina
    "ar_cuit": {
        "regs": [],
        "req": "Argentina PDPA (Law 25.326) — CUIT is personal/business identifier",
        "mask": "20-1234****-9",
        "never_store": False,
        "notes": "Argentinian CUIT — tax identifier; Law 25.326 personal data",
    },
    "ar_dni": {
        "regs": [],
        "req": "Argentina PDPA (Law 25.326) — DNI is national personal ID",
        "mask": "12****78",
        "never_store": False,
        "notes": "Argentinian DNI — national personal identifier",
    },

    # Chile
    "cl_rut": {
        "regs": [],
        "req": "Chile Law 19.628 (Datos Personales) — RUT is national identifier",
        "mask": "12.345.***-9",
        "never_store": False,
        "notes": "Chilean RUT — national tax/ID number; Law 19.628",
    },

    # Colombia
    "co_nit": {
        "regs": [],
        "req": "Colombia Law 1581/2012 (Habeas Data) — NIT is business/personal identifier",
        "mask": "800123****5",
        "never_store": False,
        "notes": "Colombian NIT — tax identifier; Law 1581 personal data",
    },

    # Israel
    "il_idnr": {
        "regs": [],
        "req": "Israel Privacy Protection Law 1981 — ID is personal identifier",
        "mask": "12345****2",
        "never_store": False,
        "notes": "Israeli ID number — national personal identifier",
    },

    # Romania
    "ro_cnp": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) / Romania Law 677/2001 — CNP encodes DOB and gender",
        "mask": "1700101****56",
        "never_store": False,
        "notes": "Romanian CNP — national ID with encoded DOB and gender; GDPR applies",
    },
    "ro_cui": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1)",
        "mask": "RO123****85",
        "never_store": False,
        "notes": "Romanian CUI — company identifier; GDPR if linked to sole trader",
    },

    # Croatia
    "hr_oib": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) / Croatia OIB Act — OIB is permanent personal identifier",
        "mask": "12345****01",
        "never_store": False,
        "notes": "Croatian OIB — personal identifier used for all government/financial purposes",
    },

    # Bulgaria
    "bg_egn": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) — EGN encodes DOB and gender",
        "mask": "700101****",
        "never_store": False,
        "notes": "Bulgarian EGN — national ID with encoded DOB; GDPR personal data",
    },

    # Lithuania
    "lt_asmens": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) / Lithuania Personal Data Protection Law",
        "mask": "3800101****",
        "never_store": False,
        "notes": "Lithuanian personal code — same algorithm as Estonian IK; GDPR applies",
    },

    # Estonia
    "ee_ik": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) / Estonia Isikuandmete kaitse seadus",
        "mask": "3800101****",
        "never_store": False,
        "notes": "Estonian Isikukood — personal code with DOB/gender prefix; GDPR applies",
    },

    # Portugal
    "pt_cc": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) / Portugal Lei 58/2019",
        "mask": "12345*** 0 **4",
        "never_store": False,
        "notes": "Portuguese Citizen Card number — national personal identifier; GDPR + Lei 58/2019",
    },

    # Egypt
    "eg_tn": {
        "regs": [],
        "req": "Egypt Data Protection Law 151/2020 — TN is business identifier",
        "mask": "12345****",
        "never_store": False,
        "notes": "Egyptian Tax Registration Number — business identifier; Law 151/2020",
    },

    # ══════════════════════════════════════════════════════════════════════
    # CLI COMMANDS — not data types; no PII regulation
    # ══════════════════════════════════════════════════════════════════════
    "bulk":     {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "CLI command — generates N values of any type; inherits regulation of the target type"},
    "template": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "CLI command — combines types into a record; inherits regulations of constituent types"},
    "export":   {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "CLI command — bulk export; inherits regulations of constituent types"},
    "profile":  {"regs": [KVKK, GDPR], "req": "KVKK Madde 12 / GDPR Art 4(1) — composite personal record", "mask": "", "never_store": False, "notes": "Person profile (name+ID+phone+email+address) — composite personal data record"},
    "company":  {"regs": [KVKK, GDPR], "req": "KVKK Madde 12 / GDPR Art 4(1)", "mask": "", "never_store": False, "notes": "Company profile (name+taxID+IBAN) — may contain personal data if sole trader"},
}


def get_regulations(type_name: str) -> list[str]:
    """Return list of regulation constants for a given generator type."""
    entry = REGULATION_TAGS.get(type_name)
    return entry["regs"] if entry else []


def is_pci_scope(type_name: str) -> bool:
    """Return True if the type falls within PCI DSS scope."""
    return PCI_DSS in get_regulations(type_name)


def must_never_store(type_name: str) -> bool:
    """Return True if type is PCI DSS Sensitive Authentication Data (SAD)."""
    entry = REGULATION_TAGS.get(type_name)
    return bool(entry and entry.get("never_store"))


def mask_format(type_name: str) -> str:
    """Return the recommended masked display format for a type, or '' if N/A."""
    entry = REGULATION_TAGS.get(type_name)
    return entry["mask"] if entry else ""


def is_health_data(type_name: str) -> bool:
    """Return True if the type is health/special-category data."""
    return GDPR_ART9 in get_regulations(type_name)
