"""
Tests for God Mode #27 — Otomotiv: OBD-II ve CAN Bus Paketleri
Types: can_frame, obd2_response

Core invariants:
  can_frame:
    - JSON with frame_type, can_id, can_id_int, dlc, data, data_hex,
      crc15, crc15_hex, socketcan
    - frame_type in {standard, extended}
    - standard: can_id_int in [0, 2047]   (11-bit)
    - extended: can_id_int in [0, 536870911] (29-bit)
    - dlc in [0, 8]
    - len(data) == dlc
    - len(data_hex) == dlc * 2
    - crc15 in [0, 32767]  (15-bit)
    - crc15 recomputed from (can_id_int, dlc, data, is_extended) == returned crc15
    - crc15_hex == hex(crc15)
    - socketcan format: HEXID#HEXDATA (no '0x' prefix)

  obd2_response:
    - JSON with ecu_id, mode, pids, dtcs, dtc_count,
      rpm, speed_kmh, coolant_temp_c, throttle_pct,
      engine_load_pct, fuel_level_pct
    - ecu_id == '7E8'
    - mode == '01'
    - rpm in [0, 16383.75]
    - speed_kmh in [0, 255]
    - coolant_temp_c in [-40, 215]
    - throttle_pct in [0, 100]
    - engine_load_pct in [0, 100]
    - fuel_level_pct in [0, 100]
    - pids is non-empty list; each pid has crc15 in [0, 32767]
    - each pid's crc15 recomputed from (can_id_int, can_dlc, can_data, False) matches
    - dtcs is list; len(dtcs) == dtc_count
    - each DTC matches [PCBU][0-3][0-9A-F]{3}
"""

import json
import re
import pytest
from mockjutsu.core import MockJutsuCore

jutsu = MockJutsuCore()

_DTC_RE = re.compile(r'^[PCBU][0-3][0-9A-F]{3}$')


def _crc15_verify(can_id_int: int, dlc: int, data: list, extended: bool) -> int:
    """Independently compute CAN CRC-15 (ISO 11898-1, polynomial 0xC599)."""
    POLY = 0xC599
    bits = [0]  # SOF
    if not extended:
        for i in range(10, -1, -1):
            bits.append((can_id_int >> i) & 1)
        bits += [0, 0, 0]          # RTR, IDE, r0
    else:
        for i in range(28, -1, -1):
            bits.append((can_id_int >> i) & 1)
        bits += [1, 1, 0, 0, 0]    # SRR, IDE, RTR, r1, r0
    for i in range(3, -1, -1):
        bits.append((dlc >> i) & 1)
    for byte in data:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    crc = 0
    for bit in bits:
        if ((crc >> 14) ^ bit) & 1:
            crc = ((crc << 1) ^ POLY) & 0x7FFF
        else:
            crc = (crc << 1) & 0x7FFF
    return crc


# ── can_frame ─────────────────────────────────────────────────────────────────

