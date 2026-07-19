"""
mock-jutsu — MT940 / CAMT.053 Bank Statement Generator
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)

Generates realistic bank statements in industry-standard formats.

Supported types:
  mt940   — SWIFT MT940 text format: :20: :25: :28C: :60F: :61: :86: :62F:
  camt053 — ISO 20022 CAMT.053 XML: MsgId, IBAN, OPBD/CLBD balances, Ntry entries

MT940  amounts use comma decimal (500,00).
CAMT.053 amounts use dot decimal (500.00) per ISO 20022.
Zero external dependencies: datetime, random (all stdlib).
"""

import datetime
import random
import uuid

from mockjutsu.algorithms import iban_check_digits


# ── Locale data ───────────────────────────────────────────────────────────────

_CURRENCIES = {
    'TR': 'TRY', 'DE': 'EUR', 'FR': 'EUR',
    'UK': 'GBP', 'US': 'USD', 'RU': 'RUB',
}

_TX_DESCRIPTIONS = [
    'TRANSFER FROM CUSTOMER', 'INCOMING WIRE TRANSFER', 'SALARY PAYMENT',
    'VENDOR PAYMENT', 'ATM WITHDRAWAL', 'CARD PAYMENT', 'DIRECT DEBIT',
    'STANDING ORDER', 'TAX PAYMENT', 'UTILITY BILL', 'INSURANCE PREMIUM',
    'LOAN REPAYMENT', 'RENT PAYMENT', 'INVOICE SETTLEMENT',
]

_MT940_TX_CODES = ['NTRN', 'NTRF', 'NCHK', 'NDDP', 'NFEX']


# ── IBAN helpers ──────────────────────────────────────────────────────────────

def _mock_iban(locale: str) -> str:
    """Locale-specific mock IBAN with real ISO 13616 MOD-97 check digits."""
    d = lambda n: ''.join(str(random.randint(0, 9)) for _ in range(n))
    a = lambda n: ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(n))
    loc = locale.upper()
    if loc == 'US':
        return d(12)  # US uses routing+account, not IBAN
    country, bban = {
        'TR': ('TR', f"{d(5)}{d(1)}{d(16)}"),
        'DE': ('DE', f"{d(8)}{d(10)}"),
        'FR': ('FR', f"{d(5)}{d(5)}{d(11)}{d(2)}"),
        'UK': ('GB', f"{a(4)}{d(6)}{d(8)}"),
    }.get(loc, ('RU', f"{d(3)}{d(15)}"))
    return f"{country}{iban_check_digits(country, bban)}{bban}"


def _rand_ref(n: int = 8) -> str:
    return ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(n))


# ── Transaction builder ───────────────────────────────────────────────────────

def _build_transactions(n: int, opening: float):
    """Generate n transactions, keeping balance positive (≥ 100)."""
    balance  = opening
    today    = datetime.date.today()
    base     = today - datetime.timedelta(days=random.randint(2, 7))
    date     = base
    txns     = []
    for i in range(n):
        if i > 0 and random.random() < 0.35:
            date = min(date + datetime.timedelta(days=1), today - datetime.timedelta(days=1))
        amount    = round(random.uniform(10.0, 5000.0), 2)
        is_credit = random.random() > 0.4
        if not is_credit and balance - amount < 100:
            is_credit = True
        balance  += amount if is_credit else -amount
        txns.append({
            'date':      date,
            'credit':    is_credit,
            'amount':    amount,
            'code':      random.choice(_MT940_TX_CODES),
            'ref':       _rand_ref(8),
            'desc':      random.choice(_TX_DESCRIPTIONS),
        })
    return txns, round(balance, 2)


# ── MT940 ─────────────────────────────────────────────────────────────────────

def _mt940_date(d: datetime.date) -> str:
    return d.strftime('%y%m%d')


def _mt940_amount(v: float) -> str:
    """Format float as MT940 comma-decimal, e.g. 1234.56 → '1234,56'."""
    whole = int(v)
    cents = round((v - whole) * 100)
    return f"{whole},{cents:02d}"


def generate_mt940(locale: str = 'TR') -> str:
    loc      = locale.upper()
    currency = _CURRENCIES.get(loc, 'EUR')
    iban     = _mock_iban(loc)
    opening  = round(random.uniform(1000.0, 50000.0), 2)
    txns, closing = _build_transactions(random.randint(2, 5), opening)

    start_date = txns[0]['date']
    end_date   = txns[-1]['date']
    stmt_num   = random.randint(1, 99)
    ref_num    = _rand_ref(10)

    lines = [
        f":20:{ref_num}",
        f":25:{iban}/{currency}",
        f":28C:{stmt_num:05d}/001",
        f":60F:C{_mt940_date(start_date)}{currency}{_mt940_amount(opening)}",
    ]
    for t in txns:
        ind  = 'C' if t['credit'] else 'D'
        d    = _mt940_date(t['date'])           # value date YYMMDD
        mmdd = t['date'].strftime('%m%d')       # booking date MMDD (MT940 :61: spec)
        lines.append(f":61:{d}{mmdd}{ind}{_mt940_amount(t['amount'])}{t['code']}{t['ref']}//{t['ref'][:8]}")
        lines.append(f":86:{t['desc']}")
    lines.append(f":62F:C{_mt940_date(end_date)}{currency}{_mt940_amount(closing)}")

    return '\n'.join(lines)


