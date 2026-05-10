import hashlib
import binascii
import pytest
from mockjutsu.core import jutsu
from mockjutsu.data.bip39_en import WORDLIST

def validate_bip39_checksum(mnemonic_str):
    """
    Strict validation of BIP-39 mnemonic checksum.
    """
    words = mnemonic_str.split()
    if len(words) not in [12, 15, 18, 21, 24]:
        return False

    try:
        # Convert words to indices
        indices = [WORDLIST.index(w) for w in words]
    except ValueError:
        return False # Word not in list

    # Convert indices to bits
    bits = "".join([bin(i)[2:].zfill(11) for i in indices])
    
    # Split entropy and checksum
    ent_bits_count = {12: 128, 15: 160, 18: 192, 21: 224, 24: 256}[len(words)]
    checksum_len = len(words) // 3
    
    entropy_bits = bits[:ent_bits_count]
    checksum_bits = bits[ent_bits_count:]
    
    # Convert entropy bits back to bytes
    entropy_bytes = int(entropy_bits, 2).to_bytes(ent_bits_count // 8, byteorder='big')
    
    # Calculate expected checksum
    h = hashlib.sha256(entropy_bytes).digest()
    # Checksum is first cs_len bits of first byte (since cs_len is 4 to 8 bits)
    # Actually, we need to be careful with bit offsets if cs_len > 8, 
    # but for 24 words it's 256/32 = 8 bits.
    h_bits = "".join([bin(b)[2:].zfill(8) for b in h])
    expected_checksum = h_bits[:checksum_len]
    
    return checksum_bits == expected_checksum

def test_bip39_generate_12_words():
    """Test generating a 12-word mnemonic seed."""
    mnemonic = jutsu.generate('mnemonic', words=12)
    assert not mnemonic.startswith("ERROR")
    assert validate_bip39_checksum(mnemonic)
    words = mnemonic.split()
    assert len(words) == 12

def test_bip39_generate_24_words():
    """Test generating a 24-word mnemonic seed."""
    mnemonic = jutsu.generate('mnemonic', words=24)
    assert not mnemonic.startswith("ERROR")
    assert validate_bip39_checksum(mnemonic)
    words = mnemonic.split()
    assert len(words) == 24

def test_bip39_unique_outputs():
    """Test that subsequent calls generate different seeds."""
    m1 = jutsu.generate('mnemonic')
    m2 = jutsu.generate('mnemonic')
    assert m1 != m2
