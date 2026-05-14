"""
mock-jutsu — Payment Messaging Standards Generator (Wave 8-A)
SWIFT MT103, ISO 20022 Pain.001, NACHA ACH, SEPA Mandate, Fedwire
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)
"""

import random
import secrets
from datetime import datetime, timezone, timedelta

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


def _swift_mt103(locale="TR"):
    ccy = _SWIFT_CCY.get(locale.upper(), "USD")
    date = datetime.now(timezone.utc).strftime("%y%m%d")
    amount = f"{random.randint(100, 9999999)},{random.randint(0, 99):02d}"
    ref = _swift_ref()
    ordering_acc = f"/ACC{random.randint(10000000, 99999999)}"
    ordering_name = f"ACME CORP {random.randint(100, 999)}"
    beneficiary_acc = f"/ACC{random.randint(10000000, 99999999)}"
    beneficiary_name = f"BENEFICIARY {random.randint(100, 999)}"
    return "\n".join([
        f":20:{ref}",
        f":23B:{random.choice(_SWIFT_23B)}",
        f":32A:{date}{ccy}{amount}",
        f":50K:{ordering_acc}",
        ordering_name,
        f":59:{beneficiary_acc}",
        beneficiary_name,
        f":71A:{random.choice(_SWIFT_71A)}",
    ])


# ─── ISO 20022 Pain.001 ──────────────────────────────────────────────────────

_PAIN001_BICS = [
    "DEUTDEDB", "COBADEFF", "BNPAFRPP", "SOGEFRPP",
    "HBUKGB4B", "BUKBGB22", "ABNANL2A", "BBRUBEBB",
    "RZBAATWW", "BBVAESBB", "BCITITMM",
]

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


def _pain001():
    now = datetime.now(timezone.utc)
    msg_id = "PAIN001-" + secrets.token_hex(8).upper()
    end_to_end_id = "E2E-" + secrets.token_hex(6).upper()
    creation_dt = now.strftime("%Y-%m-%dT%H:%M:%S")
    debtor_country = random.choice(_PAIN001_COUNTRIES)
    creditor_country = random.choice(_PAIN001_COUNTRIES)
    debtor_iban = _random_iban(debtor_country)
    creditor_iban = _random_iban(creditor_country)
    debtor_bic = random.choice(_PAIN001_BICS)
    creditor_bic = random.choice([b for b in _PAIN001_BICS if b != debtor_bic])
    amount = f"{random.randint(1, 99999)}.{random.randint(0, 99):02d}"
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03">\n'
        "  <CstmrCdtTrfInitn>\n"
        "    <GrpHdr>\n"
        f"      <MsgId>{msg_id}</MsgId>\n"
        f"      <CreDtTm>{creation_dt}</CreDtTm>\n"
        "      <NbOfTxs>1</NbOfTxs>\n"
        f"      <CtrlSum>{amount}</CtrlSum>\n"
        "    </GrpHdr>\n"
        "    <PmtInf>\n"
        f"      <PmtInfId>PMT-{secrets.token_hex(4).upper()}</PmtInfId>\n"
        "      <PmtMtd>TRF</PmtMtd>\n"
        "      <DbtrAgt>\n"
        "        <FinInstnId>\n"
        f"          <BICFI>{debtor_bic}</BICFI>\n"
        "        </FinInstnId>\n"
        "      </DbtrAgt>\n"
        f"      <Dbtr><Nm>Debtor Corp {random.randint(100, 999)}</Nm></Dbtr>\n"
        "      <DbtrAcct>\n"
        "        <Id>\n"
        f"          <IBAN>{debtor_iban}</IBAN>\n"
        "        </Id>\n"
        "      </DbtrAcct>\n"
        "      <CdtTrfTxInf>\n"
        "        <PmtId>\n"
        f"          <EndToEndId>{end_to_end_id}</EndToEndId>\n"
        "        </PmtId>\n"
        "        <Amt>\n"
        f'          <InstdAmt Ccy="EUR">{amount}</InstdAmt>\n'
        "        </Amt>\n"
        "        <CdtrAgt>\n"
        "          <FinInstnId>\n"
        f"            <BICFI>{creditor_bic}</BICFI>\n"
        "          </FinInstnId>\n"
        "        </CdtrAgt>\n"
        f"        <Cdtr><Nm>Creditor Corp {random.randint(100, 999)}</Nm></Cdtr>\n"
        "        <CdtrAcct>\n"
        "          <Id>\n"
        f"            <IBAN>{creditor_iban}</IBAN>\n"
        "          </Id>\n"
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
    routing8 = f"{prefix:02d}{random.randint(0, 999999):06d}"  # 2+6=8 transit digits
    weights = (3, 7, 1, 3, 7, 1, 3, 7)
    total = sum(int(routing8[i]) * weights[i] for i in range(8))
    check = (10 - (total % 10)) % 10
    return routing8 + str(check)  # 8+1=9 chars total


