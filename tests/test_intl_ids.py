"""
International ID Generator Tests — stdnum validation
=====================================================
48 country-specific ID/tax/business number types.
All checksum-bearing types validated against python-stdnum.

Run:
    pip install python-stdnum
    pytest tests/test_intl_ids.py -v
"""
from __future__ import annotations
import re
import pytest
from mockjutsu.core import MockJutsuCore

jutsu = MockJutsuCore()
N = 50  # samples per type


def _gen(t):
    return [jutsu.generate(t) for _ in range(N)]


def _ok(name, results):
    fails = [i for i, ok in enumerate(results) if not ok]
    assert not fails, f"{name}: {len(fails)}/{N} failed. First: sample #{fails[0]}"


# ── Brazil ──────────────────────────────────────────────────────────────────

class TestBrazil:
    def test_br_cpf(self):
        stdnum_cpf = pytest.importorskip("stdnum.br.cpf")
        _ok("br_cpf", [stdnum_cpf.is_valid(v) for v in _gen("br_cpf")])

    def test_br_cnpj(self):
        stdnum_cnpj = pytest.importorskip("stdnum.br.cnpj")
        _ok("br_cnpj", [stdnum_cnpj.is_valid(v) for v in _gen("br_cnpj")])


# ── India ────────────────────────────────────────────────────────────────────

class TestIndia:
    def test_in_pan(self):
        stdnum_pan = pytest.importorskip("stdnum.in_.pan")
        _ok("in_pan", [stdnum_pan.is_valid(v) for v in _gen("in_pan")])

    def test_in_aadhaar(self):
        stdnum_aad = pytest.importorskip("stdnum.in_.aadhaar")
        _ok("in_aadhaar", [stdnum_aad.is_valid(v) for v in _gen("in_aadhaar")])

    def test_in_gstin(self):
        stdnum_gst = pytest.importorskip("stdnum.in_.gstin")
        _ok("in_gstin", [stdnum_gst.is_valid(v) for v in _gen("in_gstin")])

    def test_in_epic(self):
        pat = re.compile(r'^[A-Z]{3}\d{7}$')
        _ok("in_epic", [bool(pat.match(v)) for v in _gen("in_epic")])


# ── China ────────────────────────────────────────────────────────────────────

class TestChina:
    def test_cn_ric(self):
        stdnum_ric = pytest.importorskip("stdnum.cn.ric")
        _ok("cn_ric", [stdnum_ric.is_valid(v) for v in _gen("cn_ric")])


# ── Mexico ───────────────────────────────────────────────────────────────────

class TestMexico:
    def test_mx_curp(self):
        stdnum_curp = pytest.importorskip("stdnum.mx.curp")
        _ok("mx_curp", [stdnum_curp.is_valid(v) for v in _gen("mx_curp")])

    def test_mx_rfc(self):
        stdnum_rfc = pytest.importorskip("stdnum.mx.rfc")
        _ok("mx_rfc", [stdnum_rfc.is_valid(v) for v in _gen("mx_rfc")])


# ── Italy ────────────────────────────────────────────────────────────────────

class TestItaly:
    def test_it_codicefiscale(self):
        stdnum_cf = pytest.importorskip("stdnum.it.codicefiscale")
        _ok("it_codicefiscale", [stdnum_cf.is_valid(v) for v in _gen("it_codicefiscale")])


# ── Spain ────────────────────────────────────────────────────────────────────

class TestSpain:
    def test_es_dni(self):
        stdnum_dni = pytest.importorskip("stdnum.es.dni")
        _ok("es_dni", [stdnum_dni.is_valid(v) for v in _gen("es_dni")])

    def test_es_nie(self):
        stdnum_nie = pytest.importorskip("stdnum.es.nie")
        _ok("es_nie", [stdnum_nie.is_valid(v) for v in _gen("es_nie")])

    def test_es_ccc(self):
        stdnum_ccc = pytest.importorskip("stdnum.es.ccc")
        _ok("es_ccc", [stdnum_ccc.is_valid(v) for v in _gen("es_ccc")])


