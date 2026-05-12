"""
mock-jutsu — TLE (Two-Line Element Set) Satellite Orbit Generator
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)

Supported types:
  tle_satellite — Two-Line Element Set per NORAD/USSPACECOM standard.
                  Line 1 (69 chars): catalog number, classification,
                    international designator, epoch, 1st/2nd mean motion
                    derivatives, BSTAR drag term, element set number,
                    NORAD Modulo-10 checksum.
                  Line 2 (69 chars): catalog number, inclination, RAAN,
                    eccentricity (7-digit no-decimal), argument of perigee,
                    mean anomaly, mean motion (rev/day), revolution number,
                    NORAD Modulo-10 checksum.
                  Orbit types: LEO, MEO, GEO, SSO, HEO with
                    physics-consistent orbital parameters per type.
                  Checksum: sum(digits) + count('-') over positions 0-67,
                    modulo 10.

Zero external dependencies: json, math, random (stdlib only).
"""

import json
import math
import random

# ── Orbit type configurations ──────────────────────────────────────────────────

_ORBIT_CONFIGS = {
    'LEO': {
        'mean_motion':  (11.25, 16.0),
        'inclination':  (0.0,   97.0),
        'eccentricity': (0.0,   0.001),
        'weight':       40,
    },
    'MEO': {
        'mean_motion':  (2.0,   11.25),
        'inclination':  (20.0,  65.0),
        'eccentricity': (0.0,   0.01),
        'weight':       20,
    },
    'GEO': {
        'mean_motion':  (0.99,  1.01),
        'inclination':  (0.0,   0.1),
        'eccentricity': (0.0,   0.0001),
        'weight':       20,
    },
    'SSO': {
        'mean_motion':  (14.0,  15.0),
        'inclination':  (96.0,  98.0),
        'eccentricity': (0.0,   0.001),
        'weight':       15,
    },
    'HEO': {
        'mean_motion':  (2.0,   4.0),
        'inclination':  (50.0,  65.0),
        'eccentricity': (0.5,   0.85),
        'weight':       5,
    },
}

_ORBIT_TYPES   = list(_ORBIT_CONFIGS.keys())
_ORBIT_WEIGHTS = [_ORBIT_CONFIGS[k]['weight'] for k in _ORBIT_TYPES]

_CLASSIFICATION = ['U', 'U', 'U', 'U', 'C', 'S']

_SAT_PREFIXES = [
    'MOCKSAT', 'TESTBIRD', 'SIMSTAR', 'JUTSU', 'DEMOSAT',
    'TESTBED', 'MOCKSTAR', 'SIMBIRD', 'DEMOSTAR', 'MOCKBIRD',
]

_LAUNCH_YEARS = list(range(70, 100)) + list(range(0, 27))  # 1970-1999, 2000-2026


# ── NORAD Modulo-10 checksum ───────────────────────────────────────────────────

def _tle_checksum(line: str) -> int:
    """NORAD Modulo-10 checksum: sum of digits + 1 per '-' sign, mod 10."""
    total = 0
    for ch in line[:68]:
        if ch.isdigit():
            total += int(ch)
        elif ch == '-':
            total += 1
    return total % 10


# ── TLE formatting helpers ─────────────────────────────────────────────────────

def _fmt_1st_deriv(v: float) -> str:
    """10-char first time derivative of mean motion: ±.NNNNNNNN"""
    sign    = '-' if v < 0 else ' '
    abs_v   = min(abs(v), 0.99999999)
    frac    = f'{abs_v:.8f}'[2:]   # '0.00001717' → '00001717'
    return f'{sign}.{frac}'


def _fmt_exp(value: float) -> str:
    """
    8-char TLE exponential notation: ±NNNNN±N
    Actual value = ±0.NNNNN × 10^(±N).
    """
    if value == 0.0:
        return ' 00000-0'
    neg = value < 0
    v   = abs(value)
    # exp: smallest integer such that v / 10^exp is in [0.1, 1.0)
    exp = int(math.floor(math.log10(v))) + 1
    exp = max(-9, min(9, exp))   # TLE exponent field is one digit
    mantissa = round(v / (10.0 ** (exp - 5)))
    mantissa = max(10000, min(99999, mantissa))
    exp_sign = '+' if exp >= 0 else '-'
    return f"{'-' if neg else ' '}{mantissa:05d}{exp_sign}{abs(exp)}"


# ── Main generator ─────────────────────────────────────────────────────────────

