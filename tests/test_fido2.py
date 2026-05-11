"""
Tests for God Mode #12 — Passkey / FIDO2 (WebAuthn) Mocks
Types: webauthn_credential, fido2_assertion

Core invariants:
  - webauthn_credential: CBOR attestationObject + clientDataJSON (webauthn.create)
  - fido2_assertion: authenticatorData (37 bytes) + DER signature + clientDataJSON (webauthn.get)
  - All binary fields are base64url encoded
  - Zero external dependencies (stdlib only)
"""

import base64
import json
import pytest
from mockjutsu.core import MockJutsuCore

jutsu = MockJutsuCore()


def _b64url_decode(s: str) -> bytes:
    s += '=' * (-len(s) % 4)
    return base64.urlsafe_b64decode(s)


def _parse_credential(gen_type: str) -> dict:
    return json.loads(jutsu.generate(gen_type))


# ── webauthn_credential ───────────────────────────────────────────────────────

class TestWebAuthnCredential:

    def test_returns_valid_json(self):
        val = jutsu.generate('webauthn_credential')
        assert isinstance(json.loads(val), dict)

    def test_no_error_prefix(self):
        for _ in range(5):
            assert not jutsu.generate('webauthn_credential').startswith('ERROR')

    def test_top_level_keys(self):
        data = _parse_credential('webauthn_credential')
        for key in ('id', 'rawId', 'type', 'response', 'clientExtensionResults'):
            assert key in data, f"Missing key: {key}"

    def test_type_is_public_key(self):
        assert _parse_credential('webauthn_credential')['type'] == 'public-key'

    def test_id_equals_raw_id(self):
        data = _parse_credential('webauthn_credential')
        assert data['id'] == data['rawId']

    def test_id_is_32_byte_base64url(self):
        data = _parse_credential('webauthn_credential')
        assert len(_b64url_decode(data['id'])) == 32

    def test_response_required_fields(self):
        resp = _parse_credential('webauthn_credential')['response']
        assert 'clientDataJSON' in resp
        assert 'attestationObject' in resp

    def test_client_data_json_type(self):
        resp = _parse_credential('webauthn_credential')['response']
        cdj = json.loads(_b64url_decode(resp['clientDataJSON']))
        assert cdj['type'] == 'webauthn.create'

    def test_client_data_json_has_challenge_and_origin(self):
        resp = _parse_credential('webauthn_credential')['response']
        cdj = json.loads(_b64url_decode(resp['clientDataJSON']))
        assert 'challenge' in cdj
        assert 'origin' in cdj
        assert cdj['origin'].startswith('http')

    def test_challenge_is_32_bytes(self):
        resp = _parse_credential('webauthn_credential')['response']
        cdj = json.loads(_b64url_decode(resp['clientDataJSON']))
        assert len(_b64url_decode(cdj['challenge'])) == 32

    def test_attestation_object_is_cbor_map_with_3_items(self):
        resp = _parse_credential('webauthn_credential')['response']
        att = _b64url_decode(resp['attestationObject'])
        # 0xa3 = CBOR map (major type 5) with 3 items
        assert att[0] == 0xa3, f"Expected CBOR map header 0xa3, got 0x{att[0]:02x}"

    def test_attestation_object_minimum_length(self):
        resp = _parse_credential('webauthn_credential')['response']
        att = _b64url_decode(resp['attestationObject'])
        # fmt + attStmt + authData headers + 37-byte authData minimum
        assert len(att) > 60

    def test_bulk_produces_unique_ids(self):
        results = jutsu.bulk('webauthn_credential', 15)
        ids = [json.loads(r)['id'] for r in results]
        assert len(set(ids)) == 15

    def test_cross_origin_is_false(self):
        resp = _parse_credential('webauthn_credential')['response']
        cdj = json.loads(_b64url_decode(resp['clientDataJSON']))
        assert cdj.get('crossOrigin') is False


# ── fido2_assertion ───────────────────────────────────────────────────────────

class TestFido2Assertion:

    def test_returns_valid_json(self):
        val = jutsu.generate('fido2_assertion')
        assert isinstance(json.loads(val), dict)

    def test_no_error_prefix(self):
        for _ in range(5):
            assert not jutsu.generate('fido2_assertion').startswith('ERROR')

    def test_top_level_keys(self):
        data = _parse_credential('fido2_assertion')
        for key in ('id', 'rawId', 'type', 'response', 'clientExtensionResults'):
            assert key in data

    def test_type_is_public_key(self):
        assert _parse_credential('fido2_assertion')['type'] == 'public-key'

    def test_response_required_fields(self):
        resp = _parse_credential('fido2_assertion')['response']
        for key in ('clientDataJSON', 'authenticatorData', 'signature', 'userHandle'):
            assert key in resp, f"Missing response key: {key}"

    def test_client_data_type_is_get(self):
        resp = _parse_credential('fido2_assertion')['response']
        cdj = json.loads(_b64url_decode(resp['clientDataJSON']))
        assert cdj['type'] == 'webauthn.get'

    def test_auth_data_is_exactly_37_bytes(self):
        resp = _parse_credential('fido2_assertion')['response']
        auth_data = _b64url_decode(resp['authenticatorData'])
        assert len(auth_data) == 37, f"Expected 37 bytes, got {len(auth_data)}"

    def test_auth_data_up_flag_set(self):
        resp = _parse_credential('fido2_assertion')['response']
        flags = _b64url_decode(resp['authenticatorData'])[32]
        assert flags & 0x01, "User Present (UP) flag must be set"

    def test_auth_data_uv_flag_set(self):
        resp = _parse_credential('fido2_assertion')['response']
        flags = _b64url_decode(resp['authenticatorData'])[32]
        assert flags & 0x04, "User Verified (UV) flag must be set"

    def test_auth_data_counter_nonzero(self):
        # counter is bytes 33-36 (big-endian uint32)
        resp = _parse_credential('fido2_assertion')['response']
        auth_data = _b64url_decode(resp['authenticatorData'])
        counter = int.from_bytes(auth_data[33:37], 'big')
        assert counter > 0

    def test_signature_is_der_sequence(self):
        resp = _parse_credential('fido2_assertion')['response']
        sig = _b64url_decode(resp['signature'])
        assert sig[0] == 0x30, f"Expected DER SEQUENCE tag 0x30, got 0x{sig[0]:02x}"

    def test_signature_der_r_and_s_are_integers(self):
        resp = _parse_credential('fido2_assertion')['response']
        sig = _b64url_decode(resp['signature'])
        # sig[2] should be INTEGER tag 0x02
        assert sig[2] == 0x02, "r component must be DER INTEGER"

    def test_user_handle_is_16_bytes(self):
        resp = _parse_credential('fido2_assertion')['response']
        assert len(_b64url_decode(resp['userHandle'])) == 16

    def test_bulk_unique_ids(self):
        results = jutsu.bulk('fido2_assertion', 15)
        ids = [json.loads(r)['id'] for r in results]
        assert len(set(ids)) == 15

    def test_id_equals_raw_id(self):
        data = _parse_credential('fido2_assertion')
        assert data['id'] == data['rawId']