# ── Germany ──────────────────────────────────────────────────────────────────

class TestGermany:
    def test_de_idnr(self):
        stdnum_idnr = pytest.importorskip("stdnum.de.idnr")
        _ok("de_idnr", [stdnum_idnr.is_valid(v) for v in _gen("de_idnr")])

    def test_de_stnr(self):
        # ELSTER unified format: NN/NNN/NNNNN N
        pat = re.compile(r'^\d{2}/\d{3}/\d{5} \d$')
        _ok("de_stnr", [bool(pat.match(v)) for v in _gen("de_stnr")])


# ── Pakistan ─────────────────────────────────────────────────────────────────

class TestPakistan:
    def test_pk_cnic(self):
        stdnum_cnic = pytest.importorskip("stdnum.pk.cnic")
        _ok("pk_cnic", [stdnum_cnic.is_valid(v) for v in _gen("pk_cnic")])


# ── Japan ────────────────────────────────────────────────────────────────────

class TestJapan:
    def test_jp_cn(self):
        stdnum_jpcn = pytest.importorskip("stdnum.jp.cn")
        _ok("jp_cn", [stdnum_jpcn.is_valid(v) for v in _gen("jp_cn")])

    def test_jp_in(self):
        stdnum_jpin = pytest.importorskip("stdnum.jp.in_")
        _ok("jp_in", [stdnum_jpin.is_valid(v) for v in _gen("jp_in")])


# ── South Korea ──────────────────────────────────────────────────────────────

class TestKorea:
    def test_kr_rrn(self):
        stdnum_rrn = pytest.importorskip("stdnum.kr.rrn")
        _ok("kr_rrn", [stdnum_rrn.is_valid(v) for v in _gen("kr_rrn")])

    def test_kr_brn(self):
        pat = re.compile(r'^\d{3}-\d{2}-\d{5}$')
        _ok("kr_brn", [bool(pat.match(v)) for v in _gen("kr_brn")])


# ── Netherlands ──────────────────────────────────────────────────────────────

class TestNetherlands:
    def test_nl_bsn(self):
        stdnum_bsn = pytest.importorskip("stdnum.nl.bsn")
        _ok("nl_bsn", [stdnum_bsn.is_valid(v) for v in _gen("nl_bsn")])


# ── Poland ───────────────────────────────────────────────────────────────────

class TestPoland:
    def test_pl_pesel(self):
        stdnum_pesel = pytest.importorskip("stdnum.pl.pesel")
        _ok("pl_pesel", [stdnum_pesel.is_valid(v) for v in _gen("pl_pesel")])


# ── Sweden ───────────────────────────────────────────────────────────────────

class TestSweden:
    def test_se_personnummer(self):
        stdnum_pnr = pytest.importorskip("stdnum.se.personnummer")
        _ok("se_personnummer", [stdnum_pnr.is_valid(v) for v in _gen("se_personnummer")])


# ── Denmark ──────────────────────────────────────────────────────────────────

class TestDenmark:
    def test_dk_cpr(self):
        stdnum_cpr = pytest.importorskip("stdnum.dk.cpr")
        _ok("dk_cpr", [stdnum_cpr.is_valid(v) for v in _gen("dk_cpr")])


# ── Finland ──────────────────────────────────────────────────────────────────

class TestFinland:
    def test_fi_hetu(self):
        stdnum_hetu = pytest.importorskip("stdnum.fi.hetu")
        _ok("fi_hetu", [stdnum_hetu.is_valid(v) for v in _gen("fi_hetu")])


# ── Norway ───────────────────────────────────────────────────────────────────

class TestNorway:
    def test_no_fodselsnummer(self):
        stdnum_fod = pytest.importorskip("stdnum.no.fodselsnummer")
        _ok("no_fodselsnummer", [stdnum_fod.is_valid(v) for v in _gen("no_fodselsnummer")])


# ── Australia ────────────────────────────────────────────────────────────────

