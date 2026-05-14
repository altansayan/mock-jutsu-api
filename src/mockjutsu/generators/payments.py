"""
mock-jutsu — Payment Messaging Standards Generator (Wave 8-A)
SWIFT MT103, ISO 20022 Pain.001, NACHA ACH, SEPA Mandate, Fedwire
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)
"""

import random
import secrets
from datetime import datetime, timezone, timedelta

# ─── Shared: MOCKJ fictional BIC codes ──────────────────────────────────────
# "MOCK" institution prefix — any real bank firewall/log can filter on this
# pattern, blocking misuse before it reaches core banking.

_MOCKJ_BICS = [
    "MOCKDE01", "MOCKDE02", "MOCKDE03",
    "MOCKGB01", "MOCKGB02",
    "MOCKFR01", "MOCKFR02",
    "MOCKNL01", "MOCKAT01",
    "MOCKES01", "MOCKIT01",
    "MOCKBE01",
]

# strict=True: position 8 = "0" — official SWIFT Test/Training BIC convention
# (ISO 9362: location code second char "0" = test, no registry registration needed)
_MOCKJ_BICS_STRICT = [
    "MOCKDE00", "MOCKGB00", "MOCKFR00",
    "MOCKNL00", "MOCKAT00", "MOCKES00",
    "MOCKIT00", "MOCKBE00",
]


def _bic_pool(strict=False):
    return _MOCKJ_BICS_STRICT if strict else _MOCKJ_BICS

# ─── SWIFT MT103 ─────────────────────────────────────────────────────────────

_SWIFT_CCY = {
    "TR": "TRY", "US": "USD", "UK": "GBP",
    "DE": "EUR", "FR": "EUR", "RU": "RUB",
}

_SWIFT_23B = ("CRED", "CRTS", "SPAY", "SPRI", "SSTD")
_SWIFT_71A = ("OUR", "SHA", "BEN")
_SWIFT_REF_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def _swift_ref():
    return "".join(random.choices(_SWIFT_REF_CHARS, k=random.randint(8, 16)))


def _swift_mt103(locale="TR", strict=False):
    loc = locale.upper()
    ccy = _SWIFT_CCY.get(loc, "USD")
    date = datetime.now(timezone.utc).strftime("%y%m%d")
    amount = f"{random.randint(100, 9999999)},{random.randint(0, 99):02d}"
    ref = f"MOCKJ-{_swift_ref()}"[:16]

    pool = _bic_pool(strict)
    sender_bic = random.choice(pool)
    receiver_bic = random.choice([b for b in pool if b != sender_bic])

    # Block 1: F01 + BIC8 + LT(1) + branch(3) + session(4) + sequence(6)
    b1 = f"1:F01{sender_bic}AXXX0000000000"

    # Block 2 Input: I + MT + BIC8 + branch(3=XXX) + priority
    b2 = f"2:I103{receiver_bic}XXXN"

    ordering_acc = f"/ACC{random.randint(10000000, 99999999)}"
    beneficiary_acc = f"/ACC{random.randint(10000000, 99999999)}"

    tags = [
        f":20:{ref}",
        f":23B:{random.choice(_SWIFT_23B)}",
        f":32A:{date}{ccy}{amount}",
        f":50K:{ordering_acc}",
        f"MOCKJ CORP {random.randint(100, 999)}",
        f":59:{beneficiary_acc}",
        f"MOCKJ BENE {random.randint(100, 999)}",
        f":71A:{random.choice(_SWIFT_71A)}",
    ]
    b4_content = "\n".join(tags)
    b4 = f"4:\n{b4_content}\n-"

    # Block 5: CHK field is 12 hex chars (SHA-1 truncated format)
    checksum = secrets.token_hex(6).upper()
    b5 = f"5:{{CHK:{checksum}}}"

    return f"{{{b1}}}{{{b2}}}{{{b4}}}{{{b5}}}"


# ─── ISO 20022 Pain.001 ──────────────────────────────────────────────────────

_IBAN_BBAN_LEN = {
    "DE": 18, "GB": 18, "FR": 23, "NL": 14,
    "BE": 12, "AT": 16, "ES": 20, "IT": 23,
}
_PAIN001_COUNTRIES = list(_IBAN_BBAN_LEN)


