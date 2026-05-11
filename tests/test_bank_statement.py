"""
Tests for God Mode #16 — MT940 / CAMT.053 Bank Statement Generator
Types: mt940, camt053

Core invariants:
  - mt940   : SWIFT MT940 format — :20: :25: :28C: :60F: :61: :86: :62F: fields
  - camt053 : ISO 20022 XML — well-formed, MsgId, IBAN, OPBD/CLBD balances, Ntry entries
  - Amounts  : MT940 uses comma decimal (500,00), CAMT.053 uses dot (500.00)
  - Currency : 3-letter ISO code derived from locale
  - Zero external dependencies (stdlib xml.etree for parse verification)
"""

import re
import xml.etree.ElementTree as ET
import pytest
from mockjutsu.core import MockJutsuCore

jutsu = MockJutsuCore()

_MT940_DATE_RE   = re.compile(r'^\d{6}$')          # YYMMDD
_MT940_AMOUNT_RE = re.compile(r'^\d+,\d{2}$')      # comma decimal
_CURRENCY_RE     = re.compile(r'^[A-Z]{3}$')
_NS = 'urn:iso:std:iso:20022:tech:xsd:camt.053.001.02'


# ── mt940 ─────────────────────────────────────────────────────────────────────

class TestMt940:

    def test_no_error(self):
        assert not jutsu.generate('mt940').startswith('ERROR')

    def test_returns_string(self):
        assert isinstance(jutsu.generate('mt940'), str)

    def test_has_reference_field(self):
        assert ':20:' in jutsu.generate('mt940')

    def test_has_account_field(self):
        assert ':25:' in jutsu.generate('mt940')

    def test_has_statement_number(self):
        assert ':28C:' in jutsu.generate('mt940')

    def test_has_opening_balance(self):
        assert ':60F:' in jutsu.generate('mt940')

    def test_has_closing_balance(self):
        assert ':62F:' in jutsu.generate('mt940')

    def test_has_transaction_lines(self):
        assert ':61:' in jutsu.generate('mt940')

    def test_has_narrative_lines(self):
        assert ':86:' in jutsu.generate('mt940')

    def test_opening_balance_format(self):
        """':60F:C230101EUR12345,67' — indicator + YYMMDD + currency + comma-amount."""
        stmt = jutsu.generate('mt940')
        line = next(l for l in stmt.splitlines() if l.startswith(':60F:'))
        body = line[5:]                         # strip ':60F:'
        indicator = body[0]
        assert indicator in ('C', 'D')
        date_part = body[1:7]
        assert _MT940_DATE_RE.match(date_part), f"Bad date: {date_part}"
        currency = body[7:10]
        assert _CURRENCY_RE.match(currency), f"Bad currency: {currency}"
        amount = body[10:]
        assert _MT940_AMOUNT_RE.match(amount), f"Bad amount: {amount}"

    def test_closing_balance_format(self):
        stmt = jutsu.generate('mt940')
        line = next(l for l in stmt.splitlines() if l.startswith(':62F:'))
        body = line[5:]
        assert body[0] in ('C', 'D')
        assert _MT940_DATE_RE.match(body[1:7])
        assert _CURRENCY_RE.match(body[7:10])
        assert _MT940_AMOUNT_RE.match(body[10:])

    def test_amount_uses_comma_not_dot(self):
        """MT940 uses comma as decimal separator, never dot."""
        stmt = jutsu.generate('mt940')
        for line in stmt.splitlines():
            if line.startswith(':61:'):
                # amount part starts after YYMMDDYYMMDD + C/D
                body = line[4:]
                # find the amount section (after 2nd date + indicator)
                # format: :61:YYMMDDY YMMDD C/D amount CODE ref
                # simple check: no dot in amount region
                assert '.' not in line, f":61: line contains dot: {line}"

    def test_locale_tr_generates_try(self):
        stmt = jutsu.generate('mt940', locale='TR')
        assert 'TRY' in stmt

    def test_locale_de_generates_eur(self):
        stmt = jutsu.generate('mt940', locale='DE')
        assert 'EUR' in stmt

    def test_locale_uk_generates_gbp(self):
        stmt = jutsu.generate('mt940', locale='UK')
        assert 'GBP' in stmt

    def test_locale_us_generates_usd(self):
        stmt = jutsu.generate('mt940', locale='US')
        assert 'USD' in stmt

    def test_bulk_unique_references(self):
        results = jutsu.bulk('mt940', 5)
        refs = []
        for r in results:
            ref_line = next(l for l in r.splitlines() if l.startswith(':20:'))
            refs.append(ref_line)
        assert len(set(refs)) == 5


# ── camt053 ───────────────────────────────────────────────────────────────────

class TestCamt053:

    def test_no_error(self):
        assert not jutsu.generate('camt053').startswith('ERROR')

    def test_returns_string(self):
        assert isinstance(jutsu.generate('camt053'), str)

    def test_has_xml_declaration(self):
        assert jutsu.generate('camt053').startswith('<?xml')

    def test_has_camt053_namespace(self):
        assert 'camt.053' in jutsu.generate('camt053')

    def test_is_well_formed_xml(self):
        xml_str = jutsu.generate('camt053')
        ET.fromstring(xml_str)  # raises if malformed

    def test_has_msg_id(self):
        root = ET.fromstring(jutsu.generate('camt053'))
        msg_id = root.find(f'.//{{{_NS}}}MsgId')
        assert msg_id is not None and msg_id.text

    def test_has_iban(self):
        root = ET.fromstring(jutsu.generate('camt053'))
        iban = root.find(f'.//{{{_NS}}}IBAN')
        assert iban is not None and iban.text

    def test_has_opening_balance_opbd(self):
        xml_str = jutsu.generate('camt053')
        assert 'OPBD' in xml_str

    def test_has_closing_balance_clbd(self):
        xml_str = jutsu.generate('camt053')
        assert 'CLBD' in xml_str

    def test_has_at_least_one_entry(self):
        root = ET.fromstring(jutsu.generate('camt053'))
        entries = root.findall(f'.//{{{_NS}}}Ntry')
        assert len(entries) >= 1

    def test_entry_has_crdt_or_dbit(self):
        xml_str = jutsu.generate('camt053')
        assert 'CRDT' in xml_str or 'DBIT' in xml_str

    def test_amount_uses_dot_decimal(self):
        """CAMT.053 uses dot as decimal separator (ISO 20022 standard)."""
        root = ET.fromstring(jutsu.generate('camt053'))
        amounts = root.findall(f'.//{{{_NS}}}Amt')
        assert amounts, "No Amt elements found"
        for amt in amounts:
            assert re.match(r'^\d+\.\d{2}$', amt.text), f"Bad amount format: {amt.text}"

    def test_locale_tr_generates_try(self):
        assert 'TRY' in jutsu.generate('camt053', locale='TR')

    def test_locale_de_generates_eur(self):
        assert 'EUR' in jutsu.generate('camt053', locale='DE')

    def test_bulk_unique_msg_ids(self):
        results = jutsu.bulk('camt053', 5)
        msg_ids = []
        for r in results:
            root = ET.fromstring(r)
            msg_ids.append(root.find(f'.//{{{_NS}}}MsgId').text)
        assert len(set(msg_ids)) == 5
