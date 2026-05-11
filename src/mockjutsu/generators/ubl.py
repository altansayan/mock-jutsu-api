"""
mock-jutsu — UBL 2.1 E-Invoice and W3C XMLDSig Generator
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)

Supported types:
  ubl_invoice — OASIS UBL 2.1 Invoice XML (Turkey GIB e-fatura compatible).
                Random line items with consistent amounts: net + tax = gross.
                Fields: ID, UUID, IssueDate, InvoiceTypeCode, CurrencyCode,
                        AccountingSupplierParty, AccountingCustomerParty,
                        TaxTotal (KDV), LegalMonetaryTotal, InvoiceLine(s).
                Returns JSON with 'xml' (raw XML string) + parsed metadata.
  xmldsig     — W3C XML Digital Signature (XMLDSig) enveloped structure.
                Algorithms: RSA-SHA256 signature, SHA-256 digest, C14N canonicalization.
                DigestValue = 32 random bytes (SHA-256 size) → Base64 (44 chars).
                SignatureValue = 256 random bytes (RSA-2048 size) → Base64 (344 chars).
                Returns JSON with 'xml' (raw XML) + parsed metadata.

Zero external dependencies: base64, datetime, json, random, uuid (stdlib only).
"""

import base64
import datetime
import json
import random
import uuid

# ── Constants ─────────────────────────────────────────────────────────────────

_INVOICE_TYPES = ['SATIS', 'IADE', 'TEVKIFAT', 'IHTIYAT', 'ISTISNA']
_CURRENCIES    = ['TRY', 'EUR', 'USD', 'GBP']
_TAX_RATES     = [0, 8, 18, 20]

_PRODUCT_NAMES = [
    'Yazilim Lisansi', 'Danismanlik Hizmeti', 'Donanim Ekipmani',
    'Egitim Hizmeti', 'Teknik Destek', 'Proje Yonetimi',
    'Network Altyapisi', 'Bulut Depolama', 'API Entegrasyonu',
    'Sistem Kurulumu',
]
_UNIT_CODES = ['C62', 'HUR', 'MTR', 'KGM', 'LTR', 'SET', 'MON']

# W3C XMLDSig algorithm URIs
_C14N_ALGO    = 'http://www.w3.org/TR/2001/REC-xml-c14n-20010315'
_SIG_ALGO     = 'http://www.w3.org/2001/04/xmldsig-more#rsa-sha256'
_DIGEST_ALGO  = 'http://www.w3.org/2001/04/xmlenc#sha256'
_ENV_ALGO     = 'http://www.w3.org/2000/09/xmldsig#enveloped-signature'


# ── Helpers ───────────────────────────────────────────────────────────────────

def _b64(n_bytes: int) -> str:
    return base64.b64encode(random.randbytes(n_bytes)).decode()


def _fake_vkn() -> str:
    return ''.join(str(random.randint(0, 9)) for _ in range(10))


def _fake_tckn() -> str:
    return str(random.randint(1, 9)) + ''.join(str(random.randint(0, 9)) for _ in range(10))


# ── UBL 2.1 Invoice ──────────────────────────────────────────────────────────

