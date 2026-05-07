"""
mock-jutsu — API endpoint tests (FastAPI TestClient)
"""

import json
import pytest
from fastapi.testclient import TestClient
from mockjutsu.api.main import app

client = TestClient(app)


# ── Root & Health ─────────────────────────────────────────────────────────────

class TestRoot:

    def test_root_ok(self):
        r = client.get("/")
        assert r.status_code == 200

    def test_root_has_endpoints(self):
        data = r = client.get("/")
        assert "endpoints" in r.json()

    def test_health_ok(self):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


# ── List ──────────────────────────────────────────────────────────────────────

class TestListEndpoint:

    def test_list_returns_types(self):
        r = client.get("/list")
        assert r.status_code == 200
        data = r.json()
        assert data["count"] == 174
        assert len(data["types"]) == 174

    def test_list_type_has_required_fields(self):
        r = client.get("/list")
        first = r.json()["types"][0]
        assert "type" in first
        assert "category" in first
        assert "locale_aware" in first
        assert "example" in first

    def test_list_filter_by_cat(self):
        r = client.get("/list?cat=Financial")
        assert r.status_code == 200
        data = r.json()
        assert data["count"] > 0
        for t in data["types"]:
            assert "financial" in t["category"].lower()

    def test_list_filter_unknown_cat_returns_empty(self):
        r = client.get("/list?cat=zzz_nonexistent")
        assert r.status_code == 200
        assert r.json()["count"] == 0


# ── Generate ──────────────────────────────────────────────────────────────────

class TestGenerateEndpoint:

    def test_generate_tckn(self):
        r = client.get("/generate/tckn")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        assert len(str(data["result"])) == 11

    def test_generate_unknown_type_returns_error_status(self):
        r = client.get("/generate/xyzzy_nonexistent")
        assert r.status_code == 200
        assert r.json()["status"] == "error"

    def test_generate_response_has_required_fields(self):
        r = client.get("/generate/uuid")
        data = r.json()
        assert "type" in data
        assert "locale" in data
        assert "result" in data
        assert "status" in data

    def test_generate_locale_param(self):
        r = client.get("/generate/iban?locale=DE")
        assert r.status_code == 200
        assert str(r.json()["result"]).startswith("DE")

    def test_generate_network_param(self):
        r = client.get("/generate/cardnum?network=amex")
        assert r.status_code == 200
        result = str(r.json()["result"])
        assert result.startswith("3")

    def test_generate_currency_param(self):
        r = client.get("/generate/eth_address?currency=eth")
        assert r.status_code == 200
        assert str(r.json()["result"]).startswith("0x")

    def test_generate_carrier_param(self):
        r = client.get("/generate/tracking_number?carrier=ups")
        assert r.status_code == 200
        assert r.json()["status"] == "success"

    def test_generate_algorithm_param(self):
        r = client.get("/generate/hash?algorithm=md5")
        assert r.status_code == 200
        result = str(r.json()["result"])
        assert len(result) == 32

    @pytest.mark.parametrize("data_type", [
        "tckn", "ssn", "nin", "snils", "iban", "cardnum", "phone",
        "email", "uuid", "ipv4", "jwt", "ean13", "imei", "btc_address",
        "product_name", "latitude", "username", "blood_type",
    ])
    def test_generate_common_types(self, data_type):
        r = client.get(f"/generate/{data_type}")
        assert r.status_code == 200
        assert r.json()["status"] == "success", f"{data_type}: {r.json()}"

    @pytest.mark.parametrize("locale", ["TR", "UK", "US", "DE", "FR", "RU"])
    def test_generate_all_locales(self, locale):
        r = client.get(f"/generate/phone?locale={locale}")
        assert r.status_code == 200
        assert r.json()["status"] == "success"


# ── Bulk ──────────────────────────────────────────────────────────────────────

class TestBulkEndpoint:

    def test_bulk_default_count(self):
        r = client.get("/bulk/tckn")
        assert r.status_code == 200
        data = r.json()
        assert data["count"] == 10
        assert len(data["results"]) == 10

    def test_bulk_custom_count(self):
        r = client.get("/bulk/uuid?count=5")
        assert r.status_code == 200
        assert len(r.json()["results"]) == 5

    def test_bulk_locale(self):
        r = client.get("/bulk/iban?count=3&locale=DE")
        assert r.status_code == 200
        for val in r.json()["results"]:
            assert str(val).startswith("DE")

    def test_bulk_response_fields(self):
        r = client.get("/bulk/pin?count=2")
        data = r.json()
        assert "type" in data
        assert "locale" in data
        assert "count" in data
        assert "results" in data

    def test_bulk_count_limit(self):
        r = client.get("/bulk/uuid?count=1001")
        assert r.status_code == 422

    def test_bulk_count_zero(self):
        r = client.get("/bulk/uuid?count=0")
        assert r.status_code == 422


# ── Template ──────────────────────────────────────────────────────────────────

