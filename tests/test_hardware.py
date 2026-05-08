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
