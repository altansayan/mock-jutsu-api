import sys
import os

# Define the full, clean reference list with 6 elements each
REFERENCE_DATA = [
    # Identity
    ("tckn",          "Identity",    False, "45678901234",            "generate tckn", "Turkish ID (TCKN) with Modulo 10/11 validation."),
    ("ykn",           "Identity",    False, "99012345678",            "generate ykn",  "Foreigner ID (YKN) with Modulo 10/11 validation."),
    ("nationalid",    "Identity",    True,  "(by locale)",            "generate nationalid --locale TR", "Generic National ID for the specified locale."),
    ("vkn",           "Identity",    False, "1234567890",             "generate vkn",  "Tax Identification Number (VKN) with Modulo 11 validation."),
    ("taxid",         "Identity",    True,  "(by locale)",            "generate taxid --locale TR", "Generic Tax ID for the specified locale."),
    ("employer_id",   "Identity",    True,  "(by locale)",            "generate employer_id --locale TR", "Employer Registration ID with algorithmic checks."),
    ("insurance_id",  "Identity",    True,  "(by locale)",            "generate insurance_id --locale TR", "Social Security / Insurance ID for specified locale."),
    ("sgk",           "Identity",    False, "34-0012345-1.01-02",     "generate sgk", "Turkish Social Security (SGK) number format."),
    ("mersis",        "Identity",    False, "1234567890012345",        "generate mersis", "Turkish Central Registry System (MERSIS) number."),
    ("ssn",           "Identity",    False, "234-56-7890",            "generate ssn", "US Social Security Number (SSN) with area/group rules."),
    ("ein",           "Identity",    False, "12-3456789",             "generate ein", "US Employer Identification Number (EIN) format."),
    ("nin",           "Identity",    False, "AB 12 34 56 C",          "generate nin", "UK National Insurance Number (NIN) format."),
    ("utr",           "Identity",    False, "1234567890",             "generate utr", "UK Unique Taxpayer Reference (UTR) with Modulo 11 check."),
    ("crn",           "Identity",    False, "12345678",               "generate crn", "UK Company Registration Number (CRN) format."),
    ("paye",          "Identity",    False, "123/AB4567",             "generate paye", "UK PAYE (Pay As You Earn) reference format."),
    ("ust_id",        "Identity",    False, "DE123456789",            "generate ust_id", "German VAT ID (USt-IdNr.) with ISO 7064 check."),
    ("ustid",         "Identity",    False, "DE123456789",            "generate ustid", "Alias for German VAT ID."),
    ("hrb",           "Identity",    False, "HRB 123456",             "generate hrb", "German Commercial Register (Handelsregister) ID."),
    ("rvn",           "Identity",    False, "65 070892 W 1235",       "generate rvn", "German Pension Insurance Number (RVNR) format."),
    ("siren",         "Identity",    False, "732829320",              "generate siren", "French Business Identifier (SIREN) with Luhn validation."),
    ("siret",         "Identity",    False, "73282932000074",         "generate siret", "French Establishment Identifier (SIRET) with Luhn validation."),
    ("tva",           "Identity",    False, "FR73732829320",          "generate tva", "French VAT Number (TVA) with ISO 7064 check."),
    ("inn",           "Identity",    False, "7707083893",             "generate inn", "Russian Tax ID (INN) with checksum validation."),
    ("snils",         "Identity",    False, "112-233-445 95",         "generate snils", "Russian Pension Insurance (SNILS) with checksum."),
    ("kpp",           "Identity",    False, "770701001",              "generate kpp", "Russian Industrial Enterprises Code (KPP) format."),
    ("ogrn",          "Identity",    False, "1027700132195",          "generate ogrn", "Russian Primary State Registration Number (OGRN)."),
    # Name
    ("firstname",     "Name",        True,  "Emre",                   "generate firstname --locale TR", "Random first name for the specified locale."),
    ("lastname",      "Name",        True,  "Yilmaz",                 "generate lastname --locale TR", "Random last name for the specified locale."),
    ("fullname",      "Name",        True,  "Emre Kaya",              "generate fullname --locale TR", "Full name (First + Last) for the specified locale."),
    ("patronymic",    "Name",        True,  "Ivanovich",              "generate patronymic --locale RU", "Patronymic middle name (common in Russian locale)."),
    # Document
    ("passport",      "Document",    False, "P1234567",               "generate passport", "Generic passport number format."),
    ("license",       "Document",    False, "654321",                 "generate license", "Generic driver license number format."),
    # Demographic
    ("age",           "Demographic", False, "34",                     "generate age", "Random human age (typically 18-90)."),
    ("gender",        "Demographic", False, "Male",                   "generate gender", "Binary gender values (Male/Female)."),
    ("birthdate",     "Demographic", False, "1990-05-14",             "generate birthdate", "Random date of birth in YYYY-MM-DD format."),
    # Financial
    ("cardnum",       "Financial",   False, "4532 0151 9283 1029",    "generate cardnum --network visa", "Credit card number with Luhn algorithm validation."),
    ("cardtype",      "Financial",   False, "Credit",                 "generate cardtype", "Payment card type (Credit/Debit/Prepaid)."),
    ("cardstatus",    "Financial",   False, "Active",                 "generate cardstatus", "Payment card status (Active/Blocked/Expired)."),
    ("cardcategory",  "Financial",   False, "Gold",                   "generate cardcategory", "Card level (Classic/Gold/Platinum/Infinite)."),
    ("cardowner",     "Financial",   True,  "JOHN SMITH",             "generate cardowner --locale TR", "Cardholder name in appropriate format for locale."),
    ("cvv3",          "Financial",   False, "847",                    "generate cvv3", "3-digit Card Verification Value (CVV/CVC)."),
    ("cvv4",          "Financial",   False, "1234",                   "generate cvv4", "4-digit Card Verification Value for Amex."),
    ("pin",           "Financial",   False, "7291",                   "generate pin", "4-digit randomized Personal Identification Number."),
    ("expiry",        "Financial",   False, "09/27",                  "generate expiry", "Card expiry date (MM/YY) in the future."),
    ("expirymonth",   "Financial",   False, "09",                     "generate expirymonth", "Card expiry month (01-12)."),
    ("expiryyear",    "Financial",   False, "27",                     "generate expiryyear", "Card expiry year (last 2 digits)."),
    ("issuer",        "Financial",   True,  "BosphorusBank A.S.",     "generate issuer --locale TR", "Simulated bank or card issuing entity."),
    ("balance",       "Financial",   False, "12450.75",               "generate balance", "Random account balance with 2 decimal precision."),
    ("iban",          "Financial",   True,  "TR330006100519...",      "generate iban --locale TR", "International Bank Account Number (IBAN) with Modulo 97 check."),
    ("sepa_qr",       "Financial",   True,  "BCD\n002...",             "generate sepa_qr --locale DE", "SEPA Credit Transfer QR code (EPC standard)."),
    ("emv_qr_p2p",    "Financial",   True,  "000201010211...",        "generate emv_qr_p2p --locale TR", "EMV QRCPS P2P payment QR code (TRQR compatible)."),
    ("emv_qr_atm",    "Financial",   True,  "000201010212...",        "generate emv_qr_atm --locale DE", "EMV QRCPS ATM cash-out QR code."),
    ("emv_qr_pos",    "Financial",   True,  "000201010211...",        "generate emv_qr_pos --locale FR", "EMV QRCPS Merchant/POS QR code."),
    # Hardware / Payment
    ("track2_data",   "Hardware",    False, ";4532...=2812201...?",   "generate track2_data", "Magnetic stripe Track 2 data (PAN=Expiry+ServiceCode+CVV)."),
    ("chip_data",     "Hardware",    False, "9F0206000000001000...",  "generate chip_data", "Simulated EMV chip (ICC) tag-length-value (TLV) data."),
    ("pin_block",     "Hardware",    False, "0123456789ABCDEF",       "generate pin_block", "ISO 9564 format encrypted PIN block (Format 0/1)."),
    # Contact
    ("phone",         "Contact",     True,  "+905325551234",          "generate phone --locale TR", "Full E.164 formatted telephone number."),
    ("phone_country", "Contact",     True,  "+90",                    "generate phone_country --locale TR", "International telephone country dial code."),
    ("phone_area",    "Contact",     True,  "532",                    "generate phone_area --locale TR", "Localized telephone area/operator code."),
    ("phone_local",   "Contact",     True,  "5551234",                "generate phone_local --locale TR", "Local telephone number part."),
    ("address_city",  "Contact",     True,  "Istanbul",               "generate address_city --locale TR", "Major city name for the specified locale."),
    ("address_street","Contact",     True,  "Bagdat Caddesi",         "generate address_street --locale TR", "Realistic street/avenue name for the locale."),
    ("address_full",  "Contact",     True,  "Istanbul, Bagdat Cad.",  "generate address_full --locale TR", "Complete mailing address for the specified locale."),
    ("postalcode",    "Contact",     True,  "34500",                  "generate postalcode --locale TR", "Locale-specific postal/zip code format."),
    ("plate",         "Contact",     True,  "34 ABC 123",             "generate plate --locale TR", "Vehicle license plate format for the specified country."),
    ("email",         "Contact",     True,  "user42@gmail.com",       "generate email --locale TR", "Randomized email address using common domains."),
    # Banking
    ("swift",         "Banking",     True,  "DEUTDEDB",               "generate swift --locale TR", "ISO 9362 Business Identifier Code (BIC/SWIFT)."),
    ("bic",           "Banking",     True,  "DEUTDEDB",               "generate bic --locale TR", "Alias for SWIFT/BIC code."),
    ("sort_code",     "Banking",     False, "20-00-00",               "generate sort_code", "UK 6-digit bank sort code format."),
    ("routing_number","Banking",     False, "021000021",              "generate routing_number", "US 9-digit ABA routing transit number with checksum."),
    ("bik_code",      "Banking",     False, "044525225",              "generate bik_code", "Russian Bank Identification Code (BIK)."),
    ("bank_name",     "Banking",     True,  "Berliner Finanzbank",    "generate bank_name --locale TR", "Randomized bank name for the specified locale."),
    ("transaction",   "Banking",     True,  "{ref, iban*2, amount}",  "generate transaction --locale TR", "Complex banking transaction record simulation."),
    # Corporate
    ("company_name",  "Corporate",   True,  "Fischer Tech. GmbH",     "generate company_name --locale TR", "Official business name for the specified locale."),
    ("job_title",     "Corporate",   True,  "Software Engineer",      "generate job_title --locale TR", "Professional job title for the specified locale."),
    ("jobtitle",      "Corporate",   True,  "Software Engineer",      "generate jobtitle --locale TR", "Alias for job title."),
    ("occupation",    "Corporate",   True,  "Software Engineer",      "generate occupation --locale TR", "Professional occupation classification."),
    # Health
    ("bloodtype",     "Health",      False, "A+",                     "generate bloodtype", "Human blood groups (ABO and Rh factor)."),
    ("blood_type",    "Health",      False, "A+",                     "generate blood_type", "Alias for blood type."),
    ("nhs_number",    "Health",      False, "943 476 5919",           "generate nhs_number", "UK National Health Service number with Modulo 11 check."),
    ("nhsnumber",     "Health",      False, "943 476 5919",           "generate nhsnumber", "Alias for NHS number."),
    ("icd10",         "Health",      False, "J45.909",                "generate icd10", "International Classification of Diseases 10th Revision (ICD-10) code."),
    ("bmi",           "Health",      False, "22.5",                   "generate bmi", "Body Mass Index (BMI) calculated value."),
    ("height",        "Health",      True,  '178 cm / 5\'10"',        "generate height --locale TR", "Localized height measurement (cm/inch)."),
    ("weight",        "Health",      True,  "74 kg / 163 lbs",        "generate weight --locale TR", "Localized weight measurement (kg/lbs)."),
    # Commerce
    ("currency",      "Commerce",    True,  "{code:TRY, symbol:TL}",  "generate currency --locale TR", "Localized currency details (ISO code and symbol)."),
    ("tax_rate",      "Commerce",    True,  "{name:KDV, rate:20}",    "generate tax_rate --locale TR", "Localized tax names and rates (e.g., KDV, VAT)."),
    ("taxrate",       "Commerce",    True,  "{name:KDV, rate:20}",    "generate taxrate --locale TR", "Alias for tax rate."),
    ("invoice_number","Commerce",    True,  "INV-2024-001234",        "generate invoice_number --locale TR", "Localized invoice number formats."),
    ("invoicenumber", "Commerce",    True,  "INV-2024-001234",        "generate invoicenumber --locale TR", "Alias for invoice number."),
    ("vin",           "Commerce",    True,  "WBA3A5C5XMD123456",      "generate vin --locale TR", "Vehicle Identification Number (VIN) with ISO 3779 checksum."),
    ("vehicle",       "Commerce",    True,  "{make,model,year,vin}",  "generate vehicle --locale TR", "Comprehensive vehicle data including make/model."),
    # Meta
    ("uuid",          "Meta",        False, "550e8400-e29b-41d4-...", "generate uuid", "RFC 4122 compliant Universally Unique Identifier (UUID v4)."),
    ("requestid",     "Meta",        False, "550e8400-e29b-41d4-...", "generate requestid", "Unique request identifier (UUID format)."),
    ("correlationid", "Meta",        False, "550e8400-e29b-41d4-...", "generate correlationid", "Tracing correlation identifier (UUID format)."),
    ("sessionid",     "Meta",        False, "550e8400-e29b-41d4-...", "generate sessionid", "Unique session identifier (UUID format)."),
    ("idempotencykey","Meta",        False, "550e8400-e29b-41d4-...", "generate idempotencykey", "API idempotency key for safe retries (UUID format)."),
    ("deviceid",      "Meta",        False, "550E8400-E29B-41D4-...", "generate deviceid", "Unique hardware/device identifier (Uppercase UUID)."),
    ("timestamp",     "Meta",        False, "1714900000",             "generate timestamp", "Current Unix epoch timestamp (seconds)."),
    ("timestamp_iso", "Meta",        False, "2024-05-05T14:30:00",    "generate timestamp_iso", "ISO 8601 formatted date-time string."),
    ("ipv4",          "Meta",        False, "192.168.1.42",           "generate ipv4", "Random public or private IPv4 address."),
    ("ipv6",          "Meta",        False, "fe80:0000:0000:...",     "generate ipv6", "RFC 4291 compliant IPv6 address."),
    ("browser_name",  "Meta",        False, "Chrome",                 "generate browser_name", "Common web browser names."),
    ("browser_version","Meta",       False, "124.0.6367.78",          "generate browser_version", "Simulated browser version strings."),
    ("browser_engine","Meta",        False, "Blink",                  "generate browser_engine", "Web browser layout engines (Blink, WebKit, etc.)."),
    ("useragent",     "Meta",        False, "Mozilla/5.0 ...",        "generate useragent", "Realistic browser User-Agent strings."),
    ("jwt",           "Meta",        False, "eyJ....eyJ....sig",      "generate jwt", "Mock JSON Web Token (JWT) with header/payload/signature structure."),
    ("bearertoken",   "Meta",        False, "Bearer eyJ....sig",      "generate bearertoken", "HTTP Bearer authorization token."),
    ("hash",          "Meta",        False, "e3b0c44298fc...(64hex)", "generate hash --algorithm sha256", "Cryptographic hash values for various algorithms."),
    ("mac_address",   "Meta",        False, "A4:C3:F0:3D:8E:21",      "generate mac_address", "48-bit hardware MAC address (IEEE 802)."),
    ("url",           "Meta",        True,  "https://api-42.co.uk/..", "generate url --locale TR", "Localized web URLs."),
    ("domain",        "Meta",        True,  "test-77.com.tr",         "generate domain --locale TR", "Localized domain names with regional TLDs."),
    ("color",         "Meta",        False, "#3A7BF0",                "generate color", "Hexadecimal or named color values."),
    ("clientversion", "Meta",        False, "2.4.1",                  "generate clientversion", "Software client versioning (SemVer)."),
    ("signature",     "Meta",        False, "a1b2c3d4... (hex)",      "generate signature", "Digital signature hex strings."),
    ("apppassword",   "Meta",        False, "481302",                 "generate apppassword", "One-time application passwords / PINs."),
    # RFID
    ("rfid_uid",      "RFID",        False, "04:A3:B2:C1:D0:E5:F6",  "generate rfid_uid", "RFID chip unique identifier (UID)."),
    ("epc",           "RFID",        False, "3034257BF400B718...",    "generate epc", "Electronic Product Code (EPC) for RFID tags."),
    ("rfid_tag",      "RFID",        False, "{uid,standard,freq,mem}","generate rfid_tag", "Comprehensive RFID tag data (UID, Freq, Memory)."),
    # NFC
    ("nfc_uid",       "NFC",         False, "04:A3:B2:C1:D0:E5:F6",  "generate nfc_uid", "NFC chip unique identifier (UID)."),
    ("nfc_atqa",      "NFC",         False, "00:44",                  "generate nfc_atqa", "NFC Answer to Request (ATQA) code."),
    ("nfc_sak",       "NFC",         False, "20",                     "generate nfc_sak", "NFC Select Acknowledge (SAK) code."),
    ("ndef_uri",      "NFC",         False, "{raw_hex, decoded url}", "generate ndef_uri", "NFC Data Exchange Format (NDEF) URI record."),
    ("ndef_text",     "NFC",         True,  "{raw_hex, decoded txt}", "generate ndef_text --locale TR", "NFC Data Exchange Format (NDEF) Text record."),
    ("apdu",          "NFC",         False, "{cla,ins,p1,p2,hex}",   "generate apdu", "Smart card Application Protocol Data Unit (APDU) commands."),
    ("nfc_tag",       "NFC",         False, "{uid,atqa,sak,ndef}",   "generate nfc_tag", "Comprehensive NFC tag details."),
    # IR
    ("ir_nec",        "IR",          False, "{addr,cmd,hex:20DF10EF}","generate ir_nec", "Infrared NEC protocol signal data."),
    ("ir_rc5",        "IR",          False, "{system,cmd,frame_bits}","generate ir_rc5", "Infrared Philips RC5 protocol signal data."),
    ("ir_pronto",     "IR",          False, "0000 006D 0022 0000 ..", "generate ir_pronto", "Infrared Pronto Hex format data."),
    ("ir_raw",        "IR",          False, "{carrier_hz,pulses:[]}","generate ir_raw", "Infrared raw pulse/space timing data."),
    # Barcode
    ("ean13",         "Barcode",     True,  "8680001234567",          "generate ean13 --locale TR", "International Article Number (EAN-13) with checksum."),
    ("ean8",          "Barcode",     True,  "86812345",               "generate ean8 --locale TR", "Compressed EAN-8 barcode with checksum."),
    ("upca",          "Barcode",     False, "036000291452",           "generate upca", "Universal Product Code (UPC-A) with checksum."),
    ("isbn13",        "Barcode",     False, "9780306406157",          "generate isbn13", "International Standard Book Number (ISBN-13)."),
    ("isbn10",        "Barcode",     False, "0306406152",             "generate isbn10", "Legacy ISBN-10 with checksum."),
    ("gs1_128",       "Barcode",     False, "(01)...(17)...(10)...", "generate gs1_128", "GS1-128 (formerly UCC/EAN-128) application identifiers."),
    # Telecom
    ("imei",          "Telecom",     False, "490154203237518",        "generate imei", "International Mobile Equipment Identity (IMEI) with Luhn."),
    ("imei2",         "Telecom",     False, "49-015420-323751-8",     "generate imei2", "IMEI in hyphenated format."),
    ("iccid",         "Telecom",     True,  "8990053412345678901",    "generate iccid --locale TR", "SIM card Integrated Circuit Card Identifier (ICCID)."),
    ("imsi",          "Telecom",     True,  "286011234567890",        "generate imsi --locale TR", "International Mobile Subscriber Identity (IMSI)."),
    # Securities
    ("isin",          "Securities",  True,  "US0378331005",           "generate isin --locale US", "International Securities Identification Number (ISO 6166)."),
    ("cusip",         "Securities",  False, "037833100",              "generate cusip", "Committee on Uniform Security Identification Procedures ID."),
    ("sedol",         "Securities",  False, "0263494",                "generate sedol", "Stock Exchange Daily Official List (UK)."),
    ("lei",           "Securities",  False, "529900T8BM49AURSDO55",   "generate lei", "Legal Entity Identifier (ISO 17442)."),
    # Crypto / Web3
    ("btc_address",    "Crypto",     False, "1A1zP1eP5QGefi2DMPTfTL5SLmv7Divf",  "generate btc_address", "Bitcoin wallet address (P2PKH, P2SH, Bech32)."),
    ("eth_address",    "Crypto",     False, "0x5aAeb6053F3E94C9b9A0...",           "generate eth_address", "Ethereum/EVM compatible wallet address."),
    ("crypto_address", "Crypto",     False, "(btc or eth)",                        "generate crypto_address --currency eth", "Generic crypto address for specified currency."),
    ("tx_hash",        "Crypto",     False, "a1b2c3...64hex",                      "generate tx_hash --currency btc", "Blockchain transaction hash (SHA-256/Keccak-256)."),
    ("block_hash",     "Crypto",     False, "0x+64hex (eth)",                      "generate block_hash --currency eth", "Blockchain block hash identifier."),
    # E-Commerce
    ("product_name",    "E-Commerce", False, "Wireless Headphones",               "generate product_name", "Randomized e-commerce product names."),
    ("sku",             "E-Commerce", False, "AB-123456",                          "generate sku", "Stock Keeping Unit (SKU) identifiers."),
    ("order_id",        "E-Commerce", False, "ORD-A1B2C3D4E5F6",                  "generate order_id", "Unique e-commerce order identifiers."),
    ("tracking_number", "E-Commerce", False, "9400111899223397522384",             "generate tracking_number --carrier usps", "Logistic tracking numbers for major carriers."),
    ("dhl_tracking",    "E-Commerce", False, "JD123456789",                        "generate dhl_tracking", "DHL Express tracking number format."),
    ("category",        "E-Commerce", False, "Electronics",                        "generate category", "Product category classifications."),
    ("rating",          "E-Commerce", False, "4.5",                                "generate rating", "Product rating scores (1.0 - 5.0)."),
    # Location / Geo
    ("latitude",     "Location",  True,  "39.925533",                              "generate latitude --locale TR", "Geographic latitude coordinate."),
    ("longitude",    "Location",  True,  "32.866287",                              "generate longitude --locale TR", "Geographic longitude coordinate."),
    ("timezone",     "Location",  True,  "Europe/Istanbul",                        "generate timezone --locale TR", "IANA/Olson timezone identifiers."),
    ("country_code", "Location",  True,  "TR",                                     "generate country_code --locale TR", "ISO 3166-1 alpha-2 country codes."),
    ("coordinates",  "Location",  True,  "39.925533,32.866287",                    "generate coordinates --locale TR", "Combined Lat/Long coordinate pairs."),
    # Social Media
    ("username",       "Social",   False, "cooldev42",                             "generate username", "Social media profile usernames."),
    ("follower_count", "Social",   False, "14273",                                 "generate follower_count", "Simulated follower/subscriber counts."),
    # Security / API
    ("api_key",          "Security", False, "sk-aBcDeFgH...",            "generate api_key", "Simulated secure API keys with prefix/suffix entropy."),
    ("totp_code",        "Security", False, "482931",                    "generate totp_code", "6-digit Time-based One-Time Password (TOTP) codes."),
    ("webhook_signature","Security", False, "sha256=e3b0c44...(71 chars)",         "generate webhook_signature", "HMAC webhook signatures for secure delivery."),
    ("transaction_id",   "Security", False, "TXN1A2B3C4D5E6F7G8",                 "generate transaction_id", "Unique secure transaction identifier."),
    ("public_ip",        "Security", False, "185.46.212.33",                       "generate public_ip", "Public-facing IPv4 address."),
    ("private_ip",       "Security", False, "192.168.1.42",                        "generate private_ip", "Internal/Private IPv4 address."),
    # Masked / Special
    ("tckn_masked",      "Identity", False, "***123456**",                         "generate tckn_masked", "Masked Turkish ID for privacy compliance."),
    ("ssn_masked",       "Identity", False, "***-**-6789",                         "generate ssn_masked", "Masked US SSN for privacy compliance."),
    ("nationality",      "Identity", False, "TUR",                                 "generate nationality", "ISO 3166-1 alpha-3 nationality codes."),
]

