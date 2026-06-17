"""
Mock Jutsu - CLI
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)
"""

import io
import json
import os
import sys

import click
from mockjutsu.core import jutsu


def _read_test_count() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    for _ in range(6):
        candidate = os.path.join(here, "compliance", "test_stats.json")
        if os.path.exists(candidate):
            try:
                with open(candidate, encoding="utf-8-sig") as f:
                    return json.load(f).get("passed", 0)
            except Exception:
                return 0
        here = os.path.dirname(here)
    return 0


def _fix_utf8_streams() -> None:
    # Force UTF-8 on Windows terminals that default to cp1254/cp1252.
    # Called only at CLI entry — never at import time so pytest capture stays intact.
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "buffer"):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def _print_banner() -> None:
    from pyfiglet import Figlet
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text

    console = Console(highlight=False)

    raw_art = Figlet(font="small").renderText("Mock Jutsu").rstrip("\n")
    art_lines = [line.rstrip() for line in raw_art.splitlines()]
    min_i = min((len(l) - len(l.lstrip()) for l in art_lines if l.strip()), default=0)
    art_lines = [l[min_i:] for l in art_lines]

    mid = len(art_lines) // 2
    body = Text(justify="center")
    for i, line in enumerate(art_lines):
        if i == mid:
            body.append("⚔  ", style="bold yellow")
            body.append(line, style="bold bright_green")
            body.append("  ✦\n", style="bold yellow")
        else:
            body.append(line + "\n", style="bold bright_green")

    # Calculate dynamic stats
    types_count = len([r for r in _REFERENCE if r[0].strip() and not r[0].strip().startswith("--")])
    
    body.append("\n")
    body.append("The Ultimate Algorithmic Mock Data Engine\n", style="bold white")
    body.append(f"{types_count} Types", style="cyan")
    body.append("  |  ", style="dim white")
    body.append("6 Locales", style="cyan")
    body.append("  |  ", style="dim white")
    test_count = _read_test_count()
    body.append(f"{test_count} Tests\n" if test_count else "Tests\n", style="cyan")
    body.append("\n")
    body.append("Developed by: Altan Sezer Ayan (A.S.A)\n", style="dim white")
    body.append("https://github.com/altansayan\n",           style="dim blue")
    body.append("\n")
    body.append("MockJutsu - Api\n",                         style="dim white")
    body.append("https://github.com/altansayan/mock-jutsu-api\n", style="dim blue")
    body.append("\n")
    body.append("MockJutsu JMeter\n",                        style="dim white")
    body.append("https://github.com/altansayan/mock-jutsu-jmeter\n", style="dim blue")
    body.append("\n")
    body.append("MockJutsu Postman Collection\n",            style="dim white")
    body.append("https://github.com/altansayan/mock-jutsu-postman-collection\n", style="dim blue")
    body.append("\n")
    body.append("Licensed under the MIT License\n", style="dim white")
    body.append("Copyright (c) 2025 Altan Sezer Ayan - A.S.A", style="dim white")

    console.print(Panel(body, border_style="bright_green", padding=(1, 2)))