class TestCanFrame:

    def test_no_error(self):
        assert not jutsu.generate('can_frame').startswith('ERROR')

    def test_returns_string(self):
        assert isinstance(jutsu.generate('can_frame'), str)

    def test_is_valid_json(self):
        json.loads(jutsu.generate('can_frame'))

    def test_is_dict(self):
        assert isinstance(json.loads(jutsu.generate('can_frame')), dict)

    def test_has_required_fields(self):
        d = json.loads(jutsu.generate('can_frame'))
        for f in ('frame_type', 'can_id', 'can_id_int', 'dlc',
                  'data', 'data_hex', 'crc15', 'crc15_hex', 'socketcan'):
            assert f in d, f"Missing field: {f}"

    def test_frame_type_valid(self):
        for _ in range(20):
            ft = json.loads(jutsu.generate('can_frame'))['frame_type']
            assert ft in ('standard', 'extended'), f"Invalid frame_type: {ft}"

    def test_standard_id_range(self):
        """11-bit standard CAN ID: 0-2047."""
        for _ in range(50):
            d = json.loads(jutsu.generate('can_frame'))
            if d['frame_type'] == 'standard':
                assert 0 <= d['can_id_int'] <= 2047, \
                    f"Standard ID out of 11-bit range: {d['can_id_int']}"

    def test_extended_id_appears(self):
        """Extended frames must appear within 200 tries (~30% probability)."""
        found = any(
            json.loads(jutsu.generate('can_frame'))['frame_type'] == 'extended'
            for _ in range(200)
        )
        assert found, "No extended frame generated in 200 tries"

    def test_extended_id_range(self):
        """29-bit extended CAN ID: 0-536870911."""
        for _ in range(200):
            d = json.loads(jutsu.generate('can_frame'))
            if d['frame_type'] == 'extended':
                assert 0 <= d['can_id_int'] <= 536870911
                return
        pytest.skip("No extended frame in 200 tries")

    def test_dlc_range(self):
        for _ in range(20):
            dlc = json.loads(jutsu.generate('can_frame'))['dlc']
            assert 0 <= dlc <= 8, f"DLC out of range: {dlc}"

    def test_data_length_matches_dlc(self):
        for _ in range(20):
            d = json.loads(jutsu.generate('can_frame'))
            assert len(d['data']) == d['dlc'], \
                f"data length {len(d['data'])} != dlc {d['dlc']}"

    def test_data_bytes_in_range(self):
        for _ in range(10):
            d = json.loads(jutsu.generate('can_frame'))
            for b in d['data']:
                assert 0 <= b <= 255, f"data byte {b} out of range"

    def test_data_hex_length_matches_dlc(self):
        """data_hex must have exactly 2 hex chars per byte, no spaces."""
        for _ in range(20):
            d = json.loads(jutsu.generate('can_frame'))
            assert len(d['data_hex']) == d['dlc'] * 2, \
                f"data_hex length {len(d['data_hex'])} != dlc*2={d['dlc']*2}"

    def test_crc15_range(self):
        """CRC-15 must fit in 15 bits: [0, 32767]."""
        for _ in range(20):
            crc = json.loads(jutsu.generate('can_frame'))['crc15']
            assert 0 <= crc <= 32767, f"CRC-15 out of 15-bit range: {crc}"

    def test_crc15_verified(self):
        """CRC-15 recomputed from frame fields must match the returned value."""
        for _ in range(10):
            d = json.loads(jutsu.generate('can_frame'))
            expected = _crc15_verify(
                d['can_id_int'], d['dlc'], d['data'],
                d['frame_type'] == 'extended'
            )
            assert d['crc15'] == expected, \
                f"CRC-15 mismatch: got {d['crc15']}, expected {expected}"

    def test_crc15_hex_consistent(self):
        """crc15_hex must be the hex string of crc15 int."""
        for _ in range(10):
            d = json.loads(jutsu.generate('can_frame'))
            assert int(d['crc15_hex'], 16) == d['crc15'], \
                f"crc15_hex '{d['crc15_hex']}' != crc15 {d['crc15']}"

    def test_socketcan_no_0x_prefix(self):
        """SocketCAN format uses bare hex, not '0x...'."""
        for _ in range(10):
            sc = json.loads(jutsu.generate('can_frame'))['socketcan']
            assert not sc.startswith('0x'), f"socketcan should not have 0x prefix: {sc}"

    def test_socketcan_hash_separator(self):
        for _ in range(10):
            sc = json.loads(jutsu.generate('can_frame'))['socketcan']
            assert '#' in sc, f"socketcan missing '#': {sc}"
            parts = sc.split('#')
            assert len(parts) == 2

    def test_socketcan_id_is_hex(self):
        for _ in range(10):
            sc = json.loads(jutsu.generate('can_frame'))['socketcan']
            id_part = sc.split('#')[0]
            assert all(c in '0123456789ABCDEFabcdef' for c in id_part), \
                f"socketcan ID not hex: {id_part}"

    def test_socketcan_data_matches_data_hex(self):
        for _ in range(10):
            d = json.loads(jutsu.generate('can_frame'))
            data_part = d['socketcan'].split('#')[1]
            assert data_part.upper() == d['data_hex'].upper(), \
                f"socketcan data '{data_part}' != data_hex '{d['data_hex']}'"

    def test_bulk_variety(self):
        ids = {json.loads(r)['can_id_int'] for r in jutsu.bulk('can_frame', 5)}
        assert len(ids) > 1


# ── obd2_response ─────────────────────────────────────────────────────────────

