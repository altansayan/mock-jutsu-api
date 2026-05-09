"""
mock-jutsu — Hardware Generators Unit Tests
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)
"""

import re
from mockjutsu.core import jutsu

def test_track2_data_format():
    """
    track2_data must match ISO/IEC 7813 Track 2 Magnetic Stripe format:
    ;PAN=YYMMServiceCodeDiscretionaryData?
    """
    for _ in range(50):
        val = jutsu.generate('track2_data')
        # Validate format:
        # Starts with ;
        # Followed by 13-19 digits (PAN)
        # Followed by =
        # Followed by 4 digits (YYMM)
        # Followed by 3 digits (Service Code)
        # Followed by 0-5 digits (Discretionary Data)
        # Ends with ?
        assert re.match(r'^;\d{13,19}=\d{4}\d{3}\d{0,5}\?$', str(val)), f"Invalid track2 data format: {val}"

def test_chip_data_tlv_format():
    """chip_data must be a valid hex string representing EMV TLV structure (tags like 9F02, 5F2A, etc.)."""
    # Simple check for hex and minimum length (EMV chips carry quite a bit of data)
    for _ in range(50):
        val = jutsu.generate('chip_data')
        assert re.match(r'^[0-9A-F]{32,}$', str(val)), f"Invalid chip data format: {val}"
        # Should contain some common EMV tags (9F02 is Amount, 5F2A is Currency)
        assert '9F02' in str(val) or '5F2A' in str(val), f"Chip data missing standard tags: {val}"

def test_pin_block_format():
    """pin_block must be a 16-character hex string (ISO 9564 Format 0/1)."""
    for _ in range(50):
        val = jutsu.generate('pin_block')
        assert re.match(r'^[0-9A-F]{16}$', str(val)), f"Invalid pin block format: {val}"
