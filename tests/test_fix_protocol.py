"""
mock-jutsu — FIX Protocol 4.4 Tests
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)

Standard: FIX Protocol 4.4 — FIX Trading Community (fixtradingcommunity.org)

Coverage:
  - Message structure (tag order: 8, 9, ..., 10)
  - BeginString format validation
  - BodyLength algorithm correctness
  - CheckSum algorithm (sum of all bytes mod 256)
  - Required tags for New Order Single (MsgType=D)
  - Side and OrdType enum validation
  - Limit/Stop orders must include Price (tag 44)
  - SendingTime / TransactTime format (YYYYMMDD-HH:MM:SS.sss)
  - Uniqueness (CSPRNG)
  - CLI integration
"""

import re
import pytest
from click.testing import CliRunner
from mockjutsu.core import jutsu
from mockjutsu.cli import main

SOH = chr(1)

# ── Parser helpers ────────────────────────────────────────────────────────────

def _parse(msg: str) -> dict:
    """Parse FIX message into ordered list and tag→value dict."""
    fields = [f for f in msg.split(SOH) if f]
    parsed = {}
    order = []
    for f in fields:
        if '=' in f:
            tag, val = f.split('=', 1)
            parsed[tag] = val
            order.append(tag)
    return parsed, order


def _compute_checksum(msg_before_10: str) -> int:
    """FIX CheckSum: sum of all byte values before tag-10 field, mod 256."""
    return sum(ord(c) for c in msg_before_10) % 256


def _compute_body_length(msg: str) -> int:
    """FIX BodyLength: byte count from start of tag-35 to SOH after last body tag."""
    # Everything after "9=NNN\x01" and before "10=NNN\x01"
    start = msg.index(f"{SOH}35=") + 1        # byte right after "9=NNN\x01"
    end   = msg.rindex(f"{SOH}10=") + 1       # SOH before "10=" is still body
    return len(msg[start:end])


# ── Structure tests ───────────────────────────────────────────────────────────

def test_fix_message_is_string():
    msg = jutsu.generate('fix_message')
    assert isinstance(msg, str)
    assert not msg.startswith('ERROR')


def test_fix_message_begins_with_tag_8():
    msg = jutsu.generate('fix_message')
    assert msg.startswith('8='), f"Must start with tag 8, got: {msg[:20]}"


def test_fix_message_ends_with_soh():
    msg = jutsu.generate('fix_message')
    assert msg.endswith(SOH), "FIX message must end with SOH"


def test_fix_begin_string_is_fix44():
    msg = jutsu.generate('fix_message')
    parsed, _ = _parse(msg)
    assert parsed['8'] == 'FIX.4.4', f"BeginString must be FIX.4.4, got: {parsed.get('8')}"


def test_fix_tag_order_8_9_first():
    msg = jutsu.generate('fix_message')
    _, order = _parse(msg)
    assert order[0] == '8', "Tag 8 (BeginString) must be first"
    assert order[1] == '9', "Tag 9 (BodyLength) must be second"


def test_fix_tag_10_is_last():
    msg = jutsu.generate('fix_message')
    _, order = _parse(msg)
    assert order[-1] == '10', "Tag 10 (CheckSum) must be last"


def test_fix_checksum_valid():
    """CheckSum = sum of all bytes before '10=' field, mod 256."""
    msg = jutsu.generate('fix_message')
    parsed, _ = _parse(msg)

    # Split at the last occurrence of SOH + "10="
    split_point = msg.rindex(f'{SOH}10=') + 1   # include the SOH before 10=
    before_10 = msg[:split_point]

    expected = _compute_checksum(before_10)
    actual   = int(parsed['10'])
    assert actual == expected, (
        f"CheckSum mismatch: expected {expected:03d}, got {actual:03d}"
    )


def test_fix_checksum_is_3_digits():
    msg = jutsu.generate('fix_message')
    parsed, _ = _parse(msg)
    assert re.fullmatch(r'\d{3}', parsed['10']), (
        f"CheckSum must be 3-digit zero-padded, got: {parsed['10']}"
    )


def test_fix_body_length_valid():
    """BodyLength = byte count from start of tag-35 to SOH after last body tag."""
    msg = jutsu.generate('fix_message')
    parsed, _ = _parse(msg)

    expected = _compute_body_length(msg)
    actual   = int(parsed['9'])
    assert actual == expected, (
        f"BodyLength mismatch: expected {expected}, got {actual}"
    )


# ── Required tags ─────────────────────────────────────────────────────────────

REQUIRED_TAGS = ['8', '9', '35', '49', '56', '34', '52', '10']

@pytest.mark.parametrize("tag", REQUIRED_TAGS)
def test_fix_required_tag_present(tag):
    msg = jutsu.generate('fix_message')
    parsed, _ = _parse(msg)
    assert tag in parsed, f"Required tag {tag} missing from FIX message"


NEW_ORDER_TAGS = ['11', '55', '54', '38', '40', '60']

@pytest.mark.parametrize("tag", NEW_ORDER_TAGS)
def test_fix_new_order_tag_present(tag):
    """New Order Single (D) must include order-specific tags."""
    msg = jutsu.generate('fix_message')
    parsed, _ = _parse(msg)
    assert tag in parsed, f"New Order tag {tag} missing from FIX message"


