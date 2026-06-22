"""
mock-jutsu — FastAPI Application
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)
"""

from typing import Any, Dict, List, Optional
from fastapi import FastAPI, Query
from pydantic import BaseModel
from mockjutsu.core import jutsu
from mockjutsu.masker import apply_mask
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
    locale: str    = Query("TR",     description="TR · UK · US · DE · FR · RU"),
    network: str   = Query("visa",   description="visa · mc · amex · troy · mir · jcb · discover · unionpay · maestro"),
    currency: str  = Query("btc",    description="btc · eth"),
    carrier: str   = Query("usps",   description="usps · ups · fedex · dhl"),
    algorithm: str = Query("sha256", description="md5 · sha1 · sha256 · sha512 · sha3-256 · crc32 · adler32 · crc16"),
    gender: Optional[str]   = Query(None, description="male · female"),
    min:    Optional[float] = Query(None, description="Minimum value for numeric types"),
    max:    Optional[float] = Query(None, description="Maximum value for numeric types"),
    amount: Optional[float] = Query(None, description="Payment amount for QR/transaction types"),
    merchant: Optional[str] = Query(None, description="Merchant name for QR types"),
    city:     Optional[str] = Query(None, description="Merchant city for QR types"),
    words:    Optional[int] = Query(None, description="Word count for mnemonic: 12 · 15 · 18 · 21 · 24"),
    pattern:  Optional[str] = Query(None, description="Regex pattern for reverse_regex type — e.g. [A-Z]{3}\\d{4}"),
    dims:     Optional[int] = Query(None, description="Vector dimensions for ai_embedding / ai_vector"),
    nnz:      Optional[int] = Query(None, description="Non-zero entries for ai_sparse_vector"),
    secret:   Optional[str] = Query(None, description="HMAC signing key for signature type"),
    payload:  Optional[str] = Query(None, description="Message to sign for signature type"),
    format:   Optional[str] = Query(None, description="Color output format: hex · rgb · hsl · name"),
    mask:     bool          = Query(False, description="Return regulation-compliant masked value (PCI DSS · GDPR · KVKK)"),
    start:    Optional[str] = Query(None, description="Start date YYYY-MM-DD for date_between"),
    end:      Optional[str] = Query(None, description="End date YYYY-MM-DD for date_between"),
    pair:     Optional[str] = Query(None, description="FX pair for forex_rate — e.g. EURUSD"),
):
    extra = {k: v for k, v in {
        "gender": gender, "min": min, "max": max, "amount": amount,
        "merchant": merchant, "city": city, "words": words, "pattern": pattern,
        "dims": dims, "nnz": nnz, "secret": secret, "payload": payload,
        "format": format, "start": start, "end": end, "pair": pair,
    }.items() if v is not None}

    result = jutsu.generate(
        data_type, locale=locale, network=network,
        currency=currency, carrier=carrier, algorithm=algorithm, **extra,
    )
    if mask and "ERROR" not in str(result):
        result = apply_mask(data_type, result)

    ok = "ERROR" not in str(result)
    return {
        "type":   data_type,
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
