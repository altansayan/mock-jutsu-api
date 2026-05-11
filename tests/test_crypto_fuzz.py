"""
Tests for God Mode #20 — JWT Attack & ASN.1 Fuzzing Generator
Types: jwt_attack, asn1_fuzz

Core invariants:
  - jwt_attack : JSON dict, token has 3 dot-separated parts, header/payload decodable JSON,
                 none_alg → empty signature, expired → exp in past, kid_injection → kid in header
  - asn1_fuzz  : JSON dict, hex field is valid hex with even length, at least 2 bytes,
                 fuzz_type from known set
"""

import base64
import json
import re
import time
import pytest
from mockjutsu.core import MockJutsuCore

jutsu = MockJutsuCore()

_VALID_ATTACK_TYPES = {'none_alg', 'expired', 'invalid_signature', 'alg_confusion', 'kid_injection', 'empty_password'}
_VALID_FUZZ_TYPES   = {'truncated', 'overflow_length', 'wrong_tag', 'nested_mismatch', 'zero_length', 'random_bytes'}
_HEX_RE = re.compile(r'^[0-9a-f]+$')


def _b64url_decode(s: str) -> bytes:
    padding = '=' * (4 - len(s) % 4)
    return base64.urlsafe_b64decode(s + padding)


# ── jwt_attack ────────────────────────────────────────────────────────────────

class TestJwtAttack:

    def test_no_error(self):
        assert not jutsu.generate('jwt_attack').startswith('ERROR')

    def test_returns_string(self):
        assert isinstance(jutsu.generate('jwt_attack'), str)

    def test_is_valid_json(self):
        json.loads(jutsu.generate('jwt_attack'))

    def test_is_dict(self):
        assert isinstance(json.loads(jutsu.generate('jwt_attack')), dict)

    def test_has_token_field(self):
        assert 'token' in json.loads(jutsu.generate('jwt_attack'))

    def test_has_attack_type_field(self):
        assert 'attack_type' in json.loads(jutsu.generate('jwt_attack'))

    def test_has_description_field(self):
        assert 'description' in json.loads(jutsu.generate('jwt_attack'))

    def test_attack_type_is_valid(self):
        for _ in range(20):
            assert json.loads(jutsu.generate('jwt_attack'))['attack_type'] in _VALID_ATTACK_TYPES

    def test_token_has_exactly_two_dots(self):
        """All JWT tokens (including none_alg) must contain exactly 2 dots."""
        for _ in range(20):
            token = json.loads(jutsu.generate('jwt_attack'))['token']
            assert token.count('.') == 2, f"Expected 2 dots in: {token[:80]}"

    def test_header_is_decodable_json(self):
        token  = json.loads(jutsu.generate('jwt_attack'))['token']
        header = json.loads(_b64url_decode(token.split('.')[0]))
        assert 'alg' in header and 'typ' in header

    def test_payload_is_decodable_json(self):
        token   = json.loads(jutsu.generate('jwt_attack'))['token']
        payload = json.loads(_b64url_decode(token.split('.')[1]))
        assert isinstance(payload, dict)

    def test_payload_has_sub_and_iat(self):
        token   = json.loads(jutsu.generate('jwt_attack'))['token']
        payload = json.loads(_b64url_decode(token.split('.')[1]))
        assert 'sub' in payload and 'iat' in payload

    def test_none_alg_has_empty_signature(self):
        """none_alg attack: third part of token must be empty string."""
        for _ in range(40):
            data = json.loads(jutsu.generate('jwt_attack'))
            if data['attack_type'] == 'none_alg':
                assert data['token'].endswith('.'), "none_alg token must end with '.'"
                assert data['token'].split('.')[2] == ''
                return
        pytest.skip("none_alg not generated in 40 tries")

    def test_expired_has_past_exp(self):
        """expired attack: exp claim must be in the past."""
        now = int(time.time())
        for _ in range(40):
            data = json.loads(jutsu.generate('jwt_attack'))
            if data['attack_type'] == 'expired':
                payload = json.loads(_b64url_decode(data['token'].split('.')[1]))
                assert payload['exp'] < now, f"exp {payload['exp']} should be < {now}"
                return
        pytest.skip("expired not generated in 40 tries")

    def test_kid_injection_has_kid_in_header(self):
        """kid_injection attack: header must contain a 'kid' field."""
        for _ in range(40):
            data = json.loads(jutsu.generate('jwt_attack'))
            if data['attack_type'] == 'kid_injection':
                header = json.loads(_b64url_decode(data['token'].split('.')[0]))
                assert 'kid' in header, "kid_injection token must have 'kid' in header"
                return
        pytest.skip("kid_injection not generated in 40 tries")

    def test_bulk_attack_type_distribution(self):
        """Multiple attack types appear across 30 runs."""
        types = {json.loads(jutsu.generate('jwt_attack'))['attack_type'] for _ in range(30)}
        assert len(types) > 2, f"Expected >2 unique attack types, got: {types}"

    def test_bulk_unique_tokens(self):
        tokens = {json.loads(r)['token'] for r in jutsu.bulk('jwt_attack', 5)}
        assert len(tokens) == 5


# ── asn1_fuzz ─────────────────────────────────────────────────────────────────

class TestAsn1Fuzz:

    def test_no_error(self):
        assert not jutsu.generate('asn1_fuzz').startswith('ERROR')

    def test_returns_string(self):
        assert isinstance(jutsu.generate('asn1_fuzz'), str)

    def test_is_valid_json(self):
        json.loads(jutsu.generate('asn1_fuzz'))

    def test_is_dict(self):
        assert isinstance(json.loads(jutsu.generate('asn1_fuzz')), dict)

    def test_has_hex_field(self):
        assert 'hex' in json.loads(jutsu.generate('asn1_fuzz'))

    def test_hex_is_lowercase_hex(self):
        hex_str = json.loads(jutsu.generate('asn1_fuzz'))['hex']
        assert _HEX_RE.match(hex_str), f"Not valid hex: {hex_str[:40]}"

    def test_hex_length_is_even(self):
        hex_str = json.loads(jutsu.generate('asn1_fuzz'))['hex']
        assert len(hex_str) % 2 == 0, "Hex string must have even length"

    def test_has_at_least_2_bytes(self):
        hex_str = json.loads(jutsu.generate('asn1_fuzz'))['hex']
        assert len(hex_str) >= 4, "Must have at least 2 bytes (4 hex chars)"

    def test_has_fuzz_type_field(self):
        assert 'fuzz_type' in json.loads(jutsu.generate('asn1_fuzz'))

    def test_fuzz_type_is_valid(self):
        for _ in range(20):
            assert json.loads(jutsu.generate('asn1_fuzz'))['fuzz_type'] in _VALID_FUZZ_TYPES

    def test_bulk_fuzz_type_distribution(self):
        """Multiple fuzz types appear across 30 runs."""
        types = {json.loads(jutsu.generate('asn1_fuzz'))['fuzz_type'] for _ in range(30)}
        assert len(types) > 2, f"Expected >2 unique fuzz types, got: {types}"

    def test_bulk_unique_hex(self):
        hexes = {json.loads(r)['hex'] for r in jutsu.bulk('asn1_fuzz', 5)}
        assert len(hexes) >= 4
