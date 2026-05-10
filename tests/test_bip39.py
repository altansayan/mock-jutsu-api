"""
mock-jutsu — BIP-39 Mnemonic Generator Tests
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)

Coverage:
  - All 5 supported word counts (12, 15, 18, 21, 24)
  - Invalid word count fallback
  - Official BIP-39 test vectors (known entropy → known mnemonic)
  - Checksum validity for every word count
  - All words in WORDLIST
  - Uniqueness
  - CLI --words flag
"""

import hashlib
import pytest
from click.testing import CliRunner
from mockjutsu.core import jutsu
from mockjutsu.cli import main
from mockjutsu.data.bip39_en import WORDLIST


# ── Checksum validator ────────────────────────────────────────────────────────

def validate_bip39_checksum(mnemonic_str: str) -> bool:
    """Strict BIP-39 checksum validation against the spec algorithm."""
    words = mnemonic_str.split()
    if len(words) not in [12, 15, 18, 21, 24]:
        return False
    try:
        indices = [WORDLIST.index(w) for w in words]
    except ValueError:
        return False

    bits = "".join(bin(i)[2:].zfill(11) for i in indices)
    ent_bits_count = {12: 128, 15: 160, 18: 192, 21: 224, 24: 256}[len(words)]
    checksum_len = len(words) // 3

    entropy_bits  = bits[:ent_bits_count]
    checksum_bits = bits[ent_bits_count:]

    entropy_bytes = int(entropy_bits, 2).to_bytes(ent_bits_count // 8, byteorder='big')
    h_bits = "".join(bin(b)[2:].zfill(8) for b in hashlib.sha256(entropy_bytes).digest())
    return checksum_bits == h_bits[:checksum_len]


# ── Helper: replicate BIP-39 for known vectors ────────────────────────────────

def _entropy_to_mnemonic(entropy_hex: str) -> str:
    """Replicate BIP-39 algorithm with fixed entropy (for test vector verification)."""
    entropy = bytes.fromhex(entropy_hex)
    ent_bits = len(entropy) * 8
    cs_len   = ent_bits // 32

    bits   = "".join(bin(b)[2:].zfill(8) for b in entropy)
    h_bits = "".join(bin(b)[2:].zfill(8) for b in hashlib.sha256(entropy).digest())
    full   = bits + h_bits[:cs_len]

    return " ".join(WORDLIST[int(full[i:i+11], 2)] for i in range(0, len(full), 11))


# ── Word count tests ──────────────────────────────────────────────────────────

@pytest.mark.parametrize("word_count", [12, 15, 18, 21, 24])
def test_word_count(word_count):
    """All 5 supported word counts produce correct length output."""
    mnemonic = jutsu.generate('mnemonic', words=word_count)
    assert not mnemonic.startswith("ERROR")
    assert len(mnemonic.split()) == word_count


@pytest.mark.parametrize("word_count", [12, 15, 18, 21, 24])
def test_checksum_valid(word_count):
    """BIP-39 checksum must be valid for all supported word counts."""
    mnemonic = jutsu.generate('mnemonic', words=word_count)
    assert validate_bip39_checksum(mnemonic), (
        f"Checksum invalid for {word_count}-word mnemonic: {mnemonic}"
    )


@pytest.mark.parametrize("word_count", [12, 15, 18, 21, 24])
def test_all_words_in_wordlist(word_count):
    """Every word in the output must exist in the official BIP-39 English wordlist."""
    mnemonic = jutsu.generate('mnemonic', words=word_count)
    for word in mnemonic.split():
        assert word in WORDLIST, f"'{word}' not in BIP-39 wordlist"


# ── Fallback test ─────────────────────────────────────────────────────────────

@pytest.mark.parametrize("invalid_count", [0, 1, 7, 11, 13, 25, 100])
def test_invalid_word_count_falls_back_to_12(invalid_count):
    """Invalid word counts must silently fall back to 12."""
    mnemonic = jutsu.generate('mnemonic', words=invalid_count)
    assert not mnemonic.startswith("ERROR")
    assert len(mnemonic.split()) == 12
    assert validate_bip39_checksum(mnemonic)


def test_no_words_arg_defaults_to_12():
    """Calling without words arg defaults to 12."""
    mnemonic = jutsu.generate('mnemonic')
    assert len(mnemonic.split()) == 12
    assert validate_bip39_checksum(mnemonic)


# ── Official BIP-39 test vectors ──────────────────────────────────────────────
# Source: github.com/trezor/python-mnemonic — vectors.json (MIT)

@pytest.mark.parametrize("entropy_hex,expected_mnemonic", [
    (
        "00000000000000000000000000000000",
        "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about",
    ),
    (
        "7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f",
        "legal winner thank year wave sausage worth useful legal winner thank yellow",
    ),
    (
        "80808080808080808080808080808080",
        "letter advice cage absurd amount doctor acoustic avoid letter advice cage above",
    ),
    (
        "ffffffffffffffffffffffffffffffff",
        "zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo wrong",
    ),
    (
        "000000000000000000000000000000000000000000000000",
        "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon agent",
    ),
    (
        "7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f",
        "legal winner thank year wave sausage worth useful legal winner thank year wave sausage worth useful legal will",
    ),
    (
        "8080808080808080808080808080808080808080808080808080808080808080",
        "letter advice cage absurd amount doctor acoustic avoid letter advice cage absurd amount doctor acoustic avoid letter advice cage absurd amount doctor acoustic bless",
    ),
    (
        "0000000000000000000000000000000000000000000000000000000000000000",
        "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon art",
    ),
    (
        "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
        "zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo vote",
    ),
])
def test_known_bip39_vectors(entropy_hex, expected_mnemonic):
    """Algorithm must reproduce official BIP-39 test vectors exactly."""
    result = _entropy_to_mnemonic(entropy_hex)
    assert result == expected_mnemonic, (
        f"\nEntropy : {entropy_hex}"
        f"\nExpected: {expected_mnemonic}"
        f"\nGot     : {result}"
    )


# ── Uniqueness ────────────────────────────────────────────────────────────────

def test_unique_outputs():
    """Subsequent calls must produce different mnemonics (CSPRNG)."""
    results = {jutsu.generate('mnemonic', words=12) for _ in range(10)}
    assert len(results) == 10, "Generated duplicate mnemonics — entropy source is broken"


# ── CLI integration ───────────────────────────────────────────────────────────

@pytest.mark.parametrize("word_count", [12, 15, 18, 21, 24])
def test_cli_words_flag(word_count):
    """CLI --words flag produces correct word count and valid checksum."""
    runner = CliRunner()
    result = runner.invoke(main, ['generate', 'mnemonic', '--words', str(word_count)])
    assert result.exit_code == 0, result.output
    mnemonic = result.output.strip()
    assert len(mnemonic.split()) == word_count
    assert validate_bip39_checksum(mnemonic)


def test_cli_default_words():
    """CLI generate mnemonic without --words defaults to 12."""
    runner = CliRunner()
    result = runner.invoke(main, ['generate', 'mnemonic'])
    assert result.exit_code == 0
    mnemonic = result.output.strip()
    assert len(mnemonic.split()) == 12
    assert validate_bip39_checksum(mnemonic)


def test_cli_bulk_mnemonic():
    """CLI bulk mnemonic --count 5 returns 5 unique valid mnemonics."""
    runner = CliRunner()
    result = runner.invoke(main, ['bulk', 'mnemonic', '--count', '5', '--words', '12'])
    assert result.exit_code == 0
    import json
    mnemonics = json.loads(result.output)
    assert len(mnemonics) == 5
    for m in mnemonics:
        assert len(m.split()) == 12
        assert validate_bip39_checksum(m)