def generate_tle_satellite() -> str:
    """TLE satellite entry with verified NORAD Modulo-10 checksums on both lines."""
    orbit_type = random.choices(_ORBIT_TYPES, weights=_ORBIT_WEIGHTS)[0]
    cfg        = _ORBIT_CONFIGS[orbit_type]

    # Catalog / ID
    norad_id       = random.randint(1000, 99999)
    classification = random.choice(_CLASSIFICATION)

    # International Designator (8 chars: YYNNNAAA)
    launch_yr    = random.choice(_LAUNCH_YEARS)
    launch_num   = random.randint(1, 999)
    launch_piece = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    intl_str     = f'{launch_yr:02d}{launch_num:03d}{launch_piece:<3}'   # 8 chars

    # Epoch (14 chars: YYDDD.DDDDDDDD)
    epoch_yr  = random.randint(14, 26)
    epoch_day = round(random.uniform(1.0, 365.9999), 8)
    epoch_str = f'{epoch_yr:02d}{epoch_day:012.8f}'                     # 14 chars

    # Mean motion derivatives
    ndot     = round(random.uniform(0.0, 0.00009999), 8)
    ndot_str = _fmt_1st_deriv(ndot)     # 10 chars
    nddot_str = ' 00000-0'              # 8 chars — effectively zero (nominal)

    # BSTAR drag term
    bstar     = round(random.uniform(1e-6, 9.9e-4), 8)
    bstar_str = _fmt_exp(bstar)         # 8 chars

    # Element set number (up to 9999)
    elem_set = random.randint(1, 9999)

    # Orbital elements
    incl = round(random.uniform(*cfg['inclination']), 4)
    raan = round(random.uniform(0.0, 360.0), 4)
    ecc  = round(random.uniform(*cfg['eccentricity']), 7)
    argp = round(random.uniform(0.0, 360.0), 4)
    manom = round(random.uniform(0.0, 360.0), 4)
    mm    = round(random.uniform(*cfg['mean_motion']), 8)
    rev_num = random.randint(0, 99999)

    # ── Build Line 1 body (68 chars) ───────────────────────────────────────────
    line1_body = (
        f'1 {norad_id:05d}{classification} '   # [0:9]   9 chars
        f'{intl_str} '                           # [9:18]  9 chars
        f'{epoch_str} '                          # [18:33] 15 chars
        f'{ndot_str} '                           # [33:44] 11 chars
        f'{nddot_str} '                          # [44:53] 9 chars
        f'{bstar_str} '                          # [53:62] 9 chars
        f'0 {elem_set:4d}'                       # [62:68] 6 chars
    )
    line1 = line1_body + str(_tle_checksum(line1_body))

    # ── Build Line 2 body (68 chars) ───────────────────────────────────────────
    ecc_raw = round(ecc * 1e7)   # 7-digit integer, no decimal point

    line2_body = (
        f'2 {norad_id:05d} '     # [0:8]   8 chars
        f'{incl:8.4f} '          # [8:17]  9 chars
        f'{raan:8.4f} '          # [17:26] 9 chars
        f'{ecc_raw:07d} '        # [26:34] 8 chars
        f'{argp:8.4f} '          # [34:43] 9 chars
        f'{manom:8.4f} '         # [43:52] 9 chars
        f'{mm:11.8f}'            # [52:63] 11 chars
        f'{rev_num:05d}'         # [63:68] 5 chars
    )
    line2 = line2_body + str(_tle_checksum(line2_body))

    # ── Satellite name ─────────────────────────────────────────────────────────
    sat_name = f'{random.choice(_SAT_PREFIXES)}-{random.randint(1, 999)}'

    return json.dumps({
        'name':          sat_name,
        'line1':         line1,
        'line2':         line2,
        'norad_id':      norad_id,
        'classification': classification,
        'epoch_year':    epoch_yr,
        'epoch_day':     epoch_day,
        'inclination':   incl,
        'raan':          raan,
        'eccentricity':  ecc,
        'arg_of_perigee': argp,
        'mean_anomaly':  manom,
        'mean_motion':   mm,
        'rev_number':    rev_num,
        'orbit_type':    orbit_type,
    })


# ── Generator class ────────────────────────────────────────────────────────────

class TleGenerator:
    """TLE satellite orbit generator."""

    def generate(self, data_type: str, **kwargs) -> str:
        if data_type == 'tle_satellite':
            return generate_tle_satellite()
        return f"ERROR: Unknown type '{data_type}'"