# ---------------------------------------------------------------------------
# Reference table
# (type, category, locale_aware, example_output, cli_cmd, description, extra_params)
# cli_cmd: command string shown in the CLI COMMAND column (no "mockjutsu" prefix)
# ---------------------------------------------------------------------------
_REFERENCE = [
    ('tckn'           , 'Identity'     , False, '45678901234'           , 'generate tckn'                 , 'Turkish ID (TCKN) with Modulo 10/11 validation.', '--prefix (string)'),
    ('ykn'            , 'Identity'     , False, '99012345678'           , 'generate ykn'                  , 'Foreigner ID (YKN) with Modulo 10/11 validation.', '-'),
    ('nationalid'     , 'Identity'     , True , '(by locale)'           , 'generate nationalid --locale TR', 'Generic National ID for the specified locale.', '-'),
    ('vkn'            , 'Identity'     , False, '1234567890'            , 'generate vkn'                  , 'Tax Identification Number (VKN) with Modulo 11 validation.', '-'),
    ('taxid'          , 'Identity'     , True , '(by locale)'           , 'generate taxid --locale TR'    , 'Generic Tax ID for the specified locale.', '-'),
    ('employer_id'    , 'Identity'     , True , '(by locale)'           , 'generate employer_id --locale TR', 'Employer Registration ID with algorithmic checks.', '-'),
    ('insurance_id'   , 'Identity'     , True , '(by locale)'           , 'generate insurance_id --locale TR', 'Social Security / Insurance ID for specified locale.', '-'),
    ('sgk'            , 'Identity'     , False, '34-0012345-1.01-02'    , 'generate sgk'                  , 'Turkish Social Security (SGK) number format.', '-'),
    ('mersis'         , 'Identity'     , False, '1234567890012345'      , 'generate mersis'               , 'Turkish Central Registry System (MERSIS) number.', '-'),
    ('ssn'            , 'Identity'     , False, '234-56-7890'           , 'generate ssn'                  , 'US Social Security Number (SSN) with area/group rules.', '-'),
    ('ein'            , 'Identity'     , False, '12-3456789'            , 'generate ein'                  , 'US Employer Identification Number (EIN) format.', '-'),
    ('nin'            , 'Identity'     , False, 'AB 12 34 56 C'         , 'generate nin'                  , 'UK National Insurance Number (NIN) format.', '-'),
    ('utr'            , 'Identity'     , False, '1234567890'            , 'generate utr'                  , 'UK Unique Taxpayer Reference (UTR) with Modulo 11 check.', '-'),
    ('crn'            , 'Identity'     , False, '12345678'              , 'generate crn'                  , 'UK Company Registration Number (CRN) format.', '-'),
    ('paye'           , 'Identity'     , False, '123/AB4567'            , 'generate paye'                 , 'UK PAYE (Pay As You Earn) reference format.', '-'),
    ('ust_id'         , 'Identity'     , False, 'DE123456789'           , 'generate ust_id'               , 'German VAT ID (USt-IdNr.) with ISO 7064 check.', '-'),
    ('ustid'          , 'Identity'     , False, 'DE123456789'           , 'generate ustid'                , 'Alias for German VAT ID.', '-'),
    ('hrb'            , 'Identity'     , False, 'HRB 123456'            , 'generate hrb'                  , 'German Commercial Register (Handelsregister) ID.', '-'),
    ('rvn'            , 'Identity'     , False, '65 070892 W 1235'      , 'generate rvn'                  , 'German Pension Insurance Number (RVNR) format.', '-'),
    ('siren'          , 'Identity'     , False, '732829320'             , 'generate siren'                , 'French Business Identifier (SIREN) with Luhn validation.', '-'),
    ('siret'          , 'Identity'     , False, '73282932000074'        , 'generate siret'                , 'French Establishment Identifier (SIRET) with Luhn validation.', '-'),
    ('tva'            , 'Identity'     , False, 'FR73732829320'         , 'generate tva'                  , 'French VAT Number (TVA) with ISO 7064 check.', '-'),
    ('inn'            , 'Identity'     , False, '7707083893'            , 'generate inn'                  , 'Russian Tax ID (INN) with checksum validation.', '-'),
    ('inn_individual' , 'Identity'     , False, '7707083893'            , 'generate inn_individual'       , 'Russian Individual Tax ID (INN) with checksum.', '-'),
    ('snils'          , 'Identity'     , False, '112-233-445 95'        , 'generate snils'                , 'Russian Pension Insurance (SNILS) with checksum.', '-'),
    ('kpp'            , 'Identity'     , False, '770701001'             , 'generate kpp'                  , 'Russian Industrial Enterprises Code (KPP) format.', '-'),
    ('ogrn'           , 'Identity'     , False, '1027700132195'         , 'generate ogrn'                 , 'Russian Primary State Registration Number (OGRN).', '-'),
    ('firstname'      , 'Name'         , True , 'Emre'                  , 'generate firstname --locale TR', 'Random first name for the specified locale.', '--gender (male, female)'),
    ('lastname'       , 'Name'         , True , 'Yilmaz'                , 'generate lastname --locale TR' , 'Random last name for the specified locale.', '--gender (male, female)'),
    ('fullname'       , 'Name'         , True , 'Emre Kaya'             , 'generate fullname --locale TR' , 'Full name (First + Last) for the specified locale.', '--gender (male, female)'),
    ('patronymic'     , 'Name'         , True , 'Ivanovich'             , 'generate patronymic --locale RU', 'Patronymic middle name (common in Russian locale).', '--gender (male, female)'),
    ('passport'       , 'Document'     , False, 'P1234567'              , 'generate passport'             , 'Generic passport number format.', '-'),
    ('license'        , 'Document'     , False, '654321'                , 'generate license'              , 'Generic driver license number format.', '-'),
    ('age'            , 'Demographic'  , False, '34'                    , 'generate age'                  , 'Random human age (typically 18-90).', '--min, --max (int)'),
    ('gender'         , 'Demographic'  , False, 'Male'                  , 'generate gender'               , 'Binary gender values (Male/Female).', '-'),
    ('birthdate'      , 'Demographic'  , False, '1990-05-14'            , 'generate birthdate'            , 'Random date of birth in YYYY-MM-DD format.', '-'),
    ('cardnum'        , 'Financial'    , False, '4532 0151 9283 1029'   , 'generate cardnum --network visa', 'Credit card number with Luhn algorithm validation.', '--network (visa|mc|amex|troy|mir|jcb|discover|unionpay|maestro)'),
    ('cardtype'       , 'Financial'    , False, 'Credit'                , 'generate cardtype'             , 'Payment card type (Credit/Debit/Prepaid).', '-'),
    ('cardstatus'     , 'Financial'    , False, 'Active'                , 'generate cardstatus'           , 'Payment card status (Active/Blocked/Expired).', '-'),
    ('cardcategory'   , 'Financial'    , False, 'Gold'                  , 'generate cardcategory'         , 'Card level (Classic/Gold/Platinum/Infinite).', '-'),
    ('cardowner'      , 'Financial'    , True , 'JOHN SMITH'            , 'generate cardowner --locale TR', 'Cardholder name in appropriate format for locale.', '--gender (male, female)'),
    ('cvv3'           , 'Financial'    , False, '847'                   , 'generate cvv3'                 , '3-digit Card Verification Value (CVV/CVC).', '-'),
    ('cvv4'           , 'Financial'    , False, '1234'                  , 'generate cvv4'                 , '4-digit Card Verification Value for Amex.', '-'),
    ('pin'            , 'Financial'    , False, '7291'                  , 'generate pin'                  , '4-digit randomized Personal Identification Number.', '-'),
    ('expiry'         , 'Financial'    , False, '09/27'                 , 'generate expiry'               , 'Card expiry date (MM/YY) in the future.', '-'),
    ('expirymonth'    , 'Financial'    , False, '09'                    , 'generate expirymonth'          , 'Card expiry month (01-12).', '-'),
    ('expiryyear'     , 'Financial'    , False, '27'                    , 'generate expiryyear'           , 'Card expiry year (last 2 digits).', '-'),
    ('issuer'         , 'Financial'    , True , 'BosphorusBank A.S.'    , 'generate issuer --locale TR'   , 'Simulated bank or card issuing entity.', '-'),
    ('balance'        , 'Financial'    , False, '12450.75'              , 'generate balance'              , 'Random account balance with 2 decimal precision.', '--min, --max (float)'),
    ('iban'           , 'Financial'    , True , 'TR330006100519...'     , 'generate iban --locale TR'     , 'International Bank Account Number (IBAN) with Modulo 97 check.', '-'),
    ('sepa_qr'        , 'Financial'    , True , 'BCD\n002...'           , 'generate sepa_qr --locale DE'  , 'SEPA Credit Transfer QR code (EPC standard).', '-'),
    ('emv_qr_p2p'     , 'Financial'    , True , '000201010211...'       , 'generate emv_qr_p2p --locale TR', 'EMV QRCPS P2P payment QR code (TRQR compatible).', '-'),
    ('emv_qr_atm'     , 'Financial'    , True , '000201010212...'       , 'generate emv_qr_atm --locale DE', 'EMV QRCPS ATM cash-out QR code.', '-'),
    ('emv_qr_pos'     , 'Financial'    , True , '000201010211...'       , 'generate emv_qr_pos --locale FR', 'EMV QRCPS Merchant/POS QR code.', '-'),
    ('3ds_cavv'       , 'Financial'    , False, 'AAABBIIFmAAAAAAEggWY...', 'generate 3ds_cavv'            , '3D Secure 2.0 Cardholder Authentication Verification Value (CAVV).', '-'),
    ('3ds_eci'        , 'Financial'    , False, '05 (Visa) / 02 (MC)'   , 'generate 3ds_eci --network visa', '3D Secure Electronic Commerce Indicator (ECI) flag.', '--network (visa|mc|amex|jcb)'),
    ('cardnetwork'    , 'Financial'    , False, 'VISA / MASTERCARD'     , 'generate cardnetwork'          , 'Credit card network name (Visa, MC, Amex, etc.).', '-'),
    ('track1_data'    , 'Hardware'     , False, '%B4532...^MOCKJDOE/MOCKJJOHN^28120...?', 'generate track1_data'  , 'ISO/IEC 7813 Track 1 magnetic stripe (PAN^Name^YYMM+SC). MOCKJ marker in name.', '-'),
    ('track2_data'    , 'Hardware'     , False, ';4532...=2812201...?'  , 'generate track2_data'          , 'ISO/IEC 7813 Track 2 magnetic stripe (PAN=Expiry+ServiceCode+DD).', '-'),
    ('chip_data'      , 'Hardware'     , True , '9F0206000000001000...' , 'generate chip_data --locale TR' , 'Simulated EMV chip (ICC) TLV data. Currency (5F2A) is locale-aware.', '--locale'),
    ('pin_block'      , 'Hardware'     , False, '041234FFFFFFFFFF'      , 'generate pin_block'            , 'ISO 9564-1 Format 0 PIN block — format nibble 0, PIN digits, 0xF fill.', '-'),
    ('pin_block_fmt3' , 'Hardware'     , False, '3412347293819283'      , 'generate pin_block_fmt3'       , 'ISO 9564-1 Format 3 PIN block — format nibble 3, PIN digits, random fill.', '-'),
    ('--Security--'   , ''             , False, ''                      , ''                              , '', ''),
    ('cef_log'        , 'Security'     , False, 'CEF:0|Cisco|ASA|9.16|...', 'generate cef_log'           , 'ArcSight CEF log line — vendor, product, severity 0-10, src/dst IPs.', '-'),
    ('x509_cert'      , 'Security'     , False, '{"subject":"CN=api...",...}', 'generate x509_cert'      , 'X.509 certificate fields (JSON): subject, issuer, serial, validity, fingerprint, SANs.', '-'),
    ('pcap_hex'       , 'Security'     , False, 'ff ff 08 00 45 00 ...' , 'generate pcap_hex'             , 'Wireshark-style pcap hex dump of a mock Ethernet+IPv4+TCP frame.', '-'),
    ('creditor_ref'   , 'Banking'      , False, 'RF18539007547034'      , 'generate creditor_ref'         , 'ISO 11649 Creditor Reference: RF + 2-digit MOD-97 check + 3-21 alphanumeric chars.', '-'),
    ('vat_number'     , 'Identity'     , True , 'TR1234567890'          , 'generate vat_number --locale TR', 'EU/Global VIES VAT number with country prefix (TR/DE/FR/UK/US/RU).', '-'),
    ('--Aviation--'   , ''             , False, ''                      , ''                              , '', ''),
    ('iata_ticket'    , 'Aviation'     , False, '0012345678902'         , 'generate iata_ticket'          , 'IATA Electronic Ticket Number (ETN): 3-digit airline code + 9-digit serial + MOD-7 check digit.', '-'),
    ('imo_number'     , 'Aviation'     , False, 'IMO 9074729'           , 'generate imo_number'           , 'IMO Ship Registration Number: 7-digit identifier with MOD-10 weighted check digit.', '-'),
    ('pnr_code'       , 'Aviation'     , False, 'K7XR2B'                , 'generate pnr_code'             , 'GDS Passenger Name Record (PNR) locator: 6-char uppercase alphanumeric, no ambiguous chars.', '-'),
    ('--WebAuthn--'   , ''             , False, ''                       , ''                              , '', ''),
    ('webauthn_credential', 'WebAuthn' , False, '{"id":"aB3x...","type":"public-key",...}', 'generate webauthn_credential', 'FIDO2/WebAuthn registration response: CBOR attestationObject + clientDataJSON (webauthn.create), all fields base64url encoded.', '-'),
    ('fido2_assertion', 'WebAuthn'     , False, '{"id":"kR7m...","type":"public-key",...}', 'generate fido2_assertion'    , 'FIDO2/WebAuthn authentication response: 37-byte authenticatorData + DER ECDSA signature + userHandle, base64url encoded.', '-'),
    ('--Wallet--'     , ''             , False, ''                       , ''                              , '', ''),
    ('eth_wallet'     , 'Wallet'       , False, '{"private_key":"a1b2...","address":"0xAb...",...}', 'generate eth_wallet', 'Full ETH wallet: secp256k1 scalar mult → Keccak-256 → EIP-55 checksummed address. JSON with private_key, public_key, address.', '-'),
    ('btc_wallet'     , 'Wallet'       , False, '{"private_key":"c3d4...","wif":"K2...","address":"1A...",...}', 'generate btc_wallet', 'Full BTC wallet: secp256k1 → SHA256+RIPEMD160 → P2PKH Base58Check + compressed WIF. JSON with private_key, wif, public_key, address.', '-'),
    ('sol_wallet'     , 'Wallet'       , False, '{"private_key":"e5f6...","address":"4Aa...",...}', 'generate sol_wallet', 'Full Solana wallet: Ed25519 scalar mult → base58 address. JSON with private_key, public_key, address, keypair (Phantom format).', '-'),
    ('--AIVector--'  , ''             , False, ''                           , ''                              , '', ''),
    ('ai_embedding'  , 'AI Vector'    , False, '[0.021,-0.184,...]'         , 'generate ai_embedding'         , '1536-dim L2-normalized float vector (OpenAI Ada-002 / Pinecone compatible). JSON array of floats with |v|₂=1.', '--dims (int)'),
    ('ai_vector'     , 'AI Vector'    , False, '[0.089,-0.234,...]'         , 'generate ai_vector'            , 'N-dim L2-normalized unit vector for embedding models (default 384-dim). Configurable via --dims.', '--dims (int)'),
    ('ai_sparse_vector', 'AI Vector'  , False, '{"indices":[...],"values":[...]}', 'generate ai_sparse_vector', 'Sparse {indices, values} vector with L2-normalized positive weights for hybrid search (Pinecone/Qdrant). 128 non-zero entries in 10k-dim space.', '--dims (int), --nnz (int)'),
    ('--OIDC--'       , ''             , False, ''                           , ''                              , '', ''),
    ('oidc_token_set' , 'OIDC'         , False, '{"token":"eyJ...","jwks":{...},"kid":"...","claims":{...}}', 'generate oidc_token_set', 'ES256 key pair (P-256) → signed JWT + verifiable JWKS (kid linked). Full OIDC claims: iss, sub, aud, exp, iat, jti, email.', '-'),
    ('jwks'           , 'OIDC'         , False, '{"keys":[{"kty":"EC","crv":"P-256",...}]}', 'generate jwks', 'Standalone JWK Set — fresh P-256 EC public key (kty=EC, crv=P-256, use=sig, alg=ES256). Mock /.well-known/jwks.json endpoint.', '-'),
    ('oidc_token'     , 'OIDC'         , False, 'eyJhbGciOiJIUzI1NiJ9...'    , 'generate oidc_token'           , 'HS256 JWT with standard OIDC claims (iss, sub, aud, exp, iat, jti). Fast symmetric signing — no key pair needed.', '-'),
    ('--BankStatement--', ''           , False, ''                           , ''                              , '', ''),
    ('mt940'          , 'BankStatement', True , ':20:REF...\n:60F:C...\n:62F:C...', 'generate mt940 --locale TR', 'SWIFT MT940 bank statement: :20: :25: :28C: :60F: :61: :86: :62F: fields. Comma decimal (500,00). 2-5 transactions.', '-'),
    ('camt053'        , 'BankStatement', True , '<?xml...camt.053...'        , 'generate camt053 --locale TR'  , 'ISO 20022 CAMT.053 XML bank statement: MsgId, IBAN, OPBD/CLBD balances, Ntry entries. Dot decimal (500.00).', '-'),
    ('--EDI--'        , ''             , False, ''                           , ''                              , '', ''),
    ('edi_850'        , 'EDI'          , True , 'ISA*00*...*:~\nGS*PO*...'  , 'generate edi_850'              , 'ANSI X12 EDI 850 Purchase Order: ISA/GS/ST/BEG/N1/PO1/CTT/SE/GE/IEA. ISA13==IEA02, GS06==GE02, SE01==segment count.', '-'),
    ('edifact_orders' , 'EDI'          , True , "UNB+UNOC:3+...\nUNH+..."   , 'generate edifact_orders'       , "UN/EDIFACT ORDERS D96A: UNB/UNH/BGM/DTM/NAD/LIN/QTY/PRI/UNS/CNT/UNT/UNZ. UNT01==seg count, UNZ02==UNB ctrl ref.", '-'),
    ('--EventSourcing--', ''           , False, ''                           , ''                              , '', ''),
    ('event_stream'   , 'EventSourcing', False, '[{"event_type":"login",...}]', 'generate event_stream'         , 'Markov Chain user-journey event sequence (Login→Browse→Cart→Checkout→Logout). JSON array with correlation_id, timestamps, payloads.', '-'),
    ('cdc_event'      , 'EventSourcing', False, '{"op":"u","before":{...},"after":{...}}', 'generate cdc_event', 'Debezium-style CDC event (INSERT/UPDATE/DELETE). op c/u/d, ts_ms, source db+table, before/after payloads.', '-'),
    ('--Telemetry--'  , ''             , False, ''                           , ''                              , '', ''),
    ('fdr_record'     , 'Telemetry'    , False, '{"flight_id":...,"samples":[{"pitch":2.1,...}]}', 'generate fdr_record', 'Flight Data Recorder time-series: pitch/roll/yaw/altitude_ft/speed_kts/vspeed_fpm/g_force. Physics-constrained bounded random walk (10 Hz).', '-'),
    ('drone_telemetry', 'Telemetry'    , False, '{"drone_id":...,"samples":[{"lat":...,"alt_m":...}]}', 'generate drone_telemetry', 'Drone telemetry time-series: lat/lon/alt_m/pitch/roll/yaw/speed_ms/battery_pct/rssi. Battery monotonically decreasing (20 Hz).', '-'),
    ('--OHLCV--'       , ''             , False, ''                           , ''                              , '', ''),
    ('ohlcv_candles'  , 'OHLCV'        , False, '{"symbol":"AAPL","interval":"1h","candles":[{"t":"...","o":150.23,"h":151.45,"l":149.87,"c":150.89,"v":1234567}]}', 'generate ohlcv_candles', 'OHLCV candlestick series via Geometric Brownian Motion: H>=max(O,C), L<=min(O,C), Open[i]=Close[i-1]. 10-30 candles, intervals: 1m/5m/15m/1h/4h/1d.', '-'),
    ('market_tick'    , 'OHLCV'        , False, '{"symbol":"AAPL","price":150.23,"bid":150.20,"ask":150.25,"side":"buy","size":100}', 'generate market_tick', 'Individual exchange trade tick: bid < price <= ask, positive spread, Lee-Ready side (buy/sell), lot size, sequence number.', '-'),
    ('--MRZ--'        , ''             , False, ''                           , ''                              , '', ''),
    ('mrz_td3'        , 'MRZ'          , False, '{"mrz_type":"TD3","lines":["P<TUR...","ABCD123456<..."]}', 'generate mrz_td3', 'ICAO 9303 Passport TD3 MRZ: 2 lines × 44 chars. YYMMDD DOB/expiry, personal number, composite check digit (ICAO 9303 Part 3).', '-'),
    ('mrz_td1'        , 'MRZ'          , False, '{"mrz_type":"TD1","lines":["I<TUR...","...","SMITH<<JOHN<"]}', 'generate mrz_td1', 'ICAO 9303 ID Card TD1 MRZ: 3 lines × 30 chars. Doc number, DOB, expiry, composite check digit (ICAO 9303 Part 5).', '-'),
    ('--TLE--'         , ''             , False, ''                           , ''                              , '', ''),
    ('tle_satellite'   , 'TLE'          , False, 'name:MOCKSAT-42 | orbit:LEO | incl:51.6434 | raan:339.7939 | ecc:0.0001785 | mm:15.49320826 | line1:1 25544U... | line2:2 25544...', 'generate tle_satellite', 'Two-Line Element Set (TLE) per NORAD/USSPACECOM standard: LEO/MEO/GEO/SSO/HEO orbit types, physics-consistent parameters. NORAD Modulo-10 checksum verified on both 69-char lines.', '-'),
    ('--Automotive--'  , ''             , False, ''                           , ''                              , '', ''),
    ('can_frame'       , 'Automotive'   , False, 'frame_type:standard | can_id:0x1A2 | dlc:4 | data_hex:DEADBEEF | crc15:12345 | socketcan:1A2#DEADBEEF', 'generate can_frame', 'Raw CAN Bus frame (ISO 11898-1): standard (11-bit) or extended (29-bit) ID, DLC 0-8, CRC-15 polynomial 0xC599 verified over SOF+ID+Control+Data. SocketCAN notation.', '-'),
    ('obd2_response'   , 'Automotive'   , False, 'ecu_id:7E8 | rpm:2500.0 | speed_kmh:80 | coolant:90C | dtcs:[] | pids:[{pid:0C,crc15:...}]', 'generate obd2_response', 'OBD-II live snapshot (SAE J1979 / ISO 15765-4): Mode 01 PIDs (RPM, Speed, Coolant, Throttle, Engine Load, Fuel Level). Each PID is a CAN frame (0x7E8) with verified CRC-15. Optional DTCs.', '-'),
    ('--E-Invoice--'   , ''             , False, ''                           , ''                              , '', ''),
    ('ubl_invoice'     , 'EInvoice'     , False, 'invoice_id:INV-2026-00001 | uuid:UUID | currency:TRY | tax_rate:18 | net:1000.00 | gross:1180.00 | xml:<?xml...Invoice...', 'generate ubl_invoice', 'OASIS UBL 2.1 Invoice XML (Turkey GIB e-fatura): consistent amounts (net+tax=gross), 1-5 line items, INV-YYYY-NNNNN ID, uppercase UUID, TaxTotal, LegalMonetaryTotal.', '-'),
    ('xmldsig'         , 'EInvoice'     , False, 'sig_id:Signature-A1B2C3D4 | digest_value:44-char-base64 | signature_value:344-char-base64 | xml:<ds:Signature...', 'generate xmldsig', 'W3C XML Digital Signature (XMLDSig) enveloped: RSA-SHA256 signature, SHA-256 digest, C14N canonicalization. DigestValue=44 chars (32 bytes), SignatureValue=344 chars (256 bytes).', '-'),
    ('--GameDev--'     , ''             , False, ''                           , ''                              , '', ''),
    ('quaternion'     , 'GameDev'      , False, '{"x":0.12345678,"y":0.45678901,"z":0.78901234,"w":0.34567890,"magnitude":1.0,"euler_degrees":{"pitch":12.3,"yaw":45.6,"roll":78.9}}', 'generate quaternion', 'L2-normalized unit quaternion (Gaussian sampling): sqrt(x²+y²+z²+w²)=1.0. Pre-computed Euler angles (ZYX, degrees). Unity/Unreal compatible.', '-'),
    ('navmesh_path'   , 'GameDev'      , False, '{"start":{"x":10.5,"y":0.0,"z":20.3},"end":{...},"waypoints":[...],"total_distance":87.3,"waypoint_count":8}', 'generate navmesh_path', 'A*-compatible NavMesh waypoint path: 3-15 waypoints, random heading ±60° turns, 5-25 unit steps, terrain height bounded ±5. start=waypoints[0], end=waypoints[-1].', '-'),
    ('--Prometheus--'  , ''             , False, ''                           , ''                              , '', ''),
    ('prometheus_metrics'  , 'Prometheus', False, '{"exposition":"# HELP process_cpu_seconds_total...\\nhttp_requests_total{...} 1234\\n","format":"prometheus",...}', 'generate prometheus_metrics', 'Prometheus text exposition: process CPU/memory, HTTP counter (method/path/status), HTTP histogram (monotonic buckets, +Inf==count), Go runtime metrics.', '-'),
    ('openmetrics_snapshot', 'Prometheus', False, '{"exposition":"# HELP ...\\n# EOF\\n","format":"openmetrics",...}', 'generate openmetrics_snapshot', 'OpenMetrics exposition (Prometheus superset): same metric families, mandatory # EOF terminator. Compatible with OTLP/Grafana Mimir.', '-'),
    ('--NMEA--'       , ''             , False, ''                           , ''                              , '', ''),
    ('nmea_gpgga'    , 'NMEA'         , False, '{"sentence":"$GPGGA,123519.00,4807.0381,N,01131.0000,E,1,08,0.9,545.4,M,46.9,M,,*XX","type":"GPGGA",...}', 'generate nmea_gpgga', 'GPGGA GPS Fix Data sentence: lat/lon (DDMM.MMMM), fix quality, satellite count, HDOP, altitude. XOR checksum validated.', '-'),
    ('nmea_gprmc'    , 'NMEA'         , False, '{"sentence":"$GPRMC,123519.00,A,4807.0381,N,01131.0000,E,0.0,25.3,120526,,*XX","type":"GPRMC",...}', 'generate nmea_gprmc', 'GPRMC Recommended Minimum GPS Data sentence: status A, lat/lon, speed (knots), course, date (DDMMYY). XOR checksum validated.', '-'),
    ('--PenTest--'    , ''             , False, ''                           , ''                              , '', ''),
    ('jwt_attack'     , 'PenTest'      , False, '{"token":"eyJ...","attack_type":"none_alg","description":"..."}', 'generate jwt_attack', 'Crafted JWT attack payloads: none_alg (CVE bypass), expired, invalid_signature (bit-flip), alg_confusion (RS256/HS256), kid_injection (path/SQL), empty_password.', '-'),
    ('asn1_fuzz'      , 'PenTest'      , False, '{"hex":"3008...","fuzz_type":"truncated","length":10}', 'generate asn1_fuzz', 'ASN.1/DER malformed payloads: truncated, overflow_length (long-form 0x82), wrong_tag, nested_mismatch, zero_length, random_bytes.', '-'),
    ('regex_string'   , 'Meta'         , False, 'A4F-2819'               , 'generate regex_string'         , 'Reverse regex engine: generates a string matching any regex pattern (use --pattern flag).', '--pattern (regex)'),
    ('phone'          , 'Contact'      , True , '+905325551234'         , 'generate phone --locale TR'    , 'Full E.164 formatted telephone number.', '-'),
    ('phone_country'  , 'Contact'      , True , '+90'                   , 'generate phone_country --locale TR', 'International telephone country dial code.', '-'),
    ('phone_area'     , 'Contact'      , True , '532'                   , 'generate phone_area --locale TR', 'Localized telephone area/operator code.', '-'),
    ('phone_local'    , 'Contact'      , True , '5551234'               , 'generate phone_local --locale TR', 'Local telephone number part.', '-'),
    ('address_city'   , 'Contact'      , True , 'Istanbul'              , 'generate address_city --locale TR', 'Major city name for the specified locale.', '-'),
    ('address_street' , 'Contact'      , True , 'Bagdat Caddesi'        , 'generate address_street --locale TR', 'Realistic street/avenue name for the locale.', '-'),
    ('address_full'   , 'Contact'      , True , 'Istanbul, Bagdat Cad.' , 'generate address_full --locale TR', 'Complete mailing address for the specified locale.', '-'),
    ('postalcode'     , 'Contact'      , True , '34500'                 , 'generate postalcode --locale TR', 'Locale-specific postal/zip code format.', '-'),
    ('plate'          , 'Contact'      , True , '34 ABC 123'            , 'generate plate --locale TR'    , 'Vehicle license plate format for the specified country.', '-'),
    ('email'          , 'Contact'      , True , 'user42@gmail.com'      , 'generate email --locale TR'    , 'Randomized email address using common domains.', '-'),
    ('swift'          , 'Banking'      , True , 'DEUTDEDB'              , 'generate swift --locale TR'    , 'ISO 9362 Business Identifier Code (BIC/SWIFT).', '-'),
    ('bic'            , 'Banking'      , True , 'DEUTDEDB'              , 'generate bic --locale TR'      , 'Alias for SWIFT/BIC code.', '-'),
    ('sort_code'      , 'Banking'      , False, '20-00-00'              , 'generate sort_code'            , 'UK 6-digit bank sort code format.', '-'),
    ('routing_number' , 'Banking'      , False, '021000021'             , 'generate routing_number'       , 'US 9-digit ABA routing transit number with checksum.', '-'),
    ('bik_code'       , 'Banking'      , False, '044525225'             , 'generate bik_code'             , 'Russian Bank Identification Code (BIK).', '-'),
    ('bank_name'      , 'Banking'      , True , 'Novex Trust Corp'      , 'generate bank_name --locale TR', 'Randomized bank name for the specified locale.', '-'),
    ('transaction'    , 'Banking'      , True , '{ref, iban*2, amount}' , 'generate transaction --locale TR', 'Complex banking transaction record simulation.', '-'),
    ('company_name'   , 'Corporate'    , True , 'Fischer Tech. GmbH'    , 'generate company_name --locale TR', 'Official business name for the specified locale.', '-'),
    ('job_title'      , 'Corporate'    , True , 'Software Engineer'     , 'generate job_title --locale TR', 'Professional job title for the specified locale.', '-'),
    ('jobtitle'       , 'Corporate'    , True , 'Software Engineer'     , 'generate jobtitle --locale TR' , 'Alias for job title.', '-'),
    ('occupation'     , 'Corporate'    , True , 'Software Engineer'     , 'generate occupation --locale TR', 'Professional occupation classification.', '-'),
    ('bloodtype'      , 'Health'       , False, 'A+'                    , 'generate bloodtype'            , 'Human blood groups (ABO and Rh factor).', '-'),
    ('blood_type'     , 'Health'       , False, 'A+'                    , 'generate blood_type'           , 'Alias for blood type.', '-'),
    ('nhs_number'     , 'Health'       , False, '943 476 5919'          , 'generate nhs_number'           , 'UK National Health Service number with Modulo 11 check.', '-'),
    ('nhsnumber'      , 'Health'       , False, '943 476 5919'          , 'generate nhsnumber'            , 'Alias for NHS number.', '-'),
    ('icd10'          , 'Health'       , False, 'J45.909'               , 'generate icd10'                , 'International Classification of Diseases 10th Revision (ICD-10) code.', '-'),
    ('bmi'            , 'Health'       , False, '22.5'                  , 'generate bmi'                  , 'Body Mass Index (BMI) calculated value.', '-'),
    ('height'         , 'Health'       , True , '178 cm / 5\'10"'       , 'generate height --locale TR'   , 'Localized height measurement (cm/inch).', '-'),
    ('weight'         , 'Health'       , True , '74 kg / 163 lbs'       , 'generate weight --locale TR'   , 'Localized weight measurement (kg/lbs).', '-'),
    ('currency'       , 'Commerce'     , True , '{code:TRY, symbol:TL}' , 'generate currency --locale TR' , 'Localized currency details (ISO code and symbol).', '-'),
    ('tax_rate'       , 'Commerce'     , True , '{name:KDV, rate:20}'   , 'generate tax_rate --locale TR' , 'Localized tax names and rates (e.g., KDV, VAT).', '-'),
    ('taxrate'        , 'Commerce'     , True , '{name:KDV, rate:20}'   , 'generate taxrate --locale TR'  , 'Alias for tax rate.', '-'),
    ('invoice_number' , 'Commerce'     , True , 'INV-2024-001234'       , 'generate invoice_number --locale TR', 'Localized invoice number formats.', '-'),
    ('invoicenumber'  , 'Commerce'     , True , 'INV-2024-001234'       , 'generate invoicenumber --locale TR', 'Alias for invoice number.', '-'),
    ('vin'            , 'Commerce'     , True , 'WBA3A5C5XMD123456'     , 'generate vin --locale TR'      , 'Vehicle Identification Number (VIN) with ISO 3779 checksum.', '-'),
    ('vehicle'        , 'Commerce'     , True , '{make,model,year,vin}' , 'generate vehicle --locale TR'  , 'Comprehensive vehicle data including make/model.', '-'),
    ('uuid'           , 'Meta'         , False, '550e8400-e29b-41d4-...', 'generate uuid'                 , 'RFC 4122 compliant Universally Unique Identifier (UUID v4).', '-'),
    ('requestid'      , 'Meta'         , False, '550e8400-e29b-41d4-...', 'generate requestid'            , 'Unique request identifier (UUID format).', '-'),
    ('correlationid'  , 'Meta'         , False, '550e8400-e29b-41d4-...', 'generate correlationid'        , 'Tracing correlation identifier (UUID format).', '-'),
    ('sessionid'      , 'Meta'         , False, '550e8400-e29b-41d4-...', 'generate sessionid'            , 'Unique session identifier (UUID format).', '-'),
    ('idempotencykey' , 'Meta'         , False, '550e8400-e29b-41d4-...', 'generate idempotencykey'       , 'API idempotency key for safe retries (UUID format).', '-'),
    ('deviceid'       , 'Meta'         , False, '550E8400-E29B-41D4-...', 'generate deviceid'             , 'Unique hardware/device identifier (Uppercase UUID).', '-'),
    ('timestamp'      , 'Meta'         , False, '1714900000'            , 'generate timestamp'            , 'Current Unix epoch timestamp (seconds).', '-'),
    ('timestamp_iso'  , 'Meta'         , False, '2024-05-05T14:30:00'   , 'generate timestamp_iso'        , 'ISO 8601 formatted date-time string.', '-'),
    ('ipv4'           , 'Meta'         , False, '192.168.1.42'          , 'generate ipv4'                 , 'Random public or private IPv4 address.', '-'),
    ('ipv6'           , 'Meta'         , False, 'fe80:0000:0000:...'    , 'generate ipv6'                 , 'RFC 4291 compliant IPv6 address.', '-'),
    ('browser_name'   , 'Meta'         , False, 'Chrome'                , 'generate browser_name'         , 'Common web browser names.', '-'),
    ('browser_version', 'Meta'         , False, '124.0.6367.78'         , 'generate browser_version'      , 'Simulated browser version strings.', '-'),
    ('browser_engine' , 'Meta'         , False, 'Blink'                 , 'generate browser_engine'       , 'Web browser layout engines (Blink, WebKit, etc.).', '-'),
    ('useragent'      , 'Meta'         , False, 'Mozilla/5.0 ...'       , 'generate useragent'            , 'Realistic browser User-Agent strings.', '-'),
    ('jwt'            , 'Meta'         , False, 'eyJ....eyJ....sig'     , 'generate jwt'                  , 'Mock JSON Web Token (JWT) with header/payload/signature structure.', '-'),
    ('bearertoken'    , 'Meta'         , False, 'Bearer eyJ....sig'     , 'generate bearertoken'          , 'HTTP Bearer authorization token.', '-'),
    ('hash'           , 'Meta'         , False, 'e3b0c44298fc...(64hex)', 'generate hash --algorithm sha256', 'Cryptographic hash values for various algorithms.', '--algorithm (md5|sha1|sha224|sha256|sha384|sha512|sha3-224|sha3-256|sha3-384|sha3-512|crc32|adler32|crc16)'),
    ('mac_address'    , 'Meta'         , False, 'A4:C3:F0:3D:8E:21'     , 'generate mac_address'          , '48-bit hardware MAC address (IEEE 802).', '-'),
    ('url'            , 'Meta'         , True , 'https://api-42.co.uk/..', 'generate url --locale TR'      , 'Localized web URLs.', '-'),
    ('domain'         , 'Meta'         , True , 'test-77.com.tr'        , 'generate domain --locale TR'   , 'Localized domain names with regional TLDs.', '-'),
    ('color'          , 'Meta'         , False, '#3A7BF0'               , 'generate color'                , 'Hexadecimal or named color values.', '--format (hex|rgb|hsl|name)'),
    ('clientversion'  , 'Meta'         , False, '2.4.1'                 , 'generate clientversion'        , 'Software client versioning (SemVer).', '-'),
    ('signature'      , 'Meta'         , False, 'a1b2c3d4... (hex)'     , 'generate signature'            , 'HMAC-SHA256 digital signature hex string.', '--secret (string), --payload (string)'),
    ('apppassword'    , 'Meta'         , False, '481302'                , 'generate apppassword'          , 'One-time application passwords / PINs.', '-'),
    ('rfid_uid'       , 'RFID'         , False, '04:A3:B2:C1:D0:E5:F6'  , 'generate rfid_uid'             , 'RFID chip unique identifier (UID).', '-'),
    ('epc'            , 'RFID'         , False, '3034257BF400B718...'   , 'generate epc'                  , 'Electronic Product Code (EPC) for RFID tags.', '-'),
    ('rfid_tag'       , 'RFID'         , False, '{uid,standard,freq,mem}', 'generate rfid_tag'             , 'Comprehensive RFID tag data (UID, Freq, Memory).', '-'),
    ('nfc_uid'        , 'NFC'          , False, '04:A3:B2:C1:D0:E5:F6'  , 'generate nfc_uid'              , 'NFC chip unique identifier (UID).', '-'),
    ('nfc_atqa'       , 'NFC'          , False, '00:44'                 , 'generate nfc_atqa'             , 'NFC Answer to Request (ATQA) code.', '-'),
    ('nfc_sak'        , 'NFC'          , False, '20'                    , 'generate nfc_sak'              , 'NFC Select Acknowledge (SAK) code.', '-'),
    ('ndef_uri'       , 'NFC'          , False, '{raw_hex, decoded url}', 'generate ndef_uri'             , 'NFC Data Exchange Format (NDEF) URI record.', '-'),
    ('ndef_text'      , 'NFC'          , True , '{raw_hex, decoded txt}', 'generate ndef_text --locale TR', 'NFC Data Exchange Format (NDEF) Text record.', '-'),
    ('apdu'           , 'NFC'          , False, '{cla,ins,p1,p2,hex}'   , 'generate apdu'                 , 'Smart card Application Protocol Data Unit (APDU) commands.', '-'),
    ('nfc_tag'        , 'NFC'          , False, '{uid,atqa,sak,ndef}'   , 'generate nfc_tag'              , 'Comprehensive NFC tag details.', '-'),
    ('ir_nec'         , 'IR'           , False, '{addr,cmd,hex:20DF10EF}', 'generate ir_nec'               , 'Infrared NEC protocol signal data.', '-'),
    ('ir_rc5'         , 'IR'           , False, '{system,cmd,frame_bits}', 'generate ir_rc5'               , 'Infrared Philips RC5 protocol signal data.', '-'),
    ('ir_pronto'      , 'IR'           , False, '0000 006D 0022 0000 ..', 'generate ir_pronto'            , 'Infrared Pronto Hex format data.', '-'),
    ('ir_raw'         , 'IR'           , False, '{carrier_hz,pulses:[]}', 'generate ir_raw'               , 'Infrared raw pulse/space timing data.', '-'),
    ('--Wireless--'   , ''            , False, ''                      , ''                              , '', ''),
    ('mqtt_payload'   , 'Wireless'    , False, '{"device_id":"...","sensor_type":"temperature",...}', 'generate mqtt_payload', 'IoT sensor MQTT payload JSON (device_id, timestamp, sensor readings, RSSI, battery).', '-'),
    ('lora_packet'    , 'Wireless'    , False, '40 a1 b2 c3 d4 00 ...' , 'generate lora_packet'          , 'LoRaWAN 1.0.x uplink MAC frame hex: MHDR(0x40) + FHDR + FPort + FRMPayload + MIC.', '-'),
    ('ean13'          , 'Barcode'      , True , '8680001234567'         , 'generate ean13 --locale TR'    , 'International Article Number (EAN-13) with checksum.', '-'),
    ('ean8'           , 'Barcode'      , True , '86812345'              , 'generate ean8 --locale TR'     , 'Compressed EAN-8 barcode with checksum.', '-'),
    ('upca'           , 'Barcode'      , False, '036000291452'          , 'generate upca'                 , 'Universal Product Code (UPC-A) with checksum.', '-'),
    ('isbn13'         , 'Barcode'      , False, '9780306406157'         , 'generate isbn13'               , 'International Standard Book Number (ISBN-13).', '-'),
    ('isbn10'         , 'Barcode'      , False, '0306406152'            , 'generate isbn10'               , 'Legacy ISBN-10 with checksum.', '-'),
    ('gs1_128'        , 'Barcode'      , False, '(01)...(17)...(10)...' , 'generate gs1_128'              , 'GS1-128 (formerly UCC/EAN-128) application identifiers.', '-'),
    ('imei'           , 'Telecom'      , False, '490154203237518'       , 'generate imei'                 , 'International Mobile Equipment Identity (IMEI) with Luhn.', '-'),
    ('imei2'          , 'Telecom'      , False, '49-015420-323751-8'    , 'generate imei2'                , 'IMEI in hyphenated format.', '-'),
    ('iccid'          , 'Telecom'      , True , '8990053412345678901'   , 'generate iccid --locale TR'    , 'SIM card Integrated Circuit Card Identifier (ICCID).', '-'),
    ('imsi'           , 'Telecom'      , True , '286011234567890'       , 'generate imsi --locale TR'     , 'International Mobile Subscriber Identity (IMSI).', '-'),
    ('msisdn'         , 'Telecom'      , True , '+905321234567'         , 'generate msisdn --locale TR'   , 'Mobile Station International Subscriber Directory Number (MSISDN).', '-'),
    ('isin'           , 'CapMarkets(Trading)'   , True , 'US0378331005'          , 'generate isin --locale US'     , 'International CapMarkets(Trading) Identification Number (ISO 6166).', '-'),
    ('cusip'          , 'CapMarkets(Trading)'   , False, '037833100'             , 'generate cusip'                , 'Committee on Uniform Security Identification Procedures ID.', '-'),
    ('sedol'          , 'CapMarkets(Trading)'   , False, '0263494'               , 'generate sedol'                , 'Stock Exchange Daily Official List (UK).', '-'),
    ('lei'            , 'CapMarkets(Trading)'   , False, '529900T8BM49AURSDO55'  , 'generate lei'                  , 'Legal Entity Identifier (ISO 17442).', '-'),
    ('fix_message'    , 'CapMarkets(Trading)'   , False, '8=FIX.4.4|9=...|35=D|...|10=NNN|', 'generate fix_message'          , 'FIX Protocol 4.4 New Order Single (MsgType=D) with valid BodyLength and CheckSum.', '-'),
    ('psd2_consent'   , 'CapMarkets(Trading)'   , True , 'eyJhbGci...<JWS>'               , 'generate psd2_consent --locale UK --amount 250.00', 'PSD2 / UK Open Banking v3.1 Payment Consent — compact JWS (HMAC-SHA256).', '--amount (float)'),
    ('btc_address'    , 'Crypto'       , False, '1A1zP1eP5QGefi2DMPTfTL5SLmv7Divf', 'generate btc_address'          , 'Bitcoin wallet address (P2PKH, P2SH, Bech32).', '-'),
    ('eth_address'    , 'Crypto'       , False, '0x5aAeb6053F3E94C9b9A0...', 'generate eth_address'          , 'Ethereum/EVM compatible wallet address.', '-'),
    ('crypto_address' , 'Crypto'       , False, '(btc or eth)'          , 'generate crypto_address --currency eth', 'Generic crypto address for specified currency.', '--currency (btc, eth)'),
    ('tx_hash'        , 'Crypto'       , False, 'a1b2c3...64hex'        , 'generate tx_hash --currency btc', 'Blockchain transaction hash (SHA-256/Keccak-256).', '--currency (btc, eth)'),
    ('block_hash'     , 'Crypto'       , False, '0x+64hex (eth)'        , 'generate block_hash --currency eth', 'Blockchain block hash identifier.', '--currency (btc, eth)'),
    ('mnemonic'       , 'Crypto'       , False, 'abandon ability able...', 'generate mnemonic --words 12' , 'BIP-39 mnemonic recovery phrase (seed phrase).', '--words (12, 15, 18, 21, 24)'),
    ('product_name'   , 'E-Commerce'   , False, 'Wireless Headphones'   , 'generate product_name'         , 'Randomized e-commerce product names.', '-'),
    ('sku'            , 'E-Commerce'   , False, 'AB-123456'             , 'generate sku'                  , 'Stock Keeping Unit (SKU) identifiers.', '-'),
    ('order_id'       , 'E-Commerce'   , False, 'ORD-A1B2C3D4E5F6'      , 'generate order_id'             , 'Unique e-commerce order identifiers.', '-'),
    ('tracking_number', 'E-Commerce'   , False, '9400111899223397522384', 'generate tracking_number --carrier usps', 'Logistic tracking numbers for major carriers.', '--carrier (fedex, ups, usps, dhl)'),
    ('dhl_tracking'   , 'E-Commerce'   , False, 'JD123456789'           , 'generate dhl_tracking'         , 'DHL Express tracking number format.', '-'),
    ('category'       , 'E-Commerce'   , False, 'Electronics'           , 'generate category'             , 'Product category classifications.', '-'),
    ('rating'         , 'E-Commerce'   , False, '4.5'                   , 'generate rating'               , 'Product rating scores (1.0 - 5.0).', '-'),
    ('latitude'       , 'Location'     , True , '39.925533'             , 'generate latitude --locale TR' , 'Geographic latitude coordinate.', '-'),
    ('longitude'      , 'Location'     , True , '32.866287'             , 'generate longitude --locale TR', 'Geographic longitude coordinate.', '-'),
    ('timezone'       , 'Location'     , True , 'Europe/Istanbul'       , 'generate timezone --locale TR' , 'IANA/Olson timezone identifiers.', '-'),
    ('country_code'   , 'Location'     , True , 'TR'                    , 'generate country_code --locale TR', 'ISO 3166-1 alpha-2 country codes.', '-'),
    ('coordinates'    , 'Location'     , True , '39.925533,32.866287'   , 'generate coordinates --locale TR', 'Combined Lat/Long coordinate pairs.', '-'),
    ('username'       , 'Social'       , False, 'cooldev42'             , 'generate username'             , 'Social media profile usernames.', '-'),
    ('handle'         , 'Social'       , False, '@cooldev42'            , 'generate handle'               , 'Social media profile handle with @ prefix.', '-'),
    ('hashtag'        , 'Social'       , False, '#mockjutsu'            , 'generate hashtag'              , 'Trending social media hashtags.', '-'),
    ('bio'            , 'Social'       , False, 'Building the future...' , 'generate bio'                 , 'Social media profile biography text.', '-'),
    ('follower_count' , 'Social'       , False, '14273'                 , 'generate follower_count'       , 'Simulated follower/subscriber counts.', '-'),
    ('api_key'        , 'Security'     , False, 'sk-aBcDeFgH...'        , 'generate api_key'              , 'Simulated secure API keys with prefix/suffix entropy.', '-'),
    ('totp_code'      , 'Security'     , False, '482931'                , 'generate totp_code'            , '6-digit Time-based One-Time Password (TOTP) codes.', '-'),
    ('webhook_signature', 'Security'     , False, 'sha256=e3b0c44...(71 chars)', 'generate webhook_signature'    , 'HMAC webhook signatures for secure delivery.', '-'),
    ('transaction_id' , 'Security'     , False, 'TXN1A2B3C4D5E6F7G8'    , 'generate transaction_id'       , 'Unique secure transaction identifier.', '-'),
    ('public_ip'      , 'Security'     , False, '185.46.212.33'         , 'generate public_ip'            , 'Public-facing IPv4 address.', '-'),
    ('private_ip'     , 'Security'     , False, '192.168.1.42'          , 'generate private_ip'           , 'Internal/Private IPv4 address.', '-'),
    ('tckn_masked'    , 'Identity'     , False, '***123456**'           , 'generate tckn_masked'          , 'Masked Turkish ID for privacy compliance.', '-'),
    ('ssn_masked'     , 'Identity'     , False, '***-**-6789'           , 'generate ssn_masked'           , 'Masked US SSN for privacy compliance.', '-'),
    ('nationality'    , 'Identity'     , False, 'TUR'                   , 'generate nationality'          , 'ISO 3166-1 alpha-3 nationality codes.', '-'),
    ('sepa_ref'       , 'Banking'      , False, 'SEPAENDTOEND20240501...', 'generate sepa_ref'            , 'SEPA End-to-End identification reference.', '-'),
    ('npi'            , 'Health'       , False, '1234567893'            , 'generate npi'                 , 'US National Provider Identifier (NPI) with Luhn.', '-'),
    ('credit_score'   , 'Financial'    , False, '720'                   , 'generate credit_score'        , 'Simulated credit risk score (typically 300-850).', '-'),
    ('hl7_message'    , 'Health'       , False, 'MSH|[enc]|EMR_SYS|...|ADT^A01^ADT_A01|...|2.5', 'generate hl7_message'  , 'HL7 v2.5 ADT^A01 patient admission message (MSH/EVN/PID/PV1 segments).', '-'),
    ('fhir_patient'   , 'Health'       , True , '{"resourceType":"Patient","id":"..."}', 'generate fhir_patient --locale UK', 'FHIR R4 Patient resource (JSON) with UUID id, name, gender, birthDate, address.', '--locale'),
    ('dicom_uid'      , 'Health'       , False, '2.25.329800735698586629...', 'generate dicom_uid'        , 'DICOM UID (ISO/IEC 9834-8 root 2.25) — digits and dots, max 64 chars.', '-'),
    ('--Payments--'   , ''             , False, ''                          , ''                           , '', ''),
    ('swift_mt103'   , 'Payments'     , True , ':20:REF{:23B:CRED}{:32A:261231TRY1234,56}', 'generate swift_mt103 --locale TR', 'SWIFT MT103 Single Customer Credit Transfer message fields.', '-'),
    ('pain001'       , 'Payments'     , False, '<?xml...pain.001.001.03...GrpHdr...PmtInf...>', 'generate pain001', 'ISO 20022 Pain.001 Credit Transfer Initiation XML.', '-'),
    ('nacha_ach'     , 'Payments'     , False, '1{file_hdr}5{batch_hdr}6{entry}8{ctrl}9{file_ctrl}', 'generate nacha_ach', 'NACHA ACH file with 94-char fixed records and hash total.', '-'),
    ('sepa_mandate'  , 'Payments'     , False, 'MandateRef:...CreditorID:DE98ZZZ...SequenceType:RCUR', 'generate sepa_mandate', 'SEPA Direct Debit Mandate with Creditor ID MOD-97 check digits.', '-'),
    ('fedwire'       , 'Payments'     , False, '{1500}REF{2000}000000100000{3100}021000021', 'generate fedwire', 'Fedwire Funds Transfer message with {TAG}VALUE format.', '-'),
    ('--CardPhysics--', ''            , False, ''                          , ''                           , '', ''),
    ('iso8583_auth_request' , 'CardPhysics', True , 'MTI:0100\nBITMAP:723C...\nDE002:4532...', 'generate iso8583_auth_request --locale TR', 'ISO 8583 v1987 Authorization Request (MTI 0100) — bitmap + DEs 2,3,4,7,11-14,18,22,25,37,41,42,49.', '--locale'),
    ('iso8583_auth_response', 'CardPhysics', True , 'MTI:0110\nBITMAP:7238...\nDE039:00',     'generate iso8583_auth_response --locale TR', 'ISO 8583 v1987 Authorization Response (MTI 0110) — includes DE038 auth code, DE039 response code.', '--locale'),
    ('iso8583_reversal'     , 'CardPhysics', True , 'MTI:0400\nBITMAP:7238...\nDE056:0100...', 'generate iso8583_reversal --locale TR', 'ISO 8583 v1987 Reversal Request (MTI 0400) — DE056 original data elements.', '--locale'),
    ('emv_arqc'      , 'CardPhysics', False, 'A1B2C3D4E5F60718'     , 'generate emv_arqc'            , 'EMV Application Request Cryptogram (tag 9F26) — 8 bytes / 16 uppercase hex.', '-'),
    ('emv_atc'       , 'CardPhysics', False, '00F3'                  , 'generate emv_atc'             , 'EMV Application Transaction Counter (tag 9F36) — 2 bytes / 4 uppercase hex.', '-'),
    ('emv_iad'       , 'CardPhysics', False, '0A02102B0F12ABCD1234', 'generate emv_iad'             , 'EMV Issuer Application Data (tag 9F10) — 11 bytes / 22 hex. Format: 0A+DKI+CVN+CVR+ADD+PAD.', '-'),
    ('atm_session'   , 'CardPhysics', True , '{"session_id":"MOCKJ-ATM-...","masked_pan":"4532 **** **** 9012",...}', 'generate atm_session --locale TR', 'ATM session JSON record — session_id, terminal, masked PAN, ARQC, ATC, response code.', '--locale'),
    ('pos_receipt'   , 'CardPhysics', True , 'MOCKJ MERCHANT SERVICES\nCard: **** **** **** 9012\nAuth: MOCKJ1', 'generate pos_receipt --locale TR', 'POS receipt formatted text (40-char wide) — MOCKJ merchant, masked PAN, auth code, TEST disclaimer.', '--locale'),
    ('--Commands--'  , ''             , False, ''                          , ''                           , '', ''),
    ('bulk'           , 'Commands'     , True , '["45678901234","98701234567",...]', 'bulk tckn --count 10 --locale TR', 'Generate N values of any single type. Supports all --generate flags (--network, --currency, --locale, etc.).', '--count (int)'),
    ('template'       , 'Commands'     , True , '{"fullname":"Emre Kaya","tckn":"45678901234","phone":"+905321234567"}', 'template fullname tckn phone --locale TR', 'Combine multiple data types into one structured record. Output as JSON, CSV or SQL INSERT.', '--count (int), --format (json|csv|sql), --table (string)'),
    ('export'         , 'Commands'     , True , 'fullname,tckn,phone\n"Emre Kaya","45678901234","+905321234567"', 'export fullname tckn phone --count 10 --format csv --locale TR', 'Bulk export multiple types as JSON array, CSV file or SQL INSERT statements.', '--count (int), --format (json|csv|sql), --table (string)'),
    ('profile'        , 'Commands'     , True , '{"fullname":"Emre Kaya","tckn":"45678901234","phone":"+90532...","email":"...","address":"...","birthdate":"1990-05-14","gender":"Male"}', 'profile --locale TR', 'Generate a complete person profile: fullname, national ID, phone, email, address, birthdate, gender.', '--count (int)'),
    ('company'        , 'Commands'     , True , '{"name":"Fischer Tech. GmbH","vkn":"1234567890","address":"...","phone":"...","iban":"DE...","sector":"Technology"}', 'company --locale DE', 'Generate a complete company profile: name, tax ID, address, phone, IBAN, sector.', '--count (int)'),
]