def _random_iban(country="DE"):
    """Structurally valid IBAN with correct MOD-97 check digits (all-digit BBAN)."""
    bban_len = _IBAN_BBAN_LEN.get(country, 18)
    bban = "".join(str(random.randint(0, 9)) for _ in range(bban_len))
    rearranged = bban + country + "00"
    numeric = "".join(str(ord(c) - 55) if c.isalpha() else c for c in rearranged)
    check = 98 - (int(numeric) % 97)
    return f"{country}{check:02d}{bban}"


def _pain001(strict=False):
    now = datetime.now(timezone.utc)
    msg_id = f"MOCKJ-PAIN-{secrets.token_hex(4).upper()}"
    end_to_end_id = f"MOCKJ-E2E-{secrets.token_hex(4).upper()}"
    creation_dt = now.strftime("%Y-%m-%dT%H:%M:%S")
    req_execution_dt = (now + timedelta(days=1)).strftime("%Y-%m-%d")

    debtor_country = random.choice(_PAIN001_COUNTRIES)
    creditor_country = random.choice(_PAIN001_COUNTRIES)
    debtor_iban = _random_iban(debtor_country)
    creditor_iban = _random_iban(creditor_country)
    pool = _bic_pool(strict)
    debtor_bic = random.choice(pool)
    creditor_bic = random.choice([b for b in pool if b != debtor_bic])
    amount = f"{random.randint(1, 99999)}.{random.randint(0, 99):02d}"

    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.09">\n'
        "  <CstmrCdtTrfInitn>\n"
        "    <GrpHdr>\n"
        f"      <MsgId>{msg_id}</MsgId>\n"
        f"      <CreDtTm>{creation_dt}</CreDtTm>\n"
        "      <NbOfTxs>1</NbOfTxs>\n"
        f"      <CtrlSum>{amount}</CtrlSum>\n"
        "      <InitgPty>\n"
        f"        <Nm>MOCKJ CORP {random.randint(10, 99)}</Nm>\n"
        "      </InitgPty>\n"
        "    </GrpHdr>\n"
        "    <PmtInf>\n"
        f"      <PmtInfId>MOCKJ-PMT-{secrets.token_hex(4).upper()}</PmtInfId>\n"
        "      <PmtMtd>TRF</PmtMtd>\n"
        "      <PmtTpInf>\n"
        "        <SvcLvl><Cd>SEPA</Cd></SvcLvl>\n"
        "      </PmtTpInf>\n"
        f"      <ReqdExctnDt><Dt>{req_execution_dt}</Dt></ReqdExctnDt>\n"
        "      <Dbtr>\n"
        f"        <Nm>MOCKJ DEBTOR {random.randint(100, 999)}</Nm>\n"
        "      </Dbtr>\n"
        "      <DbtrAcct>\n"
        f"        <Id><IBAN>{debtor_iban}</IBAN></Id>\n"
        "      </DbtrAcct>\n"
        "      <DbtrAgt>\n"
        f"        <FinInstnId><BICFI>{debtor_bic}</BICFI></FinInstnId>\n"
        "      </DbtrAgt>\n"
        "      <ChrgBr>SLEV</ChrgBr>\n"
        "      <CdtTrfTxInf>\n"
        "        <PmtId>\n"
        f"          <EndToEndId>{end_to_end_id}</EndToEndId>\n"
        "        </PmtId>\n"
        "        <Amt>\n"
        f'          <InstdAmt Ccy="EUR">{amount}</InstdAmt>\n'
        "        </Amt>\n"
        "        <CdtrAgt>\n"
        f"          <FinInstnId><BICFI>{creditor_bic}</BICFI></FinInstnId>\n"
        "        </CdtrAgt>\n"
        f"        <Cdtr><Nm>MOCKJ BENE {random.randint(100, 999)}</Nm></Cdtr>\n"
        "        <CdtrAcct>\n"
        f"          <Id><IBAN>{creditor_iban}</IBAN></Id>\n"
        "        </CdtrAcct>\n"
        "      </CdtTrfTxInf>\n"
        "    </PmtInf>\n"
        "  </CstmrCdtTrfInitn>\n"
        "</Document>"
    )


