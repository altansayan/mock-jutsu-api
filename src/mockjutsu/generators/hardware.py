"""
mock-jutsu — Hardware & Telemetry Generator
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)
"""

import random

from .financial import FinancialGenerator

class HardwareGenerator:
    """Hardware level data (Magnetic Stripe, Sensors, Telemetry)."""

    def __init__(self):
        # We can reuse the financial generator for Luhn valid PANs
        self.financial = FinancialGenerator()

    def generate_track2_data(self) -> str:
        """
        Generate ISO/IEC 7813 Track 2 Magnetic Stripe Data.
        Format: ;PAN=YYMMServiceCodeDiscretionaryData?
        - PAN: 13-19 digits, Luhn valid.
        - YYMM: Expiry date.
        - ServiceCode: 3 digits.
        - DiscretionaryData: Optional, here we use 3-5 random digits.
        """
        # 1. PAN (Primary Account Number) - Luhn valid
        pan = self.financial.generate_card_number('visa')
        
        # 2. Expiry YYMM
        yy = random.randint(25, 35)
        mm = random.randint(1, 12)
        expiry = f"{yy:02d}{mm:02d}"
        
        # 3. Service Code (3 digits, e.g., 101, 201)
        # First digit: 1 (International), 2 (International IC)
        # Second digit: 0 (Normal)
        # Third digit: 1 (No restrictions), 6 (PIN required)
        sc1 = random.choice(['1', '2'])
        sc2 = '0'
        sc3 = random.choice(['1', '6'])
        service_code = f"{sc1}{sc2}{sc3}"
        
        # 4. Discretionary Data (PIN Verification Key Indicator, etc)
        discretionary_len = random.randint(3, 5)
        discretionary_data = "".join(str(random.randint(0, 9)) for _ in range(discretionary_len))
        
        return f";{pan}={expiry}{service_code}{discretionary_data}?"

    def generate(self, data_type: str, **kwargs) -> str:
        """Dispatch generation based on data_type."""
        dt = data_type.lower().strip()
        
        if dt == 'track2_data':
            return self.generate_track2_data()
            
        return "HARDWARE_DATA"
