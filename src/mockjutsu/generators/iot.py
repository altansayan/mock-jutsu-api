"""
mock-jutsu — IoT Generator (RFID, NFC, IR)
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)

Entropy strategy:
  - secrets.token_bytes / random.randrange → OS CSPRNG (urandom)
  - random.choice over fixed small pools (tag profiles) is fine —
    the unique identifier parts always come from secrets
"""

import secrets
import random

# ── RFID ─────────────────────────────────────────────────────────────────────

# ISO/IEC 7816-6 IC manufacturer codes (public registry)
_NFC_MFR_BYTES = [
    0x04,  # NXP Semiconductors (MIFARE, NTAG)
    0x02,  # STMicroelectronics
    0x05,  # Atmel / Microchip
    0x07,  # Texas Instruments (ISO 15693)
    0xE0,  # Texas Instruments (EPC Gen2)
    0x15,  # EM Microelectronic-Marin
    0x16,  # Infineon Technologies
    0x68,  # Renesas Technology
]

# (standard, frequency_mhz, memory_bytes)
_RFID_PROFILES = [
    ("ISO 14443-A", 13.56,  144),   # NTAG213
    ("ISO 14443-A", 13.56,  504),   # NTAG215
    ("ISO 14443-A", 13.56,  888),   # NTAG216
    ("ISO 14443-A", 13.56, 1024),   # MIFARE Classic 1K
    ("ISO 14443-A", 13.56, 4096),   # MIFARE Classic 4K
    ("ISO 14443-B", 13.56,  256),   # ISO-B contactless
    ("ISO 15693",   13.56,  256),   # ICODE SLI
    ("ISO 15693",   13.56,  512),   # ICODE SLIX
    ("ISO 18000-6C",  915,   96),   # EPC UHF Gen2 (US/APAC)
    ("ISO 18000-6C",  868,   96),   # EPC UHF Gen2 (EU)
    ("EM4100",       0.125,  40),   # LF 125 kHz read-only
    ("HID Prox",     0.125,  40),   # LF HID access card
    ("HID iCLASS",  13.56, 2048),   # HF HID
]

# GS1 EPC SGTIN-96 partition table → (company_prefix_bits, item_reference_bits)
# company_prefix_bits + item_reference_bits always = 44; total frame = 96 bits.
_EPC_PARTITION = {
    0: (40,  4),
    1: (37,  7),
    2: (34, 10),
    3: (30, 14),
    4: (27, 17),
    5: (24, 20),
    6: (20, 24),
}

# ── NFC ──────────────────────────────────────────────────────────────────────

# (atqa, sak, tag_type, capacity_bytes) — from NXP / NFC Forum datasheets
_NFC_TAG_PROFILES = [
    ("00:44", "00", "NTAG213",            144),
    ("00:44", "00", "NTAG215",            504),
    ("00:44", "00", "NTAG216",            888),
    ("00:04", "08", "MIFARE Classic 1K", 1024),
    ("00:02", "18", "MIFARE Classic 4K", 4096),
    ("03:44", "20", "MIFARE DESFire EV1",8192),
    ("00:44", "20", "MIFARE Plus SL3",   4096),
    ("00:04", "28", "MIFARE Plus SL1",   1024),
    ("03:04", "60", "MIFARE DESFire",    4096),
]

# NFC Forum URI RTD v1.0, Table 3 — prefix code → URI prefix string
_URI_PREFIX_MAP = {
    0x01: "http://www.",
    0x02: "https://www.",
    0x03: "http://",
    0x04: "https://",
    0x05: "tel:",
    0x06: "mailto:",
    0x08: "ftp://ftp.",
    0x09: "ftps://",
    0x0D: "urn:epc:",
}

_URI_HOSTS = [
    "example.com", "api.example.org", "shop.test.io",
    "auth.demo.net", "pay.service.co", "device.iot.local",
    "hub.connect.app", "data.edge.tech", "link.tag.cloud",
    "nfc.reader.dev",
]

