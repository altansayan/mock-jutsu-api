"""
Tests for God Mode #23 — GPS NMEA 0183 Uydu Cümleleri
Types: nmea_gpgga, nmea_gprmc

Core invariants:
  Both types:
    - JSON dict with 'sentence' field (raw NMEA string)
    - sentence: starts with '$', exactly one '*', 2 hex digits after '*'
    - XOR checksum correct (all bytes between '$' and '*')
    - lat field: DDMM.MMMM (9 chars), DD ∈ [0,90], minutes ∈ [0,60)
    - lon field: DDDMM.MMMM (10 chars), DDD ∈ [0,180], minutes ∈ [0,60)
    - lat_dir ∈ {'N', 'S'}, lon_dir ∈ {'E', 'W'}

  nmea_gpgga:
    - type == 'GPGGA', sentence starts with '$GPGGA,'
    - fix_quality ∈ {1, 2}, num_satellites ∈ [4, 12], hdop > 0
    - 15 comma-separated fields in sentence body

  nmea_gprmc:
    - type == 'GPRMC', sentence starts with '$GPRMC,'
    - status == 'A', speed_knots >= 0, course ∈ [0, 360)
    - date: 6-digit DDMMYY, 12 fields in sentence body
"""

import json
import pytest
from mockjutsu.core import MockJutsuCore

jutsu = MockJutsuCore()

_VALID_LAT_DIRS = {'N', 'S'}
_VALID_LON_DIRS = {'E', 'W'}


def _nmea_xor(sentence: str) -> str:
    """Replicated NMEA XOR checksum: bytes between '$' and '*'."""
    star_pos = sentence.rindex('*')
    body = sentence[1:star_pos]
    xor = 0
    for ch in body:
        xor ^= ord(ch)
    return f"{xor:02X}"


# ── nmea_gpgga ────────────────────────────────────────────────────────────────

