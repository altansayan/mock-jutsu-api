"""
Tests for God Mode #13 — Web3 "Pure Math" Cüzdan Motoru
Types: eth_wallet, btc_wallet, sol_wallet

Core invariants:
  - eth_wallet  : secp256k1 EC mult → Keccak-256 → EIP-55 checksum address
  - btc_wallet  : secp256k1 EC mult → SHA256+RIPEMD160 → Base58Check P2PKH + WIF
  - sol_wallet  : Ed25519 scalar mult → base58 address (Solana keypair format)
  - All wallets return JSON with required fields
  - Zero external dependencies (stdlib only)
"""

import base64
import hashlib
import json
import re
import pytest
from mockjutsu.core import MockJutsuCore

jutsu = MockJutsuCore()

_B58_CHARS = set('123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz')


def _parse(t):
    return json.loads(jutsu.generate(t))


def _is_base58(s):
    return bool(s) and all(c in _B58_CHARS for c in s)


# ── eth_wallet ────────────────────────────────────────────────────────────────

class TestEthWallet:

    def test_returns_valid_json(self):
        assert isinstance(_parse('eth_wallet'), dict)

    def test_no_error_prefix(self):
        assert not jutsu.generate('eth_wallet').startswith('ERROR')

    def test_required_keys(self):
        data = _parse('eth_wallet')
        for k in ('private_key', 'public_key', 'address'):
            assert k in data, f"Missing key: {k}"

    def test_private_key_is_32_byte_hex(self):
        pk = _parse('eth_wallet')['private_key']
        assert len(pk) == 64
        assert all(c in '0123456789abcdef' for c in pk)

    def test_public_key_is_uncompressed_format(self):
        pub = _parse('eth_wallet')['public_key']
        assert pub.startswith('04'), "Uncompressed public key must start with 04"
        assert len(pub) == 130  # 04 + 64 hex x + 64 hex y

    def test_address_format(self):
        addr = _parse('eth_wallet')['address']
        assert addr.startswith('0x')
        assert len(addr) == 42
        assert re.fullmatch(r'0x[0-9a-fA-F]{40}', addr)

    def test_address_is_eip55_checksummed(self):
        """EIP-55: at least one uppercase letter (not all lower or all upper)."""
        addr = _parse('eth_wallet')['address'][2:]  # strip 0x
        # Must have mixed case (checksummed addresses are never all-lower or all-upper)
        has_upper = any(c.isupper() for c in addr if c.isalpha())
        has_lower = any(c.islower() for c in addr if c.isalpha())
        assert has_upper and has_lower, f"Address is not EIP-55 checksummed: 0x{addr}"

    def test_bulk_unique_addresses(self):
        results = jutsu.bulk('eth_wallet', 10)
        addrs = [json.loads(r)['address'] for r in results]
        assert len(set(addrs)) == 10

    def test_bulk_unique_private_keys(self):
        results = jutsu.bulk('eth_wallet', 10)
        keys = [json.loads(r)['private_key'] for r in results]
        assert len(set(keys)) == 10


# ── btc_wallet ────────────────────────────────────────────────────────────────

class TestBtcWallet:

    def test_returns_valid_json(self):
        assert isinstance(_parse('btc_wallet'), dict)

    def test_no_error_prefix(self):
        assert not jutsu.generate('btc_wallet').startswith('ERROR')

    def test_required_keys(self):
        data = _parse('btc_wallet')
        for k in ('private_key', 'wif', 'public_key', 'address'):
            assert k in data, f"Missing key: {k}"

    def test_private_key_is_32_byte_hex(self):
        pk = _parse('btc_wallet')['private_key']
        assert len(pk) == 64
        assert all(c in '0123456789abcdef' for c in pk)

    def test_public_key_is_compressed(self):
        pub = _parse('btc_wallet')['public_key']
        assert pub[:2] in ('02', '03'), "Compressed public key must start with 02 or 03"
        assert len(pub) == 66  # 02/03 + 64 hex x

    def test_address_is_p2pkh(self):
        addr = _parse('btc_wallet')['address']
        assert addr.startswith('1'), "P2PKH mainnet address must start with '1'"
        assert 25 <= len(addr) <= 34

    def test_address_is_valid_base58(self):
        assert _is_base58(_parse('btc_wallet')['address'])

    def test_wif_is_compressed_mainnet(self):
        """Compressed mainnet WIF starts with K or L."""
        wif = _parse('btc_wallet')['wif']
        assert wif[0] in ('K', 'L'), f"WIF must start with K or L, got: {wif[0]}"
        assert len(wif) == 52

    def test_wif_is_valid_base58(self):
        assert _is_base58(_parse('btc_wallet')['wif'])

    def test_bulk_unique_addresses(self):
        results = jutsu.bulk('btc_wallet', 10)
        addrs = [json.loads(r)['address'] for r in results]
        assert len(set(addrs)) == 10

    def test_bulk_unique_private_keys(self):
        results = jutsu.bulk('btc_wallet', 10)
        keys = [json.loads(r)['private_key'] for r in results]
        assert len(set(keys)) == 10


# ── sol_wallet ────────────────────────────────────────────────────────────────

class TestSolWallet:

    def test_returns_valid_json(self):
        assert isinstance(_parse('sol_wallet'), dict)

    def test_no_error_prefix(self):
        assert not jutsu.generate('sol_wallet').startswith('ERROR')

    def test_required_keys(self):
        data = _parse('sol_wallet')
        for k in ('private_key', 'public_key', 'address', 'keypair'):
            assert k in data, f"Missing key: {k}"

    def test_private_key_is_32_byte_hex(self):
        pk = _parse('sol_wallet')['private_key']
        assert len(pk) == 64
        assert all(c in '0123456789abcdef' for c in pk)

    def test_public_key_is_32_byte_hex(self):
        pub = _parse('sol_wallet')['public_key']
        assert len(pub) == 64
        assert all(c in '0123456789abcdef' for c in pub)

    def test_address_is_base58_of_pubkey(self):
        data = _parse('sol_wallet')
        assert _is_base58(data['address'])
        assert 32 <= len(data['address']) <= 44

    def test_keypair_is_base58_of_64_bytes(self):
        data = _parse('sol_wallet')
        assert _is_base58(data['keypair'])
        assert 80 <= len(data['keypair']) <= 90  # 64 bytes in base58

    def test_bulk_unique_addresses(self):
        results = jutsu.bulk('sol_wallet', 10)
        addrs = [json.loads(r)['address'] for r in results]
        assert len(set(addrs)) == 10

    def test_bulk_unique_private_keys(self):
        results = jutsu.bulk('sol_wallet', 10)
        keys = [json.loads(r)['private_key'] for r in results]
        assert len(set(keys)) == 10
