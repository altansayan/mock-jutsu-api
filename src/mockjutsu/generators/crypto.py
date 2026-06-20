"""
mock-jutsu — Crypto / Web3 Generator
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)

Standards:
  BTC address — P2PKH Base58Check (version 0x00, SHA256d checksum)
  ETH address — EIP-55 mixed-case Keccak-256 checksum
  tx_hash     — 32-byte random hex (BTC: plain, ETH: 0x-prefixed)
  block_hash  — same format as tx_hash per chain
"""

import hashlib
import random
import secrets
import string

# ── Keccak-256 (pure Python — no external deps) ──────────────────────────────

_M = 0xFFFFFFFFFFFFFFFF

_RC = [
    0x0000000000000001, 0x0000000000008082, 0x800000000000808A,
    0x8000000080008000, 0x000000000000808B, 0x0000000080000001,
    0x8000000080008081, 0x8000000000008009, 0x000000000000008A,
    0x0000000000000088, 0x0000000080008009, 0x000000008000000A,
    0x000000008000808B, 0x800000000000008B, 0x8000000000008089,
    0x8000000000008003, 0x8000000000008002, 0x8000000000000080,
    0x000000000000800A, 0x800000008000000A, 0x8000000080008081,
    0x8000000000008080, 0x0000000080000001, 0x8000000080008008,
]

# ROT[x][y] — Keccak-f rotation offsets (state indexed as s[x + 5*y])
_ROT = [
    [ 0, 36,  3, 41, 18],
    [ 1, 44, 10, 45,  2],
    [62,  6, 43, 15, 61],
    [28, 55, 25, 21, 56],
    [27, 20, 39,  8, 14],
]


def _rot64(x: int, n: int) -> int:
    return ((x << n) | (x >> (64 - n))) & _M