def generate_ubl_invoice() -> str:
    """
    OASIS UBL 2.1 Invoice XML — Turkey GIB e-fatura compatible structure.

    Amount consistency guarantee:
      tax_amount   = round(net_amount × tax_rate / 100, 2)
      gross_amount = round(net_amount + tax_amount, 2)
    """
    now          = datetime.datetime.now(datetime.timezone.utc)
    invoice_id   = f"INV-{now.year}-{random.randint(1, 99999):05d}"
    invoice_uuid = str(uuid.uuid4()).upper()
    issue_date   = now.strftime('%Y-%m-%d')
    issue_time   = now.strftime('%H:%M:%S')

    invoice_type = random.choice(_INVOICE_TYPES)
    currency     = random.choice(_CURRENCIES)
    tax_rate     = random.choice(_TAX_RATES)

    # Build 1-5 invoice lines
    n_lines = random.randint(1, 5)
    lines   = []
    for i in range(1, n_lines + 1):
        qty        = random.randint(1, 100)
        unit_price = round(random.uniform(10.0, 5000.0), 2)
        line_total = round(qty * unit_price, 2)
        lines.append({
            'id':         i,
            'qty':        qty,
            'unit_code':  random.choice(_UNIT_CODES),
            'unit_price': unit_price,
            'line_total': line_total,
            'name':       random.choice(_PRODUCT_NAMES),
        })

    net_amount   = round(sum(l['line_total'] for l in lines), 2)
    tax_amount   = round(net_amount * tax_rate / 100, 2)
    gross_amount = round(net_amount + tax_amount, 2)

    supplier_vkn  = _fake_vkn()
    customer_tckn = _fake_tckn()

    # Build InvoiceLine XML blocks
    line_blocks = []
    for l in lines:
        line_blocks.append(
            f'  <cac:InvoiceLine>\n'
            f'    <cbc:ID>{l["id"]}</cbc:ID>\n'
            f'    <cbc:InvoicedQuantity unitCode="{l["unit_code"]}">{l["qty"]}</cbc:InvoicedQuantity>\n'
            f'    <cbc:LineExtensionAmount currencyID="{currency}">{l["line_total"]:.2f}</cbc:LineExtensionAmount>\n'
            f'    <cac:Item><cbc:Name>{l["name"]}</cbc:Name></cac:Item>\n'
            f'    <cac:Price><cbc:PriceAmount currencyID="{currency}">{l["unit_price"]:.2f}</cbc:PriceAmount></cac:Price>\n'
            f'  </cac:InvoiceLine>'
        )

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"\n'
        '  xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"\n'
        '  xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">\n'
        f'  <cbc:UBLVersionID>2.1</cbc:UBLVersionID>\n'
        f'  <cbc:CustomizationID>TR1.2</cbc:CustomizationID>\n'
        f'  <cbc:ID>{invoice_id}</cbc:ID>\n'
        f'  <cbc:CopyIndicator>false</cbc:CopyIndicator>\n'
        f'  <cbc:UUID>{invoice_uuid}</cbc:UUID>\n'
        f'  <cbc:IssueDate>{issue_date}</cbc:IssueDate>\n'
        f'  <cbc:IssueTime>{issue_time}</cbc:IssueTime>\n'
        f'  <cbc:InvoiceTypeCode>{invoice_type}</cbc:InvoiceTypeCode>\n'
        f'  <cbc:DocumentCurrencyCode>{currency}</cbc:DocumentCurrencyCode>\n'
        f'  <cbc:LineCountNumeric>{n_lines}</cbc:LineCountNumeric>\n'
        f'  <cac:AccountingSupplierParty>\n'
        f'    <cac:Party>\n'
        f'      <cac:PartyTaxScheme>\n'
        f'        <cbc:CompanyID>{supplier_vkn}</cbc:CompanyID>\n'
        f'        <cac:TaxScheme><cbc:ID>VAT</cbc:ID></cac:TaxScheme>\n'
        f'      </cac:PartyTaxScheme>\n'
        f'    </cac:Party>\n'
        f'  </cac:AccountingSupplierParty>\n'
        f'  <cac:AccountingCustomerParty>\n'
        f'    <cac:Party>\n'
        f'      <cac:PartyIdentification>\n'
        f'        <cbc:ID schemeID="TCKN">{customer_tckn}</cbc:ID>\n'
        f'      </cac:PartyIdentification>\n'
        f'    </cac:Party>\n'
        f'  </cac:AccountingCustomerParty>\n'
        f'  <cac:TaxTotal>\n'
        f'    <cbc:TaxAmount currencyID="{currency}">{tax_amount:.2f}</cbc:TaxAmount>\n'
        f'    <cac:TaxSubtotal>\n'
        f'      <cbc:TaxableAmount currencyID="{currency}">{net_amount:.2f}</cbc:TaxableAmount>\n'
        f'      <cbc:TaxAmount currencyID="{currency}">{tax_amount:.2f}</cbc:TaxAmount>\n'
        f'      <cac:TaxCategory>\n'
        f'        <cbc:Percent>{tax_rate}</cbc:Percent>\n'
        f'        <cac:TaxScheme><cbc:ID>KDV</cbc:ID></cac:TaxScheme>\n'
        f'      </cac:TaxCategory>\n'
        f'    </cac:TaxSubtotal>\n'
        f'  </cac:TaxTotal>\n'
        f'  <cac:LegalMonetaryTotal>\n'
        f'    <cbc:LineExtensionAmount currencyID="{currency}">{net_amount:.2f}</cbc:LineExtensionAmount>\n'
        f'    <cbc:TaxExclusiveAmount currencyID="{currency}">{net_amount:.2f}</cbc:TaxExclusiveAmount>\n'
        f'    <cbc:TaxInclusiveAmount currencyID="{currency}">{gross_amount:.2f}</cbc:TaxInclusiveAmount>\n'
        f'    <cbc:PayableAmount currencyID="{currency}">{gross_amount:.2f}</cbc:PayableAmount>\n'
        f'  </cac:LegalMonetaryTotal>\n'
        + '\n'.join(line_blocks) + '\n'
        '</Invoice>'
    )

    return json.dumps({
        'xml':          xml,
        'invoice_id':   invoice_id,
        'uuid':         invoice_uuid,
        'issue_date':   issue_date,
        'currency':     currency,
        'invoice_type': invoice_type,
        'tax_rate':     tax_rate,
        'net_amount':   net_amount,
        'tax_amount':   tax_amount,
        'gross_amount': gross_amount,
        'line_count':   n_lines,
        'ubl_version':  '2.1',
    }, ensure_ascii=False)


