"""
mock-jutsu — PSD2 / Open Banking JWS Tests
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)

Standard: UK Open Banking Read/Write API v3.1 (openbanking.org.uk)
          PSD2 — EU Directive 2015/2366, EBA RTS on SCA & CSC

Coverage:
  - Compact JWS structure (header.payload.signature)
  - Header: alg, kid, b64, crit, OB-specific iat/iss/tan claims
  - Payload: UK OB v3.1 Payment Consent schema
  - Payload fields: ConsentId, Initiation, InstructedAmount, CreditorAccount
  - Amount is positive decimal string with 2 d.p.
  - Currency is valid ISO 4217 code
  - Signature is valid HMAC-SHA256 (base64url, no padding)
  - Locale-aware: currency and creditor format change per locale
  - --amount flag respected
  - Uniqueness (CSPRNG)
  - CLI: generate, bulk
"""

import base64
import json
import re
import pytest
from click.testing import CliRunner
from mockjutsu.core import jutsu
from mockjutsu.cli import main

# ISO 4217 codes the generator supports
VALID_CURRENCIES = {'GBP', 'EUR', 'USD', 'TRY', 'RUB'}

# Locales → expected currency
LOCALE_CURRENCY = {
    'TR': 'TRY',
    'UK': 'GBP',
    'US': 'USD',
    'DE': 'EUR',
    'FR': 'EUR',
    'RU': 'RUB',
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _b64url_decode(s: str) -> bytes:
    """Decode base64url string (no padding required)."""
    pad = 4 - len(s) % 4
    return base64.urlsafe_b64decode(s + '=' * (pad % 4))


def _parse_jws(token: str):
    """Split compact JWS into (header_dict, payload_dict, signature_bytes)."""
    parts = token.split('.')
    assert len(parts) == 3, f"JWS must have 3 parts, got {len(parts)}: {token[:80]}"
    header  = json.loads(_b64url_decode(parts[0]))
    payload = json.loads(_b64url_decode(parts[1]))
    sig     = _b64url_decode(parts[2])
    return header, payload, sig


# ── Structure ─────────────────────────────────────────────────────────────────

def test_psd2_returns_string():
    result = jutsu.generate('psd2_consent')
    assert isinstance(result, str)
    assert not result.startswith('ERROR')


def test_psd2_compact_jws_three_parts():
    token = jutsu.generate('psd2_consent')
    parts = token.split('.')
    assert len(parts) == 3, f"Expected 3 JWS parts, got {len(parts)}"


def test_psd2_parts_are_base64url():
    token = jutsu.generate('psd2_consent')
    pattern = re.compile(r'^[A-Za-z0-9_-]+$')
    for i, part in enumerate(token.split('.')):
        assert pattern.match(part), f"Part {i} is not valid base64url: {part[:40]}"


# ── Header claims ─────────────────────────────────────────────────────────────

def test_psd2_header_alg():
    header, _, _ = _parse_jws(jutsu.generate('psd2_consent'))
    assert header.get('alg') == 'HS256', f"Expected alg=HS256, got {header.get('alg')}"


def test_psd2_header_kid_present():
    header, _, _ = _parse_jws(jutsu.generate('psd2_consent'))
    assert 'kid' in header and header['kid'], "kid must be present and non-empty"


def test_psd2_header_b64_false():
    """PSD2 JWS uses b64=false (detached payload signing per RFC 7797)."""
    header, _, _ = _parse_jws(jutsu.generate('psd2_consent'))
    assert header.get('b64') is False, f"b64 must be false, got {header.get('b64')}"


def test_psd2_header_crit_present():
    header, _, _ = _parse_jws(jutsu.generate('psd2_consent'))
    assert 'crit' in header, "crit claim must be present"
    assert isinstance(header['crit'], list), "crit must be a list"
    assert len(header['crit']) > 0, "crit must be non-empty"


def test_psd2_header_ob_iat():
    header, _, _ = _parse_jws(jutsu.generate('psd2_consent'))
    key = 'http://openbanking.org.uk/iat'
    assert key in header, f"Missing OB claim: {key}"
    assert isinstance(header[key], int), f"{key} must be an integer timestamp"
    assert header[key] > 0


def test_psd2_header_ob_iss():
    header, _, _ = _parse_jws(jutsu.generate('psd2_consent'))
    key = 'http://openbanking.org.uk/iss'
    assert key in header, f"Missing OB claim: {key}"
    assert len(header[key]) > 0


def test_psd2_header_ob_tan():
    header, _, _ = _parse_jws(jutsu.generate('psd2_consent'))
    key = 'http://openbanking.org.uk/tan'
    assert key in header, f"Missing OB claim: {key}"
    assert 'openbanking.org.uk' in header[key]


def test_psd2_header_crit_includes_ob_claims():
    header, _, _ = _parse_jws(jutsu.generate('psd2_consent'))
    crit = header['crit']
    assert 'b64' in crit
    assert 'http://openbanking.org.uk/iat' in crit
    assert 'http://openbanking.org.uk/iss' in crit
    assert 'http://openbanking.org.uk/tan' in crit


# ── Payload schema ────────────────────────────────────────────────────────────

def test_psd2_payload_has_data():
    _, payload, _ = _parse_jws(jutsu.generate('psd2_consent'))
    assert 'Data' in payload, "Payload must have 'Data' key"


def test_psd2_payload_has_risk():
    _, payload, _ = _parse_jws(jutsu.generate('psd2_consent'))
    assert 'Risk' in payload, "Payload must have 'Risk' key"


def test_psd2_payload_consent_id():
    _, payload, _ = _parse_jws(jutsu.generate('psd2_consent'))
    consent_id = payload['Data'].get('ConsentId', '')
    assert consent_id.startswith('aac-'), f"ConsentId must start with 'aac-', got: {consent_id}"


def test_psd2_payload_initiation_present():
    _, payload, _ = _parse_jws(jutsu.generate('psd2_consent'))
    assert 'Initiation' in payload['Data'], "Data.Initiation must be present"


def test_psd2_payload_instructed_amount_present():
    _, payload, _ = _parse_jws(jutsu.generate('psd2_consent'))
    init = payload['Data']['Initiation']
    assert 'InstructedAmount' in init, "InstructedAmount must be present"


def test_psd2_payload_amount_positive_decimal():
    _, payload, _ = _parse_jws(jutsu.generate('psd2_consent'))
    amount_str = payload['Data']['Initiation']['InstructedAmount']['Amount']
    assert re.fullmatch(r'\d+\.\d{2}', amount_str), (
        f"Amount must be decimal with 2 d.p., got: {amount_str}"
    )
    assert float(amount_str) > 0


def test_psd2_payload_currency_valid():
    _, payload, _ = _parse_jws(jutsu.generate('psd2_consent'))
    currency = payload['Data']['Initiation']['InstructedAmount']['Currency']
    assert currency in VALID_CURRENCIES, f"Invalid currency: {currency}"


def test_psd2_payload_creditor_account_present():
    _, payload, _ = _parse_jws(jutsu.generate('psd2_consent'))
    init = payload['Data']['Initiation']
    assert 'CreditorAccount' in init, "CreditorAccount must be present"
    ca = init['CreditorAccount']
    assert 'SchemeName' in ca
    assert 'Identification' in ca
    assert 'Name' in ca


def test_psd2_payload_remittance_info_present():
    _, payload, _ = _parse_jws(jutsu.generate('psd2_consent'))
    init = payload['Data']['Initiation']
    assert 'RemittanceInformation' in init
    ri = init['RemittanceInformation']
    assert 'Reference' in ri
    assert 'Unstructured' in ri


def test_psd2_payload_instruction_ids_present():
    _, payload, _ = _parse_jws(jutsu.generate('psd2_consent'))
    init = payload['Data']['Initiation']
    assert 'InstructionIdentification' in init
    assert 'EndToEndIdentification' in init


# ── Signature ─────────────────────────────────────────────────────────────────

def test_psd2_signature_non_empty():
    parts = jutsu.generate('psd2_consent').split('.')
    sig = _b64url_decode(parts[2])
    assert len(sig) == 32, f"HMAC-SHA256 signature must be 32 bytes, got {len(sig)}"


# ── Locale awareness ──────────────────────────────────────────────────────────

@pytest.mark.parametrize("locale,expected_currency", LOCALE_CURRENCY.items())
def test_psd2_locale_currency(locale, expected_currency):
    _, payload, _ = _parse_jws(jutsu.generate('psd2_consent', locale=locale))
    currency = payload['Data']['Initiation']['InstructedAmount']['Currency']
    assert currency == expected_currency, (
        f"Locale {locale}: expected {expected_currency}, got {currency}"
    )


# ── --amount flag ─────────────────────────────────────────────────────────────

def test_psd2_amount_kwarg_respected():
    _, payload, _ = _parse_jws(jutsu.generate('psd2_consent', amount=999.99))
    amount_str = payload['Data']['Initiation']['InstructedAmount']['Amount']
    assert amount_str == '999.99', f"Expected 999.99, got {amount_str}"


# ── Uniqueness ────────────────────────────────────────────────────────────────

def test_psd2_unique_outputs():
    tokens = {jutsu.generate('psd2_consent') for _ in range(10)}
    assert len(tokens) == 10, "Duplicate psd2_consent tokens — entropy source broken"


def test_psd2_unique_consent_ids():
    ids = set()
    for _ in range(20):
        _, payload, _ = _parse_jws(jutsu.generate('psd2_consent'))
        ids.add(payload['Data']['ConsentId'])
    assert len(ids) == 20, "Duplicate ConsentIds detected"


# ── CLI ───────────────────────────────────────────────────────────────────────

def test_cli_psd2_generate():
    runner = CliRunner()
    result = runner.invoke(main, ['generate', 'psd2_consent'])
    assert result.exit_code == 0, result.output
    token = result.output.strip()
    assert len(token.split('.')) == 3


def test_cli_psd2_locale():
    runner = CliRunner()
    result = runner.invoke(main, ['generate', 'psd2_consent', '--locale', 'DE'])
    assert result.exit_code == 0
    _, payload, _ = _parse_jws(result.output.strip())
    assert payload['Data']['Initiation']['InstructedAmount']['Currency'] == 'EUR'


def test_cli_psd2_amount():
    runner = CliRunner()
    result = runner.invoke(main, ['generate', 'psd2_consent', '--amount', '250.50'])
    assert result.exit_code == 0
    _, payload, _ = _parse_jws(result.output.strip())
    assert payload['Data']['Initiation']['InstructedAmount']['Amount'] == '250.50'


def test_cli_psd2_bulk():
    runner = CliRunner()
    result = runner.invoke(main, ['bulk', 'psd2_consent', '--count', '3'])
    assert result.exit_code == 0
    import json as _json
    tokens = _json.loads(result.output)
    assert len(tokens) == 3
    for t in tokens:
        assert len(t.split('.')) == 3
