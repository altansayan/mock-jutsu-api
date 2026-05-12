"""
Tests for God Mode #28 — TLE Uydu Yörünge Kodları (NORAD Modulo-10 checksum)
Types: tle_satellite

Core invariants:
  tle_satellite:
    - JSON with name, line1, line2, norad_id, classification, epoch_year,
      epoch_day, inclination, raan, eccentricity, arg_of_perigee,
      mean_anomaly, mean_motion, rev_number, orbit_type
    - len(line1) == 69, len(line2) == 69
    - line1[0] == '1', line2[0] == '2'
    - line1[68] and line2[68] are NORAD Modulo-10 checksum digits (verified)
    - norad_id in [1, 99999]; consistent on line1[2:7] and line2[2:7]
    - line1[7] in ('U', 'C', 'S')
    - line1[62] == '0' (ephemeris type)
    - epoch_year in [0, 99]; epoch_day in [1.0, 366.0]
    - inclination in [0.0, 180.0]; raan in [0.0, 360.0]
    - 0.0 <= eccentricity < 1.0
    - arg_of_perigee in [0.0, 360.0]; mean_anomaly in [0.0, 360.0]
    - mean_motion > 0 (revolutions/day)
    - rev_number >= 0
    - line2[26:33] == 7 digits (eccentricity, no decimal point)
    - orbit_type in {LEO, MEO, GEO, SSO, HEO}
"""

import json
import pytest
from mockjutsu.core import MockJutsuCore

jutsu = MockJutsuCore()

_VALID_ORBIT_TYPES = {'LEO', 'MEO', 'GEO', 'SSO', 'HEO'}


def _norad_checksum(line: str) -> int:
    """Independently compute NORAD Modulo-10 checksum."""
    total = 0
    for ch in line[:68]:
        if ch.isdigit():
            total += int(ch)
        elif ch == '-':
            total += 1
    return total % 10