# ── CAMT.053 ──────────────────────────────────────────────────────────────────

_NS = 'urn:iso:std:iso:20022:tech:xsd:camt.053.001.02'


def generate_camt053(locale: str = 'TR') -> str:
    loc      = locale.upper()
    currency = _CURRENCIES.get(loc, 'EUR')
    iban     = _mock_iban(loc)
    opening  = round(random.uniform(1000.0, 50000.0), 2)
    txns, closing = _build_transactions(random.randint(2, 4), opening)

    today      = datetime.date.today()
    start_date = txns[0]['date']
    end_date   = txns[-1]['date']
    now_dt     = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    msg_id     = f"MOCK{today.strftime('%Y%m%d')}{random.randint(1000, 9999)}"
    stmt_id    = f"STMT{random.randint(10000, 99999)}"

    entries_xml = ''
    for t in txns:
        cdt_dbt = 'CRDT' if t['credit'] else 'DBIT'
        end2end = _rand_ref(8)
        entries_xml += (
            f"      <Ntry>\n"
            f"        <Amt Ccy=\"{currency}\">{t['amount']:.2f}</Amt>\n"
            f"        <CdtDbtInd>{cdt_dbt}</CdtDbtInd>\n"
            f"        <Sts><Cd>BOOK</Cd></Sts>\n"
            f"        <BookgDt><Dt>{t['date'].strftime('%Y-%m-%d')}</Dt></BookgDt>\n"
            f"        <ValDt><Dt>{t['date'].strftime('%Y-%m-%d')}</Dt></ValDt>\n"
            f"        <BkTxCd><Domn><Cd>PMNT</Cd><Fmly><Cd>ICDT</Cd>"
            f"<SubFmlyCd>AUTT</SubFmlyCd></Fmly></Domn></BkTxCd>\n"
            f"        <NtryDtls><TxDtls><Refs><EndToEndId>{end2end}</EndToEndId></Refs>"
            f"<RmtInf><Ustrd>{t['desc']}</Ustrd></RmtInf></TxDtls></NtryDtls>\n"
            f"      </Ntry>\n"
        )

    return (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<Document xmlns="{_NS}"'
        f' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n'
        f'  <BkToCstmrStmt>\n'
        f'    <GrpHdr>\n'
        f'      <MsgId>{msg_id}</MsgId>\n'
        f'      <CreDtTm>{now_dt}</CreDtTm>\n'
        f'      <MsgPgntn><PgNb>1</PgNb><LastPgInd>true</LastPgInd></MsgPgntn>\n'
        f'    </GrpHdr>\n'
        f'    <Stmt>\n'
        f'      <Id>{stmt_id}</Id>\n'
        f'      <CreDtTm>{now_dt}</CreDtTm>\n'
        f'      <FrToDt>\n'
        f'        <FrDtTm>{start_date.strftime("%Y-%m-%d")}T00:00:00</FrDtTm>\n'
        f'        <ToDtTm>{end_date.strftime("%Y-%m-%d")}T23:59:59</ToDtTm>\n'
        f'      </FrToDt>\n'
        f'      <Acct>\n'
        f'        <Id><IBAN>{iban}</IBAN></Id>\n'
        f'        <Ccy>{currency}</Ccy>\n'
        f'      </Acct>\n'
        f'      <Bal>\n'
        f'        <Tp><CdOrPrtry><Cd>OPBD</Cd></CdOrPrtry></Tp>\n'
        f'        <Amt Ccy="{currency}">{opening:.2f}</Amt>\n'
        f'        <CdtDbtInd>CRDT</CdtDbtInd>\n'
        f'        <Dt><Dt>{start_date.strftime("%Y-%m-%d")}</Dt></Dt>\n'
        f'      </Bal>\n'
        f'{entries_xml}'
        f'      <Bal>\n'
        f'        <Tp><CdOrPrtry><Cd>CLBD</Cd></CdOrPrtry></Tp>\n'
        f'        <Amt Ccy="{currency}">{closing:.2f}</Amt>\n'
        f'        <CdtDbtInd>CRDT</CdtDbtInd>\n'
        f'        <Dt><Dt>{end_date.strftime("%Y-%m-%d")}</Dt></Dt>\n'
        f'      </Bal>\n'
        f'    </Stmt>\n'
        f'  </BkToCstmrStmt>\n'
        f'</Document>'
    )


# ── Generator class ───────────────────────────────────────────────────────────

class BankStatementGenerator:
    """MT940 (SWIFT text) and CAMT.053 (ISO 20022 XML) bank statement generator."""

    def generate(self, data_type: str, **kwargs) -> str:
        locale = kwargs.get('locale', 'TR')
        if data_type == 'mt940':
            return generate_mt940(locale=locale)
        if data_type == 'camt053':
            return generate_camt053(locale=locale)
        return f"ERROR: Unknown type '{data_type}'"