# Category display order
_CAT_ORDER = [
    "Identity", "Name", "Document", "Demographic",
    "Financial", "Contact", "Banking", "Payments", "CardPhysics", "Corporate",
    "Health", "Commerce", "Meta", "Security", "RFID", "NFC", "IR",
    "Barcode", "Telecom", "CapMarkets(Trading)", "Crypto",
    "E-Commerce", "Location", "Social", "Hardware", "Aviation", "Wireless", "WebAuthn", "Wallet",
    "AI Vector", "OIDC", "BankStatement", "EDI", "EventSourcing", "Telemetry", "OHLCV", "TLE", "Automotive", "EInvoice", "GameDev", "Prometheus", "NMEA", "MRZ", "PenTest",
    "Commands",
]

_CAT_COLORS = {
    "Identity":    "bright_blue",
    "Name":        "green",
    "Document":    "cyan",
    "Demographic": "magenta",
    "Financial":   "bright_blue",
    "Contact":     "green",
    "Banking":     "cyan",
    "Corporate":   "yellow",
    "Health":      "green",
    "Commerce":    "magenta",
    "Meta":        "yellow",
    "Security":    "bright_red",
    "RFID":        "cyan",
    "NFC":         "bright_blue",
    "IR":          "red",
    "Barcode":     "bright_yellow",
    "Telecom":     "bright_magenta",
    "CapMarkets(Trading)":  "bright_cyan",
    "Crypto":      "bright_green",
    "E-Commerce":  "yellow",
    "Location":    "bright_blue",
    "Social":      "magenta",
    "Hardware":    "bright_green",
    "Aviation":    "bright_cyan",
    "Wireless":    "bright_magenta",
    "WebAuthn":    "bright_yellow",
    "Wallet":      "bright_green",
    "AI Vector":   "bright_magenta",
    "OIDC":        "bright_cyan",
    "Payments":      "bright_yellow",
    "CardPhysics":   "cyan",
    "BankStatement": "bright_blue",
    "EDI":           "bright_yellow",
    "EventSourcing": "magenta",
    "Telemetry":     "bright_cyan",
    "OHLCV":         "bright_green",
    "TLE":           "bright_cyan",
    "Automotive":    "bright_yellow",
    "EInvoice":      "bright_cyan",
    "GameDev":       "bright_magenta",
    "Prometheus":    "bright_red",
    "NMEA":          "bright_yellow",
    "MRZ":           "bright_blue",
    "PenTest":       "bright_red",
    "Commands":      "bright_cyan",
}


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """Mock Jutsu - The Ultimate Algorithmic Mock Data Engine"""
    _fix_utf8_streams()
    if ctx.invoked_subcommand is None:
        _print_banner()
        click.echo(ctx.get_help())


