"""
Tests for God Mode #25 — Oyun Geliştirme: Quaternion & NavMesh Verileri
Types: quaternion, navmesh_path

Core invariants:
  quaternion:
    - x, y, z, w all floats in [-1.0, 1.0]
    - magnitude == 1.0 (L2 norm of components, within 1e-6)
    - sqrt(x²+y²+z²+w²) == 1.0 independently verified (within 1e-6)
    - euler_degrees: pitch ∈ [-90, 90], yaw ∈ (-180, 180], roll ∈ (-180, 180]
    - Not all-zero components

  navmesh_path:
    - waypoints is a list, 3-15 waypoints
    - waypoint_count == len(waypoints)
    - start == waypoints[0]
    - end  == waypoints[-1]
    - Each waypoint has x, y, z (floats)
    - No two consecutive waypoints are identical
    - total_distance > 0
    - total_distance matches recomputed sum of segment distances (±0.1)
    - Each segment distance > 0 (no teleportation)
    - y values bounded (terrain height, not flying away)
"""

import json
import math
import pytest
from mockjutsu.core import MockJutsuCore

jutsu = MockJutsuCore()


# ── quaternion ────────────────────────────────────────────────────────────────

class TestQuaternion:

    def test_no_error(self):
        assert not jutsu.generate('quaternion').startswith('ERROR')

    def test_returns_string(self):
        assert isinstance(jutsu.generate('quaternion'), str)

    def test_is_valid_json(self):
        json.loads(jutsu.generate('quaternion'))

    def test_is_dict(self):
        assert isinstance(json.loads(jutsu.generate('quaternion')), dict)

    def test_has_required_fields(self):
        data = json.loads(jutsu.generate('quaternion'))
        for f in ('x', 'y', 'z', 'w', 'magnitude', 'euler_degrees'):
            assert f in data, f"Missing field: {f}"

    def test_components_are_floats(self):
        for _ in range(10):
            data = json.loads(jutsu.generate('quaternion'))
            for c in ('x', 'y', 'z', 'w'):
                assert isinstance(data[c], float), \
                    f"Component {c}={data[c]} is not float"

    def test_components_in_unit_range(self):
        """All quaternion components must be in [-1.0, 1.0]."""
        for _ in range(20):
            data = json.loads(jutsu.generate('quaternion'))
            for c in ('x', 'y', 'z', 'w'):
                assert -1.0 <= data[c] <= 1.0, \
                    f"Component {c}={data[c]} out of [-1, 1]"

    def test_magnitude_field_is_one(self):
        """Stored magnitude must be 1.0 within 1e-6."""
        for _ in range(20):
            data = json.loads(jutsu.generate('quaternion'))
            assert abs(data['magnitude'] - 1.0) < 1e-6, \
                f"magnitude={data['magnitude']} not close to 1.0"

    def test_magnitude_recomputed_from_components(self):
        """Independently compute sqrt(x²+y²+z²+w²): must be 1.0 within 1e-6."""
        for _ in range(20):
            data = json.loads(jutsu.generate('quaternion'))
            x, y, z, w = data['x'], data['y'], data['z'], data['w']
            mag = math.sqrt(x*x + y*y + z*z + w*w)
            assert abs(mag - 1.0) < 1e-6, \
                f"Recomputed magnitude {mag:.10f} not close to 1.0"

    def test_not_zero_quaternion(self):
        """All components should not be zero simultaneously."""
        for _ in range(10):
            data = json.loads(jutsu.generate('quaternion'))
            total = abs(data['x']) + abs(data['y']) + abs(data['z']) + abs(data['w'])
            assert total > 0.01, "Degenerate zero quaternion"

    def test_euler_has_required_fields(self):
        data = json.loads(jutsu.generate('quaternion'))
        euler = data['euler_degrees']
        for f in ('pitch', 'yaw', 'roll'):
            assert f in euler, f"Missing euler field: {f}"

    def test_euler_values_are_floats(self):
        for _ in range(10):
            euler = json.loads(jutsu.generate('quaternion'))['euler_degrees']
            for f in ('pitch', 'yaw', 'roll'):
                assert isinstance(euler[f], (int, float)), \
                    f"euler.{f}={euler[f]} not numeric"

    def test_pitch_range(self):
        """Pitch (asin result) must be in [-90, 90] degrees."""
        for _ in range(20):
            pitch = json.loads(jutsu.generate('quaternion'))['euler_degrees']['pitch']
            assert -90.0 <= pitch <= 90.0, f"pitch={pitch} out of [-90, 90]"

    def test_yaw_range(self):
        """Yaw (atan2 result) must be in (-180, 180] degrees."""
        for _ in range(20):
            yaw = json.loads(jutsu.generate('quaternion'))['euler_degrees']['yaw']
            assert -180.0 < yaw <= 180.0 or abs(yaw + 180.0) < 1e-9, \
                f"yaw={yaw} out of (-180, 180]"

    def test_roll_range(self):
        """Roll (atan2 result) must be in (-180, 180] degrees."""
        for _ in range(20):
            roll = json.loads(jutsu.generate('quaternion'))['euler_degrees']['roll']
            assert -180.0 < roll <= 180.0 or abs(roll + 180.0) < 1e-9, \
                f"roll={roll} out of (-180, 180]"

    def test_w_sign_varies(self):
        """w component should be both positive and negative across many samples."""
        signs = {json.loads(jutsu.generate('quaternion'))['w'] > 0 for _ in range(30)}
        assert len(signs) == 2, "w is always the same sign — not uniformly distributed"

    def test_bulk_variety(self):
        xs = {json.loads(r)['x'] for r in jutsu.bulk('quaternion', 5)}
        assert len(xs) > 1


