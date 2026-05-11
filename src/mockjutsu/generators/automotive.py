"""
mock-jutsu — Automotive OBD-II and CAN Bus Generator
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)

Supported types:
  can_frame     — Raw CAN Bus frame (ISO 11898-1).
                  Standard (11-bit) or Extended (29-bit) arbitration ID.
                  CRC-15 computed with polynomial 0xC599 over SOF+ID+Control+Data.
                  DLC: 0-8 bytes. Output includes SocketCAN notation (HEX_ID#HEXDATA).

  obd2_response — OBD-II diagnostic snapshot (SAE J1979 over ISO 15765-4 CAN).
                  Mode 01: Live PIDs (RPM, Speed, Coolant Temp, Throttle,
                           Engine Load, Fuel Level).
                  Each PID response is a valid CAN frame (ID=0x7E8) with CRC-15.
                  Optional DTCs (30% probability), format: [PCBU][0-3][0-9A-F]{3}.
                  RPM formula: (A*256+B)/4.  Coolant: A-40.  Pct: A*100/255.

Zero external dependencies: json, random (stdlib only).
"""

import json
import random

# ── Constants ─────────────────────────────────────────────────────────────────

_CAN_CRC_POLY    = 0xC599   # ISO 11898-1 CRC-15 polynomial
_OBD2_ECU_ID     = 0x7E8    # Standard ECU response CAN ID
_OBD2_ECU_ID_STR = '7E8'
_OBD2_MODE_01    = 0x41     # Positive response to Mode 01 (0x40 | 0x01)

_COMMON_DTCS = [
    'P0300', 'P0301', 'P0302', 'P0303', 'P0304',
    'P0171', 'P0174', 'P0128', 'P0420', 'P0430',
    'P0401', 'P0442', 'P0455', 'P0325', 'P0340',
    'C0001', 'C0031', 'C0034', 'C0040', 'C0110',
    'B1234', 'B1341', 'B2100',
    'U0100', 'U0101', 'U0121', 'U0155',
]


# ── CRC-15 ────────────────────────────────────────────────────────────────────

def _can_crc15(can_id: int, dlc: int, data: bytes, extended: bool) -> int:
    """
    CAN CRC-15 (ISO 11898-1, polynomial 0xC599).
    Computed over: SOF + Arbitration field + Control field + Data field.
    Standard frame: SOF(1) + ID(11) + RTR(1) + IDE(1) + r0(1) + DLC(4) + Data.
    Extended frame: SOF(1) + ID(29) + SRR(1) + IDE(1) + RTR(1) + r1(1) + r0(1) + DLC(4) + Data.
    """
    bits = [0]  # SOF — dominant
    if not extended:
        for i in range(10, -1, -1):
            bits.append((can_id >> i) & 1)
        bits += [0, 0, 0]          # RTR, IDE, r0
    else:
        for i in range(28, -1, -1):
            bits.append((can_id >> i) & 1)
        bits += [1, 1, 0, 0, 0]    # SRR, IDE, RTR, r1, r0
    for i in range(3, -1, -1):
        bits.append((dlc >> i) & 1)
    for byte in data:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    crc = 0
    for bit in bits:
        if ((crc >> 14) ^ bit) & 1:
            crc = ((crc << 1) ^ _CAN_CRC_POLY) & 0x7FFF
        else:
            crc = (crc << 1) & 0x7FFF
    return crc


# ── CAN Frame ─────────────────────────────────────────────────────────────────

def generate_can_frame() -> str:
    """Raw CAN Bus frame with verified CRC-15 (ISO 11898-1)."""
    extended = random.random() < 0.3
    can_id   = random.randint(0, 536870911 if extended else 2047)
    dlc      = random.randint(0, 8)
    data     = [random.randint(0, 255) for _ in range(dlc)]
    crc15    = _can_crc15(can_id, dlc, bytes(data), extended)
    data_hex = ''.join(f'{b:02X}' for b in data)
    id_str   = f'{can_id:08X}' if extended else f'{can_id:03X}'

    return json.dumps({
        'frame_type': 'extended' if extended else 'standard',
        'can_id':     f'0x{id_str}',
        'can_id_int': can_id,
        'dlc':        dlc,
        'data':       data,
        'data_hex':   data_hex,
        'crc15':      crc15,
        'crc15_hex':  f'{crc15:04X}',
        'socketcan':  f'{id_str}#{data_hex}',
    })