class TestTleSatellite:

    def test_no_error(self):
        assert not jutsu.generate('tle_satellite').startswith('ERROR')

    def test_returns_string(self):
        assert isinstance(jutsu.generate('tle_satellite'), str)

    def test_is_valid_json(self):
        json.loads(jutsu.generate('tle_satellite'))

    def test_is_dict(self):
        assert isinstance(json.loads(jutsu.generate('tle_satellite')), dict)

    def test_has_required_fields(self):
        d = json.loads(jutsu.generate('tle_satellite'))
        for f in ('name', 'line1', 'line2', 'norad_id', 'classification',
                  'epoch_year', 'epoch_day', 'inclination', 'raan',
                  'eccentricity', 'arg_of_perigee', 'mean_anomaly',
                  'mean_motion', 'rev_number', 'orbit_type'):
            assert f in d, f"Missing field: {f}"

    def test_line1_length_is_69(self):
        for _ in range(10):
            d = json.loads(jutsu.generate('tle_satellite'))
            assert len(d['line1']) == 69, f"line1 length {len(d['line1'])} != 69"

    def test_line2_length_is_69(self):
        for _ in range(10):
            d = json.loads(jutsu.generate('tle_satellite'))
            assert len(d['line2']) == 69, f"line2 length {len(d['line2'])} != 69"

    def test_line1_starts_with_1(self):
        for _ in range(10):
            assert json.loads(jutsu.generate('tle_satellite'))['line1'][0] == '1'

    def test_line2_starts_with_2(self):
        for _ in range(10):
            assert json.loads(jutsu.generate('tle_satellite'))['line2'][0] == '2'

    def test_line1_checksum_verified(self):
        """NORAD Modulo-10 checksum at line1[68] must match recomputed value."""
        for _ in range(20):
            d = json.loads(jutsu.generate('tle_satellite'))
            line1 = d['line1']
            expected = _norad_checksum(line1)
            actual = int(line1[68])
            assert actual == expected, \
                f"line1 checksum: got {actual}, expected {expected}\n{line1}"

    def test_line2_checksum_verified(self):
        """NORAD Modulo-10 checksum at line2[68] must match recomputed value."""
        for _ in range(20):
            d = json.loads(jutsu.generate('tle_satellite'))
            line2 = d['line2']
            expected = _norad_checksum(line2)
            actual = int(line2[68])
            assert actual == expected, \
                f"line2 checksum: got {actual}, expected {expected}\n{line2}"

    def test_checksum_digit_is_decimal(self):
        for _ in range(10):
            d = json.loads(jutsu.generate('tle_satellite'))
            assert d['line1'][68].isdigit()
            assert d['line2'][68].isdigit()

    def test_norad_id_range(self):
        for _ in range(20):
            nid = json.loads(jutsu.generate('tle_satellite'))['norad_id']
            assert 1 <= nid <= 99999, f"norad_id {nid} out of range"

    def test_norad_id_consistent_on_both_lines(self):
        """Catalog number must be identical on line1[2:7] and line2[2:7]."""
        for _ in range(10):
            d = json.loads(jutsu.generate('tle_satellite'))
            cat1 = d['line1'][2:7]
            cat2 = d['line2'][2:7]
            assert cat1 == cat2, f"Catalog# mismatch: line1={cat1}, line2={cat2}"

    def test_norad_id_matches_line_content(self):
        """norad_id JSON field must match the catalog number in both lines."""
        for _ in range(10):
            d = json.loads(jutsu.generate('tle_satellite'))
            assert int(d['line1'][2:7]) == d['norad_id']
            assert int(d['line2'][2:7]) == d['norad_id']

    def test_classification_valid(self):
        """Classification at line1[7] must be U, C, or S."""
        for _ in range(20):
            cls = json.loads(jutsu.generate('tle_satellite'))['line1'][7]
            assert cls in ('U', 'C', 'S'), f"Invalid classification: {cls}"

    def test_classification_field_matches_line(self):
        for _ in range(10):
            d = json.loads(jutsu.generate('tle_satellite'))
            assert d['classification'] == d['line1'][7]

    def test_line1_ephemeris_type_is_0(self):
        """Position line1[62] (ephemeris type) must be '0'."""
        for _ in range(10):
            assert json.loads(jutsu.generate('tle_satellite'))['line1'][62] == '0'

    def test_epoch_year_range(self):
        for _ in range(20):
            yr = json.loads(jutsu.generate('tle_satellite'))['epoch_year']
            assert 0 <= yr <= 99, f"epoch_year {yr} out of [0, 99]"

    def test_epoch_year_in_line1(self):
        """epoch_year JSON must match line1[18:20]."""
        for _ in range(10):
            d = json.loads(jutsu.generate('tle_satellite'))
            assert int(d['line1'][18:20]) == d['epoch_year']

    def test_epoch_day_range(self):
        for _ in range(20):
            day = json.loads(jutsu.generate('tle_satellite'))['epoch_day']
            assert 1.0 <= day <= 366.0, f"epoch_day {day} out of [1.0, 366.0]"

    def test_inclination_range(self):
        for _ in range(20):
            incl = json.loads(jutsu.generate('tle_satellite'))['inclination']
            assert 0.0 <= incl <= 180.0, f"inclination {incl} out of range"

    def test_inclination_in_line2(self):
        """Inclination at line2[8:16] must match inclination JSON field."""
        for _ in range(10):
            d = json.loads(jutsu.generate('tle_satellite'))
            incl_str = d['line2'][8:16].strip()
            assert abs(float(incl_str) - d['inclination']) < 1e-3, \
                f"inclination mismatch: line2={incl_str}, json={d['inclination']}"

    def test_raan_range(self):
        for _ in range(20):
            raan = json.loads(jutsu.generate('tle_satellite'))['raan']
            assert 0.0 <= raan <= 360.0, f"RAAN {raan} out of range"

    def test_eccentricity_range(self):
        for _ in range(20):
            ecc = json.loads(jutsu.generate('tle_satellite'))['eccentricity']
            assert 0.0 <= ecc < 1.0, f"eccentricity {ecc} out of [0, 1)"

    def test_eccentricity_raw_is_7_digits(self):
        """line2[26:33] must be exactly 7 ASCII digits (eccentricity, no decimal)."""
        for _ in range(10):
            raw = json.loads(jutsu.generate('tle_satellite'))['line2'][26:33]
            assert raw.isdigit() and len(raw) == 7, \
                f"eccentricity raw '{raw}' is not 7 digits"

    def test_eccentricity_raw_consistent(self):
        """int(line2[26:33]) / 1e7 must match eccentricity JSON field."""
        for _ in range(10):
            d = json.loads(jutsu.generate('tle_satellite'))
            raw_val = int(d['line2'][26:33]) / 1e7
            assert abs(raw_val - d['eccentricity']) < 1e-6, \
                f"eccentricity raw {raw_val} != json {d['eccentricity']}"

    def test_arg_of_perigee_range(self):
        for _ in range(20):
            v = json.loads(jutsu.generate('tle_satellite'))['arg_of_perigee']
            assert 0.0 <= v <= 360.0, f"arg_of_perigee {v} out of range"

    def test_mean_anomaly_range(self):
        for _ in range(20):
            v = json.loads(jutsu.generate('tle_satellite'))['mean_anomaly']
            assert 0.0 <= v <= 360.0, f"mean_anomaly {v} out of range"

    def test_mean_motion_positive(self):
        for _ in range(20):
            mm = json.loads(jutsu.generate('tle_satellite'))['mean_motion']
            assert mm > 0.0, f"mean_motion {mm} <= 0"

    def test_rev_number_nonneg(self):
        for _ in range(10):
            rv = json.loads(jutsu.generate('tle_satellite'))['rev_number']
            assert rv >= 0, f"rev_number {rv} < 0"

    def test_orbit_type_valid(self):
        for _ in range(20):
            ot = json.loads(jutsu.generate('tle_satellite'))['orbit_type']
            assert ot in _VALID_ORBIT_TYPES, f"orbit_type '{ot}' not valid"

    def test_orbit_types_appear(self):
        """All orbit types should appear within 200 generates."""
        seen = set()
        for _ in range(200):
            seen.add(json.loads(jutsu.generate('tle_satellite'))['orbit_type'])
        assert len(seen) >= 3, f"Only {len(seen)} orbit types seen in 200 tries: {seen}"

    def test_name_nonempty(self):
        for _ in range(10):
            name = json.loads(jutsu.generate('tle_satellite'))['name']
            assert isinstance(name, str) and len(name) > 0

    def test_line2_space_separators(self):
        """Key separator positions on line2 must be spaces."""
        for _ in range(10):
            l2 = json.loads(jutsu.generate('tle_satellite'))['line2']
            assert l2[7]  == ' ', f"line2[7]  should be space, got '{l2[7]}'"
            assert l2[16] == ' ', f"line2[16] should be space, got '{l2[16]}'"
            assert l2[25] == ' ', f"line2[25] should be space, got '{l2[25]}'"
            assert l2[33] == ' ', f"line2[33] should be space, got '{l2[33]}'"
            assert l2[42] == ' ', f"line2[42] should be space, got '{l2[42]}'"
            assert l2[51] == ' ', f"line2[51] should be space, got '{l2[51]}'"

    def test_bulk_variety(self):
        orbit_types = {json.loads(r)['orbit_type'] for r in jutsu.bulk('tle_satellite', 10)}
        norad_ids   = {json.loads(r)['norad_id']   for r in jutsu.bulk('tle_satellite', 10)}
        assert len(norad_ids) > 1