class TestTemplateEndpoint:

    def test_template_single_record(self):
        r = client.post("/template", json={"types": ["nin", "snils", "cardtype"], "count": 1})
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data["result"], dict)
        assert "nin" in data["result"]
        assert "snils" in data["result"]
        assert "cardtype" in data["result"]

    def test_template_multiple_records(self):
        r = client.post("/template", json={"types": ["uuid", "phone"], "count": 5})
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data["result"], list)
        assert len(data["result"]) == 5

    def test_template_locale(self):
        r = client.post("/template", json={"types": ["iban", "phone"], "count": 1, "locale": "DE"})
        assert r.status_code == 200
        result = r.json()["result"]
        assert str(result["iban"]).startswith("DE")

    def test_template_response_fields(self):
        r = client.post("/template", json={"types": ["uuid"], "count": 1})
        data = r.json()
        assert "types" in data
        assert "locale" in data
        assert "count" in data
        assert "result" in data

    def test_template_no_errors_in_result(self):
        r = client.post("/template", json={
            "types": ["tckn", "firstname", "lastname", "phone", "iban", "email"],
            "count": 3,
            "locale": "TR",
        })
        assert r.status_code == 200
        for rec in r.json()["result"]:
            for k, v in rec.items():
                assert "ERROR" not in str(v), f"{k}: {v}"

    def test_template_missing_types_returns_422(self):
        r = client.post("/template", json={"count": 1})
        assert r.status_code == 422


# ── Profile ───────────────────────────────────────────────────────────────────

class TestProfileEndpoint:

    def test_profile_default(self):
        r = client.get("/profile")
        assert r.status_code == 200
        data = r.json()
        result = data["result"]
        assert "id" in result
        assert "firstname" in result
        assert "lastname" in result
        assert "phone" in result
        assert "iban" in result
        assert "email" in result

    def test_profile_single_returns_dict(self):
        r = client.get("/profile?count=1")
        assert r.status_code == 200
        assert isinstance(r.json()["result"], dict)

    def test_profile_multiple_returns_list(self):
        r = client.get("/profile?count=3")
        assert r.status_code == 200
        assert isinstance(r.json()["result"], list)
        assert len(r.json()["result"]) == 3

    @pytest.mark.parametrize("locale", ["TR", "UK", "US", "DE", "FR", "RU"])
    def test_profile_all_locales(self, locale):
        r = client.get(f"/profile?locale={locale}")
        assert r.status_code == 200
        assert "ERROR" not in str(r.json()["result"])


# ── Company ───────────────────────────────────────────────────────────────────

class TestCompanyEndpoint:

    def test_company_default(self):
        r = client.get("/company")
        assert r.status_code == 200
        result = r.json()["result"]
        assert "id" in result
        assert "name" in result
        assert "iban" in result
        assert "phone" in result

    def test_company_single_returns_dict(self):
        r = client.get("/company?count=1")
        assert r.status_code == 200
        assert isinstance(r.json()["result"], dict)

    def test_company_multiple_returns_list(self):
        r = client.get("/company?count=2")
        assert r.status_code == 200
        assert isinstance(r.json()["result"], list)
        assert len(r.json()["result"]) == 2

    @pytest.mark.parametrize("locale", ["TR", "UK", "US", "DE", "FR", "RU"])
    def test_company_all_locales(self, locale):
        r = client.get(f"/company?locale={locale}")
        assert r.status_code == 200
        assert "ERROR" not in str(r.json()["result"])


# ── Export ────────────────────────────────────────────────────────────────────

class TestExportEndpoint:

    def test_export_json_default(self):
        r = client.post("/export", json={
            "schema_map": {"id": "uuid", "name": "fullname"},
            "count": 3,
        })
        assert r.status_code == 200
        result = r.json()["result"]
        parsed = json.loads(result)
        assert isinstance(parsed, list)
        assert len(parsed) == 3
        assert "id" in parsed[0]
        assert "name" in parsed[0]

    def test_export_csv_format(self):
        r = client.post("/export", json={
            "schema_map": {"id": "uuid", "phone": "phone"},
            "count": 3,
            "format": "csv",
        })
        assert r.status_code == 200
        lines = r.json()["result"].strip().split("\n")
        assert len(lines) == 4  # header + 3 rows
        assert "id" in lines[0]
        assert "phone" in lines[0]

    def test_export_sql_format(self):
        r = client.post("/export", json={
            "schema_map": {"id": "uuid", "name": "fullname"},
            "count": 2,
            "format": "sql",
            "table": "users",
        })
        assert r.status_code == 200
        result = r.json()["result"]
        assert result.startswith("INSERT INTO users")

    def test_export_response_fields(self):
        r = client.post("/export", json={"schema_map": {"v": "uuid"}, "count": 1})
        data = r.json()
        assert "locale" in data
        assert "count" in data
        assert "format" in data
        assert "result" in data

    def test_export_missing_schema_returns_422(self):
        r = client.post("/export", json={"count": 5})
        assert r.status_code == 422
