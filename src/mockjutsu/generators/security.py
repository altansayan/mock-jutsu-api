"""
mock-jutsu — Security Generator (God Mode #7)
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)

CEF log (ArcSight/SIEM format), X.509 certificate fields, pcap hex dump.
All output is algorithmically generated — not cryptographically valid.
"""

import json
import random
import secrets
import string
from datetime import datetime, timezone, timedelta

_PWD_SPECIAL = '!@#$%^&*()-_=+[]{}|;:,.<>?'
_BCRYPT_ALPHABET = './ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'


_CEF_DEVICES = [
    ("Cisco", "ASA", "9.16"),
    ("Palo Alto Networks", "PAN-OS", "10.2"),
    ("Fortinet", "FortiGate", "7.4"),
    ("Check Point", "Firewall-1", "R81.20"),
    ("CrowdStrike", "Falcon", "6.58"),
    ("IBM", "QRadar SIEM", "7.5"),
    ("Splunk", "Enterprise Security", "7.3"),
    ("Darktrace", "Enterprise Immune System", "5.2"),
]

_CEF_EVENTS = [
    ("100001", "Outbound Connection Allowed",  3,  "proto=TCP act=allowed"),
    ("100002", "Inbound Connection Blocked",   5,  "proto=TCP act=blocked"),
    ("200001", "Authentication Success",       2,  "outcome=success"),
    ("200002", "Authentication Failure",       7,  "outcome=failure"),
    ("300001", "Malware Detected",             9,  "fname=payload.exe cs1=Trojan.GenericKD"),
    ("400001", "DDoS Attack Detected",         10, "cnt=50000 proto=UDP"),
    ("500001", "Data Exfiltration Attempt",    10, "bytesOut=10485760 proto=FTP"),
    ("600001", "Port Scan Detected",           6,  "proto=TCP cnt=1024"),
    ("700001", "SQL Injection Attempt",        8,  "request=/api/login cs1=blind"),
    ("800001", "Brute Force Attack",           7,  "attempt=100 outcome=failure"),
    ("900001", "Privilege Escalation",         8,  "suser=guest duser=root"),
    ("110001", "Lateral Movement",             7,  "proto=SMB cs1=PsExec"),
]

_COMMON_NAMES = [
    "api.example.com", "secure.corp.net", "auth.internal.io",
    "app.enterprise.org", "gateway.prod.local", "portal.company.com",
    "vpn.office.net", "sso.enterprise.io",
]

_CA_ISSUERS = [
    "CN=DigiCert TLS RSA SHA256 2020 CA1, O=DigiCert Inc, C=US",
    "CN=Let's Encrypt Authority X3, O=Let's Encrypt, C=US",
    "CN=Sectigo RSA Domain Validation Secure Server CA, O=Sectigo Limited, C=GB",
    "CN=GlobalSign RSA OV SSL CA 2018, O=GlobalSign nv-sa, C=BE",
    "CN=Amazon RSA 2048 M02, O=Amazon, C=US",
    "CN=Microsoft Azure TLS Issuing CA 01, O=Microsoft Corporation, C=US",
]

_ORGANIZATIONS = [
    "Acme Corp", "TechCorp Inc", "SecureBank Ltd", "GlobalFinance AG",
    "Enterprise Solutions LLC", "DataSystems GmbH", "InfoSec Corp",
]

_ALGORITHMS  = ["sha256WithRSAEncryption", "ecdsa-with-SHA256"]
_KEY_SIZES   = [2048, 4096]
_COUNTRIES   = ["US", "GB", "DE", "TR", "NL", "FR", "JP", "SG"]

_PCAP_PAYLOADS = [
    b'GET / HTTP/1.1\r\nHost: api.example.com\r\nUser-Agent: Mozilla/5.0\r\n\r\n',
    b'POST /api/v1/auth HTTP/1.1\r\nContent-Type: application/json\r\nContent-Length: 42\r\n\r\n',
    b'\x16\x03\x01\x00\xf1\x01\x00\x00\xed\x03\x03',
    b'SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.6\r\n',
    b'\x00\x00\x00\x05\x01\x00\x00\x00\x00',
]

_COMMON_PORTS = [22, 80, 443, 8080, 8443, 3306, 5432, 6379, 3389, 5900]


def _rip():
    return bytes([random.randint(1, 254), random.randint(0, 254),
                  random.randint(0, 254), random.randint(1, 254)])


def generate_cef_log():
    vendor, product, version      = random.choice(_CEF_DEVICES)
    sig_id, name, severity, b_ext = random.choice(_CEF_EVENTS)
    src_ip   = '.'.join(str(b) for b in _rip())
    dst_ip   = '.'.join(str(b) for b in _rip())
    src_port = random.randint(1024, 65535)
    dst_port = random.choice(_COMMON_PORTS)
    user     = f"user{random.randint(100, 9999)}"
    ext      = f"src={src_ip} dst={dst_ip} spt={src_port} dpt={dst_port} suser={user} {b_ext}"
    return f"CEF:0|{vendor}|{product}|{version}|{sig_id}|{name}|{severity}|{ext}"


