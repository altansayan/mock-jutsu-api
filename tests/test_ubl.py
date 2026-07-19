"""
Tests for God Mode #26 — UBL 2.1 E-Fatura ve XMLDSig
Types: ubl_invoice, xmldsig

Core invariants:
  ubl_invoice:
    - JSON with 'xml' (raw UBL 2.1 XML) + metadata fields
    - xml starts with '<?xml', contains '<Invoice', 'UBLVersionID>2.1'
    - invoice_id pattern: INV-YYYY-NNNNN
    - uuid: uppercase UUID v4 (8-4-4-4-12)
    - issue_date: YYYY-MM-DD
    - currency in valid ISO set
    - invoice_type in Turkish e-invoice types
    - tax_rate in [0, 8, 18, 20]
    - net_amount > 0, tax_amount >= 0, gross_amount > 0
    - gross_amount == net_amount + tax_amount (±0.01)
    - gross_amount appears in xml as formatted string
    - xml contains TaxTotal, LegalMonetaryTotal, InvoiceLine, PayableAmount

  xmldsig:
    - JSON with 'xml' (W3C XMLDSig) + metadata fields
    - xml starts with '<ds:Signature', ends with '</ds:Signature>'
    - Contains: ds:SignedInfo, ds:DigestValue, ds:SignatureValue, ds:X509Certificate
    - algorithm contains 'rsa-sha256'
    - digest_method contains 'sha256'
    - digest_value: Base64 of 32 bytes (SHA-256) → 44 chars
    - signature_value: Base64 of 256 bytes (RSA-2048) → 344 chars
    - Both values are valid Base64 characters only
"""

import json
import re
import pytest
from mockjutsu.core import MockJutsuCore
from mockjutsu.algorithms import tckn_valid, vkn_valid

jutsu = MockJutsuCore()

_VALID_CURRENCIES    = {'TRY', 'EUR', 'USD', 'GBP'}
_VALID_INVOICE_TYPES = {'SATIS', 'IADE', 'TEVKIFAT', 'IHTIYAT', 'ISTISNA'}
_VALID_TAX_RATES     = {0, 8, 18, 20}
_B64_CHARS           = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=')
_UUID_UPPER_RE       = re.compile(
    r'^[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}$'
)
_DATE_RE             = re.compile(r'^\d{4}-\d{2}-\d{2}$')
_INVOICE_ID_RE       = re.compile(r'^INV-\d{4}-\d{5}$')


# ── ubl_invoice ───────────────────────────────────────────────────────────────