# EMVCo AIDs + ISO 7816-5 registered AIDs (public registry)
_EMVCO_AIDS = [
    ("A0000000031010",         "Visa Credit/Debit"),
    ("A0000000032010",         "Visa Electron"),
    ("A0000000033010",         "Visa V Pay"),
    ("A0000000041010",         "Mastercard Credit/Debit"),
    ("A0000000043060",         "Maestro"),
    ("A0000000044010",         "Mastercard Cirrus"),
    ("A0000000025010",         "American Express"),
    ("A0000000651010",         "JCB"),
    ("A0000003241010",         "Discover"),
    ("A000000333010101",       "UnionPay Credit"),
    ("315041592E5359532E4444463031", "EMV PPSE"),
]

_APDU_GENERAL = [
    ("00", "B0", "00", "00", "READ BINARY"),
    ("00", "CA", "9F", "17", "GET DATA — PIN try counter"),
    ("00", "CA", "9F", "36", "GET DATA — ATC"),
    ("00", "CA", "5F", "50", "GET DATA — issuer URL"),
    ("00", "84", "00", "00", "GET CHALLENGE"),
    ("00", "20", "00", "82", "VERIFY PIN — format 2"),
    ("80", "AE", "80", "00", "GENERATE AC — ARQC"),
]

# ── IR ────────────────────────────────────────────────────────────────────────

# Philips RC-5 system addresses (public standard, Table 1)
_RC5_SYSTEMS = {
     0: "TV",
     1: "TV2 / Monitor",
     2: "Teletext",
     3: "Video",
     5: "VCR",
     6: "VCR2",
    12: "Laser Disc",
    16: "Audio Pre-amp",
    17: "Tuner / Radio",
    18: "Cassette / Tape",
    20: "CD Player",
    21: "Phono",
    26: "Satellite Receiver",
    29: "Lighting",
}

_NEC_CARRIER_HZ  = 38_000
# Pronto frequency word = round(4_145_146 / carrier_hz) for 38 kHz → 109 = 0x006D
_PRONTO_FREQ_WORD = round(4_145_146 / _NEC_CARRIER_HZ)
_RC5_CARRIER_HZ  = 36_000


def _us_to_cycles(us: float, carrier_hz: int) -> int:
    return round(us * carrier_hz / 1_000_000)