# ─── NACHA ACH ───────────────────────────────────────────────────────────────

_ACH_SEC_CODES = ("PPD", "CCD", "CTX", "WEB", "TEL")
_ABA_PREFIXES = list(range(1, 13)) + list(range(21, 33)) + list(range(61, 73)) + [80]


def _ach_routing():
    """9-digit ABA routing transit number with valid check digit."""
    prefix = random.choice(_ABA_PREFIXES)
    routing8 = f"{prefix:02d}{random.randint(0, 999999):06d}"
    weights = (3, 7, 1, 3, 7, 1, 3, 7)
    total = sum(int(routing8[i]) * weights[i] for i in range(8))
    check = (10 - (total % 10)) % 10
    return routing8 + str(check)


def _nacha_ach():
    now = datetime.now(timezone.utc)
    file_date = now.strftime("%y%m%d")
    file_time = now.strftime("%H%M")

    odfi_routing = _ach_routing()
    rdfi_routing = _ach_routing()
    sec_code = random.choice(_ACH_SEC_CODES)
    company_name = f"MOCKJ CORP {random.randint(10, 99)}"
    company_id = f"1{random.randint(100000000, 999999999)}"
    batch_num = f"{random.randint(1, 9999999):07d}"
    amount_cents = random.randint(100, 9999999)
    amount_str = str(amount_cents).zfill(10)
    indiv_name = f"MOCKJ USER {random.randint(100, 999)}"
    indiv_id = f"MOCKJ-{random.randint(100000, 999999)}"[:15]
    # Trace Number = 16 chars: ODFI routing (8) + sequence (8, zero-padded)
    trace_num = odfi_routing[:8] + f"{random.randint(1, 99999999):08d}"
    account_num = f"{random.randint(10000000000, 99999999999)}"[:17].ljust(17)

    # ── Entry Detail (type 6), 94 chars ─────────────────────────────────────
    entry = (
        "6"
        + "22"
        + rdfi_routing
        + account_num
        + amount_str
        + indiv_id.ljust(15)
        + indiv_name[:22].ljust(22)
        + " "   # pos 77: discretionary data
        + "1"   # pos 78: addenda record indicator
        + trace_num  # pos 79-94: 16-char trace (ODFI 8 + seq 8)
    )

    # ── Addenda (type 7), 94 chars ───────────────────────────────────────────
    addenda_info = f"MOCKJ PAYMENT REF {secrets.token_hex(4).upper()}".ljust(80)
    addenda = (
        "7"
        + "05"
        + addenda_info[:80]
        + "0001"
        + trace_num[-7:]  # last 7 digits of trace = sequence number
    )

    hash_total = str(int(rdfi_routing[:8]) % 10 ** 10).zfill(10)

    # ── File Header (type 1), 94 chars ───────────────────────────────────────
    dest = (" " + odfi_routing).ljust(10)
    origin = company_id[:10].ljust(10)
    file_header = (
        "1" + "01" + dest + origin + file_date + file_time + "A" + "094" + "10" + "1"
        + "MOCKJ FEDERAL BANK".ljust(23)
        + company_name[:23].ljust(23)
        + " " * 8
    )

    # ── Batch Header (type 5), 94 chars ─────────────────────────────────────
    batch_header = (
        "5" + "200" + company_name[:16].ljust(16) + " " * 20 + company_id[:10].ljust(10)
        + sec_code + "PAYMENT   " + " " * 6 + file_date + " " * 3 + "1"
        + odfi_routing[:8] + batch_num
    )

    # ── Batch Control (type 8), 94 chars ─────────────────────────────────────
    batch_control = (
        "8" + "200" + "000002"
        + hash_total + str(amount_cents).zfill(12) + str(amount_cents).zfill(12)
        + company_id[:10].ljust(10) + " " * 19 + " " * 6 + odfi_routing[:8] + batch_num
    )

    # ── File Control (type 9), 94 chars ─────────────────────────────────────
    file_control = (
        "9" + "000001" + "000001" + "00000002" + hash_total
        + str(amount_cents).zfill(12) + str(amount_cents).zfill(12) + " " * 39
    )

    records = [file_header, batch_header, entry, addenda, batch_control, file_control]
    while len(records) % 10 != 0:
        records.append("9" * 94)

    return "\n".join(records)