@main.command()
@click.argument('data_type', required=False)
@click.option('--locale',    default='TR',     help='Locale: TR UK US DE FR RU')
@click.option('--network',   default='visa',   help='Card network: visa mc amex troy mir')
@click.option('--currency',  default='btc',    help='Crypto currency: btc eth')
@click.option('--carrier',   default='usps',   help='Tracking carrier: usps ups fedex')
@click.option('--algorithm', default='sha256', help='Hash algorithm: md5 sha1 sha224 sha256 sha384 sha512 sha3-224 sha3-256 sha3-384 sha3-512 crc32 adler32 crc16')
@click.option('--prefix',    default='',       help='Prefix for IDs (e.g. TCKN)')
@click.option('--gender',    default='',       help='Gender: male/female')
@click.option('--min',       default=None,     help='Minimum value', type=float)
@click.option('--max',       default=None,     help='Maximum value', type=float)
@click.option('--amount',    default=None,     help='Amount for QR/Transactions', type=float)
@click.option('--merchant',  default='MOCK STORE', help='Merchant name')
@click.option('--city',      default='ISTANBUL', help='Merchant city')
@click.option('--words',     default=None,     help='Word count for mnemonic (12, 15, 18, 21, 24)', type=int)
@click.option('--pattern',   default=None,     help='Regex pattern for regex_string type (e.g. "[A-Z]{3}\\d{4}")')
@click.option('--dims',      default=None,     help='Vector dimension for ai_embedding / ai_vector / ai_sparse_vector', type=int)
@click.option('--nnz',      default=None,     help='Non-zero entry count for ai_sparse_vector (default 128)', type=int)
@click.option('--secret',   default=None,     help='HMAC signing key for signature type (default: ninja)')
@click.option('--payload',  default=None,     help='Message to sign for signature type (default: mock)')
@click.option('--format',   'color_format',   default=None, help='Color output format: hex rgb hsl name')
def generate(data_type, locale, network, currency, carrier, algorithm, prefix, gender, min, max, amount, merchant, city, words, pattern, dims, nnz, secret, payload, color_format):
    """Generate mock data.  Example: mockjutsu generate tckn --locale TR"""
    if not data_type:
        click.echo("Error: specify a type. Run 'mockjutsu list' to see all types.")
        return

    # Pack extra kwargs (only non-empty/non-None)
    raw_kwargs = {
        'prefix': prefix,
        'gender': gender,
        'min': min,
        'max': max,
        'amount': amount,
        'merchant': merchant,
        'city': city,
        'words': words,
        'pattern': pattern,
        'dims': dims,
        'nnz': nnz,
        'secret': secret,
        'payload': payload,
        'format': color_format,
    }
    kwargs = {k: v for k, v in raw_kwargs.items() if v is not None and v != ''}

    result = jutsu.generate(data_type, locale=locale, network=network,
                            currency=currency, carrier=carrier, algorithm=algorithm, **kwargs)
    color  = 'red' if "ERROR" in str(result) else 'green'
    click.echo(click.style(str(result), fg=color, bold=True))