def _nacha_ach():
    now = datetime.now(timezone.utc)
    file_date = now.strftime("%y%m%d")
    file_time = now.strftime("%H%M")

    odfi_routing = _ach_routing()
    rdfi_routing = _ach_routing()
    sec_code = random.choice(_ACH_SEC_CODES)
    company_name = f"ACME CORP {random.randint(10, 99)}"
    company_id = f"{random.randint(1000000000, 9999999999)}"
    batch_num = f"{random.randint(1, 9999999):07d}"
    amount_cents = random.randint(100, 9999999)
    amount_str = str(amount_cents).zfill(10)
    indiv_name = f"JOHN DOE {random.randint(100, 999)}"
    indiv_id = f"ID{random.randint(100000, 999999):09d}"[:15]
    trace_num = odfi_routing[:8] + f"{random.randint(1, 9999999):07d}"
    account_num = f"{random.randint(10000000000, 99999999999)}"[:17].ljust(17)

    # ── Entry Detail Record (type 6), 94 chars ──────────────────────────────
    # [0]      record type "6"
    # [1:3]    transaction code
    # [3:12]   9-digit RDFI routing (8-digit ABA + check digit)
    # [12:29]  account number (17 chars)
    # [29:39]  amount in cents (10 digits)
    # [39:54]  individual ID (15 chars)
    # [54:76]  individual name (22 chars)
    # [76:78]  discretionary data (2 spaces)
    # [78]     addenda record indicator "0"
    # [79:94]  trace number (15 chars)
    entry = (
        "6"
        + "22"
        + rdfi_routing
        + account_num
        + amount_str
        + indiv_id.ljust(15)
        + indiv_name[:22].ljust(22)
        + "  "
        + "0"
        + trace_num[:15]
    )

    # NACHA hash uses first 8 digits of each RDFI routing (no check digit)
    hash_total = str(int(entry[3:11]) % 10 ** 10).zfill(10)

    # ── File Header (type 1), 94 chars ──────────────────────────────────────
    dest = (" " + odfi_routing).ljust(10)
    origin = company_id[:10].ljust(10)
    dest_name = "FIRST FEDERAL BANK".ljust(23)[:23]
    origin_name = company_name[:23].ljust(23)
    file_header = (
        "1"
        + "01"
        + dest
        + origin
        + file_date
        + file_time
        + "A"
        + "094"
        + "10"
        + "1"
        + dest_name
        + origin_name
        + "        "
    )

    # ── Batch Header (type 5), 94 chars ─────────────────────────────────────
    # [0]      "5"
    # [1:4]    service class code
    # [4:20]   company name (16)
    # [20:40]  company discretionary data (20 spaces)
    # [40:50]  company ID (10)
    # [50:53]  SEC code
    # [53:63]  entry description (10)
    # [63:69]  company descriptive date (6 spaces)
    # [69:75]  effective entry date YYMMDD
    # [75:78]  settlement date (3 spaces, bank fills)
    # [78]     originator status code "1"
    # [79:87]  ODFI routing (8 digits)
    # [87:94]  batch number (7 digits)
    batch_header = (
        "5"
        + "200"
        + company_name[:16].ljust(16)
        + " " * 20
        + company_id[:10].ljust(10)
        + sec_code
        + "PAYMENT   "
        + " " * 6
        + file_date
        + "   "
        + "1"
        + odfi_routing[:8]
        + batch_num
    )

    # ── Batch Control (type 8), 94 chars ─────────────────────────────────────
    # [0]      "8"
    # [1:4]    service class code
    # [4:10]   entry/addenda count (6 digits)
    # [10:20]  entry hash (10 digits)  ← NACHA spec: 1-indexed positions 11-20
    # [20:32]  total debit dollar amount (12 digits)
    # [32:44]  total credit dollar amount (12 digits)
    # [44:54]  company identification (10)
    # [54:73]  message authentication code (19 spaces)
    # [73:79]  reserved (6 spaces)
    # [79:87]  ODFI identification (8 digits)
    # [87:94]  batch number (7 digits)
    batch_control = (
        "8"
        + "200"
        + "000001"
        + hash_total
        + str(amount_cents).zfill(12)
        + str(amount_cents).zfill(12)
        + company_id[:10].ljust(10)
        + " " * 19
        + " " * 6
        + odfi_routing[:8]
        + batch_num
    )

    # ── File Control (type 9), 94 chars ──────────────────────────────────────
    # Reserved field uses "9" (not spaces) so val.strip() doesn't clip trailing chars
    file_control = (
        "9"
        + "000001"
        + "000001"
        + "00000001"
        + hash_total
        + str(amount_cents).zfill(12)
        + str(amount_cents).zfill(12)
        + "9" * 39
    )

    return "\n".join([file_header, batch_header, entry, batch_control, file_control])