# ─── SEPA Direct Debit Mandate ───────────────────────────────────────────────

_SEPA_COUNTRIES = ["DE", "FR", "NL", "BE", "AT", "ES"]
_SEPA_SEQUENCES = ("FRST", "RCUR", "FNAL", "OOFF")


def _sepa_creditor_id(country="DE"):
    """SEPA Creditor ID with MOD-97 check digits (same algorithm as IBAN)."""
    biz_code = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=3))
    nat_id = "".join(random.choices("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=random.randint(6, 11)))
    rearranged = biz_code + nat_id + country + "00"
    numeric = "".join(str(ord(c) - 55) if c.isalpha() else c for c in rearranged)
    check = 98 - (int(numeric) % 97)
    return f"{country}{check:02d}{biz_code}{nat_id}"


def _sepa_mandate(strict=False):
    now = datetime.now(timezone.utc)
    msg_id = f"MOCKJ-SDD-{secrets.token_hex(4).upper()}"
    # UMR = Unique Mandate Reference (SEPA/German banking term) — keeps "UMR"
    # keyword for test detection while MOCKJ marks it as non-real.
    mandate_ref = f"UMR-MOCKJ-{secrets.token_hex(4).upper()}"
    creation_dt = now.strftime("%Y-%m-%dT%H:%M:%S")

    country = random.choice(_SEPA_COUNTRIES)
    debtor_iban = _random_iban(country)
    pool = _bic_pool(strict)
    debtor_bic = random.choice(pool)
    creditor_id = _sepa_creditor_id(country)
    amount = f"{random.randint(10, 5000)}.{random.randint(0, 99):02d}"

    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.008.001.08">\n'
        "  <CstmrDrctDbtInitn>\n"
        "    <GrpHdr>\n"
        f"      <MsgId>{msg_id}</MsgId>\n"
        f"      <CreDtTm>{creation_dt}</CreDtTm>\n"
        "      <NbOfTxs>1</NbOfTxs>\n"
        "      <InitgPty>\n"
        f"        <Nm>MOCKJ CORP {random.randint(10, 99)}</Nm>\n"
        "      </InitgPty>\n"
        "    </GrpHdr>\n"
        "    <PmtInf>\n"
        f"      <PmtInfId>MOCKJ-SDD-PMT-{secrets.token_hex(4).upper()}</PmtInfId>\n"
        "      <PmtMtd>DD</PmtMtd>\n"
        "      <NbOfTxs>1</NbOfTxs>\n"
        "      <PmtTpInf>\n"
        "        <SvcLvl><Cd>SEPA</Cd></SvcLvl>\n"
        "        <LclInstrm><Cd>CORE</Cd></LclInstrm>\n"
        f"        <SeqTp>{random.choice(_SEPA_SEQUENCES)}</SeqTp>\n"
        "      </PmtTpInf>\n"
        f"      <ReqdColltnDt>{(now + timedelta(days=5)).strftime('%Y-%m-%d')}</ReqdColltnDt>\n"
        "      <Cdtr>\n"
        f"        <Nm>MOCKJ CREDITOR {random.randint(100, 999)}</Nm>\n"
        "      </Cdtr>\n"
        "      <CdtrAcct>\n"
        f"        <Id><IBAN>{_random_iban(country)}</IBAN></Id>\n"
        "      </CdtrAcct>\n"
        "      <CdtrAgt>\n"
        f"        <FinInstnId><BICFI>{random.choice(pool)}</BICFI></FinInstnId>\n"
        "      </CdtrAgt>\n"
        "      <CdtrSchmeId>\n"
        f"        <Id><PrvtId><Othr><Id>{creditor_id}</Id><SchmeNm><Prtry>SEPA</Prtry></SchmeNm></Othr></PrvtId></Id>\n"
        "      </CdtrSchmeId>\n"
        "      <DrctDbtTxInf>\n"
        "        <PmtId>\n"
        f"          <EndToEndId>MOCKJ-E2E-{secrets.token_hex(4).upper()}</EndToEndId>\n"
        "        </PmtId>\n"
        f"        <InstdAmt Ccy=\"EUR\">{amount}</InstdAmt>\n"
        "        <DrctDbtTx>\n"
        "          <MndtRltdInf>\n"
        f"            <MndtId>{mandate_ref}</MndtId>\n"
        f"            <DtOfSgntr>{now.strftime('%Y-%m-%d')}</DtOfSgntr>\n"
        "          </MndtRltdInf>\n"
        "        </DrctDbtTx>\n"
        "        <DbtrAgt>\n"
        f"          <FinInstnId><BICFI>{debtor_bic}</BICFI></FinInstnId>\n"
        "        </DbtrAgt>\n"
        "        <Dbtr>\n"
        f"          <Nm>MOCKJ DEBTOR {random.randint(100, 999)}</Nm>\n"
        "        </Dbtr>\n"
        "        <DbtrAcct>\n"
        f"          <Id><IBAN>{debtor_iban}</IBAN></Id>\n"
        "        </DbtrAcct>\n"
        "      </DrctDbtTxInf>\n"
        "    </PmtInf>\n"
        "  </CstmrDrctDbtInitn>\n"
        "</Document>"
    )


# ─── Fedwire Funds Transfer ───────────────────────────────────────────────────

_FEDWIRE_TYPE_CODES = ("10", "15", "16")
_FEDWIRE_BFC = ("CTR", "BTR", "DEP")  # Customer Transfer, Bank Transfer, Deposit
_FEDWIRE_REF_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def _fedwire_routing():
    """9-digit Fedwire routing number with valid ABA check digit."""
    prefix = random.choice(_ABA_PREFIXES)
    routing8 = f"{prefix:02d}{random.randint(0, 999999):06d}"
    weights = (3, 7, 1, 3, 7, 1, 3, 7)
    total = sum(int(routing8[i]) * weights[i] for i in range(8))
    check = (10 - (total % 10)) % 10
    return routing8 + str(check)


def _fedwire():
    date = datetime.now(timezone.utc).strftime("%Y%m%d")
    sender_ref = f"MOCKJ-{_swift_ref()}"[:16]
    # IMAD: date(8) + FRB line ID(8) + sequence(6) = exactly 22 chars
    frb_line_id = f"{random.randint(10000000, 99999999):08d}"
    sequence = f"{random.randint(100000, 999999):06d}"
    imad = date + frb_line_id + sequence
    amount_cents = random.randint(1, 99999999)
    amount_str = str(amount_cents).zfill(12)
    sender_routing = _fedwire_routing()
    receiver_routing = _fedwire_routing()
    type_code = random.choice(_FEDWIRE_TYPE_CODES)
    return "\n".join([
        f"{{1500}}{sender_ref}",
        f"{{1510}}{type_code}00",
        f"{{1520}}{imad}",
        f"{{2000}}{amount_str}",
        f"{{3100}}{sender_routing}MOCKJSNDR",
        f"{{3400}}{receiver_routing}MOCKJRCVR",
        f"{{3600}}{random.choice(_FEDWIRE_BFC)}",
        f"{{4200}}MOCKJ BENE {random.randint(100, 999)}",
    ])


# ─── Generator class ─────────────────────────────────────────────────────────

class PaymentsGenerator:
    def generate(self, data_type, **kwargs):
        locale = str(kwargs.get("locale", "TR")).upper()
        strict = bool(kwargs.get("strict", False))
        if data_type == "swift_mt103":
            return _swift_mt103(locale=locale, strict=strict)
        elif data_type == "pain001":
            return _pain001(strict=strict)
        elif data_type == "nacha_ach":
            return _nacha_ach()
        elif data_type == "sepa_mandate":
            return _sepa_mandate(strict=strict)
        elif data_type == "fedwire":
            return _fedwire()
        return f"ERROR: Unknown type '{data_type}'"