@main.command(name='list')
@click.option('--cat', default='', help='Filter by category  e.g. Financial, NFC, RFID, IR')
def list_types(cat):
    """List all supported data types with CLI usage examples."""
    # Column widths
    W_TYPE = 16
    W_EX   = 22
    W_CLI  = 48
    W_PARAM = 35
    # Total width with spaces between columns
    W = 2 + W_TYPE + 1 + W_EX + 1 + W_CLI + 1 + W_PARAM + 2

    sep = click.style("-" * W, fg='bright_black')

    # Banner
    _print_banner()
    click.echo()
    click.echo(click.style(
        "  Locales:  TR (Turkey)  |  US (United States)  |  UK (United Kingdom)\n"
        "            DE (Germany) |  FR (France)          |  RU (Russia)",
        fg='bright_black'
    ))
    click.echo()

    # Column headers
    h_type = click.style(f"  {'TYPE':<{W_TYPE}}", fg='bright_black', bold=True)
    h_ex   = click.style(f"{'EXAMPLE OUTPUT':<{W_EX}}", fg='bright_black', bold=True)
    h_cli  = click.style(f"{'CLI COMMAND':<{W_CLI}}", fg='bright_black', bold=True)
    h_par  = click.style(f"{'EXTRA PARAM':<{W_PARAM}}", fg='bright_black', bold=True)
    h_loc  = click.style("L", fg='bright_black', bold=True)
    click.echo(f"{h_type} {h_ex} {h_cli} {h_par} {h_loc}")
    click.echo(click.style("  " + "-" * (W - 2), fg='bright_black'))

    # Group rows by category
    cat_filter = cat.strip().lower()
    groups: dict[str, list] = {c: [] for c in _CAT_ORDER}
    for row in _REFERENCE:
        groups.setdefault(row[1], []).append(row)

    printed = 0
    for category in _CAT_ORDER:
        rows = groups.get(category, [])
        if not rows:
            continue
        if cat_filter and cat_filter not in category.lower():
            continue

        color = _CAT_COLORS.get(category, "white")
        click.echo()
        click.echo(click.style(
            f"  >> {category.upper()} ({len(rows)} types)",
            fg=color, bold=True
        ))

        for (typ, _cat, locale_aware, example, cli_cmd, _desc, extra_params) in rows:
            loc_flag = click.style("v", fg="green") if locale_aware else click.style("-", fg='bright_black')
            typ_s    = click.style(f"  {typ:<{W_TYPE}}", fg='white', bold=True)
            ex_clean = str(example).replace("\n", " ")
            ex_s     = click.style(f"{ex_clean:<{W_EX}}", fg='bright_yellow')
            full_cmd = f"mockjutsu {cli_cmd}"
            cli_s    = click.style(f"{full_cmd:<{W_CLI}}", fg='cyan')
            param_s  = click.style(f"{extra_params:<{W_PARAM}}", fg='bright_white')
            click.echo(f"{typ_s} {ex_s} {cli_s} {param_s} {loc_flag}")
            printed += 1

    # Footer — types summary
    click.echo()
    click.echo(sep)
    click.echo(click.style(
        f"  {printed} types listed  "
        "|  L=v -> supports --locale flag",
        fg='bright_black'
    ))
    click.echo(click.style(
        "  Filter:  mockjutsu list --cat Financial\n"
        "  Filter:  mockjutsu list --cat NFC",
        fg='bright_black'
    ))
    click.echo(sep)

    # Footer — CLI commands reference
    click.echo()
    click.echo(click.style("  >> CLI COMMANDS", fg='bright_white', bold=True))
    click.echo()

    _COMMANDS = [
        ("generate  <type>",   "Single value",          "mockjutsu generate tckn --locale TR"),
        ("bulk      <type>",   "Multiple same type",    "mockjutsu bulk iban --count 10 --locale TR"),
        ("template  <types…>", "Multi-type record",     "mockjutsu template nin snils cardtype address_street"),
        ("",                   "",                      "mockjutsu template uuid phone iban --count 5"),
        ("",                   "",                      "mockjutsu template tckn iban --count 10 --format csv"),
        ("",                   "",                      "mockjutsu template firstname lastname --format sql --table users"),
        ("profile",            "Person profile",        "mockjutsu profile --locale DE --count 3"),
        ("company",            "Company profile",       "mockjutsu company --locale TR"),
        ("export   <types…>",  "Bulk multi-type",       "mockjutsu export fullname tckn phone --count 5 --format csv"),
        ("list",               "Show all types",        "mockjutsu list  |  mockjutsu list --cat Financial"),
        ("start-api",          "Start REST API server", "mockjutsu start-api --port 8000"),
    ]

    W_CMD  = 22
    W_DESC = 22
    for cmd, desc, example in _COMMANDS:
        cmd_s  = click.style(f"  {cmd:<{W_CMD}}", fg='bright_green', bold=bool(cmd))
        desc_s = click.style(f"{desc:<{W_DESC}}", fg='bright_black')
        ex_s   = click.style(example, fg='cyan')
        click.echo(f"{cmd_s}{desc_s}{ex_s}")

    click.echo()
    click.echo(click.style(
        "  template options:  --count N  --locale TR|UK|US|DE|FR|RU  --format json|csv|sql  --table <name>",
        fg='bright_black'
    ))
    click.echo(sep)


