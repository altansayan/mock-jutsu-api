"""
mock-jutsu — Mask functionality tests (Seçenek B)

Covers three layers:
  1. apply_mask() unit tests — all major regulation groups
  2. jutsu.generate/bulk(mask=True) integration tests
  3. _MASKERS registry sanity tests
"""

import re
import pytest
from mockjutsu.masker import apply_mask, _MASKERS
from mockjutsu.core import jutsu


# ── Helpers ───────────────────────────────────────────────────────────────────

def _has_star(v) -> bool:
    return "*" in str(v)


def _no_error(v) -> bool:
    return v is not None and "ERROR" not in str(v)


# ── 1. Unit: PCI DSS SAD — Sensitive Authentication Data ─────────────────────

class TestPciSad:

    @pytest.mark.parametrize("t,value", [
        ("cvv3",         "123"),
        ("cvv4",         "1234"),
        ("pin",          "1234"),
        ("track1_data",  "B4111111111111111^HOLDER/TEST^2512101"),
        ("track2_data",  "4111111111111111=2512101234567890"),
        ("3ds_cavv",     "AAABBJg0VhI0VniQEjRWAAAAAAA="),
        ("password",     "secr3tPa55!"),
        ("password_hash","$2b$12$abc123xyz"),
    ])
    def test_sad_fully_redacted(self, t, value):
        result = apply_mask(t, value)
        assert all(c == "*" or not c.isalnum() for c in result), (
            f"{t}: non-* alphanumeric found in '{result}'"
        )

    def test_cvv3_always_three_stars(self):
        assert apply_mask("cvv3", "999") == "***"

    def test_cvv4_always_four_stars(self):
        assert apply_mask("cvv4", "9999") == "****"

    def test_pin_always_four_stars(self):
        assert apply_mask("pin", "0000") == "****"


# ── 2. Unit: PCI DSS PAN — Card number ───────────────────────────────────────

class TestPciPan:

    def test_cardnum_shows_bin6(self):
        result = apply_mask("cardnum", "4532015112830366")
        d = result.replace(" ", "")
        assert re.match(r"^\d{6}", d), f"BIN not visible: {result}"

    def test_cardnum_shows_last4(self):
        result = apply_mask("cardnum", "4111111111111111")
        assert result.replace(" ", "").endswith("1111")

    def test_cardnum_middle_all_stars(self):
        result = apply_mask("cardnum", "4111111111111111")
        d = result.replace(" ", "")
        assert d[6:12] == "******"

    def test_cardnum_short_passthrough(self):
        result = apply_mask("cardnum", "123456")
        assert "*" in result


# ── 3. Unit: KVKK — Turkish national IDs ────────────────────────────────────

class TestKvkk:

    def test_tckn_first2_last2_visible(self):
        result = apply_mask("tckn", "25807694128")
        assert result[:2] == "25"
        assert result[-2:] == "28"

    def test_tckn_seven_stars_in_middle(self):
        result = apply_mask("tckn", "25807694128")
        assert result[2:9] == "*" * 7

    def test_tckn_total_length_11(self):
        assert len(apply_mask("tckn", "25807694128")) == 11

    def test_ykn_same_rule(self):
        result = apply_mask("ykn", "98765432100")
        assert result[:2] == "98" and result[-2:] == "00"
        assert "*" * 7 in result

    def test_vkn_first3_last3(self):
        result = apply_mask("vkn", "1234567890")
        assert result.startswith("123") and result.endswith("890")
        assert "*" in result


# ── 4. Unit: US IDs — SSN, EIN ───────────────────────────────────────────────

class TestUsIds:

    def test_ssn_irs_format(self):
        assert apply_mask("ssn", "123-45-6789") == "***-**-6789"

    def test_ssn_shows_last4(self):
        result = apply_mask("ssn", "001-23-4567")
        assert result.endswith("4567")

    def test_ein_masked_middle(self):
        result = apply_mask("ein", "12-3456789")
        # EIN: **-***last4 truncated to 10 chars → "**-*****67"
        assert result.startswith("**-") and "*" in result


# ── 5. Unit: UK IDs — NIN, UTR, NHS Number ───────────────────────────────────

class TestUkIds:

    def test_nin_masked_format(self):
        assert apply_mask("nin", "AB123456C") == "AB ** ** ** C"

    def test_utr_first5_visible(self):
        result = apply_mask("utr", "1234567890")
        assert result.startswith("12345") and result.endswith("*" * 5)

    def test_nhs_number_first_group_visible(self):
        result = apply_mask("nhs_number", "9434765919")
        assert result.startswith("943") and "***" in result


# ── 6. Unit: Banking — IBAN, balance, credit score ───────────────────────────

