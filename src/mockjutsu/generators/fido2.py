"""
mock-jutsu — FIDO2 / WebAuthn Mock Generator
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)

Generates realistic WebAuthn registration (attestation) and authentication
(assertion) responses for testing passwordless login flows.

Supported types:
  webauthn_credential — registration response with CBOR attestationObject
  fido2_assertion     — authentication response with DER-encoded signature

Zero external dependencies: hashlib, base64, json, secrets (all stdlib).

CBOR encoding (RFC 7049):
  Implements a minimal encoder for the subset needed by WebAuthn:
  unsigned int, negative int, byte string, text string, map.
"""

import base64
import hashlib
import json
import secrets

# ── Minimal CBOR encoder (RFC 7049) ──────────────────────────────────────────

def _cbor_uint(major: int, value: int) -> bytes:
    mt = major << 5
    if value <= 23:
        return bytes([mt | value])
    if value <= 0xFF:
        return bytes([mt | 24, value])
    if value <= 0xFFFF:
        return bytes([mt | 25]) + value.to_bytes(2, 'big')
    return bytes([mt | 26]) + value.to_bytes(4, 'big')


def _cbor_encode(obj) -> bytes:
    if isinstance(obj, bool):
        return bytes([0xf5 if obj else 0xf4])
    if isinstance(obj, int):
        if obj >= 0:
            return _cbor_uint(0, obj)
        return _cbor_uint(1, -obj - 1)
    if isinstance(obj, bytes):
        return _cbor_uint(2, len(obj)) + obj
    if isinstance(obj, str):
        b = obj.encode('utf-8')
        return _cbor_uint(3, len(b)) + b
    if isinstance(obj, dict):
        items = b''.join(_cbor_encode(k) + _cbor_encode(v) for k, v in obj.items())
        return _cbor_uint(5, len(obj)) + items
    raise TypeError(f"Cannot CBOR encode {type(obj)}")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()


_RP_IDS = [
    'example.com',
    'login.acme.io',
    'auth.mockjutsu.dev',
    'accounts.test.org',
    'secure.app.localhost',
]

_ORIGINS = {
    'example.com':          'https://example.com',
    'login.acme.io':        'https://login.acme.io',
    'auth.mockjutsu.dev':   'https://auth.mockjutsu.dev',
    'accounts.test.org':    'https://accounts.test.org',
    'secure.app.localhost': 'http://localhost:3000',
}


def _cose_key(x: bytes, y: bytes) -> bytes:
    """EC P-256 public key in COSE_Key (CBOR) format — RFC 8152."""
    return _cbor_encode({1: 2, 3: -7, -1: 1, -2: x, -3: y})


def _auth_data_registration(rp_id: str, counter: int, cred_id: bytes, cose: bytes) -> bytes:
    """WebAuthn authenticatorData for registration (AT flag set, credential data included)."""
    rp_hash   = hashlib.sha256(rp_id.encode()).digest()   # 32 bytes
    flags     = bytes([0x45])                              # UP=1 | UV=4 | AT=64
    counter_b = counter.to_bytes(4, 'big')
    aaguid    = bytes(16)                                  # no specific authenticator model
    cred_len  = len(cred_id).to_bytes(2, 'big')
    return rp_hash + flags + counter_b + aaguid + cred_len + cred_id + cose


def _der_signature() -> bytes:
    """Fake DER-encoded ECDSA signature (r, s — 32 bytes each, positive integers)."""
    r = bytearray(secrets.token_bytes(32))
    s = bytearray(secrets.token_bytes(32))
    r[0] &= 0x7F  # ensure positive (no sign extension)
    s[0] &= 0x7F
    r, s = bytes(r), bytes(s)
    body = bytes([0x02, len(r)]) + r + bytes([0x02, len(s)]) + s
    return bytes([0x30, len(body)]) + body


# ── Public generators ─────────────────────────────────────────────────────────

def generate_webauthn_credential() -> str:
    """WebAuthn registration response: attestationObject (CBOR) + clientDataJSON.

    MOCK LIMITATION: x/y coordinates are random bytes, NOT a real EC P-256 keypair.
    The attestation format is 'none' (self-attestation). A real credential requires
    a hardware authenticator that signs with its private key. Will NOT pass FIDO2
    attestation verification or rpId/origin binding checks in a real relying party.
    Use for JSON structure and field presence tests only.
    """
    rp_id    = secrets.choice(_RP_IDS)
    origin   = _ORIGINS[rp_id]
    cred_id  = secrets.token_bytes(32)
    challenge = secrets.token_bytes(32)
    counter  = secrets.randbelow(1000)
    x, y     = secrets.token_bytes(32), secrets.token_bytes(32)

    client_data = {
        'type':        'webauthn.create',
        'challenge':   _b64url(challenge),
        'origin':      origin,
        'crossOrigin': False,
    }
    cdj_bytes = json.dumps(client_data, separators=(',', ':')).encode()

    cose     = _cose_key(x, y)
    auth_data = _auth_data_registration(rp_id, counter, cred_id, cose)
    att_obj  = _cbor_encode({'fmt': 'none', 'attStmt': {}, 'authData': auth_data})

    return json.dumps({
        'id':                   _b64url(cred_id),
        'rawId':                _b64url(cred_id),
        'type':                 'public-key',
        'response': {
            'clientDataJSON':   _b64url(cdj_bytes),
            'attestationObject': _b64url(att_obj),
        },
        'clientExtensionResults': {},
    }, separators=(',', ':'))


def generate_fido2_assertion() -> str:
    """WebAuthn authentication response: authenticatorData + DER signature.

    MOCK LIMITATION: DER signature bytes are random — NOT produced by a real
    authenticator private key. Will NOT pass ECDSA signature verification in any
    real relying party. Use for JSON structure and field presence tests only.
    """
    rp_id     = secrets.choice(_RP_IDS)
    origin    = _ORIGINS[rp_id]
    cred_id   = secrets.token_bytes(32)
    challenge = secrets.token_bytes(32)
    counter   = secrets.randbelow(99999) + 1
    user_id   = secrets.token_bytes(16)

    client_data = {
        'type':        'webauthn.get',
        'challenge':   _b64url(challenge),
        'origin':      origin,
        'crossOrigin': False,
    }
    cdj_bytes = json.dumps(client_data, separators=(',', ':')).encode()

    # authenticatorData: rp_id_hash (32) + flags (1) + counter (4) = 37 bytes
    rp_hash   = hashlib.sha256(rp_id.encode()).digest()
    flags     = bytes([0x05])       # UP=1 | UV=4, no AT
    auth_data = rp_hash + flags + counter.to_bytes(4, 'big')

    return json.dumps({
        'id':    _b64url(cred_id),
        'rawId': _b64url(cred_id),
        'type':  'public-key',
        'response': {
            'clientDataJSON':   _b64url(cdj_bytes),
            'authenticatorData': _b64url(auth_data),
            'signature':        _b64url(_der_signature()),
            'userHandle':       _b64url(user_id),
        },
        'clientExtensionResults': {},
    }, separators=(',', ':'))


# ── Generator class ───────────────────────────────────────────────────────────

class Fido2Generator:
    """Generates FIDO2/WebAuthn mock payloads for passwordless login testing."""

    def generate(self, data_type: str, **kwargs) -> str:
        if data_type == 'webauthn_credential':
            return generate_webauthn_credential()
        if data_type == 'fido2_assertion':
            return generate_fido2_assertion()
        return f"ERROR: Unknown type '{data_type}'"