def _keccak_f(s: list) -> list:
    for rc in _RC:
        # θ
        C = [s[x] ^ s[x+5] ^ s[x+10] ^ s[x+15] ^ s[x+20] for x in range(5)]
        D = [C[(x - 1) % 5] ^ _rot64(C[(x + 1) % 5], 1) for x in range(5)]
        s = [s[i] ^ D[i % 5] for i in range(25)]
        # ρ + π  (pi: (x,y) → new position (y, (2x+3y)%5) → index y + 5*((2x+3y)%5))
        B = [0] * 25
        for x in range(5):
            for y in range(5):
                B[y + 5 * ((2*x + 3*y) % 5)] = _rot64(s[x + 5*y], _ROT[x][y])
        # χ
        s = [B[i] ^ (~B[(i % 5 + 1) % 5 + (i // 5) * 5] & B[(i % 5 + 2) % 5 + (i // 5) * 5])
             for i in range(25)]
        # ι
        s[0] ^= rc
    return s


def _keccak256(data: bytes) -> bytes:
    """Keccak-256 hash (Ethereum variant — padding 0x01, NOT SHA3's 0x06)."""
    rate = 136  # 1088 bits / 8
    msg = bytearray(data)
    msg.append(0x01)
    while len(msg) % rate:
        msg.append(0x00)
    msg[-1] |= 0x80

    state = [0] * 25
    for off in range(0, len(msg), rate):
        chunk = msg[off:off + rate]
        for i in range(rate // 8):
            state[i] ^= int.from_bytes(chunk[i*8:(i+1)*8], 'little')
        state = _keccak_f(state)

    return b''.join(s.to_bytes(8, 'little') for s in state[:4])


# ── Sprint 7 — DeFi / Crypto Extended constants ──────────────────────────────

_DEFI_PROTOCOLS = [
    'Uniswap', 'Aave', 'Compound', 'Curve Finance', 'MakerDAO', 'Lido',
    'Convex Finance', 'Balancer', 'dYdX', 'GMX', 'Synthetix', 'Yearn Finance',
    '1inch', 'Sushiswap', 'Pancakeswap', 'Velodrome', 'Camelot', 'Stargate',
    'Pendle', 'Morpho', 'Euler Finance', 'Radiant Capital', 'Beefy Finance',
]
_BLOCKCHAIN_NETWORKS = [
    'Ethereum', 'Polygon', 'Arbitrum', 'Optimism', 'Base', 'Avalanche',
    'BNB Chain', 'Solana', 'Bitcoin', 'Fantom', 'Cronos', 'zkSync Era',
]
_WALLET_LABELS = [
    'Hot Wallet', 'Cold Storage', 'Trading Wallet', 'DeFi Wallet',
    'Hardware Wallet', 'Custodial Wallet', 'Multi-sig Vault', 'Treasury',
    'Yield Farm', 'Staking Wallet', 'Airdrop Wallet', 'Development Wallet',
]
_DEFI_POSITION_TYPES = [
    'Liquidity Provider', 'Lending', 'Borrowing', 'Staking',
    'Yield Farming', 'Perpetual', 'Options', 'Vaulted',
]
_CRYPTO_NAMES = [
    'Bitcoin', 'Ethereum', 'Tether', 'BNB', 'Solana', 'USDC', 'XRP',
    'Cardano', 'Avalanche', 'Polkadot', 'Dogecoin', 'Shiba Inu', 'Polygon',
    'Chainlink', 'Litecoin', 'Cosmos', 'Uniswap', 'Aave', 'Arbitrum', 'Optimism',
]
_GAS_LIMITS = [21000, 45000, 65000, 100000, 150000, 200000, 300000, 500000, 1_000_000]

# ── Base58 (Bitcoin alphabet) ─────────────────────────────────────────────────

_B58_ALPHABET = b'123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


def _base58_encode(payload: bytes) -> str:
    n = int.from_bytes(payload, 'big')
    result = []
    while n:
        n, r = divmod(n, 58)
        result.append(_B58_ALPHABET[r])
    # leading zero bytes → '1' characters
    for byte in payload:
        if byte == 0:
            result.append(ord('1'))
        else:
            break
    return bytes(reversed(result)).decode('ascii')


# ── Generator ─────────────────────────────────────────────────────────────────

class CryptoGenerator:
    """BTC P2PKH, ETH EIP-55, tx_hash, block_hash — cryptographically correct."""

    def generate(self, data_type: str, **kwargs):
        dt = data_type.lower().strip()
        currency = str(kwargs.get('currency', 'btc')).lower()
        words = int(kwargs.get('words', 12))

        if dt == 'btc_address':
            return self._btc_address()
        if dt == 'eth_address':
            return self._eth_address()
        if dt == 'crypto_address':
            return self._eth_address() if currency == 'eth' else self._btc_address()
        if dt == 'tx_hash':
            return self._tx_hash(currency)
        if dt == 'block_hash':
            return self._block_hash(currency)
        if dt == 'mnemonic':
            return self._mnemonic(words)

        if dt == 'nft_token_id':
            # Most ERC-721 tokens use sequential IDs (0–9999) or large random IDs
            if random.random() < 0.6:
                return str(random.randint(0, 9999))
            return str(random.randint(10000, 10 ** 18))

        if dt == 'gas_price':
            # Realistic ETH gas prices in Gwei: 1–500 (peak up to 5000)
            tier = random.randrange(10)
            if tier <= 5:
                return str(random.randint(1, 30))     # low/normal
            elif tier <= 8:
                return str(random.randint(30, 200))   # moderate
            else:
                return str(random.randint(200, 5000)) # high/peak

        if dt == 'gas_limit':
            return str(random.choice(_GAS_LIMITS))

        if dt == 'defi_protocol_name':
            return random.choice(_DEFI_PROTOCOLS)

        if dt == 'blockchain_network':
            return random.choice(_BLOCKCHAIN_NETWORKS)

        if dt == 'wallet_label':
            return random.choice(_WALLET_LABELS)

        if dt == 'defi_position_type':
            return random.choice(_DEFI_POSITION_TYPES)

        if dt == 'cryptocurrency_name':
            return random.choice(_CRYPTO_NAMES)

        if dt == 'liquidity_pool_id':
            # Pool addresses are standard EIP-55 ETH addresses (contract address)
            raw = secrets.token_bytes(20)
            hex_lower = raw.hex()
            keccak_hex = _keccak256(hex_lower.encode('ascii')).hex()
            checksummed = ''.join(
                c.upper() if int(keccak_hex[i], 16) >= 8 else c.lower()
                for i, c in enumerate(hex_lower)
            )
            return '0x' + checksummed

        if dt == 'liquidity_pool_id_masked':
            # FATF Recommendation 16 (Travel Rule): show first 6 + last 4 chars of address
            # 0x + 40 hex chars → show 0x + first 4 hex + ... + last 4 hex
            raw = secrets.token_bytes(20)
            hex_lower = raw.hex()
            return f"0x{hex_lower[:4]}...{hex_lower[-4:]}"

        return f"ERROR: Unknown DataType '{dt}'"

    # ── BIP-39 Mnemonic ───────────────────────────────────────────────────────

    def _mnemonic(self, words: int = 12) -> str:
        """
        BIP-39 Mnemonic Seed: Entropy -> SHA256 Checksum -> 11-bit Wordlist Mapping.
        Supported word counts: 12, 15, 18, 21, 24.
        """
        if words not in [12, 15, 18, 21, 24]:
            words = 12

        ent_bits = {12: 128, 15: 160, 18: 192, 21: 224, 24: 256}[words]
        entropy = secrets.token_bytes(ent_bits // 8)

        # Checksum is first (ENT/32) bits of SHA256(Entropy)
        h = hashlib.sha256(entropy).digest()
        cs_len = ent_bits // 32

        # Bit stream: Entropy bits + Checksum bits
        bits = "".join([bin(b)[2:].zfill(8) for b in entropy])
        h_bits = "".join([bin(b)[2:].zfill(8) for b in h])
        full_bits = bits + h_bits[:cs_len]

        # Lazy import of the wordlist to keep memory low if not used
        try:
            from ..data.bip39_en import WORDLIST
        except ImportError:
            # Fallback for direct script execution or testing environments
            from mockjutsu.data.bip39_en import WORDLIST

        mnemonic_words = []
        for i in range(0, len(full_bits), 11):
            idx = int(full_bits[i:i+11], 2)
            mnemonic_words.append(WORDLIST[idx])

        return " ".join(mnemonic_words)

    # ── BTC P2PKH ─────────────────────────────────────────────────────────────

    def _btc_address(self) -> str:
        """P2PKH address: version(0x00) + 20-byte hash + 4-byte SHA256d checksum → Base58."""
        pubkey_hash = secrets.token_bytes(20)
        versioned = b'\x00' + pubkey_hash
        checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
        return _base58_encode(versioned + checksum)

    # ── ETH EIP-55 ────────────────────────────────────────────────────────────

    def _eth_address(self) -> str:
        """EIP-55 checksummed address: 0x + 40 hex chars with Keccak-256 mixed case."""
        raw = secrets.token_bytes(20)
        hex_lower = raw.hex()
        keccak_hex = _keccak256(hex_lower.encode('ascii')).hex()
        checksummed = ''.join(
            c.upper() if int(keccak_hex[i], 16) >= 8 else c.lower()
            for i, c in enumerate(hex_lower)
        )
        return '0x' + checksummed

    # ── tx_hash / block_hash ──────────────────────────────────────────────────

    def _tx_hash(self, currency: str) -> str:
        """32-byte random hash. BTC: 64 lowercase hex. ETH: 0x + 64 lowercase hex."""
        h = secrets.token_bytes(32).hex()
        return ('0x' + h) if currency == 'eth' else h

    def _block_hash(self, currency: str) -> str:
        """Same format as tx_hash per chain."""
        return self._tx_hash(currency)
