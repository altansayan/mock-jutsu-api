"""
Tests for God Mode #15 — OIDC / JWT Cryptographic Signature Kit
Types: oidc_token_set, jwks, oidc_token

Core invariants:
  - oidc_token_set : ES256 (P-256) key pair → signed JWT + verifiable JWKS, kid linked
  - jwks           : standalone JWK Set with fresh P-256 public key
  - oidc_token     : HS256 JWT with standard OIDC claims (fast, symmetric)
  - Zero external dependencies (stdlib hashlib, hmac, secrets)
"""

import base64
import json
import re
import time
import pytest
from mockjutsu.core import MockJutsuCore

jutsu = MockJutsuCore()

_B64URL_RE = re.compile(r'^[A-Za-z0-9_-]+$')


def _parse(t, **kwargs):
    return json.loads(jutsu.generate(t, **kwargs))


def _b64url_decode(s: str) -> bytes:
    pad = (4 - len(s) % 4) % 4
    return base64.urlsafe_b64decode(s + '=' * pad)


def _jwt_parts(token: str):
    parts = token.split('.')
    assert len(parts) == 3, f"JWT must have 3 parts, got {len(parts)}"
    return parts


def _jwt_header(token: str) -> dict:
    return json.loads(_b64url_decode(_jwt_parts(token)[0]))


def _jwt_payload(token: str) -> dict:
    return json.loads(_b64url_decode(_jwt_parts(token)[1]))


# ── oidc_token_set ────────────────────────────────────────────────────────────

class TestOidcTokenSet:

    def test_no_error(self):
        assert not jutsu.generate('oidc_token_set').startswith('ERROR')

    def test_returns_dict(self):
        assert isinstance(_parse('oidc_token_set'), dict)

    def test_required_keys(self):
        data = _parse('oidc_token_set')
        for k in ('token', 'jwks', 'kid', 'claims'):
            assert k in data, f"Missing key: {k}"

    def test_token_is_three_part_jwt(self):
        token = _parse('oidc_token_set')['token']
        _jwt_parts(token)  # asserts internally

    def test_header_alg_es256(self):
        token = _parse('oidc_token_set')['token']
        assert _jwt_header(token)['alg'] == 'ES256'

    def test_header_typ_jwt(self):
        token = _parse('oidc_token_set')['token']
        assert _jwt_header(token)['typ'] == 'JWT'

    def test_header_kid_matches_top_level(self):
        data  = _parse('oidc_token_set')
        assert _jwt_header(data['token'])['kid'] == data['kid']

    def test_jwks_key_kid_matches_token(self):
        data    = _parse('oidc_token_set')
        jwk_kid = data['jwks']['keys'][0]['kid']
        assert jwk_kid == data['kid']

    def test_jwks_structure(self):
        jwks = _parse('oidc_token_set')['jwks']
        assert 'keys' in jwks
        assert len(jwks['keys']) == 1

    def test_jwks_key_is_ec_p256(self):
        key = _parse('oidc_token_set')['jwks']['keys'][0]
        assert key['kty'] == 'EC'
        assert key['crv'] == 'P-256'

    def test_jwks_x_y_are_32_bytes(self):
        key = _parse('oidc_token_set')['jwks']['keys'][0]
        assert len(_b64url_decode(key['x'])) == 32
        assert len(_b64url_decode(key['y'])) == 32

    def test_claims_required_oidc_fields(self):
        claims = _parse('oidc_token_set')['claims']
        for f in ('iss', 'sub', 'aud', 'exp', 'iat', 'jti'):
            assert f in claims, f"Missing claim: {f}"

    def test_claims_exp_after_iat(self):
        claims = _parse('oidc_token_set')['claims']
        assert claims['exp'] > claims['iat']

    def test_claims_exp_in_future(self):
        claims = _parse('oidc_token_set')['claims']
        assert claims['exp'] > int(time.time())

    def test_signature_is_64_bytes(self):
        """ES256 JWS raw signature = r||s = 64 bytes."""
        token = _parse('oidc_token_set')['token']
        sig_b64 = _jwt_parts(token)[2]
        assert _B64URL_RE.match(sig_b64), "Signature is not valid base64url"
        assert len(_b64url_decode(sig_b64)) == 64

    def test_bulk_unique_kids(self):
        results = jutsu.bulk('oidc_token_set', 5)
        kids = [json.loads(r)['kid'] for r in results]
        assert len(set(kids)) == 5

    def test_bulk_unique_tokens(self):
        results = jutsu.bulk('oidc_token_set', 5)
        tokens = [json.loads(r)['token'] for r in results]
        assert len(set(tokens)) == 5


# ── jwks ──────────────────────────────────────────────────────────────────────

class TestJwks:

    def test_no_error(self):
        assert not jutsu.generate('jwks').startswith('ERROR')

    def test_returns_dict_with_keys(self):
        data = _parse('jwks')
        assert isinstance(data, dict)
        assert 'keys' in data

    def test_keys_is_nonempty_list(self):
        assert len(_parse('jwks')['keys']) >= 1

    def test_key_type_ec(self):
        assert _parse('jwks')['keys'][0]['kty'] == 'EC'

    def test_key_curve_p256(self):
        assert _parse('jwks')['keys'][0]['crv'] == 'P-256'

    def test_key_has_required_fields(self):
        key = _parse('jwks')['keys'][0]
        for f in ('kty', 'crv', 'x', 'y', 'kid', 'use', 'alg'):
            assert f in key, f"Missing JWK field: {f}"

    def test_key_use_sig(self):
        assert _parse('jwks')['keys'][0]['use'] == 'sig'

    def test_key_alg_es256(self):
        assert _parse('jwks')['keys'][0]['alg'] == 'ES256'

    def test_x_y_are_32_bytes(self):
        key = _parse('jwks')['keys'][0]
        assert len(_b64url_decode(key['x'])) == 32
        assert len(_b64url_decode(key['y'])) == 32

    def test_bulk_unique_kids(self):
        results = jutsu.bulk('jwks', 5)
        kids = [json.loads(r)['keys'][0]['kid'] for r in results]
        assert len(set(kids)) == 5


# ── oidc_token ────────────────────────────────────────────────────────────────

class TestOidcToken:

    def test_no_error(self):
        assert not jutsu.generate('oidc_token').startswith('ERROR')

    def test_is_three_part_jwt(self):
        token = jutsu.generate('oidc_token')
        _jwt_parts(token)

    def test_header_alg_hs256(self):
        token = jutsu.generate('oidc_token')
        assert _jwt_header(token)['alg'] == 'HS256'

    def test_header_typ_jwt(self):
        token = jutsu.generate('oidc_token')
        assert _jwt_header(token)['typ'] == 'JWT'

    def test_payload_has_oidc_claims(self):
        token = jutsu.generate('oidc_token')
        claims = _jwt_payload(token)
        for f in ('iss', 'sub', 'aud', 'exp', 'iat', 'jti'):
            assert f in claims, f"Missing claim: {f}"

    def test_exp_after_iat(self):
        claims = _jwt_payload(jutsu.generate('oidc_token'))
        assert claims['exp'] > claims['iat']

    def test_exp_in_future(self):
        claims = _jwt_payload(jutsu.generate('oidc_token'))
        assert claims['exp'] > int(time.time())

    def test_bulk_unique(self):
        results = jutsu.bulk('oidc_token', 5)
        assert len(set(results)) == 5
