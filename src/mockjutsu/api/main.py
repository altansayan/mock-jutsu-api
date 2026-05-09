"""
mock-jutsu — FastAPI Application
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)
"""

from typing import Any, Dict, List, Optional
from fastapi import FastAPI, Query
from pydantic import BaseModel
from mockjutsu.core import jutsu
from mockjutsu.cli import _REFERENCE

app = FastAPI(
    title="mock-jutsu API",
    description="Algorithmic Mock Data Engine — 174 Types, 6 Locales",
    version="1.0.0",
    contact={
        "name": "Altan Sezer Ayan - A.S.A",
        "url": "https://github.com/altansayan",
    },
)


# ── Request bodies ────────────────────────────────────────────────────────────

class TemplateRequest(BaseModel):
    types: List[str]
    count: int = 1
    locale: str = "TR"


class ExportRequest(BaseModel):
    schema_: Dict[str, str]
    count: int = 10
    locale: str = "TR"
    format: str = "json"
    table: str = "records"

    class Config:
        populate_by_name = True

    @classmethod
    def model_validator_alias(cls):
        return {"schema": "schema_"}


# ── Root ─────────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "service": "mock-jutsu API",
        "developer": "Altan Sezer Ayan - A.S.A",
        "github": "https://github.com/altansayan",
        "endpoints": [
            "GET  /generate/{type}",
            "GET  /bulk/{type}",
            "POST /template",
            "GET  /profile",
            "GET  /company",
            "POST /export",
            "GET  /list",
            "GET  /health",
        ],
    }


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok"}


# ── List ──────────────────────────────────────────────────────────────────────

@app.get("/list")
async def list_types(cat: str = ""):
    rows = [
        {
            "type": r[0].strip(),
            "category": r[1],
            "locale_aware": r[2],
            "example": r[3],
            "description": r[5] if len(r) > 5 else "",
        }
        for r in _REFERENCE
        if r[0].strip() and not r[0].strip().startswith("--")
        and (not cat or cat.lower() in r[1].lower())
    ]
    return {"count": len(rows), "types": rows}


# ── Generate ──────────────────────────────────────────────────────────────────

@app.get("/generate/{data_type}")
async def generate(
    data_type: str,
    locale: str = Query("TR", description="TR UK US DE FR RU"),
    network: str = Query("visa", description="visa mc amex troy mir"),
    currency: str = Query("btc", description="btc eth"),
    carrier: str = Query("usps", description="usps ups fedex"),
    algorithm: str = Query("sha256", description="md5 sha1 sha256 sha384 sha512 sha3-256 crc32"),
):
    result = jutsu.generate(
        data_type,
        locale=locale,
        network=network,
        currency=currency,
        carrier=carrier,
        algorithm=algorithm,
    )
    ok = "ERROR" not in str(result)
    return {
        "type": data_type,
        "locale": locale,
        "result": result,
        "status": "success" if ok else "error",
    }


# ── Bulk ──────────────────────────────────────────────────────────────────────

@app.get("/bulk/{data_type}")
async def bulk(
    data_type: str,
    count: int = Query(10, ge=1, le=1000),
    locale: str = Query("TR", description="TR UK US DE FR RU"),
):
    results = jutsu.bulk(data_type, count=count, locale=locale)
    return {
        "type": data_type,
        "locale": locale,
        "count": count,
        "results": results,
    }


# ── Template ──────────────────────────────────────────────────────────────────

@app.post("/template")
async def template(req: TemplateRequest):
    schema = {t: t for t in req.types}
    records = jutsu.template(schema, count=req.count, locale=req.locale)
    output = records[0] if req.count == 1 else records
    return {
        "types": req.types,
        "locale": req.locale,
        "count": req.count,
        "result": output,
    }


# ── Profile ───────────────────────────────────────────────────────────────────

@app.get("/profile")
async def profile(
    locale: str = Query("TR", description="TR UK US DE FR RU"),
    count: int = Query(1, ge=1, le=100),
):
    results = [jutsu.profile(locale=locale) for _ in range(count)]
    output = results[0] if count == 1 else results
    return {"locale": locale, "count": count, "result": output}


# ── Company ───────────────────────────────────────────────────────────────────

@app.get("/company")
async def company(
    locale: str = Query("TR", description="TR UK US DE FR RU"),
    count: int = Query(1, ge=1, le=100),
):
    results = [jutsu.company(locale=locale) for _ in range(count)]
    output = results[0] if count == 1 else results
    return {"locale": locale, "count": count, "result": output}


# ── Export ────────────────────────────────────────────────────────────────────

class ExportRequest(BaseModel):
    schema_map: Dict[str, str]
    count: int = 10
    locale: str = "TR"
    format: str = "json"
    table: str = "records"


@app.post("/export")
async def export(req: ExportRequest):
    output = jutsu.export(
        req.schema_map,
        count=req.count,
        format=req.format,
        locale=req.locale,
        table=req.table,
    )
    return {
        "locale": req.locale,
        "count": req.count,
        "format": req.format,
        "result": output,
    }