class TestBanking:

    def test_iban_tr_prefix_last4(self):
        result = apply_mask("iban", "TR330006100519786457841326")
        assert result.startswith("TR33")
        assert result.replace(" ", "").endswith("1326")
        assert "****" in result

    def test_iban_gb_prefix_last4(self):
        result = apply_mask("iban", "GB29NWBK60161331926819")
        assert result.startswith("GB29")
        assert result.replace(" ", "").endswith("6819")

    def test_balance_decimal_preserved(self):
        result = apply_mask("balance", "12450.75")
        assert ".75" in result and "*" in result

    def test_credit_score_first_digit_visible(self):
        result = apply_mask("credit_score", "720")
        assert result.startswith("7") and "**" in result


# ── 7. Unit: Contact — Email, Phone ──────────────────────────────────────────

class TestContact:

    def test_email_first2_and_domain(self):
        result = apply_mask("email", "altan@gmail.com")
        assert result == "al***@gmail.com"

    def test_email_domain_untouched(self):
        result = apply_mask("email", "test@example.org")
        assert result.endswith("@example.org")

    def test_phone_e164_tr(self):
        result = apply_mask("phone", "+905325551234")
        assert result.startswith("+90") and result.endswith("34") and "***" in result

    def test_phone_e164_us_single_digit_cc(self):
        result = apply_mask("phone", "+12125551234")
        assert result.startswith("+1") and "***" in result

    def test_msisdn_same_as_phone(self):
        r = apply_mask("msisdn", "+905325551234")
        assert r.startswith("+90") and "***" in r


# ── 8. Unit: Demographics — Birthdate, Age ───────────────────────────────────

class TestDemographics:

    def test_birthdate_hides_month_day(self):
        assert apply_mask("birthdate", "1990-05-14") == "1990-**-**"

    def test_birthdate_slash_separator(self):
        assert apply_mask("birthdate", "1985/12/25") == "1985/**/**"

    def test_age_always_two_stars(self):
        assert apply_mask("age", "35") == "**"
        assert apply_mask("age", "7") == "**"


# ── 9. Unit: Names — first char + *** per word ───────────────────────────────

class TestNames:

    def test_firstname_single_word(self):
        assert apply_mask("firstname", "Altan") == "A***"

    def test_lastname_single_word(self):
        assert apply_mask("lastname", "Sezer") == "S***"

    def test_fullname_two_words(self):
        assert apply_mask("fullname", "Emre Kaya") == "E*** K***"

    def test_fullname_three_words(self):
        result = apply_mask("fullname", "Altan Sezer Ayan")
        parts = result.split()
        assert len(parts) == 3
        assert all(p.endswith("***") for p in parts)


# ── 10. Unit: Documents ───────────────────────────────────────────────────────

class TestDocuments:

    def test_passport_first2_last2(self):
        result = apply_mask("passport", "P1234567")
        assert result.startswith("P1") and result.endswith("67") and "*" in result

    def test_license_same_rule(self):
        result = apply_mask("license", "AB123456")
        assert result.startswith("AB") and result.endswith("56")


# ── 11. Unit: Telecom — IMEI, ICCID, IMSI ───────────────────────────────────

class TestTelecom:

    def test_imei_tac8_visible(self):
        result = apply_mask("imei", "356938035643809")
        d = result.replace("-", "").replace(" ", "")
        assert d[:8] == "35693803" and "*" in d

    def test_iccid_first6_visible(self):
        result = apply_mask("iccid", "8990011916180280010")
        d = "".join(c for c in result if c.isdigit() or c == "*")
        assert d[:6] == "899001"

    def test_imsi_first5_visible(self):
        result = apply_mask("imsi", "310150123456789")
        assert result[:5] == "31015" and "*" in result


# ── 12. Unit: Network — IPv4, MAC ────────────────────────────────────────────

class TestNetwork:

    def test_ipv4_last_two_octets_masked(self):
        assert apply_mask("ipv4", "192.168.1.42") == "192.168.*.*"

    def test_mac_last_three_octets_masked(self):
        assert apply_mask("mac_address", "A4:C3:F0:3D:8E:21") == "A4:C3:F0:**:**:**"

    def test_sessionid_first_group_visible(self):
        result = apply_mask("sessionid", "550e8400-e29b-41d4-a716-446655440000")
        assert result.startswith("550e8400") and "****" in result


# ── 13. Unit: International IDs ──────────────────────────────────────────────