class TestNmeaGpgga:

    def test_no_error(self):
        assert not jutsu.generate('nmea_gpgga').startswith('ERROR')

    def test_returns_string(self):
        assert isinstance(jutsu.generate('nmea_gpgga'), str)

    def test_is_valid_json(self):
        json.loads(jutsu.generate('nmea_gpgga'))

    def test_is_dict(self):
        assert isinstance(json.loads(jutsu.generate('nmea_gpgga')), dict)

    def test_has_required_fields(self):
        data = json.loads(jutsu.generate('nmea_gpgga'))
        for f in ('sentence', 'type', 'time', 'lat', 'lat_dir', 'lon', 'lon_dir',
                  'fix_quality', 'num_satellites', 'hdop', 'altitude', 'checksum'):
            assert f in data, f"Missing field: {f}"

    def test_type_is_gpgga(self):
        assert json.loads(jutsu.generate('nmea_gpgga'))['type'] == 'GPGGA'

    def test_sentence_starts_with_dollar_gpgga(self):
        for _ in range(10):
            s = json.loads(jutsu.generate('nmea_gpgga'))['sentence']
            assert s.startswith('$GPGGA,'), f"Bad prefix: {s[:12]}"

    def test_sentence_has_exactly_one_asterisk(self):
        for _ in range(10):
            s = json.loads(jutsu.generate('nmea_gpgga'))['sentence']
            assert s.count('*') == 1, f"Expected 1 asterisk, got {s.count('*')}"

    def test_checksum_is_two_uppercase_hex(self):
        for _ in range(20):
            cs = json.loads(jutsu.generate('nmea_gpgga'))['checksum']
            assert len(cs) == 2, f"Checksum length {len(cs)} != 2"
            assert cs == cs.upper(), f"Checksum not uppercase: {cs}"
            assert all(c in '0123456789ABCDEF' for c in cs), \
                f"Checksum not hex: {cs}"

    def test_checksum_in_sentence_matches_field(self):
        for _ in range(20):
            data = json.loads(jutsu.generate('nmea_gpgga'))
            s = data['sentence']
            star_pos = s.rindex('*')
            assert s[star_pos + 1:star_pos + 3] == data['checksum'], \
                f"Sentence/field checksum mismatch"

    def test_checksum_is_correct_xor(self):
        """XOR of all bytes between '$' and '*' must equal checksum."""
        for _ in range(20):
            data = json.loads(jutsu.generate('nmea_gpgga'))
            s = data['sentence']
            assert _nmea_xor(s) == data['checksum'], \
                f"Wrong XOR checksum in: {s}"

    def test_lat_length(self):
        """Latitude is DDMM.MMMM — exactly 9 characters."""
        for _ in range(10):
            lat = json.loads(jutsu.generate('nmea_gpgga'))['lat']
            assert len(lat) == 9, f"Lat length {len(lat)} != 9: '{lat}'"

    def test_lon_length(self):
        """Longitude is DDDMM.MMMM — exactly 10 characters."""
        for _ in range(10):
            lon = json.loads(jutsu.generate('nmea_gpgga'))['lon']
            assert len(lon) == 10, f"Lon length {len(lon)} != 10: '{lon}'"

    def test_lat_degrees_range(self):
        """Latitude degrees (first 2 chars) in [0, 90]."""
        for _ in range(20):
            lat = json.loads(jutsu.generate('nmea_gpgga'))['lat']
            d = int(lat[:2])
            assert 0 <= d <= 90, f"Lat degrees {d} out of range"

    def test_lon_degrees_range(self):
        """Longitude degrees (first 3 chars) in [0, 180]."""
        for _ in range(20):
            lon = json.loads(jutsu.generate('nmea_gpgga'))['lon']
            d = int(lon[:3])
            assert 0 <= d <= 180, f"Lon degrees {d} out of range"

    def test_lat_minutes_range(self):
        """Latitude minutes (chars [2:]) in [0.0, 60.0)."""
        for _ in range(20):
            lat = json.loads(jutsu.generate('nmea_gpgga'))['lat']
            m = float(lat[2:])
            assert 0.0 <= m < 60.0, f"Lat minutes {m} out of range"

    def test_lon_minutes_range(self):
        """Longitude minutes (chars [3:]) in [0.0, 60.0)."""
        for _ in range(20):
            lon = json.loads(jutsu.generate('nmea_gpgga'))['lon']
            m = float(lon[3:])
            assert 0.0 <= m < 60.0, f"Lon minutes {m} out of range"

    def test_lat_dir_valid(self):
        for _ in range(20):
            ld = json.loads(jutsu.generate('nmea_gpgga'))['lat_dir']
            assert ld in _VALID_LAT_DIRS, f"Invalid lat_dir: {ld}"

    def test_lon_dir_valid(self):
        for _ in range(20):
            ld = json.loads(jutsu.generate('nmea_gpgga'))['lon_dir']
            assert ld in _VALID_LON_DIRS, f"Invalid lon_dir: {ld}"

    def test_lat_dir_distribution(self):
        """Both N and S must appear across 20 samples."""
        dirs = {json.loads(jutsu.generate('nmea_gpgga'))['lat_dir'] for _ in range(20)}
        assert len(dirs) == 2

    def test_lon_dir_distribution(self):
        """Both E and W must appear across 20 samples."""
        dirs = {json.loads(jutsu.generate('nmea_gpgga'))['lon_dir'] for _ in range(20)}
        assert len(dirs) == 2

    def test_fix_quality_valid(self):
        for _ in range(20):
            fq = json.loads(jutsu.generate('nmea_gpgga'))['fix_quality']
            assert fq in (1, 2), f"Invalid fix_quality: {fq}"

    def test_num_satellites_range(self):
        for _ in range(20):
            ns = json.loads(jutsu.generate('nmea_gpgga'))['num_satellites']
            assert 4 <= ns <= 12, f"Satellites {ns} out of range"

    def test_hdop_positive(self):
        for _ in range(20):
            hdop = json.loads(jutsu.generate('nmea_gpgga'))['hdop']
            assert hdop > 0, f"HDOP {hdop} <= 0"

    def test_altitude_is_number(self):
        for _ in range(10):
            alt = json.loads(jutsu.generate('nmea_gpgga'))['altitude']
            assert isinstance(alt, (int, float)), f"Altitude not numeric: {alt}"

    def test_sentence_field_count(self):
        """GPGGA sentence body must have exactly 15 comma-separated fields."""
        for _ in range(10):
            s = json.loads(jutsu.generate('nmea_gpgga'))['sentence']
            star_pos = s.rindex('*')
            body = s[1:star_pos]  # strip leading $ and trailing *XX
            fields = body.split(',')
            assert len(fields) == 15, \
                f"GPGGA field count {len(fields)} != 15 in: {body}"

    def test_bulk_variety(self):
        checksums = {json.loads(r)['checksum'] for r in jutsu.bulk('nmea_gpgga', 5)}
        assert len(checksums) > 1


# ── nmea_gprmc ────────────────────────────────────────────────────────────────