# ── Field value validation ────────────────────────────────────────────────────

def test_fix_msg_type_is_new_order():
    msg = jutsu.generate('fix_message')
    parsed, _ = _parse(msg)
    assert parsed['35'] == 'D', f"MsgType must be 'D' (New Order Single), got: {parsed['35']}"


def test_fix_side_valid():
    """Side: 1=Buy, 2=Sell (FIX 4.4 tag 54 enum)."""
    results = {_parse(jutsu.generate('fix_message'))[0]['54'] for _ in range(30)}
    assert results.issubset({'1', '2'}), f"Invalid Side values found: {results}"
    assert len(results) > 1, "Side should alternate between Buy and Sell"


def test_fix_ord_type_valid():
    """OrdType: 1=Market, 2=Limit, 3=Stop (FIX 4.4 tag 40 enum)."""
    results = {_parse(jutsu.generate('fix_message'))[0]['40'] for _ in range(50)}
    assert results.issubset({'1', '2', '3'}), f"Invalid OrdType values: {results}"


def test_fix_limit_order_has_price():
    """Limit (2) and Stop (3) orders must include Price (tag 44)."""
    for _ in range(100):
        msg = jutsu.generate('fix_message')
        parsed, _ = _parse(msg)
        if parsed['40'] in ('2', '3'):
            assert '44' in parsed, (
                f"Limit/Stop order (OrdType={parsed['40']}) missing Price (tag 44)"
            )


def test_fix_market_order_no_price():
    """Market orders (OrdType=1) must NOT include Price (tag 44)."""
    for _ in range(100):
        msg = jutsu.generate('fix_message')
        parsed, _ = _parse(msg)
        if parsed['40'] == '1':
            assert '44' not in parsed, (
                "Market order must not include Price (tag 44)"
            )


def test_fix_order_qty_positive_integer():
    for _ in range(10):
        parsed, _ = _parse(jutsu.generate('fix_message'))
        qty = int(parsed['38'])
        assert qty > 0, f"OrderQty must be positive, got: {qty}"


def test_fix_seq_num_positive_integer():
    parsed, _ = _parse(jutsu.generate('fix_message'))
    assert int(parsed['34']) > 0


def test_fix_sending_time_format():
    """SendingTime (tag 52) must match YYYYMMDD-HH:MM:SS.sss."""
    parsed, _ = _parse(jutsu.generate('fix_message'))
    pattern = r'^\d{8}-\d{2}:\d{2}:\d{2}\.\d{3}$'
    assert re.fullmatch(pattern, parsed['52']), (
        f"SendingTime format invalid: {parsed['52']}"
    )


def test_fix_transact_time_format():
    """TransactTime (tag 60) must match YYYYMMDD-HH:MM:SS.sss."""
    parsed, _ = _parse(jutsu.generate('fix_message'))
    pattern = r'^\d{8}-\d{2}:\d{2}:\d{2}\.\d{3}$'
    assert re.fullmatch(pattern, parsed['60']), (
        f"TransactTime format invalid: {parsed['60']}"
    )


def test_fix_price_format():
    """Price (tag 44) when present must be a valid decimal with 2 decimal places."""
    for _ in range(100):
        parsed, _ = _parse(jutsu.generate('fix_message'))
        if '44' in parsed:
            price = float(parsed['44'])
            assert price > 0, f"Price must be positive, got: {price}"
            assert re.fullmatch(r'\d+\.\d{2}', parsed['44']), (
                f"Price must have 2 decimal places, got: {parsed['44']}"
            )
            break


def test_fix_cl_ord_id_unique():
    """ClOrdID (tag 11) must be unique across calls (CSPRNG)."""
    ids = {_parse(jutsu.generate('fix_message'))[0]['11'] for _ in range(20)}
    assert len(ids) == 20, "Duplicate ClOrdID detected — entropy source broken"


# ── Uniqueness ────────────────────────────────────────────────────────────────

def test_fix_message_unique():
    messages = {jutsu.generate('fix_message') for _ in range(10)}
    assert len(messages) == 10, "Duplicate FIX messages detected"


# ── CLI integration ───────────────────────────────────────────────────────────

def test_cli_fix_message():
    runner = CliRunner()
    result = runner.invoke(main, ['generate', 'fix_message'])
    assert result.exit_code == 0, result.output
    msg = result.output.strip()
    assert msg.startswith('8=FIX.4.4')
    parsed, _ = _parse(msg)
    assert '35' in parsed
    assert parsed['35'] == 'D'


def test_cli_bulk_fix_message():
    runner = CliRunner()
    result = runner.invoke(main, ['bulk', 'fix_message', '--count', '3'])
    assert result.exit_code == 0
    import json
    messages = json.loads(result.output)
    assert len(messages) == 3
    for msg in messages:
        assert msg.startswith('8=FIX.4.4')
        parsed, _ = _parse(msg)
        checksum_split = msg.rindex(f'{SOH}10=') + 1
        expected_cs = sum(ord(c) for c in msg[:checksum_split]) % 256
        assert int(parsed['10']) == expected_cs
