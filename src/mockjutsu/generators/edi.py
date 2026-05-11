"""
mock-jutsu — X12 EDI 850 & EDIFACT ORDERS Generator
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)

Supported types:
  edi_850        — ANSI X12 EDI 850 Purchase Order
                   ISA (105-char fixed) / GS / ST / BEG / N1 / PO1 / CTT / SE / GE / IEA
                   Control numbers: ISA13==IEA02, GS06==GE02, ST02==SE02, SE01==segment count
  edifact_orders — UN/EDIFACT ORDERS D96A
                   UNB / UNH / BGM / DTM / NAD / LIN+QTY+PRI / UNS / CNT / UNT / UNZ
                   UNT01==segment count (UNH..UNT), UNZ02==UNB interchange ref

Zero external dependencies: datetime, random (stdlib only).
"""

import datetime
import random


_COMPANIES = [
    'ACME CORP', 'GLOBAL TRADE INC', 'APEX SOLUTIONS', 'METRO SUPPLY CO',
    'PINNACLE GOODS', 'SUMMIT TRADING', 'HORIZON GROUP', 'NEXUS LOGISTICS',
]


def _rand_alpha(n: int) -> str:
    return ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(n))


def _rand_alphanum(n: int) -> str:
    return ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(n))


def _rand_numeric(n: int) -> str:
    return ''.join(str(random.randint(0, 9)) for _ in range(n))


# ── X12 EDI 850 ───────────────────────────────────────────────────────────────

def generate_edi_850() -> str:
    """ANSI X12 EDI 850 Purchase Order with matching control numbers and correct segment count."""
    today = datetime.date.today()
    now   = datetime.datetime.now()

    ctrl_num   = _rand_numeric(9)                         # ISA13 == IEA02
    grp_num    = _rand_numeric(4)                         # GS06  == GE02
    trans_num  = _rand_numeric(4)                         # ST02  == SE02
    po_num     = f"PO{_rand_numeric(6)}"

    date_6  = today.strftime('%y%m%d')   # YYMMDD  — ISA09
    date_8  = today.strftime('%Y%m%d')   # YYYYMMDD — GS04, BEG05
    time_4  = now.strftime('%H%M')       # HHMM

    # ISA sender/receiver: 10 alphanum chars padded to 15 (fixed-width field)
    sender_id   = f"{_rand_alphanum(10):<15}"
    receiver_id = f"{_rand_alphanum(10):<15}"

    buyer_name  = random.choice(_COMPANIES)
    seller_name = random.choice(_COMPANIES)
    buyer_id    = _rand_alphanum(6)
    seller_id   = _rand_alphanum(6)

    n_lines = random.randint(1, 3)
    po1_segs = []
    for i in range(1, n_lines + 1):
        qty   = random.randint(1, 100)
        price = round(random.uniform(5.0, 500.0), 2)
        part  = _rand_alphanum(8)
        po1_segs.append(f"PO1*{i}*{qty}*EA*{price:.2f}**VP*{part}")

    # Build ST..SE block; SE01 = count of all segments from ST to SE inclusive
    inner = [
        f"ST*850*{trans_num}",
        f"BEG*00*SA*{po_num}**{date_8}",
        f"N1*BY*{buyer_name}*92*{buyer_id}",
        f"N1*SE*{seller_name}*92*{seller_id}",
    ] + po1_segs + [f"CTT*{n_lines}"]

    seg_count = len(inner) + 1   # +1 for SE itself
    inner.append(f"SE*{seg_count}*{trans_num}")

    # ISA: exactly 105 characters (without segment terminator ~)
    isa = (
        f"ISA*00*          *00*          "
        f"*ZZ*{sender_id}*ZZ*{receiver_id}"
        f"*{date_6}*{time_4}*^*00501*{ctrl_num}*0*P*:"
    )

    segments = [
        isa,
        f"GS*PO*{sender_id.strip()}*{receiver_id.strip()}*{date_8}*{time_4}*{grp_num}*X*004010",
    ] + inner + [
        f"GE*1*{grp_num}",
        f"IEA*1*{ctrl_num}",
    ]

    return '~\n'.join(segments) + '~'


# ── EDIFACT ORDERS D96A ───────────────────────────────────────────────────────

def generate_edifact_orders() -> str:
    """UN/EDIFACT ORDERS D96A with correct UNT segment count and UNZ/UNB ctrl ref match."""
    today = datetime.date.today()
    now   = datetime.datetime.now()

    ctrl_ref  = _rand_numeric(9)          # UNB field 5 == UNZ field 2
    msg_ref   = _rand_alphanum(8)         # UNH field 1 == UNT field 2
    po_num    = f"ORD{_rand_numeric(6)}"

    date_8  = today.strftime('%Y%m%d')   # YYYYMMDD
    time_4  = now.strftime('%H%M')       # HHMM

    sender_id   = _rand_alphanum(10)
    receiver_id = _rand_alphanum(10)

    buyer_name  = random.choice(_COMPANIES)
    seller_name = random.choice(_COMPANIES)
    buyer_id    = _rand_alphanum(6)
    seller_id   = _rand_alphanum(6)

    n_lines = random.randint(1, 3)
    line_segs = []
    for i in range(1, n_lines + 1):
        qty   = random.randint(1, 100)
        price = round(random.uniform(5.0, 500.0), 2)
        part  = _rand_alphanum(8)
        line_segs += [
            f"LIN+{i}++{part}:SA",
            f"QTY+21:{qty}",
            f"PRI+AAA:{price:.2f}",
        ]

    # Build UNH..UNT block; UNT01 = count from UNH to UNT inclusive
    inner = [
        f"UNH+{msg_ref}+ORDERS:D:96A:UN",
        f"BGM+220+{po_num}+9",
        f"DTM+137:{date_8}:102",
        f"NAD+BY+{buyer_id}::92++{buyer_name}",
        f"NAD+SE+{seller_id}::92++{seller_name}",
    ] + line_segs + [
        "UNS+S",
        f"CNT+2:{n_lines}",
    ]

    seg_count = len(inner) + 1   # +1 for UNT itself
    inner.append(f"UNT+{seg_count}+{msg_ref}")

    segments = [
        f"UNB+UNOC:3+{sender_id}:ZZZ+{receiver_id}:ZZZ+{date_8}:{time_4}+{ctrl_ref}",
    ] + inner + [
        f"UNZ+1+{ctrl_ref}",
    ]

    return "'\n".join(segments) + "'"


# ── Generator class ───────────────────────────────────────────────────────────

class EdiGenerator:
    """X12 EDI 850 Purchase Order and EDIFACT ORDERS D96A generator."""

    def generate(self, data_type: str, **kwargs) -> str:
        if data_type == 'edi_850':
            return generate_edi_850()
        if data_type == 'edifact_orders':
            return generate_edifact_orders()
        return f"ERROR: Unknown type '{data_type}'"
