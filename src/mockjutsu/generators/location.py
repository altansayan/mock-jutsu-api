"""
mock-jutsu — Location / Geo Generator
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)

Standards:
  Latitude / Longitude — WGS 84 (ISO 6709), locale-aware bounding boxes
  Timezone             — IANA Time Zone Database (public domain, iana.org)
  Country Code         — ISO 3166-1 alpha-2
"""

import secrets

# ── Geographic bounding boxes (WGS 84) ───────────────────────────────────────
# Source: geodatos.net · naturalearthdata.com

_LAT_RANGE = {
    'TR': (36.0, 42.0),
    'US': (25.0, 49.0),
    'UK': (50.0, 59.0),
    'DE': (47.0, 55.0),
    'FR': (42.0, 51.0),
    'RU': (41.0, 82.0),
}

_LON_RANGE = {
    'TR': (26.0,  45.0),
    'US': (-125.0, -66.0),
    'UK': (-8.0,   2.0),
    'DE': (6.0,   15.0),
    'FR': (-5.0,   8.0),
    'RU': (27.0, 170.0),
}

# ── IANA Timezones ────────────────────────────────────────────────────────────
# Source: IANA Time Zone Database (data.iana.org) — public domain

_TIMEZONES = {
    'TR': ['Europe/Istanbul'],
    'US': ['America/New_York', 'America/Chicago', 'America/Denver',
           'America/Los_Angeles', 'America/Phoenix', 'America/Anchorage'],
    'UK': ['Europe/London'],
    'DE': ['Europe/Berlin'],
    'FR': ['Europe/Paris'],
    'RU': ['Europe/Moscow', 'Asia/Yekaterinburg', 'Asia/Novosibirsk',
           'Asia/Krasnoyarsk', 'Asia/Irkutsk', 'Asia/Vladivostok'],
}

# ── Country codes (ISO 3166-1 alpha-2) ───────────────────────────────────────

_COUNTRY_CODE = {
    'TR': 'TR', 'US': 'US', 'UK': 'GB', 'DE': 'DE', 'FR': 'FR', 'RU': 'RU',
}


# ── Generator ─────────────────────────────────────────────────────────────────

class LocationGenerator:
    """WGS-84 coordinates, IANA timezones, ISO 3166-1 country codes — locale-aware."""

    def generate(self, data_type: str, locale: str = 'TR', **kwargs):
        dt  = data_type.lower().strip()
        loc = locale.upper()

        if dt == 'latitude':
            return self._latitude(loc)
        if dt == 'longitude':
            return self._longitude(loc)
        if dt == 'timezone':
            return self._timezone(loc)
        if dt == 'country_code':
            return _COUNTRY_CODE.get(loc, 'TR')
        if dt == 'coordinates':
            return self._coordinates(loc)

        return f"ERROR: Unknown DataType '{dt}'"

    # ── Coordinate helpers ────────────────────────────────────────────────────

    def _rand_float(self, lo: float, hi: float) -> float:
        """CSPRNG float in [lo, hi] with 6 decimal places."""
        span = hi - lo
        raw = secrets.randbelow(10 ** 8) / 10 ** 8
        return round(lo + raw * span, 6)

    def _latitude(self, locale: str) -> float:
        lo, hi = _LAT_RANGE.get(locale, _LAT_RANGE['TR'])
        return self._rand_float(lo, hi)

    def _longitude(self, locale: str) -> float:
        lo, hi = _LON_RANGE.get(locale, _LON_RANGE['TR'])
        return self._rand_float(lo, hi)

    def _timezone(self, locale: str) -> str:
        zones = _TIMEZONES.get(locale, _TIMEZONES['TR'])
        return secrets.choice(zones)

    def _coordinates(self, locale: str) -> str:
        """Returns 'lat,lon' as a comma-separated string."""
        return f"{self._latitude(locale)},{self._longitude(locale)}"