# ── W3C XMLDSig ───────────────────────────────────────────────────────────────

def generate_xmldsig() -> str:
    """
    W3C XML Digital Signature (XMLDSig) enveloped structure.

    Structural invariants:
      digest_value    = base64(32 random bytes)   → 44 chars (SHA-256 output size)
      signature_value = base64(256 random bytes)  → 344 chars (RSA-2048 output size)
      x509_cert       = base64(512 random bytes)  → simulated DER-encoded certificate
    """
    sig_id  = f"Signature-{uuid.uuid4().hex[:8].upper()}"
    ref_id  = f"Reference-{uuid.uuid4().hex[:8].upper()}"

    digest_value    = _b64(32)    # SHA-256 = 32 bytes → 44 Base64 chars
    signature_value = _b64(256)   # RSA-2048 = 256 bytes → 344 Base64 chars
    x509_cert       = _b64(512)   # Simulated DER cert

    xml = (
        f'<ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#" Id="{sig_id}">\n'
        f'  <ds:SignedInfo>\n'
        f'    <ds:CanonicalizationMethod Algorithm="{_C14N_ALGO}"/>\n'
        f'    <ds:SignatureMethod Algorithm="{_SIG_ALGO}"/>\n'
        f'    <ds:Reference Id="{ref_id}" URI="">\n'
        f'      <ds:Transforms>\n'
        f'        <ds:Transform Algorithm="{_ENV_ALGO}"/>\n'
        f'      </ds:Transforms>\n'
        f'      <ds:DigestMethod Algorithm="{_DIGEST_ALGO}"/>\n'
        f'      <ds:DigestValue>{digest_value}</ds:DigestValue>\n'
        f'    </ds:Reference>\n'
        f'  </ds:SignedInfo>\n'
        f'  <ds:SignatureValue Id="SignatureValue">{signature_value}</ds:SignatureValue>\n'
        f'  <ds:KeyInfo>\n'
        f'    <ds:X509Data>\n'
        f'      <ds:X509Certificate>{x509_cert}</ds:X509Certificate>\n'
        f'    </ds:X509Data>\n'
        f'  </ds:KeyInfo>\n'
        f'</ds:Signature>'
    )

    return json.dumps({
        'xml':             xml,
        'signature_id':    sig_id,
        'reference_id':    ref_id,
        'algorithm':       _SIG_ALGO,
        'digest_method':   _DIGEST_ALGO,
        'c14n_method':     _C14N_ALGO,
        'digest_value':    digest_value,
        'signature_value': signature_value,
    }, ensure_ascii=False)


# ── Generator class ────────────────────────────────────────────────────────────

class UblGenerator:
    """UBL 2.1 E-Invoice and W3C XMLDSig generator."""

    def generate(self, data_type: str, **kwargs) -> str:
        if data_type == 'ubl_invoice':
            return generate_ubl_invoice()
        if data_type == 'xmldsig':
            return generate_xmldsig()
        return f"ERROR: Unknown type '{data_type}'"
