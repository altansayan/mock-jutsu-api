"""
mock-jutsu — OIDC / JWT Cryptographic Signature Kit
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)

Generates linked ES256-signed JWTs and verifiable JWKS in pure Python.
Private key → P-256 scalar mult → EC public key → JWK → JWKS.
Signs JWT header+payload with ECDSA (SHA-256) and encodes as JWS compact.

Supported types:
  oidc_token_set — ES256 key pair → signed JWT + JWKS (kid linked), full OIDC claims
  jwks           — standalone JWK Set (EC P-256 public key, sig use)
  oidc_token     — HS256 JWT with standard OIDC claims (fast, no key pair)

Zero external dependencies: hashlib, hmac, secrets, base64, json (all stdlib).
"""

import base64
import hashlib
import hmac as _hmac
import json
import random
import secrets
import time
import uuid


# ── P-256 (secp256r1 / prime256v1) curve parameters ──────────────────────────

_P  = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF
_A  = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFC  # = p - 3
_GX = 0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296
_GY = 0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5
_N  = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551


# ── Jacobian arithmetic (P-256, a = p-3) ─────────────────────────────────────

def _dbl(x1, y1, z1):
    """P-256 Jacobian point doubling."""
    if z1 == 0:
        return 0, 1, 0
    y1sq = y1 * y1 % _P
    s    = 4 * x1 * y1sq % _P
    z1sq = z1 * z1 % _P
    m    = (3 * x1 * x1 + _A * (z1sq * z1sq % _P)) % _P
    x3   = (m * m - 2 * s) % _P
    y3   = (m * (s - x3) - 8 * y1sq * y1sq) % _P
    z3   = 2 * y1 * z1 % _P
    return x3, y3, z3


def _add(x1, y1, z1, x2, y2):
    """P-256 Jacobian + affine mixed addition."""
    if z1 == 0:
        return x2, y2, 1
    z1sq = z1 * z1 % _P
    u2   = x2 * z1sq % _P
    s2   = y2 * z1 * z1sq % _P
    h    = (u2 - x1) % _P
    r    = (s2 - y1) % _P
    if h == 0:
        if r == 0:
            return _dbl(x1, y1, z1)
        return 0, 1, 0
    h2   = h * h % _P
    h3   = h * h2 % _P
    x3   = (r * r - h3 - 2 * x1 * h2) % _P
    y3   = (r * (x1 * h2 - x3) - y1 * h3) % _P
    z3   = h * z1 % _P
    return x3, y3, z3


def _p256_mult(k):
    """Scalar multiply P-256 base point G by k → affine (x, y)."""
    Rx = Ry = Rz = None
    for i in range(k.bit_length() - 1, -1, -1):
        if Rz is not None:
            Rx, Ry, Rz = _dbl(Rx, Ry, Rz)
        if (k >> i) & 1:
            if Rz is None:
                Rx, Ry, Rz = _GX, _GY, 1
            else:
                Rx, Ry, Rz = _add(Rx, Ry, Rz, _GX, _GY)
    zi  = pow(Rz, _P - 2, _P)
    zi2 = zi * zi % _P
    return Rx * zi2 % _P, Ry * zi2 * zi % _P


# ── ECDSA sign (ES256 = ECDSA + SHA-256 + P-256) ─────────────────────────────

def _ecdsa_sign(privkey: int, msg_hash: bytes) -> bytes:
    """Returns raw r‖s (64 bytes) — JWS ES256 signature format."""
    h = int.from_bytes(msg_hash, 'big')
    while True:
        k   = secrets.randbelow(_N - 1) + 1
        rx, _ = _p256_mult(k)
        r   = rx % _N
        if r == 0:
            continue
        k_inv = pow(k, _N - 2, _N)
        s     = k_inv * (h + r * privkey) % _N
        if s == 0:
            continue
        return r.to_bytes(32, 'big') + s.to_bytes(32, 'big')


# ── Base64url helpers (RFC 7515 — no padding) ────────────────────────────────

def _b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()


def _b64u_uint(n: int) -> str:
    return _b64u(n.to_bytes(32, 'big'))


def _b64u_json(obj: dict) -> str:
    return _b64u(json.dumps(obj, separators=(',', ':')).encode())


# ── OIDC claims ───────────────────────────────────────────────────────────────

def _oidc_claims() -> dict:
    now = int(time.time())
    return {
        "iss": "https://mock-issuer.example.com",
        "sub": f"user-{uuid.uuid4()}",
        "aud": "mock-client",
        "exp": now + 3600,
        "iat": now,
        "jti": str(uuid.uuid4()),
        "email": f"user{random.randint(1, 9999)}@example.com",
        "name":  f"Mock User {random.randint(1, 999)}",
    }


# ── Public generators ─────────────────────────────────────────────────────────

def generate_oidc_token_set() -> str:
    """ES256 key pair → signed JWT + JWKS linked by kid."""
    privkey = secrets.randbelow(_N - 1) + 1
    px, py  = _p256_mult(privkey)
    kid     = str(uuid.uuid4())[:8]

    jwk = {
        "kty": "EC",
        "crv": "P-256",
        "x":   _b64u_uint(px),
        "y":   _b64u_uint(py),
        "kid": kid,
        "use": "sig",
        "alg": "ES256",
    }
    claims  = _oidc_claims()
    header  = _b64u_json({"alg": "ES256", "typ": "JWT", "kid": kid})
    payload = _b64u_json(claims)
    signing = f"{header}.{payload}".encode()
    sig     = _ecdsa_sign(privkey, hashlib.sha256(signing).digest())
    token   = f"{header}.{payload}.{_b64u(sig)}"

    return json.dumps({
        "token":  token,
        "jwks":   {"keys": [jwk]},
        "kid":    kid,
        "claims": claims,
    }, separators=(',', ':'))


def generate_jwks() -> str:
    """Standalone JWK Set — fresh P-256 public key, private key discarded."""
    privkey = secrets.randbelow(_N - 1) + 1
    px, py  = _p256_mult(privkey)
    kid     = str(uuid.uuid4())[:8]
    return json.dumps({
        "keys": [{
            "kty": "EC",
            "crv": "P-256",
            "x":   _b64u_uint(px),
            "y":   _b64u_uint(py),
            "kid": kid,
            "use": "sig",
            "alg": "ES256",
        }]
    }, separators=(',', ':'))


def generate_oidc_token() -> str:
    """HS256 JWT with standard OIDC claims — symmetric key, no EC math."""
    secret  = secrets.token_bytes(32)
    claims  = _oidc_claims()
    header  = _b64u_json({"alg": "HS256", "typ": "JWT"})
    payload = _b64u_json(claims)
    signing = f"{header}.{payload}".encode()
    sig     = _hmac.new(secret, signing, hashlib.sha256).digest()
    return f"{header}.{payload}.{_b64u(sig)}"


# ── Generator class ───────────────────────────────────────────────────────────

class OidcGenerator:
    """OIDC / JWT cryptographic signature kit — ES256 + HS256, zero external deps."""

    def generate(self, data_type: str, **kwargs) -> str:
        if data_type == 'oidc_token_set':
            return generate_oidc_token_set()
        if data_type == 'jwks':
            return generate_jwks()
        if data_type == 'oidc_token':
            return generate_oidc_token()
        return f"ERROR: Unknown type '{data_type}'"