class TestIntlIds:

    @pytest.mark.parametrize("t,value,check_fn", [
        ("br_cpf",          "123.456.789-09", lambda r: r.startswith("123") and "*" in r),
        ("in_aadhaar",      "1234 5678 9012", lambda r: "XXXX XXXX" in r),
        ("cn_ric",          "110000198001011234", lambda r: r[:6] == "110000" and "*" in r),
        ("kr_rrn",          "700101-1280009", lambda r: r.startswith("700101-") and "*" in r),
        ("nl_bsn",          "123456789", lambda r: r[:3] == "123" and "*" in r),
        ("se_personnummer",  "19700101-1234", lambda r: r.startswith("19700101-") and "****" in r),
        ("dk_cpr",          "010170-1234", lambda r: r.startswith("010170-") and "****" in r),
        ("fi_hetu",         "010170-123A", lambda r: r.startswith("010170-") and "****" in r),
        ("au_tfn",          "123456782", lambda r: r[:3] == "123" and "*" in r),
        ("pl_pesel",        "70010112345", lambda r: r[:6] == "700101" and "*" in r),
        ("it_codicefiscale","RSSMRA85M01H501Z", lambda r: r[:4] == "RSSM" and "*" in r),
        ("br_cnpj",         "11.222.333/0001-81", lambda r: r.startswith("11.") and r.endswith("-81") and "*" in r),
        ("in_pan",          "ABCDE1234F",         lambda r: r == "ABCDE****F"),
    ])
    def test_intl_id_masked(self, t, value, check_fn):
        result = apply_mask(t, value)
        assert check_fn(result), f"{t}: unexpected result '{result}'"


# ── 14. Unit: Already-masked and non-maskable pass-through ───────────────────

class TestPassthrough:

    @pytest.mark.parametrize("t,value", [
        ("uuid",        "550e8400-e29b-41d4-a716-446655440000"),
        ("cardnetwork", "Visa"),
        ("currency",    "USD"),
        ("color",       "#FF5733"),
        ("ean13",       "4006381333931"),
        ("blood_type",  "A+"),
        ("gender",      "Male"),
        ("nationality", "TR"),
    ])
    def test_non_maskable_unchanged(self, t, value):
        assert apply_mask(t, value) == value

    def test_tckn_masked_not_double_masked(self):
        already = "25*******28"
        assert apply_mask("tckn_masked", already) == already

    def test_ssn_masked_not_double_masked(self):
        already = "***-**-6789"
        assert apply_mask("ssn_masked", already) == already


# ── 15. Integration: jutsu.generate(type, mask=True) ─────────────────────────

class TestCoreGenerateMask:

    @pytest.mark.parametrize("t", [
        "cardnum", "cvv3", "pin",
        "tckn", "ssn", "nin",
        "iban", "email", "phone",
        "birthdate", "firstname", "fullname",
        "passport", "imei", "ipv4",
    ])
    def test_maskable_type_has_star(self, t):
        result = jutsu.generate(t, mask=True)
        assert _has_star(result), f"{t} masked: no * in {result!r}"

    @pytest.mark.parametrize("t", [
        "uuid", "currency", "color", "ean13", "blood_type", "gender",
    ])
    def test_non_maskable_no_error(self, t):
        result = jutsu.generate(t, mask=True)
        assert _no_error(result), f"{t} mask=True returned error: {result!r}"

    def test_mask_false_no_star_in_tckn(self):
        result = jutsu.generate("tckn", mask=False)
        assert not _has_star(result)
        assert len(str(result)) == 11

    def test_mask_true_star_in_tckn(self):
        result = jutsu.generate("tckn", mask=True)
        assert _has_star(result)

    def test_cardnum_bin_visible_after_mask(self):
        for _ in range(5):
            result = str(jutsu.generate("cardnum", mask=True))
            d = result.replace(" ", "")
            assert re.match(r"^\d{6}", d), f"BIN not visible: {result}"

    def test_cardnum_last4_visible_after_mask(self):
        for _ in range(5):
            result = str(jutsu.generate("cardnum", mask=True))
            d = result.replace(" ", "")
            assert re.match(r"\d{4}$", d[-4:]), f"Last 4 not visible: {result}"

    def test_email_domain_visible_after_mask(self):
        result = str(jutsu.generate("email", mask=True))
        assert "@" in result and "***@" in result

    def test_birthdate_year_visible_after_mask(self):
        result = str(jutsu.generate("birthdate", mask=True))
        assert re.match(r"\d{4}-\*\*-\*\*", result), f"Bad format: {result}"

    def test_iban_country_code_visible(self):
        for _ in range(3):
            result = str(jutsu.generate("iban", locale="TR", mask=True))
            assert result.startswith("TR")

    def test_mask_default_is_false(self):
        result = jutsu.generate("tckn")
        assert not _has_star(result)

    @pytest.mark.parametrize("locale", ["TR", "UK", "US", "DE", "FR", "RU"])
    def test_tckn_mask_all_locales(self, locale):
        result = jutsu.generate("tckn", locale=locale, mask=True)
        assert _has_star(result)