@main.command()
@click.option('--locale', default='TR',  help='Locale: TR UK US DE FR RU')
@click.option('--count',  default=1,     help='Number of profiles to generate', type=int)
def profile(locale, count):
    """Generate a complete person profile.  Example: mockjutsu profile --locale TR"""
    import json
    results = [jutsu.profile(locale=locale) for _ in range(count)]
    output  = results[0] if count == 1 else results
    click.echo(json.dumps(output, ensure_ascii=False, indent=2))


@main.command()
@click.option('--locale', default='TR', help='Locale: TR UK US DE FR RU')
@click.option('--count',  default=1,    help='Number of companies to generate', type=int)
def company(locale, count):
    """Generate a complete company profile.  Example: mockjutsu company --locale DE"""
    import json
    results = [jutsu.company(locale=locale) for _ in range(count)]
    output  = results[0] if count == 1 else results
    click.echo(json.dumps(output, ensure_ascii=False, indent=2))


@main.command()
@click.argument('data_type')
@click.option('--count',     default=10,       help='Number of values to generate', type=int)
@click.option('--locale',    default='TR',     help='Locale: TR UK US DE FR RU')
@click.option('--network',   default='visa',   help='Card network: visa mc amex troy mir')
@click.option('--currency',  default='btc',    help='Crypto currency: btc eth')
@click.option('--carrier',   default='usps',   help='Tracking carrier: usps ups fedex')
@click.option('--algorithm', default='sha256', help='Hash algorithm')
@click.option('--prefix',    default='',       help='Prefix for IDs')
@click.option('--gender',    default='',       help='Gender: male/female')
@click.option('--min',       default=None,     help='Minimum value', type=float)
@click.option('--max',       default=None,     help='Maximum value', type=float)
@click.option('--amount',    default=None,     help='Amount', type=float)
@click.option('--words',     default=None,     help='Word count', type=int)
def bulk(data_type, count, locale, network, currency, carrier, algorithm, prefix, gender, min, max, amount, words):
    """Generate multiple values of the same type.  Example: mockjutsu bulk tckn --count 5"""
    import json
    raw_kwargs = {
        'prefix': prefix,
        'gender': gender,
        'min': min,
        'max': max,
        'amount': amount,
        'words': words,
        'network': network,
        'currency': currency,
        'carrier': carrier,
        'algorithm': algorithm
    }
    kwargs = {k: v for k, v in raw_kwargs.items() if v is not None and v != ''}
    results = jutsu.bulk(data_type, count=count, locale=locale, **kwargs)
    click.echo(json.dumps(results, ensure_ascii=False, indent=2))


