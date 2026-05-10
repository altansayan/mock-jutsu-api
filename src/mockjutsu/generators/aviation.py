"""
mock-jutsu — Aviation & Maritime Generator
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)

Standards / Algorithms:
  IATA ETN  — IATA Numeric Airline Designator (3 digits) + 9-digit serial + MOD-7 check digit (13 digits total)
  IMO number — IMO Resolution A.600(15): 7 digits, check = (d1×7 + d2×6 + d3×5 + d4×4 + d5×3 + d6×2) MOD 10
  PNR code  — GDS Passenger Name Record: 6 uppercase alphanumeric, charset excludes 0, 1, I, O (visual ambiguity)
"""

import random
import secrets

# ── IATA airline numeric designators (sample from IATA assignment list) ───────
_AIRLINE_CODES = [
    1, 4, 5, 6, 8, 9, 11, 14, 16, 20, 21, 23, 25, 26, 29, 30,
    31, 34, 36, 37, 39, 41, 42, 43, 45, 47, 48, 49, 52, 53, 55,
    57, 63, 65, 66, 67, 70, 74, 76, 80, 82, 83, 85, 86, 87, 88,
    90, 91, 95, 98, 100, 101, 105, 106, 107, 108, 109, 110, 112,
    114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125,
    127, 128, 129, 130, 131, 132, 133, 135, 139, 141, 142, 146,
    147, 148, 150, 153, 155, 157, 158, 160, 161, 162, 163, 164,
    165, 167, 168, 169, 170, 172, 174, 176, 178, 179, 180, 181,
    183, 185, 186, 187, 188, 189, 190, 191, 195, 196, 197, 198,
    200, 201, 202, 203, 205, 206, 207, 210, 212, 213, 214, 217,
    220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 232, 235,
    239, 240, 243, 245, 247, 248, 250, 251, 257, 260, 262, 263,
]

# PNR character set: A-Z + 2-9, excludes 0, 1, I, O (GDS visual clarity rule)
_PNR_CHARS = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'

# IMO check digit weights (positions 1–6, left to right)
_IMO_WEIGHTS = [7, 6, 5, 4, 3, 2]


class AviationGenerator:
    """IATA ticket numbers, IMO ship registration numbers, GDS PNR codes."""

    def generate(self, data_type: str, **kwargs) -> str:
        dt = data_type.lower().strip()

        if dt == 'iata_ticket':
            return _generate_iata_ticket()
        if dt == 'imo_number':
            return _generate_imo_number()
        if dt == 'pnr_code':
            return _generate_pnr_code()

        return f"ERROR: Unknown aviation type '{dt}'"


def _generate_iata_ticket() -> str:
    """IATA Electronic Ticket Number (ETN).

    Format: NNN SSSSSSSSS C  (13 digits, no spaces in output)
      NNN        — 3-digit airline numeric designator (IATA-assigned)
      SSSSSSSSS  — 9-digit serial number (1 – 999_999_999)
      C          — check digit = SSSSSSSSS mod 7  (0–6)
    """
    airline = random.choice(_AIRLINE_CODES)
    serial = random.randint(1, 999_999_999)
    check = serial % 7
    return f"{airline:03d}{serial:09d}{check}"


def _generate_imo_number() -> str:
    """IMO Ship Registration Number — IMO Resolution A.600(15).

    Format: 'IMO NNNNNNN'  (7 digits after prefix)
      Digits 1–6: identifier (first digit 1–9)
      Digit 7:   check = (d1×7 + d2×6 + d3×5 + d4×4 + d5×3 + d6×2) mod 10
    """
    while True:
        # First digit must be 1–9; digits 2–6 are 0–9
        d = [random.randint(1, 9)] + [random.randint(0, 9) for _ in range(5)]
        total = sum(d[i] * _IMO_WEIGHTS[i] for i in range(6))
        check = total % 10
        return f"IMO {''.join(map(str, d))}{check}"


def _generate_pnr_code() -> str:
    """GDS Passenger Name Record (PNR) locator code.

    6 uppercase alphanumeric characters. Excludes 0, 1, I, O to prevent
    visual confusion between digits and letters in printed itineraries.
    """
    return ''.join(secrets.choice(_PNR_CHARS) for _ in range(6))