class TestObd2Response:

    def test_no_error(self):
        assert not jutsu.generate('obd2_response').startswith('ERROR')

    def test_returns_string(self):
        assert isinstance(jutsu.generate('obd2_response'), str)

    def test_is_valid_json(self):
        json.loads(jutsu.generate('obd2_response'))

    def test_is_dict(self):
        assert isinstance(json.loads(jutsu.generate('obd2_response')), dict)

    def test_has_required_fields(self):
        d = json.loads(jutsu.generate('obd2_response'))
        for f in ('ecu_id', 'mode', 'pids', 'dtcs', 'dtc_count',
                  'rpm', 'speed_kmh', 'coolant_temp_c',
                  'throttle_pct', 'engine_load_pct', 'fuel_level_pct'):
            assert f in d, f"Missing field: {f}"

    def test_ecu_id_is_7e8(self):
        for _ in range(10):
            assert json.loads(jutsu.generate('obd2_response'))['ecu_id'] == '7E8'

    def test_mode_is_01(self):
        for _ in range(10):
            assert json.loads(jutsu.generate('obd2_response'))['mode'] == '01'

    def test_rpm_in_range(self):
        """OBD-II PID 0x0C max is 16383.75 RPM."""
        for _ in range(20):
            rpm = json.loads(jutsu.generate('obd2_response'))['rpm']
            assert 0 <= rpm <= 16383.75, f"RPM out of range: {rpm}"

    def test_speed_in_range(self):
        """OBD-II PID 0x0D max is 255 km/h."""
        for _ in range(20):
            spd = json.loads(jutsu.generate('obd2_response'))['speed_kmh']
            assert 0 <= spd <= 255, f"Speed out of range: {spd}"

    def test_coolant_temp_in_range(self):
        """OBD-II PID 0x05: raw byte A → value = A-40, range -40 to 215."""
        for _ in range(20):
            t = json.loads(jutsu.generate('obd2_response'))['coolant_temp_c']
            assert -40 <= t <= 215, f"Coolant temp out of range: {t}"

    def test_throttle_pct_in_range(self):
        for _ in range(20):
            v = json.loads(jutsu.generate('obd2_response'))['throttle_pct']
            assert 0 <= v <= 100, f"Throttle out of range: {v}"

    def test_engine_load_pct_in_range(self):
        for _ in range(20):
            v = json.loads(jutsu.generate('obd2_response'))['engine_load_pct']
            assert 0 <= v <= 100, f"Engine load out of range: {v}"

    def test_fuel_level_pct_in_range(self):
        for _ in range(20):
            v = json.loads(jutsu.generate('obd2_response'))['fuel_level_pct']
            assert 0 <= v <= 100, f"Fuel level out of range: {v}"

    def test_pids_is_nonempty_list(self):
        for _ in range(10):
            pids = json.loads(jutsu.generate('obd2_response'))['pids']
            assert isinstance(pids, list) and len(pids) >= 1

    def test_pid_required_fields(self):
        for _ in range(5):
            pids = json.loads(jutsu.generate('obd2_response'))['pids']
            for pid in pids:
                for f in ('pid', 'name', 'value', 'unit',
                          'raw_hex', 'can_id_int', 'can_dlc',
                          'can_data', 'crc15', 'socketcan'):
                    assert f in pid, f"pid missing field: {f}"

    def test_pid_can_dlc_is_8(self):
        """OBD-II always uses DLC=8 (padded to 8 bytes)."""
        for _ in range(10):
            pids = json.loads(jutsu.generate('obd2_response'))['pids']
            for pid in pids:
                assert pid['can_dlc'] == 8

    def test_pid_can_data_length_8(self):
        for _ in range(10):
            pids = json.loads(jutsu.generate('obd2_response'))['pids']
            for pid in pids:
                assert len(pid['can_data']) == 8

    def test_pid_crc15_range(self):
        for _ in range(10):
            pids = json.loads(jutsu.generate('obd2_response'))['pids']
            for pid in pids:
                assert 0 <= pid['crc15'] <= 32767, \
                    f"PID {pid['pid']} crc15={pid['crc15']} out of range"

    def test_pid_crc15_verified(self):
        """Each PID's CRC-15 must be independently verifiable from its CAN data."""
        for _ in range(5):
            pids = json.loads(jutsu.generate('obd2_response'))['pids']
            for pid in pids:
                expected = _crc15_verify(
                    pid['can_id_int'], pid['can_dlc'],
                    pid['can_data'], False  # OBD-II uses standard 11-bit frames
                )
                assert pid['crc15'] == expected, \
                    f"PID {pid['pid']} CRC-15: got {pid['crc15']}, expected {expected}"

    def test_pid_response_byte_is_0x41(self):
        """OBD-II positive response to mode 01 = 0x41 (0x40 | 0x01)."""
        for _ in range(10):
            pids = json.loads(jutsu.generate('obd2_response'))['pids']
            for pid in pids:
                assert pid['can_data'][1] == 0x41, \
                    f"PID {pid['pid']} response byte != 0x41"

    def test_dtcs_is_list(self):
        for _ in range(10):
            assert isinstance(json.loads(jutsu.generate('obd2_response'))['dtcs'], list)

    def test_dtc_count_matches_dtcs(self):
        for _ in range(10):
            d = json.loads(jutsu.generate('obd2_response'))
            assert d['dtc_count'] == len(d['dtcs'])

    def test_dtc_format(self):
        """DTCs must match [PCBU][0-3][0-9A-F]{3}."""
        for _ in range(50):
            dtcs = json.loads(jutsu.generate('obd2_response'))['dtcs']
            for dtc in dtcs:
                assert _DTC_RE.match(dtc), \
                    f"DTC '{dtc}' doesn't match [PCBU][0-3][0-9A-F]{{3}}"

    def test_bulk_variety(self):
        speeds = {json.loads(r)['speed_kmh'] for r in jutsu.bulk('obd2_response', 5)}
        assert len(speeds) > 1
