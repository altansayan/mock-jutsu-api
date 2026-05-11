"""
mock-jutsu — Web3 "Pure Math" Wallet Generator
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)

Generates complete, mathematically valid wallets via elliptic curve arithmetic.
Private key → EC scalar multiplication → public key → address derivation.

Supported types:
  eth_wallet  — secp256k1 → Keccak-256 → EIP-55 checksummed address
  btc_wallet  — secp256k1 → SHA256+RIPEMD160 → Base58Check P2PKH + WIF
  sol_wallet  — Ed25519   → base58 address (Solana Phantom keypair format)

Zero external dependencies: hashlib, secrets (stdlib) + keccak256 / base58 from
the existing crypto module (already in this package, not a third-party lib).
"""

import hashlib
import json
import secrets

from .crypto import _keccak256, _base58_encode

# ── secp256k1 — Jacobian coordinates (no per-step modular inverse) ────────────
# Jacobian (X:Y:Z) represents affine (X/Z², Y/Z³).
# One inversion at the end converts back to affine.

_SP  = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
_GX  = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
_GY  = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
_SN  = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def _sdbl(x1, y1, z1):
    """secp256k1 Jacobian point doubling (a = 0)."""
    ysq = y1 * y1 % _SP
    s   = 4 * x1 * ysq % _SP
    m   = 3 * x1 * x1 % _SP
    x3  = (m * m - 2 * s) % _SP
    y3  = (m * (s - x3) - 8 * ysq * ysq) % _SP
    z3  = 2 * y1 * z1 % _SP
    return x3, y3, z3


def _sadd(x1, y1, z1, x2, y2):
    """secp256k1 Jacobian + affine mixed addition."""
    z1sq = z1 * z1 % _SP
    u2   = x2 * z1sq % _SP
    s2   = y2 * z1 * z1sq % _SP
    h    = (u2 - x1) % _SP
    r    = (s2 - y1) % _SP
    if h == 0:
        if r == 0:
            return _sdbl(x1, y1, z1)
        return 0, 1, 0
    h2   = h * h % _SP
    h3   = h * h2 % _SP
    x3   = (r * r - h3 - 2 * x1 * h2) % _SP
    y3   = (r * (x1 * h2 - x3) - y1 * h3) % _SP
    z3   = h * z1 % _SP
    return x3, y3, z3


def _smult(k):
    """Multiply secp256k1 base point G by scalar k → affine (x, y)."""
    Rx = Ry = Rz = None
    bits = k.bit_length()
    for i in range(bits - 1, -1, -1):
        if Rz is not None:
            Rx, Ry, Rz = _sdbl(Rx, Ry, Rz)
        if (k >> i) & 1:
            if Rz is None:
                Rx, Ry, Rz = _GX, _GY, 1
            else:
                Rx, Ry, Rz = _sadd(Rx, Ry, Rz, _GX, _GY)
    zi  = pow(Rz, _SP - 2, _SP)
    zi2 = zi * zi % _SP
    return Rx * zi2 % _SP, Ry * zi2 * zi % _SP


# ── Ed25519 — extended twisted Edwards coordinates ────────────────────────────
# Extended (X:Y:Z:T) where affine (x,y) = (X/Z, Y/Z) and T = XY/Z.

_EP = 2 ** 255 - 19
_ED = -121665 * pow(121666, _EP - 2, _EP) % _EP


def _eadd(P, Q):
    x1, y1, z1, t1 = P
    x2, y2, z2, t2 = Q
    a = (y1 - x1) * (y2 - x2) % _EP
    b = (y1 + x1) * (y2 + x2) % _EP
    c = 2 * t1 * _ED * t2 % _EP
    d = 2 * z1 * z2 % _EP
    e = b - a;  f = d - c;  g = d + c;  h = b + a
    return e*f % _EP, g*h % _EP, f*g % _EP, e*h % _EP


def _emult(k, P):
    """Ed25519 scalar multiplication using double-and-add."""
    R = (0, 1, 1, 0)  # identity element
    while k:
        if k & 1:
            R = _eadd(R, P)
        P = _eadd(P, P)
        k >>= 1
    return R


def _eencode(P):
    """Compress Ed25519 point to 32 bytes (little-endian y, sign bit in MSB)."""
    x, y, z, _ = P
    zi = pow(z, _EP - 2, _EP)
    x  = x * zi % _EP
    y  = y * zi % _EP
    b  = bytearray(y.to_bytes(32, 'little'))
    b[31] |= (0x80 if x & 1 else 0)
    return bytes(b)


