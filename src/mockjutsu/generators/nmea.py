"""
mock-jutsu — GPS NMEA 0183 Satellite Sentence Generator
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)

Supported types:
  nmea_gpgga — GPGGA Global Positioning System Fix Data.
               UTC time, lat/lon, fix quality, satellite count, HDOP, altitude, geoid.
               Returns JSON with 'sentence' (raw NMEA) + parsed fields.
  nmea_gprmc — GPRMC Recommended Minimum Specific GPS Data.
               UTC time, status (A=Active), lat/lon, speed (knots), course, date (DDMMYY).
               Returns JSON with 'sentence' (raw NMEA) + parsed fields.

NMEA 0183 checksum rule (zero external dependencies):
  XOR of all ASCII byte values between '$' (exclusive) and '*' (exclusive).
  Rendered as 2 uppercase hex digits: f"{xor_result:02X}"

Coordinate encoding:
  Latitude:  DDMM.MMMM  — 2-digit degrees + 7-char minutes (00.0000–59.9999), N/S
  Longitude: DDDMM.MMMM — 3-digit degrees + 7-char minutes (00.0000–59.9999), E/W

Zero external dependencies: datetime, json, random (stdlib only).
"""

import datetime
import json
import random


# ── Helpers ───────────────────────────────────────────────────────────────────

def _nmea_checksum(body: str) -> str:
    """XOR of every ASCII byte in body → 2 uppercase hex digits."""
    xor = 0
    for ch in body:
        xor ^= ord(ch)
    return f"{xor:02X}"


def _lat_nmea(deg: float) -> str:
    """Absolute decimal latitude [0, 90] → DDMM.MMMM (9 chars)."""
    d = int(deg)
    m = (deg - d) * 60.0
    return f"{d:02d}{m:07.4f}"


def _lon_nmea(deg: float) -> str:
    """Absolute decimal longitude [0, 180] → DDDMM.MMMM (10 chars)."""
    d = int(deg)
    m = (deg - d) * 60.0
    return f"{d:03d}{m:07.4f}"


# ── GPGGA ─────────────────────────────────────────────────────────────────────

def generate_nmea_gpgga() -> str:
    """
    GPGGA — Global Positioning System Fix Data.

    Sentence body (15 comma-separated fields between '$' and '*'):
      GPGGA,HHMMSS.ss,DDMM.MMMM,N/S,DDDMM.MMMM,E/W,q,nn,hdop,alt,M,geoid,M,,
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    time_str = now.strftime('%H%M%S.00')

    lat_deg  = random.uniform(0.0, 90.0)
    lat_dir  = random.choice(['N', 'S'])
    lon_deg  = random.uniform(0.0, 180.0)
    lon_dir  = random.choice(['E', 'W'])
    lat_str  = _lat_nmea(lat_deg)
    lon_str  = _lon_nmea(lon_deg)

    fix_quality = random.choice([1, 2])
    num_sats    = random.randint(4, 12)
    hdop        = round(random.uniform(0.5, 5.0), 1)
    altitude    = round(random.uniform(-50.0, 8849.0), 1)
    geoid       = round(random.uniform(-100.0, 100.0), 1)

    body = (
        f"GPGGA,{time_str},{lat_str},{lat_dir},{lon_str},{lon_dir},"
        f"{fix_quality},{num_sats:02d},{hdop},{altitude},M,{geoid},M,,"
    )
    checksum = _nmea_checksum(body)
    sentence = f"${body}*{checksum}"

    return json.dumps({
        'sentence':      sentence,
        'type':          'GPGGA',
        'time':          time_str,
        'lat':           lat_str,
        'lat_dir':       lat_dir,
        'lon':           lon_str,
        'lon_dir':       lon_dir,
        'fix_quality':   fix_quality,
        'num_satellites': num_sats,
        'hdop':          hdop,
        'altitude':      altitude,
        'geoid_height':  geoid,
        'checksum':      checksum,
    }, ensure_ascii=False)


# ── GPRMC ─────────────────────────────────────────────────────────────────────

def generate_nmea_gprmc() -> str:
    """
    GPRMC — Recommended Minimum Specific GPS Data.

    Sentence body (12 comma-separated fields between '$' and '*'):
      GPRMC,HHMMSS.ss,A,DDMM.MMMM,N/S,DDDMM.MMMM,E/W,speed,course,DDMMYY,,
    """
    now      = datetime.datetime.now(datetime.timezone.utc)
    time_str = now.strftime('%H%M%S.00')
    date_str = now.strftime('%d%m%y')

    lat_deg  = random.uniform(0.0, 90.0)
    lat_dir  = random.choice(['N', 'S'])
    lon_deg  = random.uniform(0.0, 180.0)
    lon_dir  = random.choice(['E', 'W'])
    lat_str  = _lat_nmea(lat_deg)
    lon_str  = _lon_nmea(lon_deg)

    status = 'A'
    speed  = round(random.uniform(0.0, 100.0), 1)
    course = round(random.uniform(0.0, 359.9), 1)

    body = (
        f"GPRMC,{time_str},{status},{lat_str},{lat_dir},{lon_str},{lon_dir},"
        f"{speed},{course},{date_str},,"
    )
    checksum = _nmea_checksum(body)
    sentence = f"${body}*{checksum}"

    return json.dumps({
        'sentence':    sentence,
        'type':        'GPRMC',
        'time':        time_str,
        'status':      status,
        'lat':         lat_str,
        'lat_dir':     lat_dir,
        'lon':         lon_str,
        'lon_dir':     lon_dir,
        'speed_knots': speed,
        'course':      course,
        'date':        date_str,
        'checksum':    checksum,
    }, ensure_ascii=False)


# ── Generator class ────────────────────────────────────────────────────────────

class NmeaGenerator:
    """GPS NMEA 0183 satellite sentence generator (GPGGA, GPRMC)."""

    def generate(self, data_type: str, **kwargs) -> str:
        if data_type == 'nmea_gpgga':
            return generate_nmea_gpgga()
        if data_type == 'nmea_gprmc':
            return generate_nmea_gprmc()
        return f"ERROR: Unknown type '{data_type}'"