class TestNmeaGprmc:

    def test_no_error(self):
        assert not jutsu.generate('nmea_gprmc').startswith('ERROR')

    def test_returns_string(self):
        assert isinstance(jutsu.generate('nmea_gprmc'), str)

    def test_is_valid_json(self):
        json.loads(jutsu.generate('nmea_gprmc'))

    def test_is_dict(self):
        assert isinstance(json.loads(jutsu.generate('nmea_gprmc')), dict)

    def test_has_required_fields(self):
        data = json.loads(jutsu.generate('nmea_gprmc'))
        for f in ('sentence', 'type', 'time', 'status', 'lat', 'lat_dir',
                  'lon', 'lon_dir', 'speed_knots', 'course', 'date', 'checksum'):
            assert f in data, f"Missing field: {f}"

    def test_type_is_gprmc(self):
        assert json.loads(jutsu.generate('nmea_gprmc'))['type'] == 'GPRMC'

    def test_sentence_starts_with_dollar_gprmc(self):
        for _ in range(10):
            s = json.loads(jutsu.generate('nmea_gprmc'))['sentence']
            assert s.startswith('$GPRMC,'), f"Bad prefix: {s[:12]}"

    def test_sentence_has_exactly_one_asterisk(self):
        for _ in range(10):
            s = json.loads(jutsu.generate('nmea_gprmc'))['sentence']
            assert s.count('*') == 1, f"Expected 1 asterisk, got {s.count('*')}"

    def test_checksum_is_two_uppercase_hex(self):
        for _ in range(20):
            cs = json.loads(jutsu.generate('nmea_gprmc'))['checksum']
            assert len(cs) == 2, f"Checksum length {len(cs)} != 2"
            assert cs == cs.upper(), f"Checksum not uppercase: {cs}"
            assert all(c in '0123456789ABCDEF' for c in cs), \
                f"Checksum not hex: {cs}"

    def test_checksum_in_sentence_matches_field(self):
        for _ in range(20):
            data = json.loads(jutsu.generate('nmea_gprmc'))
            s = data['sentence']
            star_pos = s.rindex('*')
            assert s[star_pos + 1:star_pos + 3] == data['checksum']

    def test_checksum_is_correct_xor(self):
        """XOR of all bytes between '$' and '*' must equal checksum."""
        for _ in range(20):
            data = json.loads(jutsu.generate('nmea_gprmc'))
            s = data['sentence']
            assert _nmea_xor(s) == data['checksum'], \
                f"Wrong XOR checksum in: {s}"

    def test_lat_length(self):
        for _ in range(10):
            lat = json.loads(jutsu.generate('nmea_gprmc'))['lat']
            assert len(lat) == 9, f"Lat length {len(lat)} != 9: '{lat}'"

    def test_lon_length(self):
        for _ in range(10):
            lon = json.loads(jutsu.generate('nmea_gprmc'))['lon']
            assert len(lon) == 10, f"Lon length {len(lon)} != 10: '{lon}'"

    def test_lat_degrees_range(self):
        for _ in range(20):
            lat = json.loads(jutsu.generate('nmea_gprmc'))['lat']
            d = int(lat[:2])
            assert 0 <= d <= 90, f"Lat degrees {d} out of range"

    def test_lon_degrees_range(self):
        for _ in range(20):
            lon = json.loads(jutsu.generate('nmea_gprmc'))['lon']
            d = int(lon[:3])
            assert 0 <= d <= 180, f"Lon degrees {d} out of range"

    def test_lat_minutes_range(self):
        for _ in range(20):
            lat = json.loads(jutsu.generate('nmea_gprmc'))['lat']
            m = float(lat[2:])
            assert 0.0 <= m < 60.0, f"Lat minutes {m} out of range"

    def test_lon_minutes_range(self):
        for _ in range(20):
            lon = json.loads(jutsu.generate('nmea_gprmc'))['lon']
            m = float(lon[3:])
            assert 0.0 <= m < 60.0, f"Lon minutes {m} out of range"

    def test_lat_dir_valid(self):
        for _ in range(20):
            ld = json.loads(jutsu.generate('nmea_gprmc'))['lat_dir']
            assert ld in _VALID_LAT_DIRS

    def test_lon_dir_valid(self):
        for _ in range(20):
            ld = json.loads(jutsu.generate('nmea_gprmc'))['lon_dir']
            assert ld in _VALID_LON_DIRS

    def test_status_is_active(self):
        for _ in range(10):
            assert json.loads(jutsu.generate('nmea_gprmc'))['status'] == 'A'

    def test_speed_non_negative(self):
        for _ in range(20):
            spd = json.loads(jutsu.generate('nmea_gprmc'))['speed_knots']
            assert spd >= 0, f"Speed {spd} < 0"

    def test_course_range(self):
        """Course in [0.0, 360.0)."""
        for _ in range(20):
            c = json.loads(jutsu.generate('nmea_gprmc'))['course']
            assert 0.0 <= c < 360.0, f"Course {c} out of range"

    def test_date_is_six_digits(self):
        """Date field is exactly 6 digits (DDMMYY)."""
        for _ in range(10):
            date = json.loads(jutsu.generate('nmea_gprmc'))['date']
            assert len(date) == 6 and date.isdigit(), \
                f"Date '{date}' is not 6 digits"

    def test_date_day_range(self):
        """Day (first 2 chars) in [01, 31]."""
        for _ in range(10):
            date = json.loads(jutsu.generate('nmea_gprmc'))['date']
            dd = int(date[:2])
            assert 1 <= dd <= 31, f"Day {dd} out of range"

    def test_date_month_range(self):
        """Month (chars [2:4]) in [01, 12]."""
        for _ in range(10):
            date = json.loads(jutsu.generate('nmea_gprmc'))['date']
            mm = int(date[2:4])
            assert 1 <= mm <= 12, f"Month {mm} out of range"

    def test_sentence_field_count(self):
        """GPRMC sentence body must have exactly 12 comma-separated fields."""
        for _ in range(10):
            s = json.loads(jutsu.generate('nmea_gprmc'))['sentence']
            star_pos = s.rindex('*')
            body = s[1:star_pos]
            fields = body.split(',')
            assert len(fields) == 12, \
                f"GPRMC field count {len(fields)} != 12 in: {body}"

    def test_bulk_variety(self):
        checksums = {json.loads(r)['checksum'] for r in jutsu.bulk('nmea_gprmc', 5)}
        assert len(checksums) > 1
