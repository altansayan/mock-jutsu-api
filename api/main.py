"""
mock-jutsu — FastAPI Application
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)
Purpose: Provides a RESTful gateway for the mock-jutsu engine.
"""

from fastapi import FastAPI, Query
from typing import Optional
from mockjutsu.core import jutsu

app = FastAPI(
    title="mock-jutsu API",
    description="Atomic Mock Data Generation by Altan Sezer Ayan - A.S.A",
    version="0.1.0",
    contact={
        "name": "Altan Sezer Ayan - A.S.A",
        "url": "https://github.com/altansayan",
    }
)

@app.get("/")
async def root():
    """Welcome endpoint providing developer info."""
    return {
        "message": "Welcome to mock-jutsu API",
        "developer": "Altan Sezer Ayan - A.S.A",
        "github": "https://github.com/altansayan",
        "usage": "/generate/{type}"
    }


@app.get("/generate/{data_type}")
async def generate_data(
    data_type: str,
    locale: str = "TR",
    network: str = "visa",
    gender: Optional[str] = None,
    mask: bool = False,
):
    """
    Generate a single value for any supported data type.
    - **mask=true** returns a regulation-compliant masked value (PCI DSS, GDPR, KVKK…)
    """
    result = jutsu.generate(
        data_type,
        locale=locale,
        network=network,
        gender=gender,
        mask=mask,
    )
    return {
        "type": data_type,
        "locale": locale,
        "result": result,
        "masked": mask,
        "status": "success" if "ERROR" not in str(result) else "error",
    }


@app.get("/bulk/{data_type}")
async def bulk_data(
    data_type: str,
    count: int = Query(default=10, ge=1, le=1000),
    locale: str = "TR",
    network: str = "visa",
    gender: Optional[str] = None,
    mask: bool = False,
):
    """
    Generate *count* values for a single data type.
    - **mask=true** masks every generated value.
    """
    results = jutsu.bulk(
        data_type,
        count=count,
        locale=locale,
        network=network,
        gender=gender,
        mask=mask,
    )
    return {
        "type": data_type,
        "count": len(results),
        "locale": locale,
        "masked": mask,
        "results": results,
    }


@app.get("/profile")
async def profile_data(
    locale: str = "TR",
    count: int = Query(default=1, ge=1, le=100),
):
    """Generate one or more complete person profiles."""
    profiles = [jutsu.profile(locale=locale) for _ in range(count)]
    return {
        "locale": locale,
        "count": len(profiles),
        "results": profiles if count > 1 else profiles[0],
    }


@app.get("/company")
async def company_data(
    locale: str = "TR",
    count: int = Query(default=1, ge=1, le=100),
):
    """Generate one or more complete company profiles."""
    companies = [jutsu.company(locale=locale) for _ in range(count)]
    return {
        "locale": locale,
        "count": len(companies),
        "results": companies if count > 1 else companies[0],
    }


@app.post("/template")
async def template_data(body: dict):
    """
    Generate structured records from a type schema.

    ```json
    {"types": ["uuid", "phone", "iban"], "count": 5, "locale": "TR"}
    ```
    or with field names:
    ```json
    {"schema": {"id": "uuid", "mobile": "phone"}, "count": 5, "locale": "TR"}
    ```
    """
    locale = str(body.get("locale", "TR")).upper()
    count  = int(body.get("count", 1))
    schema = body.get("schema") or body.get("types")
    if schema is None:
        return {"status": "error", "error": "Provide 'schema' (dict) or 'types' (list)"}
    records = jutsu.template(schema, count=count, locale=locale)
    return {
        "count": len(records),
        "locale": locale,
        "results": records if count > 1 else records[0],
    }


@app.post("/export")
async def export_data(body: dict):
    """
    Export records as JSON, CSV, or SQL.

    ```json
    {
      "schema_map": {"id": "uuid", "phone": "phone"},
      "count": 10, "locale": "TR",
      "format": "csv", "table": "users"
    }
    ```
    """
    schema  = body.get("schema_map") or body.get("schema") or {}
    locale  = str(body.get("locale", "TR")).upper()
    count   = int(body.get("count", 10))
    fmt     = str(body.get("format", "json")).lower()
    table   = str(body.get("table", "records"))
    if fmt not in ("json", "csv", "sql"):
        return {"status": "error", "error": "format must be json | csv | sql"}
    output = jutsu.export(schema, count=count, format=fmt, locale=locale, table=table)
    return {"format": fmt, "count": count, "result": output}


@app.get("/list")
async def list_types(cat: Optional[str] = None):
    """List all supported data types, optionally filtered by category."""
    from mockjutsu.cli import _REFERENCE
    funcs = _REFERENCE
    if cat:
        cat_lower = cat.lower()
        funcs = [f for f in funcs if f[1].lower() == cat_lower]
    cats: dict[str, list] = {}
    for f in funcs:
        cats.setdefault(f[1], []).append(f[0])
    return {
        "total": sum(len(v) for v in cats.values()),
        "categories": cats,
    }


@app.get("/health")
async def health():
    """Simple health check."""
    return {"status": "alive"}