class TestAustralia:
    def test_au_abn(self):
        stdnum_abn = pytest.importorskip("stdnum.au.abn")
        _ok("au_abn", [stdnum_abn.is_valid(v) for v in _gen("au_abn")])

    def test_au_tfn(self):
        stdnum_tfn = pytest.importorskip("stdnum.au.tfn")
        _ok("au_tfn", [stdnum_tfn.is_valid(v) for v in _gen("au_tfn")])

    def test_au_acn(self):
        stdnum_acn = pytest.importorskip("stdnum.au.acn")
        _ok("au_acn", [stdnum_acn.is_valid(v) for v in _gen("au_acn")])


# ── Malaysia ─────────────────────────────────────────────────────────────────

class TestMalaysia:
    def test_my_nric(self):
        stdnum_nric = pytest.importorskip("stdnum.my.nric")
        _ok("my_nric", [stdnum_nric.is_valid(v) for v in _gen("my_nric")])


# ── Thailand ─────────────────────────────────────────────────────────────────

class TestThailand:
    def test_th_pin(self):
        stdnum_pin = pytest.importorskip("stdnum.th.pin")
        _ok("th_pin", [stdnum_pin.is_valid(v) for v in _gen("th_pin")])

    def test_th_tin(self):
        stdnum_tin = pytest.importorskip("stdnum.th.tin")
        _ok("th_tin", [stdnum_tin.is_valid(v) for v in _gen("th_tin")])


# ── Singapore ────────────────────────────────────────────────────────────────

class TestSingapore:
    def test_sg_uen(self):
        stdnum_uen = pytest.importorskip("stdnum.sg.uen")
        _ok("sg_uen", [stdnum_uen.is_valid(v) for v in _gen("sg_uen")])


# ── South Africa ─────────────────────────────────────────────────────────────

class TestSouthAfrica:
    def test_za_idnr(self):
        stdnum_za = pytest.importorskip("stdnum.za.idnr")
        _ok("za_idnr", [stdnum_za.is_valid(v) for v in _gen("za_idnr")])


# ── Canada ───────────────────────────────────────────────────────────────────

class TestCanada:
    def test_ca_bn(self):
        stdnum_bn = pytest.importorskip("stdnum.ca.bn")
        _ok("ca_bn", [stdnum_bn.is_valid(v) for v in _gen("ca_bn")])


# ── New Zealand ──────────────────────────────────────────────────────────────

class TestNewZealand:
    def test_nz_ird(self):
        stdnum_ird = pytest.importorskip("stdnum.nz.ird")
        _ok("nz_ird", [stdnum_ird.is_valid(v) for v in _gen("nz_ird")])


# ── Argentina ────────────────────────────────────────────────────────────────

class TestArgentina:
    def test_ar_cuit(self):
        stdnum_cuit = pytest.importorskip("stdnum.ar.cuit")
        _ok("ar_cuit", [stdnum_cuit.is_valid(v) for v in _gen("ar_cuit")])

    def test_ar_dni(self):
        pat = re.compile(r'^\d{7,8}$')
        _ok("ar_dni", [bool(pat.match(v)) for v in _gen("ar_dni")])


# ── Chile ────────────────────────────────────────────────────────────────────

class TestChile:
    def test_cl_rut(self):
        stdnum_rut = pytest.importorskip("stdnum.cl.rut")
        _ok("cl_rut", [stdnum_rut.is_valid(v) for v in _gen("cl_rut")])


# ── Colombia ─────────────────────────────────────────────────────────────────

class TestColombia:
    def test_co_nit(self):
        stdnum_nit = pytest.importorskip("stdnum.co.nit")
        _ok("co_nit", [stdnum_nit.is_valid(v) for v in _gen("co_nit")])


# ── Israel ───────────────────────────────────────────────────────────────────

class TestIsrael:
    def test_il_idnr(self):
        stdnum_il = pytest.importorskip("stdnum.il.idnr")
        _ok("il_idnr", [stdnum_il.is_valid(v) for v in _gen("il_idnr")])