class TestUblInvoice:

    def test_no_error(self):
        assert not jutsu.generate('ubl_invoice').startswith('ERROR')

    def test_returns_string(self):
        assert isinstance(jutsu.generate('ubl_invoice'), str)

    def test_is_valid_json(self):
        json.loads(jutsu.generate('ubl_invoice'))

    def test_is_dict(self):
        assert isinstance(json.loads(jutsu.generate('ubl_invoice')), dict)

    def test_has_required_fields(self):
        data = json.loads(jutsu.generate('ubl_invoice'))
        for f in ('xml', 'invoice_id', 'uuid', 'issue_date', 'currency',
                  'invoice_type', 'tax_rate', 'net_amount', 'tax_amount',
                  'gross_amount', 'line_count', 'ubl_version'):
            assert f in data, f"Missing field: {f}"

    def test_ubl_version_is_21(self):
        assert json.loads(jutsu.generate('ubl_invoice'))['ubl_version'] == '2.1'

    def test_xml_starts_with_xml_declaration(self):
        for _ in range(5):
            xml = json.loads(jutsu.generate('ubl_invoice'))['xml']
            assert xml.startswith('<?xml'), f"XML doesn't start with declaration"

    def test_xml_contains_invoice_element(self):
        for _ in range(5):
            xml = json.loads(jutsu.generate('ubl_invoice'))['xml']
            assert '<Invoice' in xml

    def test_xml_contains_ubl_version_21(self):
        for _ in range(5):
            xml = json.loads(jutsu.generate('ubl_invoice'))['xml']
            assert 'UBLVersionID>2.1' in xml

    def test_xml_contains_invoice_id(self):
        for _ in range(10):
            data = json.loads(jutsu.generate('ubl_invoice'))
            assert data['invoice_id'] in data['xml'], \
                "invoice_id not found in XML"

    def test_invoice_id_pattern(self):
        for _ in range(10):
            iid = json.loads(jutsu.generate('ubl_invoice'))['invoice_id']
            assert _INVOICE_ID_RE.match(iid), \
                f"invoice_id '{iid}' doesn't match INV-YYYY-NNNNN"

    def test_uuid_is_uppercase_uuid(self):
        for _ in range(10):
            uid = json.loads(jutsu.generate('ubl_invoice'))['uuid']
            assert _UUID_UPPER_RE.match(uid), \
                f"UUID '{uid}' doesn't match expected format"

    def test_issue_date_format(self):
        for _ in range(10):
            d = json.loads(jutsu.generate('ubl_invoice'))['issue_date']
            assert _DATE_RE.match(d), f"issue_date '{d}' not YYYY-MM-DD"

    def test_currency_is_valid(self):
        for _ in range(20):
            c = json.loads(jutsu.generate('ubl_invoice'))['currency']
            assert c in _VALID_CURRENCIES, f"currency '{c}' not valid"

    def test_invoice_type_is_valid(self):
        for _ in range(20):
            t = json.loads(jutsu.generate('ubl_invoice'))['invoice_type']
            assert t in _VALID_INVOICE_TYPES, f"invoice_type '{t}' not valid"

    def test_tax_rate_is_valid(self):
        for _ in range(20):
            r = json.loads(jutsu.generate('ubl_invoice'))['tax_rate']
            assert r in _VALID_TAX_RATES, f"tax_rate {r} not in {_VALID_TAX_RATES}"

    def test_net_amount_positive(self):
        for _ in range(10):
            assert json.loads(jutsu.generate('ubl_invoice'))['net_amount'] > 0

    def test_tax_amount_nonnegative(self):
        for _ in range(10):
            assert json.loads(jutsu.generate('ubl_invoice'))['tax_amount'] >= 0

    def test_gross_amount_positive(self):
        for _ in range(10):
            assert json.loads(jutsu.generate('ubl_invoice'))['gross_amount'] > 0

    def test_gross_equals_net_plus_tax(self):
        """gross_amount must equal net_amount + tax_amount within ±0.01."""
        for _ in range(20):
            data = json.loads(jutsu.generate('ubl_invoice'))
            expected = round(data['net_amount'] + data['tax_amount'], 2)
            assert abs(data['gross_amount'] - expected) < 0.01, \
                f"gross={data['gross_amount']} != net+tax={expected}"

    def test_line_count_at_least_one(self):
        for _ in range(10):
            assert json.loads(jutsu.generate('ubl_invoice'))['line_count'] >= 1

    def test_gross_amount_in_xml(self):
        """Formatted gross_amount (2dp) must appear in the XML."""
        for _ in range(10):
            data = json.loads(jutsu.generate('ubl_invoice'))
            formatted = f"{data['gross_amount']:.2f}"
            assert formatted in data['xml'], \
                f"'{formatted}' not found in XML"

    def test_xml_contains_tax_total(self):
        for _ in range(5):
            assert 'TaxTotal' in json.loads(jutsu.generate('ubl_invoice'))['xml']

    def test_xml_contains_legal_monetary_total(self):
        for _ in range(5):
            assert 'LegalMonetaryTotal' in json.loads(jutsu.generate('ubl_invoice'))['xml']

    def test_xml_contains_invoice_line(self):
        for _ in range(5):
            assert 'InvoiceLine' in json.loads(jutsu.generate('ubl_invoice'))['xml']

    def test_xml_contains_payable_amount(self):
        for _ in range(5):
            assert 'PayableAmount' in json.loads(jutsu.generate('ubl_invoice'))['xml']

    def test_xml_has_cbc_namespace(self):
        for _ in range(5):
            assert 'cbc:' in json.loads(jutsu.generate('ubl_invoice'))['xml']

    def test_xml_has_cac_namespace(self):
        for _ in range(5):
            assert 'cac:' in json.loads(jutsu.generate('ubl_invoice'))['xml']

    def test_bulk_variety(self):
        ids = {json.loads(r)['invoice_id'] for r in jutsu.bulk('ubl_invoice', 5)}
        assert len(ids) > 1

    def test_customer_tckn_passes_checksum(self):
        """schemeID="TCKN" value must pass the real dual MOD-10 TCKN checksum.

        Regression test: this field used to be generated by a checksumless
        _fake_tckn() helper local to ubl.py instead of IdentityGenerator.
        """
        for _ in range(20):
            xml = json.loads(jutsu.generate('ubl_invoice'))['xml']
            m = re.search(r'schemeID="TCKN">(\d+)<', xml)
            assert m, "TCKN field not found in XML"
            assert tckn_valid(m.group(1)), f"Invalid TCKN: {m.group(1)}"

    def test_supplier_vkn_passes_checksum(self):
        """Supplier CompanyID (VKN) must pass the real VKN checksum.

        Regression test: this field used to be generated by a checksumless
        _fake_vkn() helper local to ubl.py instead of IdentityGenerator.
        """
        for _ in range(20):
            xml = json.loads(jutsu.generate('ubl_invoice'))['xml']
            m = re.search(r'<cbc:CompanyID>(\d+)</cbc:CompanyID>', xml)
            assert m, "CompanyID (VKN) field not found in XML"
            assert vkn_valid(m.group(1)), f"Invalid VKN: {m.group(1)}"


# ── xmldsig ───────────────────────────────────────────────────────────────────