# ── 16. Integration: jutsu.bulk(type, mask=True) ─────────────────────────────

class TestCoreBulkMask:

    @pytest.mark.parametrize("t", [
        "cardnum", "tckn", "iban", "email",
        "ssn", "phone", "birthdate", "imei",
    ])
    def test_bulk_all_results_masked(self, t):
        results = jutsu.bulk(t, count=5, mask=True)
        assert len(results) == 5
        for r in results:
            assert _has_star(r), f"{t} bulk item not masked: {r!r}"

    def test_bulk_count_preserved(self):
        results = jutsu.bulk("tckn", count=10, mask=True)
        assert len(results) == 10

    def test_bulk_mask_false_no_stars(self):
        results = jutsu.bulk("tckn", count=5, mask=False)
        for r in results:
            assert not _has_star(r)

    def test_bulk_non_maskable_no_error(self):
        results = jutsu.bulk("uuid", count=5, mask=True)
        assert len(results) == 5
        for r in results:
            assert _no_error(r)

    def test_bulk_generates_distinct_values(self):
        results = jutsu.bulk("tckn", count=20, mask=True)
        assert len(set(results)) > 1, "All 20 masked TCKNs identical — not random"

    def test_bulk_cardnum_each_has_masked_middle(self):
        results = jutsu.bulk("cardnum", count=10, mask=True)
        for r in results:
            assert "****" in str(r), f"Cardnum middle not masked: {r}"


# ── 17. Registry: _MASKERS sanity ────────────────────────────────────────────

class TestMaskerRegistry:

    def test_maskers_not_empty(self):
        assert len(_MASKERS) > 100

    def test_all_values_callable(self):
        for k, fn in _MASKERS.items():
            assert callable(fn), f"_MASKERS['{k}'] is not callable"

    def test_smoke_all_registered_types(self):
        """Every type in _MASKERS returns non-None without raising."""
        sample = {
            "cardnum":      "4111111111111111",
            "cvv3":         "123",
            "cvv4":         "1234",
            "pin":          "4321",
            "tckn":         "25807694128",
            "ssn":          "123-45-6789",
            "nin":          "AB123456C",
            "iban":         "TR330006100519786457841326",
            "email":        "test@example.com",
            "phone":        "+905551234567",
            "birthdate":    "1990-01-01",
            "firstname":    "Altan",
            "passport":     "P1234567",
            "imei":         "356938035643809",
            "ipv4":         "192.168.1.1",
            "mac_address":  "AA:BB:CC:11:22:33",
            "sessionid":    "550e8400-e29b-41d4-a716-446655440000",
            "balance":      "12450.75",
            "credit_score": "720",
        }
        for t, fn in _MASKERS.items():
            v = sample.get(t, "test_value_123")
            result = fn(v)
            assert result is not None, f"_MASKERS['{t}'] returned None"

    def test_apply_mask_unknown_type_passthrough(self):
        value = "some_random_value"
        assert apply_mask("zzz_unknown_type_xyz", value) == value


# ── 18. Maskeleme gerçekten değiştirdi mi? ────────────────────────────────────

class TestMaskActuallyChanges:
    """apply_mask must return a string that differs from the original input."""

    @pytest.mark.parametrize("t,raw", [
        ("cardnum",   "4111111111111111"),
        ("tckn",      "25807694128"),
        ("ssn",       "123-45-6789"),
        ("iban",      "TR330006100519786457841326"),
        ("email",     "altan@gmail.com"),
        ("phone",     "+905325551234"),
        ("birthdate", "1990-05-14"),
        ("imei",      "356938035643809"),
    ])
    def test_masked_differs_from_original(self, t, raw):
        masked = apply_mask(t, raw)
        assert masked != raw, f"{t}: mask returned same string — no masking happened"
        assert "*" in masked, f"{t}: masked output has no *"


# ── 19. Edge cases — boş/kısa/formatsız input ────────────────────────────────

class TestEdgeCases:

    def test_tckn_empty_string_no_crash(self):
        result = apply_mask("tckn", "")
        assert isinstance(result, str)

    def test_iban_too_short_no_crash(self):
        result = apply_mask("iban", "TR")
        assert isinstance(result, str)
        assert "*" in result  # < 8 chars → all stars per _mask_iban

    def test_phone_without_plus_no_crash(self):
        result = apply_mask("phone", "05325551234")
        assert isinstance(result, str)
        assert "***" in result

    def test_single_char_name_masked(self):
        result = apply_mask("firstname", "A")
        assert result == "A***"