# ── OBD-II ───────────────────────────────────────────────────────────────────

def _obd2_pid_entry(pid_byte: int, name: str, unit: str,
                    value, raw_bytes: list) -> dict:
    """Build one OBD-II PID response as a CAN frame dict (ECU ID = 0x7E8)."""
    can_data = [0x00] * 8
    can_data[0] = 1 + 1 + len(raw_bytes)   # length: mode_byte + pid_byte + data
    can_data[1] = _OBD2_MODE_01             # 0x41 = positive response to Mode 01
    can_data[2] = pid_byte
    for i, b in enumerate(raw_bytes):
        can_data[3 + i] = b & 0xFF

    crc15    = _can_crc15(_OBD2_ECU_ID, 8, bytes(can_data), False)
    data_hex = ''.join(f'{b:02X}' for b in can_data)

    return {
        'pid':        f'{pid_byte:02X}',
        'name':       name,
        'value':      value,
        'unit':       unit,
        'raw_hex':    ''.join(f'{b:02X}' for b in raw_bytes),
        'can_id_int': _OBD2_ECU_ID,
        'can_dlc':    8,
        'can_data':   can_data,
        'crc15':      crc15,
        'socketcan':  f'{_OBD2_ECU_ID_STR}#{data_hex}',
    }


def generate_obd2_response() -> str:
    """
    OBD-II live-data snapshot (Mode 01) over ISO 15765-4 CAN.
    Each PID response is a valid 8-byte CAN frame (ID=0x7E8) with CRC-15.
    """
    # ── Sensor values ────────────────────────────────────────────────────────
    rpm          = round(random.uniform(600, 7000), 2)
    speed        = random.randint(0, 250)
    coolant      = random.randint(-10, 110)
    throttle     = round(random.uniform(0, 100), 1)
    engine_load  = round(random.uniform(10, 90), 1)
    fuel_level   = round(random.uniform(5, 95), 1)

    # ── Raw byte encoding (SAE J1979) ────────────────────────────────────────
    rpm_raw  = int(rpm * 4)                              # PID 0x0C: (A*256+B)/4
    rpm_a    = (rpm_raw >> 8) & 0xFF
    rpm_b    = rpm_raw & 0xFF
    thr_raw  = int(throttle * 255 / 100) & 0xFF          # PID 0x11: A*100/255
    load_raw = int(engine_load * 255 / 100) & 0xFF       # PID 0x04: A*100/255
    fuel_raw = int(fuel_level * 255 / 100) & 0xFF        # PID 0x2F: A*100/255

    pids = [
        _obd2_pid_entry(0x0C, 'Engine RPM',       'rpm',   rpm,         [rpm_a, rpm_b]),
        _obd2_pid_entry(0x0D, 'Vehicle Speed',    'km/h',  speed,       [speed]),
        _obd2_pid_entry(0x05, 'Coolant Temp',     '°C',  coolant,  [coolant + 40]),
        _obd2_pid_entry(0x11, 'Throttle Pos',     '%',     throttle,    [thr_raw]),
        _obd2_pid_entry(0x04, 'Engine Load',      '%',     engine_load, [load_raw]),
        _obd2_pid_entry(0x2F, 'Fuel Level',       '%',     fuel_level,  [fuel_raw]),
    ]

    # ── DTCs (30% probability) ───────────────────────────────────────────────
    dtcs = []
    if random.random() < 0.3:
        n    = random.randint(1, 3)
        dtcs = random.sample(_COMMON_DTCS, min(n, len(_COMMON_DTCS)))

    return json.dumps({
        'ecu_id':          _OBD2_ECU_ID_STR,
        'mode':            '01',
        'pids':            pids,
        'dtcs':            dtcs,
        'dtc_count':       len(dtcs),
        'rpm':             rpm,
        'speed_kmh':       speed,
        'coolant_temp_c':  coolant,
        'throttle_pct':    throttle,
        'engine_load_pct': engine_load,
        'fuel_level_pct':  fuel_level,
    }, ensure_ascii=False)


# ── Generator class ────────────────────────────────────────────────────────────

class AutomotiveGenerator:
    """OBD-II and CAN Bus frame generator."""

    def generate(self, data_type: str, **kwargs) -> str:
        if data_type == 'can_frame':
            return generate_can_frame()
        if data_type == 'obd2_response':
            return generate_obd2_response()
        return f"ERROR: Unknown type '{data_type}'"