# ─── SEPA Direct Debit Mandate ───────────────────────────────────────────────

_SEPA_COUNTRIES = ["DE", "FR", "NL", "BE", "AT", "ES"]
_SEPA_SEQUENCES = ("FRST", "RCUR", "FNAL", "OOFF")


def _sepa_creditor_id(country="DE"):
    """SEPA Creditor ID with MOD-97 check digits (same algorithm as IBAN)."""
    biz_code = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=3))
    nat_id = "".join(random.choices("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=random.randint(6, 11)))
    # Compute check: rearrange as biz_code + nat_id + country + "00", convert, 98 - (n % 97)
    rearranged = biz_code + nat_id + country + "00"
    numeric = "".join(str(ord(c) - 55) if c.isalpha() else c for c in rearranged)
    check = 98 - (int(numeric) % 97)
    return f"{country}{check:02d}{biz_code}{nat_id}"


def _sepa_mandate():
    country = random.choice(_SEPA_COUNTRIES)
    mandate_ref = "MandateRef-" + secrets.token_hex(6).upper()
    creditor_id = _sepa_creditor_id(country)
    debtor_iban = _random_iban(country)
    sequence = random.choice(_SEPA_SEQUENCES)
    days_ago = random.randint(0, 365)
    signing_date = (datetime.now(timezone.utc) - timedelta(days=days_ago)).strftime("%Y-%m-%d")
    return "\n".join([
        f"MandateRef: {mandate_ref}",
        f"CreditorID: {creditor_id}",
        f"DebtorIBAN: {debtor_iban}",
        f"SequenceType: {sequence}",
        f"SigningDate: {signing_date}",
    ])


# ─── Fedwire Funds Transfer ───────────────────────────────────────────────────

_FEDWIRE_TYPE_CODES = ("10", "15", "16")
_FEDWIRE_REF_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def _fedwire_routing():
    """9-digit Fedwire routing number with valid ABA check digit."""
    prefix = random.choice(_ABA_PREFIXES)
    routing8 = f"{prefix:02d}{random.randint(0, 999999):06d}"  # 2+6=8 transit digits
    weights = (3, 7, 1, 3, 7, 1, 3, 7)
    total = sum(int(routing8[i]) * weights[i] for i in range(8))
    check = (10 - (total % 10)) % 10
    return routing8 + str(check)  # 8+1=9 chars total


def _fedwire():
    sender_ref = "".join(random.choices(_FEDWIRE_REF_CHARS, k=random.randint(8, 16)))
    amount_cents = random.randint(1, 99999999)
    amount_str = str(amount_cents).zfill(12)
    sender_routing = _fedwire_routing()
    receiver_routing = _fedwire_routing()
    type_code = random.choice(_FEDWIRE_TYPE_CODES)
    return "\n".join([
        f"{{1500}}{sender_ref}",
        f"{{1510}}{type_code}00",
        f"{{2000}}{amount_str}",
        f"{{3100}}{sender_routing}",
        f"{{3400}}{receiver_routing}",
        f"{{3600}}CREDITOR-ACCT-{random.randint(1000, 9999)}",
        f"{{3700}}BENEFICIARY {random.randint(100, 999)}",
    ])


# ─── Generator class ─────────────────────────────────────────────────────────

class PaymentsGenerator:
    def generate(self, data_type, **kwargs):
        locale = str(kwargs.get("locale", "TR")).upper()
        if data_type == "swift_mt103":
            return _swift_mt103(locale=locale)
        elif data_type == "pain001":
            return _pain001()
        elif data_type == "nacha_ach":
            return _nacha_ach()
        elif data_type == "sepa_mandate":
            return _sepa_mandate()
        elif data_type == "fedwire":
            return _fedwire()
        return f"ERROR: Unknown type '{data_type}'"
