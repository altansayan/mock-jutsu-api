"""
mock-jutsu — FDR / Drone Telemetry Generator
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)

Supported types:
  fdr_record      — Flight Data Recorder time-series (pitch, roll, yaw, altitude_ft,
                    speed_kts, vspeed_fpm, g_force). Values evolve via bounded random walk —
                    no teleportation between samples (physics-constrained interpolation).
  drone_telemetry — Drone telemetry time-series (lat, lon, alt_m, pitch, roll, yaw,
                    speed_ms, battery_pct, rssi). Battery strictly non-increasing.

Both produce JSON objects with:
  - flight_id / (drone_id + mission_id)
  - recording_start  ISO-8601 UTC timestamp
  - interval_ms      sample interval
  - samples[]        t = index × interval_ms (strictly increasing)

Zero external dependencies: datetime, json, random, uuid (stdlib only).
"""

import datetime
import json
import random
import uuid


# ── Helpers ───────────────────────────────────────────────────────────────────

def _rand_uuid() -> str:
    return str(uuid.uuid4())


def _now_iso() -> str:
    dt = datetime.datetime.now(datetime.timezone.utc)
    return dt.strftime('%Y-%m-%dT%H:%M:%S.') + f"{dt.microsecond // 1000:03d}Z"


def _clamp(val: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, val))


def _walk_clamp(val: float, lo: float, hi: float, max_step: float) -> float:
    """Bounded random walk: add uniform delta, clamp to [lo, hi], round to 2dp."""
    return round(_clamp(val + random.uniform(-max_step, max_step), lo, hi), 2)


def _walk_wrap(val: float, max_step: float, mod: float = 360.0) -> float:
    """Bounded random walk with wrap-around (for heading/yaw)."""
    return round((val + random.uniform(-max_step, max_step)) % mod, 2)


# ── FDR Record ────────────────────────────────────────────────────────────────

_AIRCRAFT_TYPES = ['B737', 'B777', 'A320', 'A350', 'B787', 'A380']


def generate_fdr_record() -> str:
    """Flight Data Recorder time-series with physics-constrained bounded random walk."""
    n_samples   = random.randint(10, 30)
    interval_ms = 100   # 10 Hz — standard DFDR rate

    # Initial cruise state
    pitch       = round(random.uniform(-5.0,  5.0),  2)
    roll        = round(random.uniform(-5.0,  5.0),  2)
    yaw         = round(random.uniform(0.0,   360.0) % 360.0, 2)
    altitude_ft = round(random.uniform(28000.0, 40000.0), 2)
    speed_kts   = round(random.uniform(380.0, 480.0), 2)
    vspeed_fpm  = round(random.uniform(-200.0, 200.0), 2)
    g_force     = round(random.uniform(0.95, 1.05), 2)

    samples = []
    for i in range(n_samples):
        samples.append({
            't':           i * interval_ms,
            'pitch':       pitch,
            'roll':        roll,
            'yaw':         yaw,
            'altitude_ft': altitude_ft,
            'speed_kts':   speed_kts,
            'vspeed_fpm':  vspeed_fpm,
            'g_force':     g_force,
        })
        # Evolve state — bounded random walk (physics: values can't jump)
        pitch       = _walk_clamp(pitch,       -30.0,   30.0,   0.5)
        roll        = _walk_clamp(roll,        -45.0,   45.0,   1.0)
        yaw         = _walk_wrap(yaw,           1.0)
        altitude_ft = _walk_clamp(altitude_ft,  0.0,  45000.0, 100.0)
        speed_kts   = _walk_clamp(speed_kts,   150.0,  600.0,   5.0)
        vspeed_fpm  = _walk_clamp(vspeed_fpm, -3000.0, 3000.0, 200.0)
        g_force     = _walk_clamp(g_force,      0.5,    3.0,    0.1)

    return json.dumps({
        'flight_id':       _rand_uuid(),
        'aircraft':        random.choice(_AIRCRAFT_TYPES),
        'recording_start': _now_iso(),
        'interval_ms':     interval_ms,
        'samples':         samples,
    }, ensure_ascii=False)


# ── Drone Telemetry ────────────────────────────────────────────────────────────

_DRONE_MODELS = ['DJI-MAVIC', 'DJI-PHANTOM', 'DJI-MINI', 'PARROT-ANAFI', 'AUTEL-EVO']


def generate_drone_telemetry() -> str:
    """Drone telemetry time-series with physics-constrained walk and monotone battery drain."""
    n_samples   = random.randint(10, 25)
    interval_ms = 50    # 20 Hz — typical drone telemetry rate

    # Initial hover/flight state
    lat         = round(random.uniform(-70.0,  70.0),  6)
    lon         = round(random.uniform(-170.0, 170.0), 6)
    alt_m       = round(random.uniform(50.0,  200.0),  2)
    pitch       = round(random.uniform(-5.0,    5.0),  2)
    roll        = round(random.uniform(-5.0,    5.0),  2)
    yaw         = round(random.uniform(0.0,   360.0) % 360.0, 2)
    speed_ms    = round(random.uniform(2.0,   10.0),   2)
    battery_pct = round(random.uniform(80.0, 100.0),   1)
    rssi        = random.randint(-75, -55)

    samples = []
    for i in range(n_samples):
        samples.append({
            't':           i * interval_ms,
            'lat':         lat,
            'lon':         lon,
            'alt_m':       alt_m,
            'pitch':       pitch,
            'roll':        roll,
            'yaw':         yaw,
            'speed_ms':    speed_ms,
            'battery_pct': battery_pct,
            'rssi':        rssi,
        })
        # Evolve state
        lat         = round(lat + random.uniform(-0.00005, 0.00005), 6)
        lon         = round(lon + random.uniform(-0.00005, 0.00005), 6)
        alt_m       = _walk_clamp(alt_m,    0.0,   400.0,  2.0)
        pitch       = _walk_clamp(pitch,  -30.0,    30.0,  1.0)
        roll        = _walk_clamp(roll,   -30.0,    30.0,  1.0)
        yaw         = _walk_wrap(yaw,       2.0)
        speed_ms    = _walk_clamp(speed_ms, 0.0,    20.0,  0.5)
        # Battery: strictly non-increasing
        battery_pct = round(max(0.0, battery_pct - random.uniform(0.0, 0.3)), 1)
        rssi        = int(_clamp(rssi + random.randint(-2, 2), -100, -30))

    return json.dumps({
        'drone_id':        f"{random.choice(_DRONE_MODELS)}-{random.randint(1000, 9999)}",
        'mission_id':      _rand_uuid(),
        'recording_start': _now_iso(),
        'interval_ms':     interval_ms,
        'samples':         samples,
    }, ensure_ascii=False)


# ── Generator class ────────────────────────────────────────────────────────────

class TelemetryGenerator:
    """FDR and drone telemetry time-series generator."""

    def generate(self, data_type: str, **kwargs) -> str:
        if data_type == 'fdr_record':
            return generate_fdr_record()
        if data_type == 'drone_telemetry':
            return generate_drone_telemetry()
        return f"ERROR: Unknown type '{data_type}'"