# ── navmesh_path ──────────────────────────────────────────────────────────────

class TestNavMeshPath:

    def test_no_error(self):
        assert not jutsu.generate('navmesh_path').startswith('ERROR')

    def test_returns_string(self):
        assert isinstance(jutsu.generate('navmesh_path'), str)

    def test_is_valid_json(self):
        json.loads(jutsu.generate('navmesh_path'))

    def test_is_dict(self):
        assert isinstance(json.loads(jutsu.generate('navmesh_path')), dict)

    def test_has_required_fields(self):
        data = json.loads(jutsu.generate('navmesh_path'))
        for f in ('start', 'end', 'waypoints', 'total_distance', 'waypoint_count'):
            assert f in data, f"Missing field: {f}"

    def test_waypoints_is_list(self):
        data = json.loads(jutsu.generate('navmesh_path'))
        assert isinstance(data['waypoints'], list)

    def test_waypoint_count_in_range(self):
        """Path must have between 3 and 15 waypoints."""
        for _ in range(20):
            n = json.loads(jutsu.generate('navmesh_path'))['waypoint_count']
            assert 3 <= n <= 15, f"waypoint_count={n} out of [3, 15]"

    def test_waypoint_count_matches_list_length(self):
        for _ in range(10):
            data = json.loads(jutsu.generate('navmesh_path'))
            assert data['waypoint_count'] == len(data['waypoints']), \
                f"waypoint_count {data['waypoint_count']} != len(waypoints) {len(data['waypoints'])}"

    def test_start_equals_first_waypoint(self):
        for _ in range(10):
            data = json.loads(jutsu.generate('navmesh_path'))
            assert data['start'] == data['waypoints'][0], \
                f"start != waypoints[0]"

    def test_end_equals_last_waypoint(self):
        for _ in range(10):
            data = json.loads(jutsu.generate('navmesh_path'))
            assert data['end'] == data['waypoints'][-1], \
                f"end != waypoints[-1]"

    def test_each_waypoint_has_xyz(self):
        data = json.loads(jutsu.generate('navmesh_path'))
        for i, wp in enumerate(data['waypoints']):
            for f in ('x', 'y', 'z'):
                assert f in wp, f"Waypoint {i} missing field '{f}'"

    def test_waypoint_xyz_are_numeric(self):
        data = json.loads(jutsu.generate('navmesh_path'))
        for i, wp in enumerate(data['waypoints']):
            for f in ('x', 'y', 'z'):
                assert isinstance(wp[f], (int, float)), \
                    f"Waypoint {i}.{f}={wp[f]} not numeric"

    def test_consecutive_waypoints_differ(self):
        """No two consecutive waypoints should be identical."""
        for _ in range(10):
            wps = json.loads(jutsu.generate('navmesh_path'))['waypoints']
            for i in range(1, len(wps)):
                assert wps[i] != wps[i-1], \
                    f"Consecutive waypoints {i-1} and {i} are identical"

    def test_total_distance_positive(self):
        for _ in range(10):
            d = json.loads(jutsu.generate('navmesh_path'))['total_distance']
            assert d > 0, f"total_distance={d} <= 0"

    def test_total_distance_matches_computed(self):
        """Recomputed sum of segment distances must match total_distance ±0.1."""
        for _ in range(10):
            data = json.loads(jutsu.generate('navmesh_path'))
            wps = data['waypoints']
            computed = sum(
                math.sqrt(
                    (wps[i]['x'] - wps[i-1]['x'])**2 +
                    (wps[i]['y'] - wps[i-1]['y'])**2 +
                    (wps[i]['z'] - wps[i-1]['z'])**2
                )
                for i in range(1, len(wps))
            )
            assert abs(computed - data['total_distance']) < 0.1, \
                f"total_distance {data['total_distance']} != computed {computed:.3f}"

    def test_each_segment_distance_positive(self):
        """Every consecutive waypoint pair must have distance > 0."""
        for _ in range(10):
            wps = json.loads(jutsu.generate('navmesh_path'))['waypoints']
            for i in range(1, len(wps)):
                d = math.sqrt(
                    (wps[i]['x'] - wps[i-1]['x'])**2 +
                    (wps[i]['y'] - wps[i-1]['y'])**2 +
                    (wps[i]['z'] - wps[i-1]['z'])**2
                )
                assert d > 0, f"Segment {i} distance is 0"

    def test_y_values_bounded(self):
        """y (terrain height) should stay within game-world bounds."""
        for _ in range(10):
            wps = json.loads(jutsu.generate('navmesh_path'))['waypoints']
            for i, wp in enumerate(wps):
                assert -10.0 <= wp['y'] <= 10.0, \
                    f"Waypoint {i} y={wp['y']} out of terrain range"

    def test_start_end_differ(self):
        """Start and end of the path should not be the same point (with high probability)."""
        for _ in range(10):
            data = json.loads(jutsu.generate('navmesh_path'))
            s, e = data['start'], data['end']
            dist = math.sqrt((s['x']-e['x'])**2 + (s['y']-e['y'])**2 + (s['z']-e['z'])**2)
            assert dist > 0.001, f"Start and end are the same point"

    def test_bulk_variety(self):
        counts = {json.loads(r)['waypoint_count'] for r in jutsu.bulk('navmesh_path', 10)}
        assert len(counts) > 1
