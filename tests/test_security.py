"""Tests for God Mode #7 — Siber Güvenlik Mocks (CEF log, X.509 cert, pcap hex)."""
import json
import re
import pytest
from mockjutsu.core import MockJutsuCore

jutsu = MockJutsuCore()


class TestCEFLog:
    def test_returns_string(self):
        assert isinstance(jutsu.generate('cef_log'), str)

    def test_starts_with_cef_header(self):
        assert jutsu.generate('cef_log').startswith('CEF:0|')

    def test_has_eight_pipe_fields(self):
        # CEF:0|Vendor|Product|Version|SigID|Name|Severity|Extension
        parts = jutsu.generate('cef_log').split('|')
        assert len(parts) >= 8

    def test_severity_in_range(self):
        for _ in range(30):
            severity = int(jutsu.generate('cef_log').split('|')[6])
            assert 0 <= severity <= 10

    def test_extension_has_src_and_dst(self):
        ext = jutsu.generate('cef_log').split('|', 7)[7]
        assert 'src=' in ext
        assert 'dst=' in ext

    def test_src_ip_is_valid(self):
        ext = jutsu.generate('cef_log').split('|', 7)[7]
        match = re.search(r'src=(\d+\.\d+\.\d+\.\d+)', ext)
        assert match
        assert all(0 <= int(o) <= 255 for o in match.group(1).split('.'))

    def test_no_newlines(self):
        assert '\n' not in jutsu.generate('cef_log')

    def test_bulk_produces_variety(self):
        logs = jutsu.bulk('cef_log', 20)
        assert len(set(logs)) > 1


class TestX509Cert:
    def _cert(self):
        return json.loads(jutsu.generate('x509_cert'))

    def test_returns_valid_json(self):
        raw = jutsu.generate('x509_cert')
        assert isinstance(raw, str)
        json.loads(raw)

    def test_required_fields_present(self):
        cert = self._cert()
        for key in ('version', 'serial', 'algorithm', 'key_size',
                    'subject', 'issuer', 'not_before', 'not_after',
                    'san', 'fingerprint'):
            assert key in cert, f"missing field: {key}"

    def test_version_is_3(self):
        assert self._cert()['version'] == 3

    def test_key_size_valid(self):
        assert self._cert()['key_size'] in (2048, 4096)

    def test_algorithm_valid(self):
        assert self._cert()['algorithm'] in (
            'sha256WithRSAEncryption', 'ecdsa-with-SHA256'
        )

    def test_fingerprint_sha256_format(self):
        fp = self._cert()['fingerprint']
        assert re.match(r'^[0-9A-F]{2}(:[0-9A-F]{2}){31}$', fp), f"bad fp: {fp}"

    def test_serial_is_valid_hex(self):
        int(self._cert()['serial'], 16)

    def test_not_after_later_than_not_before(self):
        cert = self._cert()
        assert cert['not_after'] > cert['not_before']

    def test_subject_contains_cn(self):
        assert 'CN=' in self._cert()['subject']

    def test_issuer_contains_cn(self):
        assert 'CN=' in self._cert()['issuer']

    def test_san_is_list(self):
        assert isinstance(self._cert()['san'], list)
        assert len(self._cert()['san']) >= 1

    def test_bulk_serials_unique(self):
        serials = [json.loads(c)['serial'] for c in jutsu.bulk('x509_cert', 10)]
        assert len(set(serials)) == 10


class TestPcapHex:
    def _clean(self):
        return jutsu.generate('pcap_hex').replace(' ', '').replace('\n', '')

    def test_returns_string(self):
        assert isinstance(jutsu.generate('pcap_hex'), str)

    def test_valid_hex(self):
        bytes.fromhex(self._clean())

    def test_minimum_frame_length(self):
        # Ethernet(14) + IP(20) + TCP(20) = 54 bytes min → 108 hex chars
        assert len(self._clean()) >= 108

    def test_ipv4_ethertype(self):
        # Bytes 12-13 of Ethernet frame = 0x0800
        assert self._clean()[24:28] == '0800'

    def test_ip_version_4(self):
        # First nibble of IP header (frame byte 14) = 4
        assert int(self._clean()[28], 16) == 4

    def test_hex_line_format(self):
        pcap = jutsu.generate('pcap_hex')
        for line in pcap.strip().split('\n'):
            for pair in line.strip().split(' '):
                assert len(pair) == 2
                int(pair, 16)

    def test_bulk_produces_variety(self):
        dumps = jutsu.bulk('pcap_hex', 10)
        assert len(set(dumps)) > 1
