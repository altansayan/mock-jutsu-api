"""
Mock Jutsu â€” Regulation Reference Map
======================================
Maps every generator type to the data-protection regulations that govern it,
together with the masking format required by each regulation.

IMPORTANT: Mock Jutsu generates *synthetic* test data â€” no real PII.
           This file exists so the --mask flag can produce output whose
           format matches what real systems are permitted to display.

â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
  REGULATION TEXTS
â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

â”€â”€ PCI DSS v4.0.1 â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

  Requirement 3.3.1 (Sensitive Authentication Data â€” SAD):
    "SAD must not be retained after authorization, even if encrypted.
     SAD includes: full track data (magnetic stripe or chip equivalent),
     card verification codes/values (CVV2, CVC2, CAV2, CID), and PINs/PIN blocks."

  Requirement 3.4.1 (PAN Display Masking):
    "The PAN is masked when displayed (the BIN and last four digits are the
     maximum number of digits to be displayed), such that only personnel with
     a legitimate business need can see more than the BIN/last four digits
     of the PAN."
    â†’ BIN = first 6 digits (or first 8 for extended BIN networks).
    â†’ Masked format: 453201** **** 9012  (first 6 + ****** + last 4)

  Requirement 3.5.1 (PAN Storage):
    "PAN is secured with strong cryptography if stored."

  Requirement 3.3.2 (SAD in pre-authorisation):
    "All SAD collected prior to completion of authorisation is encrypted
     using strong cryptography."

â”€â”€ KVKK (KiÅŸisel Verilerin KorunmasÄ± Kanunu) â€” Law No. 6698 â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

  Madde 12 â€” Veri gÃ¼venliÄŸine iliÅŸkin yÃ¼kÃ¼mlÃ¼lÃ¼kler:
    "Veri sorumlusu; kiÅŸisel verilerin hukuka aykÄ±rÄ± olarak iÅŸlenmesini
     Ã¶nlemek, kiÅŸisel verilere hukuka aykÄ±rÄ± olarak eriÅŸilmesini Ã¶nlemek,
     kiÅŸisel verilerin muhafazasÄ±nÄ± saÄŸlamak amacÄ±yla uygun gÃ¼venlik
     dÃ¼zeyini temin etmeye yÃ¶nelik gerekli her tÃ¼rlÃ¼ teknik ve idari
     tedbirleri almak zorundadÄ±r."

  KVKK KiÅŸisel Veri GÃ¼venliÄŸi Rehberi â€” Maskeleme Ã–rneÄŸi:
    TCKN maskesi: "25*******10"  (ilk 2 hane + son 2 hane gÃ¶rÃ¼nÃ¼r)
    Telefon:      "+90 532 *** ** 34"
    E-posta:      "al***@gmail.com"

  Ã–zel nitelikli kiÅŸisel veriler (Madde 6):
    SaÄŸlÄ±k, biyometrik, cezai sicil, din, siyasi gÃ¶rÃ¼ÅŸ, etnik kÃ¶ken,
    sendika Ã¼yeliÄŸi, cinsel yaÅŸam verisi â€” iÅŸlenmesi kural olarak yasaktÄ±r.

â”€â”€ GDPR (EU General Data Protection Regulation â€” 2016/679) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

  Article 4(1) â€” Personal Data Definition:
    "'personal data' means any information relating to an identified or
     identifiable natural person; an identifiable natural person is one who
     can be identified, directly or indirectly, in particular by reference to
     an identifier such as a name, an identification number, location data,
     an online identifier or to one or more factors specific to the physical,
     physiological, genetic, mental, economic, cultural or social identity
     of that natural person."

  Article 9(1) â€” Special Categories (prohibited without explicit consent):
    "Processing of personal data revealing racial or ethnic origin, political
     opinions, religious or philosophical beliefs, or trade union membership,
     and the processing of genetic data, biometric data for the purpose of
     uniquely identifying a natural person, data concerning health or data
     concerning a natural person's sex life or sexual orientation
     shall be prohibited."

  Article 25 â€” Data Protection by Design and by Default:
    Controllers must implement pseudonymisation and data minimisation.

  Recital 26 â€” Pseudonymisation:
    "Personal data which have undergone pseudonymisation, which could be
     attributed to a natural person by the use of additional information
     should be considered to be information on an identifiable natural person."

â”€â”€ UK GDPR + Data Protection Act 2018 (DPA 2018) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

  UK GDPR mirrors EU GDPR post-Brexit.
  DPA 2018 Schedule 1 Part 1 â€” additional lawful bases for special categories.

  NIN (National Insurance Number):
    HM Revenue & Customs â€” must not be shared beyond tax/benefits purposes.
    Guidance: "You must keep your NIN secure."

  NHS Number:
    NHS Data Security and Protection Toolkit (DSPT) mandates
    masking in non-clinical contexts (e.g., NHS 943 476 5919 â†’ 943 *** ****)

â”€â”€ US Laws â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

  Privacy Act of 1974 (5 U.S.C. Â§ 552a):
    Federal agencies must safeguard SSN and other personally identifiable
    information (PII) held in systems of records.

  IRS Revenue Procedure 2007-40 / Publication 1075:
    SSN truncation on official documents:
    "Truncated SSN (TSSN): ***-**-1234 (last four visible)"

  GLBA (Gramm-Leach-Bliley Act, 15 U.S.C. Â§ 6801):
    Financial institutions must protect customers' nonpublic personal
    information including bank account numbers, routing numbers, and
    credit card numbers.

  HIPAA Privacy Rule (45 CFR Â§164.514):
    Protected Health Information (PHI) â€” 18 identifiers must be de-identified.
    Includes: names, geographic data, dates (except year), phone, fax,
    email, SSN, medical record numbers, health plan numbers, account numbers,
    certificate/license numbers, biometric identifiers, NPI.

â”€â”€ LGPD (Lei Geral de ProteÃ§Ã£o de Dados â€” Brazil, Law No. 13.709/2018) â”€â”€

  Art. 46: Controllers must adopt technical and administrative measures
    to protect personal data from unauthorized access.
  CPF and CNPJ are treated as personal/business identifiers.
  Sensitive data (Art. 11) includes: racial/ethnic origin, religious beliefs,
    health data, genetic/biometric data, political opinions.

â”€â”€ PDPA / Aadhaar Act (India) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

  Aadhaar (Targeted Delivery...) Act 2016, Section 29:
    "No Aadhaar number or biometric information collected shall be used
     for any purpose other than the purposes specified in this Act."
  UIDAI guidelines: Aadhaar must be masked as "XXXX XXXX 1234" (last 4 visible).

  Personal Data Protection Bill (PDPB) â€” draft, under review as of 2025.

â”€â”€ PIPL (Personal Information Protection Law â€” China, 2021) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

  Article 28 â€” Sensitive Personal Information:
    Includes biometrics, religious beliefs, special identity, medical health,
    financial accounts, location tracking, and minors' personal information.
  RIC (Resident Identity Card) â€” considered sensitive; processing requires
    separate consent.

â”€â”€ LFPDPPP (Ley Federal de ProtecciÃ³n de Datos Personales â€” Mexico, 2010) â”€

  Article 16 â€” Privacy Notice:
    Data subjects must be informed of data collection via privacy notice.
  CURP and RFC are national identifiers â€” treated as personal data.

â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
"""

# â”€â”€ Regulation constants â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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