class IoTGenerator:
    """RFID, NFC and IR mock data — real protocol algorithms, OS-entropy UIDs."""

    # ── RFID ─────────────────────────────────────────────────────────────────

    @staticmethod
    def generate_rfid_uid() -> str:
        """
        ISO 14443-3A UID — 4-byte (single) or 7-byte (double size).
        7-byte: manufacturer byte (ISO 7816-6) + 6 CSPRNG bytes.
        4-byte: 4 CSPRNG bytes.
        """
        if random.random() < 0.65:          # 7-byte more common in modern tags
            mfr = random.choice(_NFC_MFR_BYTES)
            raw = bytes([mfr]) + secrets.token_bytes(6)
        else:
            raw = secrets.token_bytes(4)
        return ":".join(f"{b:02X}" for b in raw)

    @staticmethod
    def generate_epc() -> str:
        """
        GS1 EPC SGTIN-96 (ISO 18000-6C / EPCglobal Gen2).
        Bit layout (MSB→LSB):
          Header(8=0x30) | Filter(3) | Partition(3) |
          CompanyPrefix(cp_bits) | ItemRef(ir_bits) | Serial(38)
        Total: 96 bits → 24 uppercase hex chars.
        All variable-length fields use random.randrange for full-range entropy.
        """
        header    = 0x30
        filt      = random.randrange(8)
        partition = random.randrange(7)
        cp_bits, ir_bits = _EPC_PARTITION[partition]

        company_prefix = random.randrange(1 << cp_bits)
        item_ref       = random.randrange(1 << ir_bits)
        serial         = random.randrange(1 << 38)

        value  = header
        value  = (value << 3)       | filt
        value  = (value << 3)       | partition
        value  = (value << cp_bits) | company_prefix
        value  = (value << ir_bits) | item_ref
        value  = (value << 38)      | serial
        return f"{value:024X}"

    @staticmethod
    def generate_rfid_tag() -> dict:
        """Profile-matched RFID tag record. EPC field added for UHF Gen2 profiles."""
        std, freq, mem = random.choice(_RFID_PROFILES)
        tag = {
            "uid":           IoTGenerator.generate_rfid_uid(),
            "standard":      std,
            "frequency_mhz": freq,
            "memory_bytes":  mem,
        }
        if "18000" in std:
            tag["epc"] = IoTGenerator.generate_epc()
        return tag

    # ── NFC ──────────────────────────────────────────────────────────────────

    @staticmethod
    def generate_nfc_uid() -> str:
        """
        ISO 14443-3A 7-byte UID.
        Byte 0: IC manufacturer code (ISO/IEC 7816-6).
        Bytes 1–6: 48-bit CSPRNG — collision probability negligible per call.
        """
        mfr = random.choice(_NFC_MFR_BYTES)
        return ":".join(f"{b:02X}" for b in bytes([mfr]) + secrets.token_bytes(6))

    @staticmethod
    def generate_nfc_atqa() -> str:
        """2-byte ATQA (Answer To reQuest type A) from real tag profiles."""
        return random.choice(_NFC_TAG_PROFILES)[0]

    @staticmethod
    def generate_nfc_sak() -> str:
        """1-byte SAK (Select AcKnowledge) from real tag profiles."""
        return random.choice(_NFC_TAG_PROFILES)[1]

    @staticmethod
    def generate_ndef_uri() -> dict:
        """
        NFC Forum NDEF URI Record (RTD v1.0, Section 3.2.2).
        Header 0xD1: MB=1 ME=1 CF=0 SR=1 IL=0 TNF=001 (Well-Known).
        Type 0x55 ('U'), payload = prefix_code(1B) + uri_bytes.
        Path suffix via secrets.token_hex(4) → 32-bit uniqueness per call.
        """
        prefix_code = random.choice(list(_URI_PREFIX_MAP.keys()))
        prefix_str  = _URI_PREFIX_MAP[prefix_code]
        host        = random.choice(_URI_HOSTS)
        path        = "/" + secrets.token_hex(4)
        uri_suffix  = host + path
        payload     = bytes([prefix_code]) + uri_suffix.encode("utf-8")
        raw         = bytes([0xD1, 0x01, len(payload), 0x55]) + payload
        return {
            "raw_hex":     raw.hex().upper(),
            "decoded":     prefix_str + uri_suffix,
            "tnf":         1,
            "type":        "U",
            "prefix_code": f"0x{prefix_code:02X}",
        }

    @staticmethod
    def generate_ndef_text(locale: str = "TR") -> dict:
        """
        NFC Forum NDEF Text Record (RTD v1.0, Section 3.2.1).
        Header 0xD1: same flags as URI. Type 0x54 ('T').
        Status byte: bit7=0 (UTF-8), bits[5:0]=lang_length.
        Payload = status(1B) + lang_code + text_bytes.
        """
        _lang_map = {"TR": "tr", "US": "en", "UK": "en", "DE": "de", "FR": "fr", "RU": "ru"}
        lang  = _lang_map.get(locale.upper(), "en")
        _pool = {
            "tr": ["Merhaba Dünya", "Test etiket verisi", "NFC bağlantı noktası",
                   "Ödeme terminali", "Akıllı etiket içeriği"],
            "en": ["Hello World", "NFC tag payload", "Smart label data",
                   "Payment terminal", "Device handshake token"],
            "de": ["Hallo Welt", "NFC-Etikett Daten", "Smarte Kennzeichnung",
                   "Zahlungsterminal", "Geräteverknüpfung"],
            "fr": ["Bonjour le monde", "Données étiquette NFC", "Terminal de paiement",
                   "Dispositif intelligent", "Jeton d'accès NFC"],
            "ru": ["Привет мир", "Данные метки NFC", "Платёжный терминал",
                   "Смарт-этикетка", "Токен устройства"],
        }
        text    = random.choice(_pool.get(lang, _pool["en"]))
        lang_b  = lang.encode("ascii")
        text_b  = text.encode("utf-8")
        status  = len(lang_b) & 0x3F    # UTF-8 flag (bit7=0) + lang_length
        payload = bytes([status]) + lang_b + text_b
        raw     = bytes([0xD1, 0x01, len(payload), 0x54]) + payload
        return {
            "raw_hex":  raw.hex().upper(),
            "decoded":  text,
            "lang":     lang,
            "tnf":      1,
            "type":     "T",
            "encoding": "UTF-8",
        }

    @staticmethod
    def generate_apdu() -> dict:
        """
        ISO 7816-4 APDU command.
        60 % probability: SELECT AID from EMVCo/ISO 7816-5 registry.
        40 % probability: general instruction (READ BINARY, GET DATA, etc.).
        """
        if random.random() < 0.6:
            aid_hex, aid_name = random.choice(_EMVCO_AIDS)
            aid_bytes = bytes.fromhex(aid_hex)
            lc  = len(aid_bytes)
            hex_str = f"00 A4 04 00 {lc:02X} {' '.join(f'{b:02X}' for b in aid_bytes)} 00"
            return {
                "cla": "00", "ins": "A4", "p1": "04", "p2": "00",
                "lc": f"{lc:02X}", "data": aid_hex, "le": "00",
                "hex": hex_str,
                "description": f"SELECT AID — {aid_name}",
            }
        cla, ins, p1, p2, desc = random.choice(_APDU_GENERAL)
        le = f"{random.randrange(256):02X}"
        return {
            "cla": cla, "ins": ins, "p1": p1, "p2": p2,
            "le": le, "data": None,
            "hex": f"{cla} {ins} {p1} {p2} {le}",
            "description": desc,
        }

    @staticmethod
    def generate_nfc_tag() -> dict:
        """
        Complete NFC tag record — profile-matched ATQA/SAK/type,
        7-byte UID, and an embedded NDEF URI message.
        """
        atqa, sak, tag_type, capacity = random.choice(_NFC_TAG_PROFILES)
        ndef = IoTGenerator.generate_ndef_uri()
        return {
            "uid":            IoTGenerator.generate_nfc_uid(),
            "atqa":           atqa,
            "sak":            sak,
            "type":           tag_type,
            "capacity_bytes": capacity,
            "ndef_message":   ndef["raw_hex"],
            "ndef_decoded":   ndef["decoded"],
        }

    # ── IR ────────────────────────────────────────────────────────────────────

    @staticmethod
    def generate_ir_nec() -> dict:
        """
        NEC IR protocol — 32-bit frame.
        Frame bytes: address | ~address | command | ~command (all 8-bit).
        Invariant: address XOR inv_address == 0xFF (always satisfied by construction).
        Carrier: 38 kHz.
        """
        address  = random.randrange(256)
        command  = random.randrange(256)
        inv_addr = (~address) & 0xFF
        inv_cmd  = (~command) & 0xFF
        return {
            "address":        f"0x{address:02X}",
            "command":        f"0x{command:02X}",
            "inv_address":    f"0x{inv_addr:02X}",
            "inv_command":    f"0x{inv_cmd:02X}",
            "hex":            f"{address:02X}{inv_addr:02X}{command:02X}{inv_cmd:02X}",
            "checksum_valid": True,
            "carrier_hz":     _NEC_CARRIER_HZ,
            "protocol":       "NEC",
        }

    @staticmethod
    def _rc5_frame_bits(system: int, command: int, toggle: int) -> str:
        """
        14-bit RC-5 logical frame (MSB first, before Manchester encoding).
        Bit[13]=Start=1 | Bit[12]=Field=NOT(cmd[6]) | Bit[11]=Toggle |
        Bits[10:6]=System(5b) | Bits[5:0]=Command[5:0].
        Extended RC-5: field bit is the inverted 6th command bit,
        giving command range 0-127 across both field values.
        """
        field = 1 - ((command >> 6) & 1)
        frame = (
            (1      << 13) |
            (field  << 12) |
            (toggle << 11) |
            (system <<  6) |
            (command & 0x3F)
        )
        return f"{frame:014b}"

    @staticmethod
    def generate_ir_rc5() -> dict:
        """
        Philips RC-5 protocol — 14-bit Manchester-encoded frame.
        System addresses 0-31 (named), command 0-127.
        Carrier: 36 kHz.
        """
        system  = random.choice(list(_RC5_SYSTEMS.keys()))
        command = random.randrange(128)
        toggle  = random.randrange(2)
        return {
            "system":      system,
            "system_name": _RC5_SYSTEMS[system],
            "command":     command,
            "toggle":      toggle,
            "frame_bits":  IoTGenerator._rc5_frame_bits(system, command, toggle),
            "carrier_hz":  _RC5_CARRIER_HZ,
            "protocol":    "RC-5",
        }

    @staticmethod
    def _nec_bits_lsb(address: int, command: int):
        """Yield 32 NEC bits in LSB-first-per-byte transmission order."""
        inv_a = (~address) & 0xFF
        inv_c = (~command)  & 0xFF
        for byte in (address, inv_a, command, inv_c):
            for bit in range(8):
                yield (byte >> bit) & 1

    @staticmethod
    def generate_ir_pronto() -> str:
        """
        Pronto Hex (CCF) format — NEC frame.
        Word layout:
          [0] 0x0000  — learned code type
          [1] freq_word = round(4_145_146 / 38000) = 0x006D
          [2] burst pair count (once sequence)
          [3] 0x0000  — no repeat sequence
          [...] mark_cycles, space_cycles pairs (carrier cycle units)
        NEC timing: leader 9ms/4.5ms, bit mark 562.5µs,
                    "1" space 1687.5µs, "0" space 562.5µs, stop gap 40ms.
        Compatible with Home Assistant, Broadlink RM, Global Caché, Logitech Harmony.
        """
        address = random.randrange(256)
        command = random.randrange(256)
        c = lambda us: _us_to_cycles(us, _NEC_CARRIER_HZ)

        pairs = [(c(9000), c(4500))]          # leader
        for bit in IoTGenerator._nec_bits_lsb(address, command):
            pairs.append((c(562.5), c(1687.5) if bit else c(562.5)))
        pairs.append((c(562.5), c(40000)))    # stop pulse + gap

        words = [0x0000, _PRONTO_FREQ_WORD, len(pairs), 0x0000]
        for m, s in pairs:
            words += [m, s]
        return " ".join(f"{w:04X}" for w in words)

    @staticmethod
    def generate_ir_raw() -> dict:
        """
        Raw pulse/space timings in microseconds (NEC protocol, LSB-first per byte).
        Integer µs values for direct compatibility with:
          ESPHome remote_transmitter, Home Assistant remote.send_command,
          Broadlink RM devices, MQTT IR blaster firmware.
        """
        address = random.randrange(256)
        command = random.randrange(256)
        pulses  = [9024, 4512]              # leader
        for bit in IoTGenerator._nec_bits_lsb(address, command):
            pulses += [562, 1686 if bit else 562]
        pulses.append(562)                  # final stop pulse
        return {
            "carrier_hz":  _NEC_CARRIER_HZ,
            "address":     f"0x{address:02X}",
            "command":     f"0x{command:02X}",
            "pulses":      pulses,
            "pulse_count": len(pulses),
        }

    # ── Dispatcher ────────────────────────────────────────────────────────────

    def generate(self, data_type: str, locale: str = "TR", **kwargs):
        dt = data_type.lower()
        _dispatch = {
            "rfid_uid":  self.generate_rfid_uid,
            "epc":       self.generate_epc,
            "rfid_tag":  self.generate_rfid_tag,
            "nfc_uid":   self.generate_nfc_uid,
            "nfc_atqa":  self.generate_nfc_atqa,
            "nfc_sak":   self.generate_nfc_sak,
            "ndef_uri":  self.generate_ndef_uri,
            "ndef_text": lambda: self.generate_ndef_text(locale),
            "apdu":      self.generate_apdu,
            "nfc_tag":   self.generate_nfc_tag,
            "ir_nec":    self.generate_ir_nec,
            "ir_rc5":    self.generate_ir_rc5,
            "ir_pronto": self.generate_ir_pronto,
            "ir_raw":    self.generate_ir_raw,
        }
        fn = _dispatch.get(dt)
        return fn() if fn else None