# ── Romania ──────────────────────────────────────────────────────────────────

class TestRomania:
    def test_ro_cnp(self):
        stdnum_cnp = pytest.importorskip("stdnum.ro.cnp")
        _ok("ro_cnp", [stdnum_cnp.is_valid(v) for v in _gen("ro_cnp")])

    def test_ro_cui(self):
        stdnum_cui = pytest.importorskip("stdnum.ro.cui")
        _ok("ro_cui", [stdnum_cui.is_valid(v) for v in _gen("ro_cui")])


# ── Croatia ──────────────────────────────────────────────────────────────────

class TestCroatia:
    def test_hr_oib(self):
        stdnum_oib = pytest.importorskip("stdnum.hr.oib")
        _ok("hr_oib", [stdnum_oib.is_valid(v) for v in _gen("hr_oib")])


# ── Bulgaria ─────────────────────────────────────────────────────────────────

class TestBulgaria:
    def test_bg_egn(self):
        stdnum_egn = pytest.importorskip("stdnum.bg.egn")
        _ok("bg_egn", [stdnum_egn.is_valid(v) for v in _gen("bg_egn")])


# ── Lithuania ────────────────────────────────────────────────────────────────

class TestLithuania:
    def test_lt_asmens(self):
        stdnum_lt = pytest.importorskip("stdnum.lt.asmens")
        _ok("lt_asmens", [stdnum_lt.is_valid(v) for v in _gen("lt_asmens")])


# ── Estonia ──────────────────────────────────────────────────────────────────

class TestEstonia:
    def test_ee_ik(self):
        stdnum_ik = pytest.importorskip("stdnum.ee.ik")
        _ok("ee_ik", [stdnum_ik.is_valid(v) for v in _gen("ee_ik")])


# ── Portugal ─────────────────────────────────────────────────────────────────

class TestPortugal:
    def test_pt_cc(self):
        stdnum_cc = pytest.importorskip("stdnum.pt.cc")
        _ok("pt_cc", [stdnum_cc.is_valid(v) for v in _gen("pt_cc")])


# ── Egypt ────────────────────────────────────────────────────────────────────

class TestEgypt:
    def test_eg_tn(self):
        stdnum_egtn = pytest.importorskip("stdnum.eg.tn")
        _ok("eg_tn", [stdnum_egtn.is_valid(v) for v in _gen("eg_tn")])


# ── Smoke — all 48 types return non-error strings ────────────────────────────

class TestSmoke:
    _ALL_TYPES = [
        'br_cpf', 'br_cnpj', 'in_pan', 'in_aadhaar', 'in_gstin', 'in_epic',
        'cn_ric', 'mx_curp', 'mx_rfc', 'it_codicefiscale', 'es_dni', 'es_nie',
        'es_ccc', 'de_idnr', 'de_stnr', 'pk_cnic', 'jp_cn', 'jp_in',
        'kr_rrn', 'kr_brn', 'nl_bsn', 'pl_pesel', 'se_personnummer', 'dk_cpr',
        'fi_hetu', 'no_fodselsnummer', 'au_abn', 'au_tfn', 'au_acn', 'my_nric',
        'th_pin', 'th_tin', 'sg_uen', 'za_idnr', 'ca_bn', 'nz_ird',
        'ar_cuit', 'ar_dni', 'cl_rut', 'co_nit', 'il_idnr', 'ro_cnp', 'ro_cui',
        'hr_oib', 'bg_egn', 'lt_asmens', 'ee_ik', 'pt_cc', 'eg_tn',
    ]

    @pytest.mark.parametrize("t", _ALL_TYPES)
    def test_no_error(self, t):
        v = jutsu.generate(t)
        assert not str(v).startswith("ERROR"), f"{t} returned: {v}"
        assert v, f"{t} returned empty"

    @pytest.mark.parametrize("t", _ALL_TYPES)
    def test_bulk_10(self, t):
        results = jutsu.bulk(t, count=10)
        assert len(results) == 10
        assert all(not str(r).startswith("ERROR") for r in results)