def generate_x509_cert():
    cn      = random.choice(_COMMON_NAMES)
    org     = random.choice(_ORGANIZATIONS)
    country = random.choice(_COUNTRIES)
    subject = f"CN={cn}, O={org}, OU=IT Security, C={country}"
    issuer  = random.choice(_CA_ISSUERS)
    serial  = secrets.token_hex(16)

    now        = datetime.now(timezone.utc)
    not_before = now - timedelta(days=random.randint(30, 365))
    not_after  = not_before + timedelta(days=random.choice([365, 397, 730]))

    fp_bytes    = secrets.token_bytes(32)
    fingerprint = ':'.join(f'{b:02X}' for b in fp_bytes)

    san_base = cn.lstrip('*.')
    sans     = [cn, f"www.{san_base}"]

    cert = {
        "version":    3,
        "serial":     serial,
        "algorithm":  random.choice(_ALGORITHMS),
        "key_size":   random.choice(_KEY_SIZES),
        "subject":    subject,
        "issuer":     issuer,
        "not_before": not_before.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "not_after":  not_after.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "san":        sans,
        "fingerprint": fingerprint,
    }
    return json.dumps(cert, ensure_ascii=False)


def generate_pcap_hex():
    # PCAP global header (libpcap format, RFC — tcpdump.org/linktypes.html)
    # magic=0xa1b2c3d4, version 2.4, thiszone=0, sigfigs=0, snaplen=65535, network=1 (ETHERNET)
    global_header = (
        b'\xd4\xc3\xb2\xa1' +   # magic (little-endian)
        b'\x02\x00' +            # version major = 2
        b'\x04\x00' +            # version minor = 4
        b'\x00\x00\x00\x00' +   # thiszone
        b'\x00\x00\x00\x00' +   # sigfigs
        b'\xff\xff\x00\x00' +   # snaplen = 65535
        b'\x01\x00\x00\x00'     # network = LINKTYPE_ETHERNET
    )

    dst_mac   = bytes(random.randint(0, 255) for _ in range(6))
    src_mac   = bytes(random.randint(0, 255) for _ in range(6))
    ethertype = b'\x08\x00'   # IPv4

    src_ip   = _rip()
    dst_ip   = _rip()
    src_port = random.randint(1024, 65535)
    dst_port = random.choice(_COMMON_PORTS)
    payload  = random.choice(_PCAP_PAYLOADS)

    tcp_header = (
        src_port.to_bytes(2, 'big') +
        dst_port.to_bytes(2, 'big') +
        secrets.randbits(32).to_bytes(4, 'big') +   # seq
        secrets.randbits(32).to_bytes(4, 'big') +   # ack
        b'\x50\x18' +                                # offset=5, PSH+ACK
        b'\xff\xff' +                                # window
        b'\x00\x00' +                                # checksum (mock)
        b'\x00\x00'                                  # urgent
    )

    total_len = 20 + len(tcp_header) + len(payload)
    ip_header = (
        b'\x45\x00' +
        total_len.to_bytes(2, 'big') +
        secrets.randbits(16).to_bytes(2, 'big') +   # ID
        b'\x40\x00' +                                # Don't Fragment
        b'\x40\x06\x00\x00' +                       # TTL=64, proto=TCP, chksum=0
        src_ip + dst_ip
    )

    frame = dst_mac + src_mac + ethertype + ip_header + tcp_header + payload
    frame_len = len(frame)

    import time as _time
    ts = int(_time.time())
    # Packet record header: ts_sec, ts_usec, incl_len, orig_len (all LE uint32)
    pkt_header = (
        ts.to_bytes(4, 'little') +
        b'\x00\x00\x00\x00' +
        frame_len.to_bytes(4, 'little') +
        frame_len.to_bytes(4, 'little')
    )

    raw = global_header + pkt_header + frame
    pairs = [f'{b:02x}' for b in raw]
    lines = [' '.join(pairs[i:i+16]) for i in range(0, len(pairs), 16)]
    return '\n'.join(lines)


def generate_password() -> str:
    """Strong random password with guaranteed complexity requirements."""
    length = random.randint(12, 20)
    # Guarantee at least one of each required character class
    mandatory = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
        secrets.choice(_PWD_SPECIAL),
    ]
    pool = string.ascii_letters + string.digits + _PWD_SPECIAL
    rest = [secrets.choice(pool) for _ in range(length - 4)]
    chars = mandatory + rest
    random.shuffle(chars)
    return ''.join(chars)


def generate_password_hash() -> str:
    """bcrypt-format password hash: $2b$<cost>$<22-char salt><31-char hash>."""
    cost = random.randint(10, 14)
    body = ''.join(secrets.choice(_BCRYPT_ALPHABET) for _ in range(53))
    return f"$2b${cost:02d}${body}"


def generate_cve_id() -> str:
    """CVE identifier: CVE-YYYY-NNNNN (year 2000–2025, number 1000–99999)."""
    year = random.randint(2000, 2025)
    num  = random.randint(1000, 99999)
    return f"CVE-{year}-{num}"


class SecurityGenerator:
    def generate(self, data_type, **_kwargs):
        if data_type == 'cef_log':
            return generate_cef_log()
        if data_type == 'x509_cert':
            return generate_x509_cert()
        if data_type == 'pcap_hex':
            return generate_pcap_hex()
        if data_type == 'password':
            return generate_password()
        if data_type == 'password_hash':
            return generate_password_hash()
        if data_type == 'cve_id':
            return generate_cve_id()
        return f"ERROR: Unknown security type '{data_type}'"
