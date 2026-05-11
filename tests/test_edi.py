"""
Tests for God Mode #17 — X12 EDI 850 & EDIFACT ORDERS Generator
Types: edi_850, edifact_orders

Core invariants:
  - edi_850        : ISA segment exactly 105 chars (no terminator), ISA13==IEA02,
                     GS06==GE02, ST02==SE02, SE01==correct segment count
  - edifact_orders : UNT01==correct segment count (UNH..UNT inclusive),
                     UNZ02==UNB interchange control ref
  - Segment terminators: '~' for X12, "'" for EDIFACT
"""

import pytest
from mockjutsu.core import MockJutsuCore

jutsu = MockJutsuCore()


def _edi850_segments(stmt: str) -> list[str]:
    return [s.strip() for s in stmt.split('~') if s.strip()]


def _edifact_segments(stmt: str) -> list[str]:
    return [s.strip() for s in stmt.split("'") if s.strip()]


# ── EDI 850 ───────────────────────────────────────────────────────────────────

class TestEdi850:

    def test_no_error(self):
        assert not jutsu.generate('edi_850').startswith('ERROR')

    def test_returns_string(self):
        assert isinstance(jutsu.generate('edi_850'), str)

    def test_has_isa_segment(self):
        assert 'ISA*' in jutsu.generate('edi_850')

    def test_has_gs_segment(self):
        assert 'GS*PO*' in jutsu.generate('edi_850')

    def test_has_st_segment(self):
        assert 'ST*850*' in jutsu.generate('edi_850')

    def test_has_beg_segment(self):
        assert 'BEG*' in jutsu.generate('edi_850')

    def test_has_po1_segment(self):
        assert 'PO1*' in jutsu.generate('edi_850')

    def test_has_ctt_segment(self):
        assert 'CTT*' in jutsu.generate('edi_850')

    def test_has_se_segment(self):
        assert 'SE*' in jutsu.generate('edi_850')

    def test_has_ge_segment(self):
        assert 'GE*' in jutsu.generate('edi_850')

    def test_has_iea_segment(self):
        assert 'IEA*' in jutsu.generate('edi_850')

    def test_segment_terminator_is_tilde(self):
        assert jutsu.generate('edi_850').endswith('~')

    def test_isa_length(self):
        """ISA segment without segment terminator must be exactly 105 characters."""
        segs = _edi850_segments(jutsu.generate('edi_850'))
        isa = next(s for s in segs if s.startswith('ISA*'))
        assert len(isa) == 105, f"ISA length {len(isa)}, expected 105: {isa!r}"

    def test_isa_control_number_matches_iea(self):
        """ISA field 13 (interchange control number) must equal IEA field 2."""
        segs = _edi850_segments(jutsu.generate('edi_850'))
        isa = next(s for s in segs if s.startswith('ISA*'))
        iea = next(s for s in segs if s.startswith('IEA*'))
        assert isa.split('*')[13] == iea.split('*')[2]

    def test_gs_group_number_matches_ge(self):
        """GS field 6 (group control number) must equal GE field 2."""
        segs = _edi850_segments(jutsu.generate('edi_850'))
        gs = next(s for s in segs if s.startswith('GS*'))
        ge = next(s for s in segs if s.startswith('GE*'))
        assert gs.split('*')[6] == ge.split('*')[2]

    def test_st_transaction_number_matches_se(self):
        """ST field 2 (transaction set control number) must equal SE field 2."""
        segs = _edi850_segments(jutsu.generate('edi_850'))
        st = next(s for s in segs if s.startswith('ST*'))
        se = next(s for s in segs if s.startswith('SE*'))
        assert st.split('*')[2] == se.split('*')[2]

    def test_se_segment_count_is_correct(self):
        """SE field 1 must equal the number of segments from ST to SE inclusive."""
        segs = _edi850_segments(jutsu.generate('edi_850'))
        st_idx = next(i for i, s in enumerate(segs) if s.startswith('ST*'))
        se_idx = next(i for i, s in enumerate(segs) if s.startswith('SE*'))
        expected = se_idx - st_idx + 1
        actual = int(segs[se_idx].split('*')[1])
        assert actual == expected, f"SE count {actual}, expected {expected}"

    def test_bulk_unique_control_numbers(self):
        results = jutsu.bulk('edi_850', 5)
        ctrl_nums = []
        for r in results:
            segs = _edi850_segments(r)
            isa = next(s for s in segs if s.startswith('ISA*'))
            ctrl_nums.append(isa.split('*')[13])
        assert len(set(ctrl_nums)) == 5


# ── EDIFACT ORDERS ────────────────────────────────────────────────────────────

class TestEdifactOrders:

    def test_no_error(self):
        assert not jutsu.generate('edifact_orders').startswith('ERROR')

    def test_returns_string(self):
        assert isinstance(jutsu.generate('edifact_orders'), str)

    def test_has_unb_segment(self):
        assert 'UNB+' in jutsu.generate('edifact_orders')

    def test_has_unh_segment(self):
        assert 'UNH+' in jutsu.generate('edifact_orders')

    def test_has_bgm_segment(self):
        assert 'BGM+220' in jutsu.generate('edifact_orders')

    def test_has_dtm_segment(self):
        assert 'DTM+' in jutsu.generate('edifact_orders')

    def test_has_nad_buyer(self):
        assert 'NAD+BY' in jutsu.generate('edifact_orders')

    def test_has_nad_seller(self):
        assert 'NAD+SE' in jutsu.generate('edifact_orders')

    def test_has_lin_segment(self):
        assert 'LIN+' in jutsu.generate('edifact_orders')

    def test_has_uns_segment(self):
        assert 'UNS+S' in jutsu.generate('edifact_orders')

    def test_has_unt_segment(self):
        assert 'UNT+' in jutsu.generate('edifact_orders')

    def test_has_unz_segment(self):
        assert 'UNZ+' in jutsu.generate('edifact_orders')

    def test_unt_segment_count_is_correct(self):
        """UNT field 1 must equal the number of segments from UNH to UNT inclusive."""
        segs = _edifact_segments(jutsu.generate('edifact_orders'))
        unh_idx = next(i for i, s in enumerate(segs) if s.startswith('UNH+'))
        unt_idx = next(i for i, s in enumerate(segs) if s.startswith('UNT+'))
        expected = unt_idx - unh_idx + 1
        actual = int(segs[unt_idx].split('+')[1])
        assert actual == expected, f"UNT count {actual}, expected {expected}"

    def test_unz_ctrl_ref_matches_unb(self):
        """UNZ field 2 (interchange control ref) must match UNB field 5."""
        segs = _edifact_segments(jutsu.generate('edifact_orders'))
        unb = next(s for s in segs if s.startswith('UNB+'))
        unz = next(s for s in segs if s.startswith('UNZ+'))
        assert unb.split('+')[5] == unz.split('+')[2]

    def test_segment_terminator_is_apostrophe(self):
        assert jutsu.generate('edifact_orders').endswith("'")

    def test_bulk_unique_ctrl_refs(self):
        results = jutsu.bulk('edifact_orders', 5)
        ctrl_refs = []
        for r in results:
            segs = _edifact_segments(r)
            unb = next(s for s in segs if s.startswith('UNB+'))
            ctrl_refs.append(unb.split('+')[5])
        assert len(set(ctrl_refs)) == 5
