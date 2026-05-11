"""
Tests for God Mode #19 — FDR / Drone Telemetry Generator
Types: fdr_record, drone_telemetry

Core invariants:
  - fdr_record      : time-series, t[i]==i*interval_ms, all params within physical bounds,
                      pitch/altitude/speed change gradually (bounded random walk)
  - drone_telemetry : time-series, t[i]==i*interval_ms, all params within physical bounds,
                      altitude/speed change gradually, battery monotonically decreasing
"""

import json
import pytest
from mockjutsu.core import MockJutsuCore

jutsu = MockJutsuCore()

_FDR_REQUIRED_TOP    = {'flight_id', 'aircraft', 'recording_start', 'interval_ms', 'samples'}
_FDR_REQUIRED_SAMPLE = {'t', 'pitch', 'roll', 'yaw', 'altitude_ft', 'speed_kts', 'vspeed_fpm', 'g_force'}
_DRONE_REQUIRED_TOP  = {'drone_id', 'mission_id', 'recording_start', 'interval_ms', 'samples'}
_DRONE_REQUIRED_SAMPLE = {'t', 'lat', 'lon', 'alt_m', 'pitch', 'roll', 'yaw', 'speed_ms', 'battery_pct', 'rssi'}


def _yaw_diff(a, b):
    """Shortest arc between two yaw values (handles 359→1 wrap)."""
    d = abs(a - b)
    return min(d, 360.0 - d)


# ── fdr_record ────────────────────────────────────────────────────────────────

class TestFdrRecord:

    def test_no_error(self):
        assert not jutsu.generate('fdr_record').startswith('ERROR')

    def test_returns_string(self):
        assert isinstance(jutsu.generate('fdr_record'), str)

    def test_is_valid_json(self):
        json.loads(jutsu.generate('fdr_record'))

    def test_is_dict(self):
        assert isinstance(json.loads(jutsu.generate('fdr_record')), dict)

    def test_has_required_top_fields(self):
        data = json.loads(jutsu.generate('fdr_record'))
        assert _FDR_REQUIRED_TOP.issubset(data.keys())

    def test_samples_is_list(self):
        assert isinstance(json.loads(jutsu.generate('fdr_record'))['samples'], list)

    def test_samples_at_least_10(self):
        assert len(json.loads(jutsu.generate('fdr_record'))['samples']) >= 10

    def test_each_sample_has_required_fields(self):
        samples = json.loads(jutsu.generate('fdr_record'))['samples']
        for s in samples:
            missing = _FDR_REQUIRED_SAMPLE - s.keys()
            assert not missing, f"Missing fields: {missing}"

    def test_t_equals_index_times_interval(self):
        data     = json.loads(jutsu.generate('fdr_record'))
        interval = data['interval_ms']
        for i, s in enumerate(data['samples']):
            assert s['t'] == i * interval, f"t[{i}]={s['t']}, expected {i * interval}"

    def test_pitch_within_bounds(self):
        samples = json.loads(jutsu.generate('fdr_record'))['samples']
        for s in samples:
            assert -30 <= s['pitch'] <= 30, f"pitch out of bounds: {s['pitch']}"

    def test_roll_within_bounds(self):
        samples = json.loads(jutsu.generate('fdr_record'))['samples']
        for s in samples:
            assert -45 <= s['roll'] <= 45, f"roll out of bounds: {s['roll']}"

    def test_yaw_within_bounds(self):
        samples = json.loads(jutsu.generate('fdr_record'))['samples']
        for s in samples:
            assert 0.0 <= s['yaw'] < 360.0, f"yaw out of bounds: {s['yaw']}"

    def test_altitude_within_bounds(self):
        samples = json.loads(jutsu.generate('fdr_record'))['samples']
        for s in samples:
            assert 0 <= s['altitude_ft'] <= 45000, f"altitude out of bounds: {s['altitude_ft']}"

    def test_speed_within_bounds(self):
        samples = json.loads(jutsu.generate('fdr_record'))['samples']
        for s in samples:
            assert 150 <= s['speed_kts'] <= 600, f"speed_kts out of bounds: {s['speed_kts']}"

    def test_pitch_changes_gradually(self):
        """Consecutive pitch change must not exceed 0.6° (max_step=0.5)."""
        samples = json.loads(jutsu.generate('fdr_record'))['samples']
        for i in range(1, len(samples)):
            diff = abs(samples[i]['pitch'] - samples[i-1]['pitch'])
            assert diff <= 0.6, f"pitch jump {diff:.3f}° at step {i}"

    def test_altitude_changes_gradually(self):
        """Consecutive altitude change must not exceed 101 ft (max_step=100)."""
        samples = json.loads(jutsu.generate('fdr_record'))['samples']
        for i in range(1, len(samples)):
            diff = abs(samples[i]['altitude_ft'] - samples[i-1]['altitude_ft'])
            assert diff <= 101, f"altitude jump {diff} ft at step {i}"

    def test_speed_changes_gradually(self):
        """Consecutive speed change must not exceed 5.1 kts (max_step=5)."""
        samples = json.loads(jutsu.generate('fdr_record'))['samples']
        for i in range(1, len(samples)):
            diff = abs(samples[i]['speed_kts'] - samples[i-1]['speed_kts'])
            assert diff <= 5.1, f"speed jump {diff:.2f} kts at step {i}"

    def test_bulk_unique_flight_ids(self):
        ids = {json.loads(r)['flight_id'] for r in jutsu.bulk('fdr_record', 5)}
        assert len(ids) == 5