def _ed25519_base():
    """Compute Ed25519 base point in extended coordinates (cached at module load)."""
    by = 4 * pow(5, _EP - 2, _EP) % _EP
    y2 = by * by % _EP
    x2 = (y2 - 1) * pow(_ED * y2 + 1, _EP - 2, _EP) % _EP
    bx = pow(x2, (_EP + 3) // 8, _EP)
    if (bx * bx - x2) % _EP != 0:
        bx = bx * pow(2, (_EP - 1) // 4, _EP) % _EP
    if bx % 2 != 0:
        bx = _EP - bx
    return (bx, by, 1, bx * by % _EP)


_ED_BASE = _ed25519_base()


def _ed25519_pubkey(privkey_bytes: bytes) -> bytes:
    """Derive Ed25519 public key from 32-byte private seed (RFC 8032)."""
    h = hashlib.sha512(privkey_bytes).digest()
    s = bytearray(h[:32])
    s[0] &= 248
    s[31] &= 127
    s[31] |= 64
    scalar = int.from_bytes(s, 'little')
    return _eencode(_emult(scalar, _ED_BASE))


# ── BTC helpers ───────────────────────────────────────────────────────────────

def _hash160(data: bytes) -> bytes:
    sha = hashlib.sha256(data).digest()
    return hashlib.new('ripemd160', sha).digest()


def _base58check(payload: bytes) -> str:
    checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    return _base58_encode(payload + checksum)


# ── ETH EIP-55 helper ─────────────────────────────────────────────────────────

def _eip55(raw20: bytes) -> str:
    hex_lower = raw20.hex()
    kh = _keccak256(hex_lower.encode()).hex()
    return '0x' + ''.join(
        c.upper() if int(kh[i], 16) >= 8 else c
        for i, c in enumerate(hex_lower)
    )


# ── Public generators ─────────────────────────────────────────────────────────

def generate_eth_wallet() -> str:
    """Full ETH wallet: private key → secp256k1 → Keccak-256 → EIP-55 address."""
    privkey = secrets.token_bytes(32)
    k = int.from_bytes(privkey, 'big') % _SN or 1
    x, y = _smult(k)
    pubkey_bytes = x.to_bytes(32, 'big') + y.to_bytes(32, 'big')
    address = _eip55(_keccak256(pubkey_bytes)[-20:])
    return json.dumps({
        'private_key': privkey.hex(),
        'public_key':  '04' + pubkey_bytes.hex(),
        'address':     address,
    }, separators=(',', ':'))


def generate_btc_wallet() -> str:
    """Full BTC wallet: private key → secp256k1 → HASH160 → P2PKH + WIF."""
    privkey = secrets.token_bytes(32)
    k = int.from_bytes(privkey, 'big') % _SN or 1
    x, y = _smult(k)
    compressed = (b'\x02' if y % 2 == 0 else b'\x03') + x.to_bytes(32, 'big')
    address = _base58check(b'\x00' + _hash160(compressed))
    wif     = _base58check(b'\x80' + privkey + b'\x01')
    return json.dumps({
        'private_key': privkey.hex(),
        'wif':         wif,
        'public_key':  compressed.hex(),
        'address':     address,
    }, separators=(',', ':'))


def generate_sol_wallet() -> str:
    """Full Solana wallet: Ed25519 keypair → base58 address (Phantom format)."""
    privkey = secrets.token_bytes(32)
    pubkey  = _ed25519_pubkey(privkey)
    address = _base58_encode(pubkey)
    keypair = _base58_encode(privkey + pubkey)  # Phantom / Solana CLI format
    return json.dumps({
        'private_key': privkey.hex(),
        'public_key':  pubkey.hex(),
        'address':     address,
        'keypair':     keypair,
    }, separators=(',', ':'))


# ── Generator class ───────────────────────────────────────────────────────────

class WalletGenerator:
    """Full EC-derived wallets: ETH (secp256k1), BTC (secp256k1+WIF), Solana (Ed25519)."""

    def generate(self, data_type: str, **kwargs) -> str:
        if data_type == 'eth_wallet':
            return generate_eth_wallet()
        if data_type == 'btc_wallet':
            return generate_btc_wallet()
        if data_type == 'sol_wallet':
            return generate_sol_wallet()
        return f"ERROR: Unknown type '{data_type}'"