cli_path = r"c:\Users\altan\repos\mock-jutsu-api\src\mockjutsu\cli.py"

with open(cli_path, "r", encoding="utf-8") as f:
    content = f.read()

# Find the start and end of _REFERENCE list
start_marker = "_REFERENCE = ["
end_marker = "]"

start_idx = content.find(start_marker)
if start_idx == -1:
    print("Error: Could not find _REFERENCE start")
    sys.exit(1)

# Find the CLOSING bracket of the list. 
# We look for the first ] after the start_idx that is followed by _CAT_ORDER (to be safe)
end_idx = content.find(end_marker + "\n\n# Category display order", start_idx)
if end_idx == -1:
    # Fallback to just the next closing bracket
    end_idx = content.find(end_marker, start_idx + len(start_marker))

if end_idx == -1:
    print("Error: Could not find _REFERENCE end")
    sys.exit(1)

# Construct new _REFERENCE string using repr() for safe string escaping
new_ref_str = "_REFERENCE = [\n"
for item in REFERENCE_DATA:
    # item is (typ, cat, loc, ex, cli, desc)
    # format: ("typ", "cat", loc, "ex", "cli", "desc"),
    row = f"    ({item[0]!r:<17}, {item[1]!r:<15}, {str(item[2]):<5}, {item[3]!r:<24}, {item[4]!r:<32}, {item[5]!r}),"
    new_ref_str += row + "\n"
new_ref_str += "]"

new_content = content[:start_idx] + new_ref_str + content[end_idx+1:]

with open(cli_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print("Successfully fixed _REFERENCE in cli.py using repr() escaping")