class TestXmlDSig:

    def test_no_error(self):
        assert not jutsu.generate('xmldsig').startswith('ERROR')

    def test_returns_string(self):
        assert isinstance(jutsu.generate('xmldsig'), str)

    def test_is_valid_json(self):
        json.loads(jutsu.generate('xmldsig'))

    def test_is_dict(self):
        assert isinstance(json.loads(jutsu.generate('xmldsig')), dict)

    def test_has_required_fields(self):
        data = json.loads(jutsu.generate('xmldsig'))
        for f in ('xml', 'signature_id', 'reference_id', 'algorithm',
                  'digest_method', 'c14n_method', 'digest_value', 'signature_value'):
            assert f in data, f"Missing field: {f}"

    def test_xml_starts_with_ds_signature(self):
        for _ in range(10):
            xml = json.loads(jutsu.generate('xmldsig'))['xml']
            assert xml.startswith('<ds:Signature'), \
                f"XML doesn't start with <ds:Signature: {xml[:30]}"

    def test_xml_ends_with_ds_signature_close(self):
        for _ in range(10):
            xml = json.loads(jutsu.generate('xmldsig'))['xml'].strip()
            assert xml.endswith('</ds:Signature>'), \
                f"XML doesn't end with </ds:Signature>"

    def test_xml_contains_signed_info(self):
        for _ in range(5):
            assert 'ds:SignedInfo' in json.loads(jutsu.generate('xmldsig'))['xml']

    def test_xml_contains_digest_value(self):
        for _ in range(5):
            assert 'ds:DigestValue' in json.loads(jutsu.generate('xmldsig'))['xml']

    def test_xml_contains_signature_value(self):
        for _ in range(5):
            assert 'ds:SignatureValue' in json.loads(jutsu.generate('xmldsig'))['xml']

    def test_xml_contains_x509_certificate(self):
        for _ in range(5):
            assert 'ds:X509Certificate' in json.loads(jutsu.generate('xmldsig'))['xml']

    def test_algorithm_contains_rsa_sha256(self):
        for _ in range(10):
            algo = json.loads(jutsu.generate('xmldsig'))['algorithm']
            assert 'rsa-sha256' in algo, f"algorithm '{algo}' doesn't contain rsa-sha256"

    def test_digest_method_contains_sha256(self):
        for _ in range(10):
            dm = json.loads(jutsu.generate('xmldsig'))['digest_method']
            assert 'sha256' in dm.lower(), f"digest_method '{dm}' doesn't contain sha256"

    def test_digest_value_length_44(self):
        """SHA-256 (32 bytes) → Base64 → 44 chars."""
        for _ in range(10):
            dv = json.loads(jutsu.generate('xmldsig'))['digest_value']
            assert len(dv) == 44, f"digest_value length {len(dv)} != 44"

    def test_signature_value_length_344(self):
        """RSA-2048 (256 bytes) → Base64 → 344 chars."""
        for _ in range(10):
            sv = json.loads(jutsu.generate('xmldsig'))['signature_value']
            assert len(sv) == 344, f"signature_value length {len(sv)} != 344"

    def test_digest_value_is_valid_base64(self):
        for _ in range(10):
            dv = json.loads(jutsu.generate('xmldsig'))['digest_value']
            assert all(c in _B64_CHARS for c in dv), \
                f"digest_value contains invalid Base64 chars"

    def test_signature_value_is_valid_base64(self):
        for _ in range(10):
            sv = json.loads(jutsu.generate('xmldsig'))['signature_value']
            assert all(c in _B64_CHARS for c in sv), \
                f"signature_value contains invalid Base64 chars"

    def test_signature_id_in_xml(self):
        for _ in range(10):
            data = json.loads(jutsu.generate('xmldsig'))
            assert data['signature_id'] in data['xml'], \
                "signature_id not found in XML"

    def test_c14n_method_contains_c14n(self):
        for _ in range(10):
            c14n = json.loads(jutsu.generate('xmldsig'))['c14n_method']
            assert 'c14n' in c14n.lower() or 'canonical' in c14n.lower(), \
                f"c14n_method '{c14n}' unexpected"

    def test_bulk_variety(self):
        ids = {json.loads(r)['signature_id'] for r in jutsu.bulk('xmldsig', 5)}
        assert len(ids) > 1

    def test_x509_cert_starts_with_der_sequence(self):
        """X.509 DER mock must start with ASN.1 SEQUENCE bytes (0x30 0x82).
        Verifies _mock_x509_der() produces structurally-plausible DER, not random bytes.
        """
        import base64
        for _ in range(5):
            data = json.loads(jutsu.generate('xmldsig'))
            xml = data['xml']
            # Extract Base64 value between X509Certificate tags
            import re
            m = re.search(r'<ds:X509Certificate>([^<]+)</ds:X509Certificate>', xml)
            assert m, "X509Certificate tag not found"
            der = base64.b64decode(m.group(1))
            # ASN.1 SEQUENCE tag = 0x30, long-form length = 0x82
            assert der[0] == 0x30, f"DER must start with 0x30 (SEQUENCE), got 0x{der[0]:02x}"
            assert der[1] == 0x82, f"DER length must use long-form 0x82, got 0x{der[1]:02x}"