# ── drone_telemetry ───────────────────────────────────────────────────────────

class TestDroneTelemetry:

    def test_no_error(self):
        assert not jutsu.generate('drone_telemetry').startswith('ERROR')

    def test_returns_string(self):
        assert isinstance(jutsu.generate('drone_telemetry'), str)

    def test_is_valid_json(self):
        json.loads(jutsu.generate('drone_telemetry'))

    def test_is_dict(self):
        assert isinstance(json.loads(jutsu.generate('drone_telemetry')), dict)

    def test_has_required_top_fields(self):
        data = json.loads(jutsu.generate('drone_telemetry'))
        assert _DRONE_REQUIRED_TOP.issubset(data.keys())

    def test_samples_is_list(self):
        assert isinstance(json.loads(jutsu.generate('drone_telemetry'))['samples'], list)

    def test_samples_at_least_10(self):
        assert len(json.loads(jutsu.generate('drone_telemetry'))['samples']) >= 10

    def test_each_sample_has_required_fields(self):
        samples = json.loads(jutsu.generate('drone_telemetry'))['samples']
        for s in samples:
            missing = _DRONE_REQUIRED_SAMPLE - s.keys()
            assert not missing, f"Missing fields: {missing}"

    def test_t_equals_index_times_interval(self):
        data     = json.loads(jutsu.generate('drone_telemetry'))
        interval = data['interval_ms']
        for i, s in enumerate(data['samples']):
            assert s['t'] == i * interval, f"t[{i}]={s['t']}, expected {i * interval}"

    def test_alt_within_bounds(self):
        samples = json.loads(jutsu.generate('drone_telemetry'))['samples']
        for s in samples:
            assert 0 <= s['alt_m'] <= 400, f"alt_m out of bounds: {s['alt_m']}"

    def test_pitch_within_bounds(self):
        samples = json.loads(jutsu.generate('drone_telemetry'))['samples']
        for s in samples:
            assert -30 <= s['pitch'] <= 30, f"pitch out of bounds: {s['pitch']}"

    def test_yaw_within_bounds(self):
        samples = json.loads(jutsu.generate('drone_telemetry'))['samples']
        for s in samples:
            assert 0.0 <= s['yaw'] < 360.0, f"yaw out of bounds: {s['yaw']}"

    def test_speed_within_bounds(self):
        samples = json.loads(jutsu.generate('drone_telemetry'))['samples']
        for s in samples:
            assert 0 <= s['speed_ms'] <= 20, f"speed_ms out of bounds: {s['speed_ms']}"

    def test_battery_within_bounds(self):
        samples = json.loads(jutsu.generate('drone_telemetry'))['samples']
        for s in samples:
            assert 0 <= s['battery_pct'] <= 100, f"battery_pct out of bounds: {s['battery_pct']}"

    def test_rssi_within_bounds(self):
        samples = json.loads(jutsu.generate('drone_telemetry'))['samples']
        for s in samples:
            assert -100 <= s['rssi'] <= -30, f"rssi out of bounds: {s['rssi']}"

    def test_battery_monotonically_decreasing(self):
        """Battery can only decrease or stay flat, never increase."""
        samples = json.loads(jutsu.generate('drone_telemetry'))['samples']
        for i in range(1, len(samples)):
            assert samples[i]['battery_pct'] <= samples[i-1]['battery_pct'], (
                f"battery increased at step {i}: {samples[i-1]['battery_pct']} → {samples[i]['battery_pct']}"
            )

    def test_alt_changes_gradually(self):
        """Consecutive altitude change must not exceed 2.1 m (max_step=2)."""
        samples = json.loads(jutsu.generate('drone_telemetry'))['samples']
        for i in range(1, len(samples)):
            diff = abs(samples[i]['alt_m'] - samples[i-1]['alt_m'])
            assert diff <= 2.1, f"alt_m jump {diff:.3f} m at step {i}"

    def test_speed_changes_gradually(self):
        """Consecutive speed change must not exceed 0.51 m/s (max_step=0.5)."""
        samples = json.loads(jutsu.generate('drone_telemetry'))['samples']
        for i in range(1, len(samples)):
            diff = abs(samples[i]['speed_ms'] - samples[i-1]['speed_ms'])
            assert diff <= 0.51, f"speed_ms jump {diff:.3f} at step {i}"

    def test_bulk_unique_mission_ids(self):
        ids = {json.loads(r)['mission_id'] for r in jutsu.bulk('drone_telemetry', 5)}
        assert len(ids) == 5