@main.command()
@click.argument('types', nargs=-1, required=True)
@click.option('--count',  default=1,    help='Number of records (default: 1)', type=int)
@click.option('--locale', default='TR', help='Locale: TR UK US DE FR RU')
@click.option('--format', 'fmt', default='json', help='Output format: json csv sql')
@click.option('--table',  default='records', help='Table name (SQL only)')
def template(types, count, locale, fmt, table):
    """Combine multiple types into one record.  Example: mockjutsu template nin snils cardtype"""
    import json
    if not types:
        click.echo("Error: specify at least one type. Run 'mockjutsu list' to see all types.", err=True)
        return
    schema = {t: t for t in types}
    if fmt in ('csv', 'sql'):
        click.echo(jutsu.export(schema, count=count, format=fmt, locale=locale, table=table))
    else:
        records = jutsu.template(schema, count=count, locale=locale)
        output  = records[0] if count == 1 else records
        click.echo(json.dumps(output, ensure_ascii=False, indent=2))


@main.command(name='export')
@click.argument('types', nargs=-1, required=True)
@click.option('--count',  default=10,    help='Number of records',           type=int)
@click.option('--locale', default='TR',  help='Locale: TR UK US DE FR RU')
@click.option('--format', 'fmt', default='json', help='Output format: json csv sql')
@click.option('--table',  default='records', help='Table name (SQL only)')
def export_cmd(types, count, locale, fmt, table):
    """Export records as JSON/CSV/SQL.  Example: mockjutsu export fullname tckn phone --count 5"""
    schema = {t: t for t in types}
    click.echo(jutsu.export(schema, count=count, format=fmt, locale=locale, table=table))


@main.command(name='start-api')
@click.option('--port', default=8000, show_default=True, help='Port to listen on.')
def start_api(port):
    """Start the FastAPI mock server.  Example: mockjutsu start-api --port 9000"""
    import uvicorn
    click.echo(click.style(f"\nmock-jutsu API -- port {port}", fg='green', bold=True))
    from mockjutsu.api.main import app
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
