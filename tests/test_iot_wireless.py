"""
Tests for God Mode #10 — IoT & Smart Device Mocks
Types: mqtt_payload, lora_packet

Standards referenced:
  MQTT 3.1.1 / 5.0  — payload is application-defined JSON; common IoT sensor schema
  LoRaWAN 1.0.x     — MAC frame: MHDR(1) + FHDR(7) + FPort(1) + FRMPayload(N) + MIC(4)
                       MHDR=0x40 (Unconfirmed Data Up), MIC is simulated (not AES-CMAC)
"""

import json
import re
import pytest
from mockjutsu.core import MockJutsuCore

jutsu = MockJutsuCore()


# ── MQTT Payload ──────────────────────────────────────────────────────────────

class TestMqttPayload:
    def test_valid_json(self):
        val = jutsu.generate('mqtt_payload')
        parsed = json.loads(val)
        assert isinstance(parsed, dict)

    def test_required_fields(self):
        val = json.loads(jutsu.generate('mqtt_payload'))
        assert 'device_id' in val
        assert 'timestamp' in val
        assert 'sensor_type' in val
        assert 'readings' in val

    def test_device_id_format(self):
        val = json.loads(jutsu.generate('mqtt_payload'))
        assert re.match(r'^[a-f0-9\-]{8,}$', val['device_id']), (
            f"device_id format unexpected: {val['device_id']!r}"
        )

    def test_timestamp_iso8601(self):
        val = json.loads(jutsu.generate('mqtt_payload'))
        ts = val['timestamp']
        assert re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', ts), (
            f"timestamp not ISO 8601: {ts!r}"
        )

    def test_sensor_type_known(self):
        known = {'temperature', 'humidity', 'pressure', 'motion', 'light', 'co2', 'voltage'}
        for _ in range(20):
            val = json.loads(jutsu.generate('mqtt_payload'))
            assert val['sensor_type'] in known, f"Unknown sensor type: {val['sensor_type']!r}"

    def test_readings_is_dict(self):
        val = json.loads(jutsu.generate('mqtt_payload'))
        assert isinstance(val['readings'], dict)
        assert len(val['readings']) >= 1

    def test_rssi_range(self):
        for _ in range(20):
            val = json.loads(jutsu.generate('mqtt_payload'))
            if 'rssi' in val:
                assert -130 <= val['rssi'] <= -20, f"RSSI out of range: {val['rssi']}"

    def test_battery_range(self):
        for _ in range(20):
            val = json.loads(jutsu.generate('mqtt_payload'))
            if 'battery_pct' in val:
                assert 0 <= val['battery_pct'] <= 100

    def test_bulk_unique(self):
        results = jutsu.bulk('mqtt_payload', 20)
        assert len(set(results)) > 1

    def test_no_error_prefix(self):
        val = jutsu.generate('mqtt_payload')
        assert not val.startswith('ERROR')

    def test_temperature_readings_range(self):
        for _ in range(30):
            val = json.loads(jutsu.generate('mqtt_payload'))
            if val['sensor_type'] == 'temperature':
                t = val['readings']['celsius']
                assert -50.0 <= t <= 100.0, f"Temperature out of range: {t}"

    def test_humidity_readings_range(self):
        for _ in range(30):
            val = json.loads(jutsu.generate('mqtt_payload'))
            if val['sensor_type'] == 'humidity':
                h = val['readings']['percent']
                assert 0.0 <= h <= 100.0, f"Humidity out of range: {h}"


# ── LoRaWAN Packet ────────────────────────────────────────────────────────────

class TestLoRaPacket:
    def _parse(self, val: str):
        """Convert hex string (space-separated or plain) to bytes."""
        clean = val.replace(' ', '').replace(':', '')
        return bytes.fromhex(clean)

    def test_valid_hex_string(self):
        val = jutsu.generate('lora_packet')
        clean = val.replace(' ', '').replace(':', '')
        assert re.match(r'^[0-9a-fA-F]+$', clean), f"Not valid hex: {val!r}"

    def test_mhdr_unconfirmed_data_up(self):
        """MHDR byte must be 0x40 = Unconfirmed Data Up, LoRaWAN 1.0."""
        for _ in range(20):
            data = self._parse(jutsu.generate('lora_packet'))
            assert data[0] == 0x40, f"MHDR expected 0x40, got 0x{data[0]:02X}"

    def test_minimum_frame_length(self):
        """Minimum: MHDR(1) + DevAddr(4) + FCtrl(1) + FCnt(2) + FPort(1) + FRMPayload(≥1) + MIC(4) = 14."""
        for _ in range(20):
            data = self._parse(jutsu.generate('lora_packet'))
            assert len(data) >= 14, f"Frame too short: {len(data)} bytes"

    def test_fctrl_byte(self):
        """FCtrl (byte 5) must be 0x00 — no ADR, no ACK, FOptsLen=0."""
        for _ in range(20):
            data = self._parse(jutsu.generate('lora_packet'))
            assert data[5] == 0x00, f"FCtrl expected 0x00, got 0x{data[5]:02X}"

    def test_fport_application_range(self):
        """FPort is at byte index 8: MHDR(1)+DevAddr(4)+FCtrl(1)+FCnt(2) = 8 bytes before FPort."""
        for _ in range(20):
            data = self._parse(jutsu.generate('lora_packet'))
            fport = data[8]
            assert 1 <= fport <= 10, f"FPort out of app range: {fport}"

    def test_mic_4_bytes_at_end(self):
        """Last 4 bytes are the MIC (Message Integrity Code)."""
        for _ in range(20):
            data = self._parse(jutsu.generate('lora_packet'))
            assert len(data) >= 4

    def test_bulk_unique(self):
        results = jutsu.bulk('lora_packet', 20)
        assert len(set(results)) > 1

    def test_no_error_prefix(self):
        val = jutsu.generate('lora_packet')
        assert not val.startswith('ERROR')