# â”€â”€ REGULATION_TAGS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Schema per entry:
#   regs        : list[str]  â€” applicable regulation constants (may be empty)
#   req         : str        â€” specific article / requirement reference
#   mask        : str        â€” masked display example ("" if not applicable)
#   never_store : bool       â€” True = must NEVER be stored even in encrypted form (PCI SAD)
#   notes       : str        â€” brief note on why this type is regulated
#
REGULATION_TAGS: dict[str, dict] = {

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # IDENTITY â€” Turkish
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "tckn": {
        "regs": [KVKK],
        "req": "KVKK Madde 12 / KVKK Rehberi",
        "mask": "25*******10",
        "never_store": False,
        "notes": "TÃ¼rk Cumhuriyeti Kimlik NumarasÄ± â€” kiÅŸisel veri (KVKK Madde 6 kapsamÄ±nda deÄŸil ama Madde 12 gÃ¼venlik yÃ¼kÃ¼mlÃ¼lÃ¼ÄŸÃ¼ var)",
    },
    "tckn_masked": {
        "regs": [KVKK],
        "req": "KVKK Madde 12 / KVKK Rehberi",
        "mask": "***123456**",
        "never_store": False,
        "notes": "Zaten maskeli TCKN â€” privacy-safe display format",
    },
    "ykn": {
        "regs": [KVKK],
        "req": "KVKK Madde 12",
        "mask": "99*******78",
        "never_store": False,
        "notes": "YabancÄ± Kimlik NumarasÄ± â€” yabancÄ± uyruklu kiÅŸisel veri",
    },
    "vkn": {
        "regs": [KVKK],
        "req": "KVKK Madde 12",
        "mask": "123****890",
        "never_store": False,
        "notes": "Vergi Kimlik NumarasÄ± â€” tÃ¼zel veya gerÃ§ek kiÅŸi tanÄ±mlayÄ±cÄ±",
    },
    "sgk": {
        "regs": [KVKK],
        "req": "KVKK Madde 12",
        "mask": "34-*******-1.01-02",
        "never_store": False,
        "notes": "SGK Sicil NumarasÄ± â€” Ã§alÄ±ÅŸan kiÅŸisel verisi",
    },
    "mersis": {
        "regs": [KVKK],
        "req": "KVKK Madde 12",
        "mask": "",
        "never_store": False,
        "notes": "MERSIS â€” tÃ¼zel kiÅŸi tanÄ±mlayÄ±cÄ±; bireysel gizlilik riski dÃ¼ÅŸÃ¼k",
    },

    # â”€â”€ Generic / locale-based identity â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "nationalid": {
        "regs": [KVKK, GDPR],
        "req": "KVKK Madde 12 (TR) / GDPR Art 4(1) (EU)",
        "mask": "**...**XX",
        "never_store": False,
        "notes": "Locale-specific national ID â€” governed by the country's own data-protection law",
    },
    "taxid": {
        "regs": [KVKK, GDPR],
        "req": "KVKK Madde 12 (TR) / GDPR Art 4(1) (EU)",
        "mask": "***...***",
        "never_store": False,
        "notes": "Generic tax ID â€” personal identifier; mask in non-tax contexts",
    },
    "employer_id": {
        "regs": [KVKK, GDPR],
        "req": "KVKK Madde 12 (TR) / GDPR Art 4(1) (EU)",
        "mask": "",
        "never_store": False,
        "notes": "Employer registration â€” usually business identifier; low individual privacy risk",
    },
    "insurance_id": {
        "regs": [KVKK, GDPR, GDPR_ART9],
        "req": "KVKK Madde 6 (TR) / GDPR Art 9(1) (EU)",
        "mask": "**...**XX",
        "never_store": False,
        "notes": "Social insurance ID can link to health/disability data â€” special category risk",
    },

    # â”€â”€ US Identity â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "ssn": {
        "regs": [US_PRIVACY],
        "req": "Privacy Act 1974 / IRS Rev. Proc. 2007-40 (truncation: ***-**-1234)",
        "mask": "***-**-6789",
        "never_store": False,
        "notes": "US Social Security Number â€” must be masked to last 4 digits on documents",
    },
    "ssn_masked": {
        "regs": [US_PRIVACY],
        "req": "Privacy Act 1974 / IRS Rev. Proc. 2007-40",
        "mask": "***-**-6789",
        "never_store": False,
        "notes": "Already-masked SSN â€” privacy-safe display format",
    },
    "ein": {
        "regs": [US_PRIVACY, US_GLBA],
        "req": "GLBA / IRS guidelines",
        "mask": "**-*456789",
        "never_store": False,
        "notes": "Employer ID Number â€” business identifier but also used for identity theft",
    },

    # â”€â”€ UK Identity â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "nin": {
        "regs": [UK_GDPR],
        "req": "UK GDPR Art 4(1) / HMRC NIN Security Guidance",
        "mask": "AB ** ** ** C",
        "never_store": False,
        "notes": "UK National Insurance Number â€” must be kept secure; share only for tax/benefits",
    },
    "utr": {
        "regs": [UK_GDPR],
        "req": "UK GDPR Art 4(1) / HMRC guidelines",
        "mask": "12345*****",
        "never_store": False,
        "notes": "Unique Taxpayer Reference â€” personal identifier, HMRC confidential",
    },
    "crn": {
        "regs": [UK_GDPR],
        "req": "UK GDPR Art 4(1)",
        "mask": "",
        "never_store": False,
        "notes": "Company Registration Number â€” public register data; low privacy risk",
    },
    "paye": {
        "regs": [UK_GDPR],
        "req": "UK GDPR Art 4(1) / HMRC PAYE guidelines",
        "mask": "123/**4567",
        "never_store": False,
        "notes": "UK PAYE reference â€” employer/employee tax reference; keep confidential",
    },

    # â”€â”€ German Identity â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "ust_id": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1)",
        "mask": "",
        "never_store": False,
        "notes": "German VAT ID â€” business identifier; publicly verifiable via VIES",
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
        "notes": "German Handelsregister â€” public commercial register entry",
    },
    "rvn": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) â€” personal identifier in German pension system",
        "mask": "65 ****92 W ****",
        "never_store": False,
        "notes": "Rentenversicherungsnummer â€” personal pension ID; keep confidential",
    },

    # â”€â”€ French Identity â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "siren": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1)",
        "mask": "",
        "never_store": False,
        "notes": "French SIREN â€” business entity; public INSEE registry",
    },
    "siret": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1)",
        "mask": "",
        "never_store": False,
        "notes": "French SIRET â€” establishment code; public INSEE registry",
    },
    "tva": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1)",
        "mask": "",
        "never_store": False,
        "notes": "French VAT number â€” business identifier; publicly verifiable",
    },

    # â”€â”€ Russian Identity â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "inn": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) (if EU data subjects involved)",
        "mask": "770*****93",
        "never_store": False,
        "notes": "Russian INN â€” personal/business tax identifier",
    },
    "inn_individual": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1)",
        "mask": "770*****93",
        "never_store": False,
        "notes": "Russian individual INN â€” personal tax ID",
    },
    "snils": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1)",
        "mask": "112-***-445 **",
        "never_store": False,
        "notes": "Russian SNILS â€” pension insurance personal account number",
    },
    "kpp": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1)",
        "mask": "",
        "never_store": False,
        "notes": "KPP â€” reason code for tax registration; business/entity identifier",
    },
    "ogrn": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1)",
        "mask": "",
        "never_store": False,
        "notes": "OGRN â€” Russian primary state registration number; legal entity",
    },

    # â”€â”€ VAT Number â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "vat_number": {
        "regs": [GDPR, KVKK],
        "req": "GDPR Art 4(1) (EU) / KVKK Madde 12 (TR)",
        "mask": "",
        "never_store": False,
        "notes": "EU/Global VAT number â€” business identifier; publicly verifiable via VIES",
    },

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # NAME
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "firstname": {
        "regs": [KVKK, GDPR],
        "req": "KVKK Madde 12 (TR) / GDPR Art 4(1) (EU)",
        "mask": "E***",
        "never_store": False,
        "notes": "Personal name â€” direct identifier",
    },
    "lastname": {
        "regs": [KVKK, GDPR],
        "req": "KVKK Madde 12 (TR) / GDPR Art 4(1) (EU)",
        "mask": "Y***az",
        "never_store": False,
        "notes": "Personal surname â€” direct identifier",
    },
    "fullname": {
        "regs": [KVKK, GDPR],
        "req": "KVKK Madde 12 (TR) / GDPR Art 4(1) (EU)",
        "mask": "E*** K***",
        "never_store": False,
        "notes": "Full name â€” direct personal identifier",
    },
    "patronymic": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1)",
        "mask": "I***vich",
        "never_store": False,
        "notes": "Russian-style patronymic â€” personal identifier",
    },

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # DOCUMENT
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "passport": {
        "regs": [KVKK, GDPR],
        "req": "KVKK Madde 12 / GDPR Art 4(1)",
        "mask": "P1****67",
        "never_store": False,
        "notes": "Passport number â€” travel document; direct personal identifier",
    },
    "license": {
        "regs": [KVKK, GDPR],
        "req": "KVKK Madde 12 / GDPR Art 4(1)",
        "mask": "6****1",
        "never_store": False,
        "notes": "Driver's license number â€” government-issued personal identifier",
    },

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # DEMOGRAPHIC
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
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
        "notes": "Gender â€” personal attribute; quasi-identifier",
    },
    "birthdate": {
        "regs": [KVKK, GDPR],
        "req": "KVKK Madde 12 / GDPR Art 4(1)",
        "mask": "1990-**-**",
        "never_store": False,
        "notes": "Date of birth â€” strong quasi-identifier; combined with name or ZIP uniquely identifies most people",
    },
    "nationality": {
        "regs": [KVKK, GDPR],
        "req": "KVKK Madde 12 / GDPR Art 4(1)",
        "mask": "",
        "never_store": False,
        "notes": "Nationality â€” can reveal ethnic/national origin (GDPR quasi-Art9 risk)",
    },

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # FINANCIAL â€” Payment Cards (PCI DSS Scope)
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "cardnum": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1 Req 3.4.1",
        "mask": "4532 01** **** 9012",
        "never_store": False,
        "notes": "Primary Account Number (PAN) â€” mask all but first 6 (BIN) and last 4 digits",
    },
    "cvv3": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1 Req 3.3.1 â€” SAD",
        "mask": "***",
        "never_store": True,
        "notes": "CVV/CVC â€” Sensitive Authentication Data; MUST NOT be stored after authorization under any circumstances",
    },
    "cvv4": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1 Req 3.3.1 â€” SAD",
        "mask": "****",
        "never_store": True,
        "notes": "4-digit CVV (Amex CID) â€” SAD; same prohibition as cvv3",
    },
    "pin": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1 Req 3.3.1 â€” SAD",
        "mask": "****",
        "never_store": True,
        "notes": "PIN â€” SAD; must never be stored, logged, or displayed after authorization",
    },
    "cardtype": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "Card type (Credit/Debit) â€” not PII alone; no direct regulation",
    },
    "cardstatus": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "Card status flag â€” not PII alone",
    },
    "cardcategory": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "Card level/category â€” not PII alone",
    },
    "cardowner": {
        "regs": [PCI_DSS, KVKK, GDPR],
        "req": "PCI DSS 4.0.1 Req 3.4.1 (cardholder name on card) / GDPR Art 4(1)",
        "mask": "J*** S***",
        "never_store": False,
        "notes": "Cardholder name â€” PAN-linked personal data; mask when displaying card details",
    },
    "expiry": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1 Req 3.4 â€” PAN-linked data",
        "mask": "**/**",
        "never_store": False,
        "notes": "Card expiry â€” PAN-linked; mask in non-payment contexts",
    },
    "expirymonth": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1 Req 3.4",
        "mask": "**",
        "never_store": False,
        "notes": "Expiry month â€” PAN-linked data",
    },
    "expiryyear": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1 Req 3.4",
        "mask": "**",
        "never_store": False,
        "notes": "Expiry year â€” PAN-linked data",
    },
    "cardnetwork": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "Card network name â€” not PII",
    },
    "issuer": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "Simulated issuing bank name â€” not real PII",
    },

    # â”€â”€ Financial â€” Account / Banking â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "balance": {
        "regs": [KVKK, GDPR, US_GLBA],
        "req": "KVKK Madde 12 / GDPR Art 4(1) / GLBA",
        "mask": "****75",
        "never_store": False,
        "notes": "Account balance â€” financial personal data; restrict access",
    },
    "iban": {
        "regs": [KVKK, GDPR],
        "req": "KVKK Madde 12 (TR) / GDPR Art 4(1) (EU)",
        "mask": "TR33 0006 **** **** **** **00 26",
        "never_store": False,
        "notes": "IBAN â€” bank account identifier; personal financial data",
    },
    "credit_score": {
        "regs": [KVKK, GDPR, US_GLBA],
        "req": "KVKK Madde 12 / GDPR Art 4(1) / GLBA",
        "mask": "7**",
        "never_store": False,
        "notes": "Credit score â€” financial profiling data; restrict access",
    },

    # â”€â”€ Financial â€” QR / 3DS / EMV â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "sepa_qr": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) â€” contains IBAN and beneficiary name",
        "mask": "",
        "never_store": False,
        "notes": "SEPA QR code contains IBAN + payee name â€” personal financial data",
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
        "notes": "ATM cash-out QR â€” PCI DSS in-scope",
    },
    "emv_qr_pos": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1 Req 3.4",
        "mask": "",
        "never_store": False,
        "notes": "POS merchant QR â€” PCI DSS in-scope",
    },
    "3ds_cavv": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1 Req 3.3.1 â€” SAD",
        "mask": "****",
        "never_store": True,
        "notes": "3DS CAVV â€” cardholder authentication value; SAD, must not be stored post-auth",
    },
    "3ds_eci": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1 Req 3.3",
        "mask": "",
        "never_store": False,
        "notes": "ECI flag â€” transaction outcome indicator; not sensitive on its own",
    },

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # HARDWARE â€” Magnetic Stripe / Chip / PIN Block (PCI DSS SAD)
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "track1_data": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1 Req 3.3.1 â€” SAD (full track data)",
        "mask": "%B4532 01** **** 9012^MOCKJ***^28120...?",
        "never_store": True,
        "notes": "ISO 7813 Track 1 â€” full track data is SAD; must NEVER be stored after authorization",
    },
    "track2_data": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1 Req 3.3.1 â€” SAD (full track data)",
        "mask": ";4532 01** **** 9012=2812...?",
        "never_store": True,
        "notes": "ISO 7813 Track 2 â€” full track data is SAD; must NEVER be stored after authorization",
    },
    "chip_data": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1 Req 3.3.1 â€” SAD (chip equivalent data)",
        "mask": "",
        "never_store": True,
        "notes": "EMV chip TLV â€” equivalent of track data; SAD, must not be stored post-auth",
    },
    "pin_block": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1 Req 3.3.1 â€” SAD (PIN block)",
        "mask": "0*FFFFFFFFFFFF",
        "never_store": True,
        "notes": "ISO 9564-1 Format 0 PIN block â€” SAD; never store",
    },
    "pin_block_fmt3": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1 Req 3.3.1 â€” SAD (PIN block)",
        "mask": "3***************",
        "never_store": True,
        "notes": "ISO 9564-1 Format 3 PIN block â€” SAD; never store",
    },

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # SECURITY â€” technical data, low PII risk
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "cef_log": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "Security log format â€” may contain IP addresses (GDPR quasi-PII if linked to person)",
    },
    "x509_cert": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "X.509 certificate fields â€” subject/SAN may contain personal email/domain",
    },
    "pcap_hex": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "Network capture hex â€” mock data; real pcaps may contain PII under GDPR",
    },

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # BANKING
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "creditor_ref": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "ISO 11649 creditor reference â€” payment metadata, no direct PII",
    },
    "swift": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "BIC/SWIFT code â€” bank identifier, public information",
    },
    "bic": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "Alias for SWIFT BIC â€” public information",
    },
    "sort_code": {
        "regs": [UK_GDPR, US_GLBA],
        "req": "UK GDPR Art 4(1) â€” when linked to account holder",
        "mask": "20-**-**",
        "never_store": False,
        "notes": "UK sort code â€” bank routing identifier; personal when combined with account number",
    },
    "routing_number": {
        "regs": [US_GLBA],
        "req": "GLBA â€” bank routing identifier",
        "mask": "021***021",
        "never_store": False,
        "notes": "US ABA routing number â€” identifies the bank; restricted under GLBA when linked to account",
    },
    "bik_code": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "Russian BIK â€” bank identifier code; public information",
    },
    "bank_name": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "Simulated bank name â€” fictitious; no PII",
    },
    "transaction": {
        "regs": [KVKK, GDPR, US_GLBA],
        "req": "KVKK Madde 12 / GDPR Art 4(1) / GLBA",
        "mask": "",
        "never_store": False,
        "notes": "Banking transaction record â€” contains IBAN, amounts, references; financial personal data",
    },
    "sepa_ref": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1)",
        "mask": "",
        "never_store": False,
        "notes": "SEPA end-to-end reference â€” payment metadata; low PII risk alone",
    },

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # AVIATION
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "iata_ticket": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) â€” EU PNR Directive 2016/681",
        "mask": "001234****902",
        "never_store": False,
        "notes": "IATA ticket number â€” links to passenger travel record (PNR); GDPR PNR Directive applies",
    },
    "imo_number": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "IMO ship registration â€” public marine registry; no personal data",
    },
    "pnr_code": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) / EU PNR Directive 2016/681",
        "mask": "K7****",
        "never_store": False,
        "notes": "Passenger Name Record locator â€” links to full travel itinerary and personal data",
    },

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # WEBAUTHN â€” technical credentials, no PII
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "webauthn_credential": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "FIDO2 credential â€” cryptographic key material; not personal data by itself",
    },
    "fido2_assertion": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "FIDO2 authentication response â€” cryptographic; no PII",
    },

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # WALLET â€” Crypto (no standard PII regulation yet)
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "eth_wallet": {
        "regs": [],
        "req": "No binding regulation (pseudo-anonymous by design)",
        "mask": "",
        "never_store": False,
        "notes": "ETH wallet â€” private key must be protected as secret; address is pseudo-anonymous",
    },
    "btc_wallet": {
        "regs": [],
        "req": "No binding regulation (pseudo-anonymous by design)",
        "mask": "",
        "never_store": False,
        "notes": "BTC wallet â€” private key / WIF must be secret; address pseudo-anonymous",
    },
    "sol_wallet": {
        "regs": [],
        "req": "No binding regulation",
        "mask": "",
        "never_store": False,
        "notes": "Solana wallet â€” same as ETH/BTC wallet",
    },

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # AI VECTOR â€” pure numeric, no PII
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "ai_embedding":     {"regs": [], "req": "", "mask": "", "never_store": False, "notes": ""},
    "ai_vector":        {"regs": [], "req": "", "mask": "", "never_store": False, "notes": ""},
    "ai_sparse_vector": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": ""},

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # OIDC â€” authentication tokens (security-sensitive but not PII regs)
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "oidc_token_set": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) â€” JWT sub/email claims are personal data",
        "mask": "eyJ***...",
        "never_store": False,
        "notes": "OIDC token contains sub (user ID) and email â€” personal data under GDPR",
    },
    "jwks": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "JWK Set â€” public key material; no PII",
    },
    "oidc_token": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1)",
        "mask": "eyJ***...",
        "never_store": False,
        "notes": "JWT with OIDC claims â€” sub/email are personal data",
    },

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # BANK STATEMENT
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "mt940": {
        "regs": [KVKK, GDPR, US_GLBA],
        "req": "KVKK Madde 12 / GDPR Art 4(1) / GLBA",
        "mask": "",
        "never_store": False,
        "notes": "MT940 bank statement â€” contains IBAN, balances, transaction details; financial personal data",
    },
    "camt053": {
        "regs": [KVKK, GDPR, US_GLBA],
        "req": "KVKK Madde 12 / GDPR Art 4(1) / GLBA",
        "mask": "",
        "never_store": False,
        "notes": "ISO 20022 CAMT.053 statement â€” same as MT940; financial personal data",
    },

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # EDI â€” business documents, no direct personal PII
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "edi_850":        {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "EDI 850 Purchase Order â€” B2B; may contain company names but typically no personal PII"},
    "edifact_orders": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "UN/EDIFACT ORDERS â€” B2B; same as edi_850"},

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # EVENT SOURCING â€” technical, no direct PII
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "event_stream": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "Event stream â€” contains user_id (UUID); if linked to real person, GDPR Art 4 applies",
    },
    "cdc_event": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "CDC event â€” reflects DB changes; if table contains personal data, inherit those regulations",
    },

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # TELEMETRY â€” no PII (device/sensor data)
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "fdr_record":      {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Flight Data Recorder â€” aircraft sensor telemetry; no personal data"},
    "drone_telemetry": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Drone telemetry â€” device data; location data could link to operator under GDPR"},

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # OHLCV / MARKET DATA â€” no PII
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "ohlcv_candles": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Market candlestick data â€” financial instrument; no PII"},
    "market_tick":   {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Exchange trade tick â€” instrument price data; no PII"},

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # MRZ â€” travel document data
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "mrz_td3": {
        "regs": [KVKK, GDPR],
        "req": "KVKK Madde 12 / GDPR Art 4(1) â€” contains name, DOB, nationality, passport number",
        "mask": "P<TUR E*** <<... / ABCD1*****<...",
        "never_store": False,
        "notes": "ICAO 9303 TD3 MRZ â€” combines passport number, name, DOB, nationality; strong personal data",
    },
    "mrz_td1": {
        "regs": [KVKK, GDPR],
        "req": "KVKK Madde 12 / GDPR Art 4(1)",
        "mask": "",
        "never_store": False,
        "notes": "ICAO 9303 TD1 MRZ (ID card) â€” same as TD3 with 3-line format",
    },

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # TLE â€” satellite data, no PII
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "tle_satellite": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Two-Line Element â€” orbital parameters; no PII"},

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # AUTOMOTIVE â€” technical, no PII (VIN is in Commerce)
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "can_frame":     {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "CAN bus frame â€” vehicle network data; no PII"},
    "obd2_response": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "OBD-II response â€” vehicle diagnostics; no PII in isolation"},

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # E-INVOICE â€” business documents
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "ubl_invoice": {
        "regs": [KVKK, GDPR],
        "req": "KVKK Madde 12 (TR GIB e-fatura) / GDPR Art 4(1) (EU)",
        "mask": "",
        "never_store": False,
        "notes": "UBL invoice â€” may contain individual customer name and address",
    },
    "xmldsig": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "XML Digital Signature â€” cryptographic; no PII",
    },

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # GAMEDEV â€” no PII
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "quaternion":   {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "3D rotation quaternion â€” mathematical; no PII"},
    "navmesh_path": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "NavMesh waypoints â€” game AI path; no PII"},

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # PROMETHEUS â€” metrics, no PII
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "prometheus_metrics":   {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Prometheus metrics â€” system monitoring; no PII"},
    "openmetrics_snapshot": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "OpenMetrics â€” same as Prometheus; no PII"},

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # NMEA â€” GPS coordinates (quasi-PII when linked to person)
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "nmea_gpgga": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) â€” location data is personal data when linked to a person",
        "mask": "$GPGGA,...,**07.****,N,...",
        "never_store": False,
        "notes": "GPS fix data â€” location is personal data under GDPR when device owner is identifiable",
    },
    "nmea_gprmc": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) â€” location data",
        "mask": "",
        "never_store": False,
        "notes": "GPS recommended minimum â€” location data; same as nmea_gpgga",
    },

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # PENTEST â€” attack payloads (no PII by design)
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "jwt_attack":  {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "JWT attack payload â€” security testing tool; no real PII"},
    "asn1_fuzz":   {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "ASN.1 fuzz payload â€” security testing; no PII"},
    "reverse_regex": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Regex-generated string â€” pattern testing; no PII"},

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # CONTACT
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "phone": {
        "regs": [KVKK, GDPR],
        "req": "KVKK Madde 12 / GDPR Art 4(1)",
        "mask": "+90 532 *** ** 34",
        "never_store": False,
        "notes": "Phone number â€” direct personal identifier",
    },
    "phone_country": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "Country dial code â€” public information, no PII",
    },
    "phone_area": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "Area/operator code â€” partial phone; quasi-identifier",
    },
    "phone_local": {
        "regs": [],
        "req": "",
        "mask": "",
        "never_store": False,
        "notes": "Local phone number part â€” partial; quasi-identifier",
    },
    "email": {
        "regs": [KVKK, GDPR],
        "req": "KVKK Madde 12 / GDPR Art 4(1)",
        "mask": "al***@gmail.com",
        "never_store": False,
        "notes": "Email address â€” direct personal identifier",
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
        "notes": "Street address â€” personal data (location identifier)",
    },
    "address_full": {
        "regs": [KVKK, GDPR],
        "req": "KVKK Madde 12 / GDPR Art 4(1)",
        "mask": "Istanbul, B*** C***.",
        "never_store": False,
        "notes": "Full address â€” strong personal location data",
    },
    "postalcode": {
        "regs": [KVKK, GDPR],
        "req": "KVKK Madde 12 / GDPR Art 4(1)",
        "mask": "",
        "never_store": False,
        "notes": "Postal code â€” location quasi-identifier; HIPAA considers ZIP â‰¤3 digits re-identifying",
    },
    "plate": {
        "regs": [KVKK, GDPR],
        "req": "KVKK Madde 12 / GDPR Art 4(1)",
        "mask": "34 A** 123",
        "never_store": False,
        "notes": "Vehicle license plate â€” links to registered owner; personal data",
    },

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # CORPORATE â€” mostly business data, low personal PII
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "company_name": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Company name â€” business entity; no personal PII unless sole trader"},
    "job_title":    {"regs": [GDPR], "req": "GDPR Art 4(1) â€” when linked to named employee", "mask": "", "never_store": False, "notes": "Job title alone is not PII; combined with name it is"},
    "jobtitle":     {"regs": [GDPR], "req": "GDPR Art 4(1)", "mask": "", "never_store": False, "notes": "Alias for job_title"},
    "occupation":   {"regs": [GDPR], "req": "GDPR Art 4(1)", "mask": "", "never_store": False, "notes": "Occupation â€” same as job_title; quasi-identifier when combined"},

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # HEALTH â€” GDPR Art 9 Special Category + HIPAA + KVKK Madde 6
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "bloodtype": {
        "regs": [GDPR_ART9, KVKK, US_HIPAA],
        "req": "GDPR Art 9(1) (health data) / KVKK Madde 6 (saÄŸlÄ±k verisi) / HIPAA PHI",
        "mask": "",
        "never_store": False,
        "notes": "Blood type â€” health/biometric data; special category under GDPR Art 9 and KVKK Madde 6",
    },
    "blood_type": {
        "regs": [GDPR_ART9, KVKK, US_HIPAA],
        "req": "GDPR Art 9(1) / KVKK Madde 6 / HIPAA PHI",
        "mask": "",
        "never_store": False,
        "notes": "Alias for bloodtype â€” same regulation",
    },
    "nhs_number": {
        "regs": [UK_GDPR, US_HIPAA],
        "req": "UK GDPR Art 4(1) / NHS DSPT â€” NHS Number must be kept confidential",
        "mask": "943 *** ***9",
        "never_store": False,
        "notes": "NHS Number â€” links to patient health record; UK GDPR + NHS Data Security Policy",
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
        "notes": "ICD-10 diagnosis code â€” health data; special category",
    },
    "bmi": {
        "regs": [GDPR_ART9, KVKK, US_HIPAA],
        "req": "GDPR Art 9(1) / KVKK Madde 6 / HIPAA PHI",
        "mask": "**.5",
        "never_store": False,
        "notes": "BMI â€” derived health metric; special category data",
    },
    "height": {
        "regs": [GDPR_ART9, KVKK, US_HIPAA],
        "req": "GDPR Art 9(1) / KVKK Madde 6 / HIPAA PHI (physical characteristic)",
        "mask": "*** cm",
        "never_store": False,
        "notes": "Height â€” biometric physical characteristic; health special category",
    },
    "weight": {
        "regs": [GDPR_ART9, KVKK, US_HIPAA],
        "req": "GDPR Art 9(1) / KVKK Madde 6 / HIPAA PHI",
        "mask": "** kg",
        "never_store": False,
        "notes": "Weight â€” biometric physical characteristic; health special category",
    },
    "npi": {
        "regs": [US_HIPAA],
        "req": "HIPAA â€” NPI is a healthcare provider identifier (not patient PII but regulated)",
        "mask": "123456****",
        "never_store": False,
        "notes": "US National Provider Identifier â€” HIPAA-mandated provider ID; public but regulated",
    },
    "hl7_message": {
        "regs": [GDPR_ART9, KVKK, US_HIPAA],
        "req": "GDPR Art 9(1) / KVKK Madde 6 / HIPAA PHI (HL7 patient record)",
        "mask": "",
        "never_store": False,
        "notes": "HL7 v2.5 ADT message â€” contains patient name, DOB, MRN; full PHI under HIPAA",
    },
    "fhir_patient": {
        "regs": [GDPR_ART9, KVKK, US_HIPAA],
        "req": "GDPR Art 9(1) / KVKK Madde 6 / HIPAA PHI (FHIR Patient resource)",
        "mask": "",
        "never_store": False,
        "notes": "FHIR R4 Patient â€” name, gender, birthDate, address; full PHI",
    },
    "dicom_uid": {
        "regs": [GDPR_ART9, US_HIPAA],
        "req": "GDPR Art 9(1) / HIPAA PHI (medical imaging study UID)",
        "mask": "2.25.****...",
        "never_store": False,
        "notes": "DICOM Study UID â€” links to medical imaging data; PHI under HIPAA",
    },

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # COMMERCE
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "currency":       {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Currency metadata â€” no PII"},
    "tax_rate":       {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Tax rate â€” no PII"},
    "taxrate":        {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Alias for tax_rate"},
    "invoice_number": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Invoice number â€” business metadata; no direct PII"},
    "invoicenumber":  {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Alias for invoice_number"},
    "vin": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) â€” VIN can identify vehicle owner via registration records",
        "mask": "WBA3A5C5X****3456",
        "never_store": False,
        "notes": "Vehicle Identification Number â€” can be cross-referenced to identify owner",
    },
    "vehicle": {
        "regs": [GDPR, KVKK],
        "req": "GDPR Art 4(1) / KVKK Madde 12",
        "mask": "",
        "never_store": False,
        "notes": "Vehicle record with VIN â€” same as VIN, plus make/model/year",
    },

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # META â€” UUIDs, tokens, technical identifiers
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "uuid":           {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "UUID v4 â€” random; no PII (but may link to user record)"},
    "requestid":      {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Request ID â€” technical tracing; no direct PII"},
    "correlationid":  {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Correlation ID â€” distributed tracing; no direct PII"},
    "sessionid":      {"regs": [GDPR], "req": "GDPR Art 4(1) â€” session ID can identify user", "mask": "550e***...", "never_store": False, "notes": "Session ID â€” online identifier; personal data under GDPR if linked to user"},
    "idempotencykey": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Idempotency key â€” API safety token; no direct PII"},
    "deviceid":       {"regs": [GDPR], "req": "GDPR Art 4(1) â€” device ID is online identifier", "mask": "550E***...", "never_store": False, "notes": "Device ID â€” GDPR considers device identifiers personal data"},
    "timestamp":      {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Unix timestamp â€” no PII"},
    "timestamp_iso":  {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "ISO timestamp â€” no PII"},
    "ipv4": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) / CJEU Case C-582/14 (Breyer) â€” dynamic IP is personal data",
        "mask": "192.168.***.***",
        "never_store": False,
        "notes": "IPv4 â€” CJEU ruled that dynamic IP addresses are personal data under GDPR",
    },
    "ipv6": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1)",
        "mask": "fe80:***:***:...",
        "never_store": False,
        "notes": "IPv6 â€” same as IPv4; often embeds MAC address (EUI-64) making it more identifying",
    },
    "browser_name":    {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Browser name â€” no PII alone"},
    "browser_version": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Browser version â€” no PII alone"},
    "browser_engine":  {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Browser engine â€” no PII alone"},
    "useragent": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) â€” user agent combined with IP is personal data",
        "mask": "",
        "never_store": False,
        "notes": "User-Agent string â€” fingerprinting risk; GDPR personal data when combined with IP",
    },
    "jwt":         {"regs": [GDPR], "req": "GDPR Art 4(1) â€” if sub/email claims are present", "mask": "eyJ***...", "never_store": False, "notes": "JWT â€” may contain personal claims (sub, email); treat as personal data"},
    "bearertoken": {"regs": [], "req": "", "mask": "Bearer eyJ***...", "never_store": False, "notes": "Bearer token â€” security credential; mask in logs"},
    "hash":        {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Hash value â€” no PII (but hashing PII doesn't always anonymize it)"},
    "mac_address": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) â€” MAC address is a device identifier (personal data)",
        "mask": "A4:C3:F0:**:**:**",
        "never_store": False,
        "notes": "MAC address â€” hardware identifier; GDPR considers it personal data",
    },
    "url":          {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "URL â€” no PII (unless contains personal parameters)"},
    "domain":       {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Domain name â€” no PII"},
    "color":        {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Color value â€” no PII"},
    "clientversion": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Software version â€” no PII"},
    "signature":    {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "HMAC signature â€” cryptographic; no PII"},
    "apppassword":  {"regs": [], "req": "", "mask": "******", "never_store": False, "notes": "One-time password â€” secret credential; mask in logs"},
    "transaction_id": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Transaction ID â€” reference number; no direct PII"},
    "public_ip":    {"regs": [GDPR], "req": "GDPR Art 4(1) â€” Breyer ruling", "mask": "185.***.***.**", "never_store": False, "notes": "Public IP â€” personal data under GDPR (Breyer)"},
    "private_ip":   {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Private IP â€” RFC1918 range; not routable, minimal PII risk"},
    "api_key":      {"regs": [], "req": "", "mask": "sk-***...***", "never_store": False, "notes": "API key â€” secret credential; mask in logs and UI"},
    "totp_code":    {"regs": [], "req": "", "mask": "******", "never_store": False, "notes": "TOTP code â€” time-limited OTP; secret but not personal data"},
    "webhook_signature": {"regs": [], "req": "", "mask": "sha256=****...", "never_store": False, "notes": "HMAC webhook signature â€” security; no PII"},

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # RFID / NFC / IR / WIRELESS â€” technical identifiers
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "rfid_uid": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) â€” RFID UID can identify card holder",
        "mask": "04:**:**:**:**:**:**",
        "never_store": False,
        "notes": "RFID UID â€” if linked to a person (access card), it is personal data under GDPR",
    },
    "epc":       {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "EPC â€” product identifier; no PII"},
    "rfid_tag":  {"regs": [GDPR], "req": "GDPR Art 4(1) â€” if linked to person", "mask": "", "never_store": False, "notes": "RFID tag â€” same as rfid_uid; personal if linked to person"},
    "nfc_uid":   {"regs": [GDPR], "req": "GDPR Art 4(1)", "mask": "04:**:**:**:**:**:**", "never_store": False, "notes": "NFC UID â€” same as RFID; personal if access/payment card linked to person"},
    "nfc_atqa":  {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "NFC ATQA â€” card type code; no PII"},
    "nfc_sak":   {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "NFC SAK â€” card capability byte; no PII"},
    "ndef_uri":  {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "NDEF URI â€” URL encoded in NFC tag; no PII unless URL contains personal data"},
    "ndef_text": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "NDEF text â€” arbitrary text; no PII"},
    "apdu":      {"regs": [PCI_DSS], "req": "PCI DSS â€” APDU may carry PAN in payment cards", "mask": "", "never_store": False, "notes": "APDU command â€” smart card protocol; may carry PAN if payment card"},
    "nfc_tag":   {"regs": [GDPR], "req": "GDPR Art 4(1)", "mask": "", "never_store": False, "notes": "Full NFC tag â€” includes UID; personal if linked to person"},
    "ir_nec":    {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "IR NEC signal â€” remote control; no PII"},
    "ir_rc5":    {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "IR RC5 signal â€” no PII"},
    "ir_pronto": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "IR Pronto hex â€” no PII"},
    "ir_raw":    {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "IR raw timing â€” no PII"},
    "mqtt_payload": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "MQTT IoT payload â€” device_id could link to owner under GDPR"},
    "lora_packet":  {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "LoRaWAN frame â€” device data; DevAddr could link to owner"},

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # BARCODE â€” product data, no PII
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "ean13":   {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "EAN-13 barcode â€” product identifier; no PII"},
    "ean8":    {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "EAN-8 barcode â€” product identifier; no PII"},
    "upca":    {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "UPC-A barcode â€” product identifier; no PII"},
    "isbn13":  {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "ISBN-13 â€” book identifier; no PII"},
    "isbn10":  {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "ISBN-10 â€” book identifier; no PII"},
    "gs1_128": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "GS1-128 â€” supply chain barcode; no direct PII"},

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # TELECOM
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "imei": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) / ePrivacy Directive â€” IMEI identifies a device (and through it, a person)",
        "mask": "490154******518",
        "never_store": False,
        "notes": "IMEI â€” unique device identifier; personal data under GDPR (links to subscriber)",
    },
    "imei2": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) / ePrivacy Directive",
        "mask": "49-0154-******-8",
        "never_store": False,
        "notes": "IMEI hyphenated format â€” same as imei",
    },
    "iccid": {
        "regs": [GDPR, KVKK],
        "req": "GDPR Art 4(1) / KVKK Madde 12 â€” SIM card identifier links to subscriber",
        "mask": "8990053412****8901",
        "never_store": False,
        "notes": "ICCID â€” SIM serial number; identifies subscriber, personal data",
    },
    "imsi": {
        "regs": [GDPR, KVKK],
        "req": "GDPR Art 4(1) / ePrivacy Directive / KVKK Madde 12",
        "mask": "2860112*****890",
        "never_store": False,
        "notes": "IMSI â€” subscriber identity; directly identifies a mobile subscriber",
    },
    "msisdn": {
        "regs": [GDPR, KVKK],
        "req": "GDPR Art 4(1) / KVKK Madde 12 â€” phone number is direct personal identifier",
        "mask": "+90 532 *** ** 67",
        "never_store": False,
        "notes": "MSISDN â€” international mobile phone number; direct personal identifier",
    },

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # CAPITAL MARKETS
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "isin":       {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "ISIN â€” financial instrument identifier; no PII"},
    "cusip":      {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "CUSIP â€” US security identifier; no PII"},
    "sedol":      {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "SEDOL â€” UK stock identifier; no PII"},
    "lei":        {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "LEI â€” legal entity identifier (ISO 17442); company, not personal data"},
    "fix_message": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "FIX protocol message â€” trading; no direct PII in mock data"},
    "psd2_consent": {
        "regs": [GDPR, UK_GDPR],
        "req": "GDPR Art 4(1) / PSD2 (EU 2015/2366) / UK Open Banking v3.1",
        "mask": "",
        "never_store": False,
        "notes": "PSD2 payment consent JWS â€” may contain account holder info; GDPR + PSD2 apply",
    },

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # CRYPTO (blockchain addresses â€” pseudo-anonymous)
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "btc_address":    {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Bitcoin address â€” pseudo-anonymous; may become PII if linked to identity via KYC"},
    "eth_address":    {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Ethereum address â€” pseudo-anonymous"},
    "crypto_address": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Generic crypto address â€” pseudo-anonymous"},
    "tx_hash":        {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Blockchain tx hash â€” public ledger data; pseudo-anonymous"},
    "block_hash":     {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Block hash â€” public; no PII"},
    "mnemonic": {
        "regs": [],
        "req": "No PII regulation â€” but treat as SECRET (controls wallet funds)",
        "mask": "abandon *** *** ... ***",
        "never_store": False,
        "notes": "BIP-39 mnemonic â€” not PII but controls crypto funds; treat as highest-sensitivity secret",
    },

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # E-COMMERCE
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "product_name":    {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Product name â€” no PII"},
    "sku":             {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "SKU â€” product code; no PII"},
    "order_id":        {"regs": [GDPR], "req": "GDPR Art 4(1) â€” order links to customer identity", "mask": "ORD-A1B2****5F6", "never_store": False, "notes": "Order ID â€” links to customer; personal data in e-commerce context"},
    "tracking_number": {"regs": [GDPR], "req": "GDPR Art 4(1) â€” tracking links to recipient address", "mask": "9400111*****7522384", "never_store": False, "notes": "Shipment tracking â€” links to recipient name and address; personal data"},
    "dhl_tracking":    {"regs": [GDPR], "req": "GDPR Art 4(1)", "mask": "JD12345****", "never_store": False, "notes": "DHL tracking â€” same as tracking_number"},
    "category":        {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Product category â€” no PII"},
    "rating":          {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Rating score â€” no PII alone"},

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # LOCATION
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "latitude": {
        "regs": [GDPR, KVKK],
        "req": "GDPR Art 4(1) â€” location data is personal when linked to a person",
        "mask": "39.9*****",
        "never_store": False,
        "notes": "Latitude â€” personal data when linked to device/person; precision-reduce for privacy",
    },
    "longitude": {
        "regs": [GDPR, KVKK],
        "req": "GDPR Art 4(1)",
        "mask": "32.8*****",
        "never_store": False,
        "notes": "Longitude â€” same as latitude",
    },
    "timezone":     {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Timezone â€” public information; no PII alone"},
    "country_code": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Country code â€” public; no PII alone"},
    "coordinates": {
        "regs": [GDPR, KVKK],
        "req": "GDPR Art 4(1)",
        "mask": "39.9*****,32.8*****",
        "never_store": False,
        "notes": "Lat+Lon pair â€” location personal data when linked to person",
    },

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # SOCIAL
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "username": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) â€” username is an online identifier",
        "mask": "c***ev42",
        "never_store": False,
        "notes": "Username â€” online identifier; personal data under GDPR",
    },
    "handle": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1)",
        "mask": "@c***ev42",
        "never_store": False,
        "notes": "Social media handle â€” online identifier; personal data",
    },
    "hashtag":       {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Hashtag â€” topic tag; no PII"},
    "bio":           {"regs": [GDPR], "req": "GDPR Art 4(1) â€” may contain personal information", "mask": "", "never_store": False, "notes": "Profile bio â€” may contain name, location, personal facts"},
    "follower_count": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "Follower count â€” public metric; no PII"},

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # PAYMENTS
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "swift_mt103": {
        "regs": [KVKK, GDPR, US_GLBA, PCI_DSS],
        "req": "KVKK Madde 12 / GDPR Art 4(1) / GLBA / PCI DSS if card data present",
        "mask": "",
        "never_store": False,
        "notes": "MT103 transfer message â€” contains sender/beneficiary name, IBAN, amount; financial PII",
    },
    "pain001": {
        "regs": [GDPR, KVKK, US_GLBA],
        "req": "GDPR Art 4(1) / KVKK Madde 12 / GLBA",
        "mask": "",
        "never_store": False,
        "notes": "ISO 20022 PAIN.001 â€” credit transfer initiation; contains debtor/creditor personal data",
    },
    "nacha_ach": {
        "regs": [US_GLBA, US_PRIVACY],
        "req": "GLBA / Privacy Act â€” ACH file contains account numbers and names",
        "mask": "",
        "never_store": False,
        "notes": "NACHA ACH file â€” bank account numbers + names; regulated under GLBA",
    },
    "sepa_mandate": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) â€” mandate contains debtor name and IBAN",
        "mask": "",
        "never_store": False,
        "notes": "SEPA Direct Debit Mandate â€” creditor ID + debtor IBAN; personal financial data",
    },
    "fedwire": {
        "regs": [US_GLBA],
        "req": "GLBA â€” Fedwire message contains account and routing numbers",
        "mask": "",
        "never_store": False,
        "notes": "Fedwire transfer message â€” routing + account numbers; GLBA regulated",
    },

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # CARD PHYSICS â€” PCI DSS Scope
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "iso8583_auth_request": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1 Req 3.3.1 / Req 3.4.1 â€” contains PAN (DE002)",
        "mask": "DE002: 4532 01** **** 9012",
        "never_store": False,
        "notes": "ISO 8583 0100 â€” PAN in DE002 must be masked per Req 3.4.1; in-flight data in-scope",
    },
    "iso8583_auth_response": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1 Req 3.4.1",
        "mask": "DE002: 4532 01** **** 9012",
        "never_store": False,
        "notes": "ISO 8583 0110 â€” contains PAN in DE002; mask for display",
    },
    "iso8583_reversal": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1 Req 3.4.1",
        "mask": "DE002: 4532 01** **** 9012",
        "never_store": False,
        "notes": "ISO 8583 0400 reversal â€” contains PAN; PCI scope",
    },
    "emv_arqc": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1 â€” EMV cryptogram (derived from PAN/session data)",
        "mask": "A1B2C3D4****0718",
        "never_store": False,
        "notes": "EMV ARQC â€” cryptogram derived from card data; PCI in-scope",
    },
    "emv_atc": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1",
        "mask": "00**",
        "never_store": False,
        "notes": "EMV ATC â€” application transaction counter; PCI in-scope",
    },
    "emv_iad": {
        "regs": [PCI_DSS],
        "req": "PCI DSS 4.0.1",
        "mask": "0A02102B****ABCD1234",
        "never_store": False,
        "notes": "EMV IAD â€” issuer application data; PCI in-scope",
    },
    "atm_session": {
        "regs": [PCI_DSS, KVKK, GDPR],
        "req": "PCI DSS 4.0.1 Req 3.4.1 / KVKK Madde 12 / GDPR Art 4(1)",
        "mask": "masked_pan: 4532 **** **** 9012",
        "never_store": False,
        "notes": "ATM session JSON â€” already contains masked_pan; PCI + KVKK/GDPR apply",
    },
    "pos_receipt": {
        "regs": [PCI_DSS, KVKK, GDPR],
        "req": "PCI DSS 4.0.1 Req 3.4.1 â€” receipt must show only last 4 digits",
        "mask": "Card: **** **** **** 9012",
        "never_store": False,
        "notes": "POS receipt â€” cardholder copy shows last 4 only per PCI DSS Req 3.4.1",
    },

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # IntlIDs â€” country-specific
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    # Brazil
    "br_cpf": {
        "regs": [LGPD],
        "req": "LGPD (Lei 13.709/2018) Art 46 â€” CPF is personal identifier",
        "mask": "123.***.***-09",
        "never_store": False,
        "notes": "Brazilian CPF â€” national personal identifier; LGPD applies",
    },
    "br_cnpj": {
        "regs": [LGPD],
        "req": "LGPD Art 46 â€” CNPJ is business identifier (personal if sole trader)",
        "mask": "11.222.***/**01-81",
        "never_store": False,
        "notes": "Brazilian CNPJ â€” company identifier; personal data if sole proprietor",
    },

    # India
    "in_pan": {
        "regs": [PDPA_IN],
        "req": "Income Tax Act 1961 + PDPB draft â€” PAN is personal financial identifier",
        "mask": "ABCDE****F",
        "never_store": False,
        "notes": "Indian PAN â€” tax identifier; personal data; PDPB will regulate",
    },
    "in_aadhaar": {
        "regs": [PDPA_IN],
        "req": "Aadhaar Act 2016 Sec 29 â€” must be masked as XXXX XXXX 1234",
        "mask": "XXXX XXXX 2346",
        "never_store": False,
        "notes": "Indian Aadhaar â€” biometric-linked; UIDAI requires masking to last 4 digits",
    },
    "in_gstin": {
        "regs": [PDPA_IN],
        "req": "PDPB draft â€” GSTIN links business to PAN (personal identifier chain)",
        "mask": "29ABCDE****1Z5",
        "never_store": False,
        "notes": "Indian GSTIN â€” GST registration; embeds PAN; personal data chain",
    },
    "in_epic": {
        "regs": [PDPA_IN],
        "req": "PDPB draft â€” Voter ID is personal identifier",
        "mask": "ABC*******",
        "never_store": False,
        "notes": "Indian Voter ID (EPIC) â€” personal government identifier",
    },

    # China
    "cn_ric": {
        "regs": [PIPL],
        "req": "PIPL (2021) Art 28 â€” RIC is sensitive personal information",
        "mask": "110000******1234",
        "never_store": False,
        "notes": "Chinese Resident ID â€” contains DOB and gender; PIPL sensitive personal data",
    },

    # Mexico
    "mx_curp": {
        "regs": [LFPDPPP],
        "req": "LFPDPPP (2010) Art 16 â€” CURP is personal identifier",
        "mask": "BOXW******HNERXN09",
        "never_store": False,
        "notes": "Mexican CURP â€” national personal identifier with encoded DOB and gender",
    },
    "mx_rfc": {
        "regs": [LFPDPPP],
        "req": "LFPDPPP Art 16",
        "mask": "ABCD82****ABC",
        "never_store": False,
        "notes": "Mexican RFC â€” tax registration; personal or business identifier",
    },

    # Italy
    "it_codicefiscale": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) â€” Codice Fiscale is personal identifier with encoded DOB",
        "mask": "RSSM**80A01H501U",
        "never_store": False,
        "notes": "Italian Codice Fiscale â€” encodes surname, name, DOB, birthplace; strong personal data",
    },

    # Spain
    "es_dni": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) â€” DNI is national ID; Spain Organic Law 3/2018",
        "mask": "12****78Z",
        "never_store": False,
        "notes": "Spanish DNI â€” national personal identifier; GDPR + Spain LOPDGDD",
    },
    "es_nie": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) / Spain LOPDGDD",
        "mask": "X12****7L",
        "never_store": False,
        "notes": "Spanish NIE â€” foreigner ID; same as DNI for personal data",
    },
    "es_ccc": {
        "regs": [GDPR, US_GLBA],
        "req": "GDPR Art 4(1) â€” Spanish bank account number",
        "mask": "2100-0418-**-**0051332",
        "never_store": False,
        "notes": "Spanish CCC â€” bank account; personal financial data",
    },

    # Germany
    "de_idnr": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) / German BDSG Â§12 â€” IdNr is unique personal tax ID",
        "mask": "024762****8",
        "never_store": False,
        "notes": "German Steuerliche Identifikationsnummer â€” permanent personal tax ID",
    },
    "de_stnr": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) / German BDSG",
        "mask": "21/815/****5",
        "never_store": False,
        "notes": "German Steuernummer â€” tax authority assigned; personal identifier",
    },

    # Pakistan
    "pk_cnic": {
        "regs": [],
        "req": "Pakistan PECA 2016 / proposed PDPB",
        "mask": "35202-123****-1",
        "never_store": False,
        "notes": "Pakistani CNIC â€” national ID; Pakistan data protection under PECA/PDPB",
    },

    # Japan
    "jp_cn": {
        "regs": [],
        "req": "Japan APPI (Act on the Protection of Personal Information)",
        "mask": "1234567****23",
        "never_store": False,
        "notes": "Japanese Corporate Number â€” public company ID; low individual PII risk",
    },
    "jp_in": {
        "regs": [],
        "req": "Japan My Number Act (Act No. 27 of 2013) â€” special care required",
        "mask": "123456******",
        "never_store": False,
        "notes": "Japanese My Number â€” individual number; My Number Act strictly limits use",
    },

    # South Korea
    "kr_rrn": {
        "regs": [],
        "req": "Korea PIPA (Personal Information Protection Act) â€” RRN restricted since 2014",
        "mask": "700101-1*****9",
        "never_store": False,
        "notes": "Korean RRN â€” encodes DOB and gender; PIPA restricts collection/use",
    },
    "kr_brn": {
        "regs": [],
        "req": "Korea PIPA",
        "mask": "123-45-*****0",
        "never_store": False,
        "notes": "Korean Business Registration Number â€” company identifier",
    },

    # Netherlands
    "nl_bsn": {
        "regs": [GDPR],
        "req": "GDPR Art 87 / Dutch Wbp successor (AVG) â€” BSN highly protected",
        "mask": "12345****2",
        "never_store": False,
        "notes": "Dutch BSN â€” citizen service number; GDPR Art 87 requires specific authorisation to process",
    },

    # Poland
    "pl_pesel": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) / Poland UODO â€” PESEL encodes DOB and gender",
        "mask": "700101****5",
        "never_store": False,
        "notes": "Polish PESEL â€” national ID with encoded DOB; strong personal identifier",
    },

    # Sweden
    "se_personnummer": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) / Sweden DPIA guidelines",
        "mask": "19700101-****",
        "never_store": False,
        "notes": "Swedish Personnummer â€” national ID; DOB embedded; personal data",
    },

    # Denmark
    "dk_cpr": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) / Danish Dataprotektionsloven Â§11",
        "mask": "010170-****",
        "never_store": False,
        "notes": "Danish CPR â€” encodes DOB; Â§11 restricts processing",
    },

    # Finland
    "fi_hetu": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) / Finnish Data Protection Act",
        "mask": "010170-***A",
        "never_store": False,
        "notes": "Finnish HETU â€” national ID with DOB; personal data",
    },

    # Norway
    "no_fodselsnummer": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) / Norway Personopplysningsloven",
        "mask": "010170*****",
        "never_store": False,
        "notes": "Norwegian FÃ¸dselsnummer â€” national ID with DOB; personal data",
    },

    # Australia
    "au_abn": {
        "regs": [],
        "req": "Australia Privacy Act 1988 â€” ABN is business identifier (personal for sole traders)",
        "mask": "51824*****6",
        "never_store": False,
        "notes": "Australian ABN â€” business number; personal if sole trader",
    },
    "au_tfn": {
        "regs": [],
        "req": "Australia Privacy Act 1988 Part IIIA â€” TFN is sensitive personal data",
        "mask": "123*****2",
        "never_store": False,
        "notes": "Australian TFN â€” Tax File Number; Privacy Act Part IIIA gives extra protection",
    },
    "au_acn": {
        "regs": [],
        "req": "Australia Privacy Act 1988",
        "mask": "004*****6",
        "never_store": False,
        "notes": "Australian ACN â€” company number; public ASIC register",
    },

    # Malaysia
    "my_nric": {
        "regs": [],
        "req": "Malaysia PDPA 2010 â€” NRIC encodes DOB and birth state",
        "mask": "701231-**-5678",
        "never_store": False,
        "notes": "Malaysian NRIC â€” national ID with encoded DOB and birth state; PDPA regulated",
    },

    # Thailand
    "th_pin": {
        "regs": [],
        "req": "Thailand PDPA 2019 (B.E. 2562)",
        "mask": "123456****234",
        "never_store": False,
        "notes": "Thai personal ID â€” 13-digit national ID; Thailand PDPA applies",
    },
    "th_tin": {
        "regs": [],
        "req": "Thailand PDPA 2019",
        "mask": "123456****234",
        "never_store": False,
        "notes": "Thai TIN â€” same format as personal ID; business or personal",
    },

    # Singapore
    "sg_uen": {
        "regs": [],
        "req": "Singapore PDPA 2012",
        "mask": "12345***X",
        "never_store": False,
        "notes": "Singapore UEN â€” business entity number; PDPA applies if linked to individual",
    },

    # South Africa
    "za_idnr": {
        "regs": [],
        "req": "South Africa POPIA 2013 â€” ID embeds DOB and gender",
        "mask": "700101****081",
        "never_store": False,
        "notes": "South African ID â€” contains DOB and gender; POPIA regulated",
    },

    # Canada
    "ca_bn": {
        "regs": [],
        "req": "Canada PIPEDA â€” business number; personal if sole proprietor",
        "mask": "12345****2",
        "never_store": False,
        "notes": "Canadian Business Number â€” PIPEDA applies for individual proprietors",
    },

    # New Zealand
    "nz_ird": {
        "regs": [],
        "req": "New Zealand Privacy Act 2020 â€” IRD is personal tax identifier",
        "mask": "490***268",
        "never_store": False,
        "notes": "New Zealand IRD number â€” tax identifier; Privacy Act 2020",
    },

    # Argentina
    "ar_cuit": {
        "regs": [],
        "req": "Argentina PDPA (Law 25.326) â€” CUIT is personal/business identifier",
        "mask": "20-1234****-9",
        "never_store": False,
        "notes": "Argentinian CUIT â€” tax identifier; Law 25.326 personal data",
    },
    "ar_dni": {
        "regs": [],
        "req": "Argentina PDPA (Law 25.326) â€” DNI is national personal ID",
        "mask": "12****78",
        "never_store": False,
        "notes": "Argentinian DNI â€” national personal identifier",
    },

    # Chile
    "cl_rut": {
        "regs": [],
        "req": "Chile Law 19.628 (Datos Personales) â€” RUT is national identifier",
        "mask": "12.345.***-9",
        "never_store": False,
        "notes": "Chilean RUT â€” national tax/ID number; Law 19.628",
    },

    # Colombia
    "co_nit": {
        "regs": [],
        "req": "Colombia Law 1581/2012 (Habeas Data) â€” NIT is business/personal identifier",
        "mask": "800123****5",
        "never_store": False,
        "notes": "Colombian NIT â€” tax identifier; Law 1581 personal data",
    },

    # Israel
    "il_idnr": {
        "regs": [],
        "req": "Israel Privacy Protection Law 1981 â€” ID is personal identifier",
        "mask": "12345****2",
        "never_store": False,
        "notes": "Israeli ID number â€” national personal identifier",
    },

    # Romania
    "ro_cnp": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) / Romania Law 677/2001 â€” CNP encodes DOB and gender",
        "mask": "1700101****56",
        "never_store": False,
        "notes": "Romanian CNP â€” national ID with encoded DOB and gender; GDPR applies",
    },
    "ro_cui": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1)",
        "mask": "RO123****85",
        "never_store": False,
        "notes": "Romanian CUI â€” company identifier; GDPR if linked to sole trader",
    },

    # Croatia
    "hr_oib": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) / Croatia OIB Act â€” OIB is permanent personal identifier",
        "mask": "12345****01",
        "never_store": False,
        "notes": "Croatian OIB â€” personal identifier used for all government/financial purposes",
    },

    # Bulgaria
    "bg_egn": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) â€” EGN encodes DOB and gender",
        "mask": "700101****",
        "never_store": False,
        "notes": "Bulgarian EGN â€” national ID with encoded DOB; GDPR personal data",
    },

    # Lithuania
    "lt_asmens": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) / Lithuania Personal Data Protection Law",
        "mask": "3800101****",
        "never_store": False,
        "notes": "Lithuanian personal code â€” same algorithm as Estonian IK; GDPR applies",
    },

    # Estonia
    "ee_ik": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) / Estonia Isikuandmete kaitse seadus",
        "mask": "3800101****",
        "never_store": False,
        "notes": "Estonian Isikukood â€” personal code with DOB/gender prefix; GDPR applies",
    },

    # Portugal
    "pt_cc": {
        "regs": [GDPR],
        "req": "GDPR Art 4(1) / Portugal Lei 58/2019",
        "mask": "12345*** 0 **4",
        "never_store": False,
        "notes": "Portuguese Citizen Card number â€” national personal identifier; GDPR + Lei 58/2019",
    },

    # Egypt
    "eg_tn": {
        "regs": [],
        "req": "Egypt Data Protection Law 151/2020 â€” TN is business identifier",
        "mask": "12345****",
        "never_store": False,
        "notes": "Egyptian Tax Registration Number â€” business identifier; Law 151/2020",
    },

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # CLI COMMANDS â€” not data types; no PII regulation
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    "bulk":     {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "CLI command â€” generates N values of any type; inherits regulation of the target type"},
    "template": {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "CLI command â€” combines types into a record; inherits regulations of constituent types"},
    "export":   {"regs": [], "req": "", "mask": "", "never_store": False, "notes": "CLI command â€” bulk export; inherits regulations of constituent types"},
    "profile":  {"regs": [KVKK, GDPR], "req": "KVKK Madde 12 / GDPR Art 4(1) â€” composite personal record", "mask": "", "never_store": False, "notes": "Person profile (name+ID+phone+email+address) â€” composite personal data record"},
    "company":  {"regs": [KVKK, GDPR], "req": "KVKK Madde 12 / GDPR Art 4(1)", "mask": "", "never_store": False, "notes": "Company profile (name+taxID+IBAN) â€” may contain personal data if sole trader"},
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

