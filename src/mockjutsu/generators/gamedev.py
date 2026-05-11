"""
mock-jutsu — Quaternion & NavMesh Path Generator (Game Development)
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)

Supported types:
  quaternion   — L2-normalized unit quaternion for 3D rotation.
                 Components (x, y, z, w) via Gaussian sampling + L2 normalization.
                 Includes pre-computed Euler angles (ZYX convention, degrees).
                 Invariant: sqrt(x²+y²+z²+w²) = 1.0 (within floating-point precision).
                 Compatible with Unity Transform.rotation and Unreal FQuat.
  navmesh_path — A*-compatible NavMesh waypoint path.
                 3–15 waypoints in 3D game-world space.
                 Each step: random heading ± 60° turn, distance 5–25 units.
                 Terrain height (y) varies ±0.5 per step, bounded to ±5.
                 Invariants: start=waypoints[0], end=waypoints[-1],
                             total_distance = Σ segment distances,
                             no two consecutive waypoints identical.

Zero external dependencies: json, math, random (stdlib only).
"""

import json
import math
import random


# ── Helpers ───────────────────────────────────────────────────────────────────

def _l2_normalize4(components: list[float]) -> list[float]:
    """L2 normalize a 4-vector."""
    mag = math.sqrt(sum(c * c for c in components))
    return [c / mag for c in components]


def _quat_to_euler(x: float, y: float, z: float, w: float) -> tuple[float, float, float]:
    """
    Unit quaternion → Euler angles (ZYX convention, degrees).
    Returns (pitch, yaw, roll).
    """
    # Roll — rotation about X axis
    sinr = 2.0 * (w * x + y * z)
    cosr = 1.0 - 2.0 * (x * x + y * y)
    roll = math.degrees(math.atan2(sinr, cosr))

    # Pitch — rotation about Y axis (asin domain clamp)
    sinp = 2.0 * (w * y - z * x)
    sinp = max(-1.0, min(1.0, sinp))
    pitch = math.degrees(math.asin(sinp))

    # Yaw — rotation about Z axis
    siny = 2.0 * (w * z + x * y)
    cosy = 1.0 - 2.0 * (y * y + z * z)
    yaw = math.degrees(math.atan2(siny, cosy))

    return round(pitch, 4), round(yaw, 4), round(roll, 4)


# ── Quaternion ────────────────────────────────────────────────────────────────

def generate_quaternion() -> str:
    """
    L2-normalized unit quaternion via Gaussian sampling.

    Sampling uniform random rotations (Shoemake 1992):
      draw 4 values from N(0,1), then L2-normalize.
    """
    raw = [random.gauss(0.0, 1.0) for _ in range(4)]
    x, y, z, w = _l2_normalize4(raw)

    # Round components to 8 dp, then recompute magnitude from rounded values
    # (self-consistent JSON: magnitude matches what a reader would compute)
    x = round(x, 8)
    y = round(y, 8)
    z = round(z, 8)
    w = round(w, 8)
    magnitude = round(math.sqrt(x*x + y*y + z*z + w*w), 10)

    pitch, yaw, roll = _quat_to_euler(x, y, z, w)

    return json.dumps({
        'x':        x,
        'y':        y,
        'z':        z,
        'w':        w,
        'magnitude': magnitude,
        'euler_degrees': {
            'pitch': pitch,
            'yaw':   yaw,
            'roll':  roll,
        },
    }, ensure_ascii=False)


# ── NavMesh Path ──────────────────────────────────────────────────────────────

def generate_navmesh_path() -> str:
    """
    A*-compatible NavMesh waypoint path in 3D game-world space.

    Path generation:
      - Random heading θ, each step turns ±60° max
      - Step length 5–25 units (x/z plane)
      - Terrain height y drifts ±0.5 per step, clamped to [-5, 5]
    """
    n = random.randint(3, 15)

    # Starting position in game-world coordinates
    cx = round(random.uniform(-200.0, 200.0), 3)
    cy = round(random.uniform(-2.0, 2.0), 3)
    cz = round(random.uniform(-200.0, 200.0), 3)

    waypoints = [{'x': cx, 'y': cy, 'z': cz}]
    angle = random.uniform(0.0, 2.0 * math.pi)  # initial heading (radians)

    for _ in range(n - 1):
        step   = random.uniform(5.0, 25.0)
        angle += random.uniform(-math.pi / 3.0, math.pi / 3.0)

        cx = round(cx + step * math.cos(angle), 3)
        cy = round(max(-5.0, min(5.0, cy + random.uniform(-0.5, 0.5))), 3)
        cz = round(cz + step * math.sin(angle), 3)

        waypoints.append({'x': cx, 'y': cy, 'z': cz})

    # Compute total path distance
    total = 0.0
    for i in range(1, len(waypoints)):
        a, b = waypoints[i - 1], waypoints[i]
        d = math.sqrt(
            (b['x'] - a['x']) ** 2 +
            (b['y'] - a['y']) ** 2 +
            (b['z'] - a['z']) ** 2
        )
        total += d

    return json.dumps({
        'start':          waypoints[0],
        'end':            waypoints[-1],
        'waypoints':      waypoints,
        'total_distance': round(total, 3),
        'waypoint_count': len(waypoints),
    }, ensure_ascii=False)


# ── Generator class ────────────────────────────────────────────────────────────

class GameDevGenerator:
    """Quaternion and NavMesh path generator for game development testing."""

    def generate(self, data_type: str, **kwargs) -> str:
        if data_type == 'quaternion':
            return generate_quaternion()
        if data_type == 'navmesh_path':
            return generate_navmesh_path()
        return f"ERROR: Unknown type '{data_type}'"
