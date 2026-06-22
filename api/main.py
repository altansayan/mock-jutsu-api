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


def _build_kwargs(
    locale: Optional[str],
    network: Optional[str],
    currency: Optional[str],
    carrier: Optional[str],
    algorithm: Optional[str],
    gender: Optional[str],
    prefix: Optional[str],
    min: Optional[float],
    max: Optional[float],
    amount: Optional[float],
    merchant: Optional[str],
    city: Optional[str],
    words: Optional[int],
    pattern: Optional[str],
    dims: Optional[int],
    nnz: Optional[int],
    secret: Optional[str],
    payload: Optional[str],
    color_format: Optional[str],
    start: Optional[str],
    end: Optional[str],
    pair: Optional[str],
    mask: bool,
) -> dict:
    """Return only non-None kwargs so generators use their own defaults when a param is absent."""
    raw = {
        "locale":    locale,
        "network":   network,
        "currency":  currency,
        "carrier":   carrier,
        "algorithm": algorithm,
        "gender":    gender,
        "prefix":    prefix,
        "min":       min,
        "max":       max,
        "amount":    amount,
        "merchant":  merchant,
        "city":      city,
        "words":     words,
        "pattern":   pattern,
        "dims":      dims,
        "nnz":       nnz,
        "secret":    secret,
        "payload":   payload,
        "format":    color_format,
        "start":     start,
        "end":       end,
        "pair":      pair,
        "mask":      mask,
    }
    return {k: v for k, v in raw.items() if v is not None}


@app.get("/generate/{data_type}")
async def generate_data(
    data_type: str,
    locale:    Optional[str]   = None,
    network:   Optional[str]   = None,
    currency:  Optional[str]   = None,
    carrier:   Optional[str]   = None,
    algorithm: Optional[str]   = None,
    gender:    Optional[str]   = None,
    prefix:    Optional[str]   = None,
    min:       Optional[float] = None,
    max:       Optional[float] = None,
    amount:    Optional[float] = None,
    merchant:  Optional[str]   = None,
    city:      Optional[str]   = None,
    words:     Optional[int]   = None,
    pattern:   Optional[str]   = None,
    dims:      Optional[int]   = None,
    nnz:       Optional[int]   = None,
    secret:    Optional[str]   = None,
    payload:   Optional[str]   = None,
    color_format: Optional[str] = Query(None, alias="format"),
    start:     Optional[str]   = None,
    end:       Optional[str]   = None,
    pair:      Optional[str]   = None,
    mask:      bool            = False,
):
    """
    Generate a single value for any supported data type.

    **Common parameters** (all optional — omit to use engine defaults):
    - `locale`: TR · UK · US · DE · FR · RU
    - `network`: visa · mc · amex · troy · mir · jcb · discover · unionpay · maestro
    - `currency`: btc · eth
    - `carrier`: fedex · ups · usps · dhl
    - `algorithm`: md5 · sha1 · sha256 · sha512 · sha3-256 · crc32 · adler32 · crc16
    - `gender`: male · female
    - `pattern`: regex pattern for `reverse_regex` type (e.g. `[A-Z]{3}\\d{4}`)
    - `min` / `max`: numeric bounds for random numeric types
    - `start` / `end`: date bounds for `date_between` (YYYY-MM-DD)
    - `words`: mnemonic word count (12 · 15 · 18 · 21 · 24)
    - `dims`: vector dimensions for `ai_embedding` / `ai_vector`
    - `nnz`: non-zero entries for `ai_sparse_vector`
    - `format`: color output format (hex · rgb · hsl · name)
    - `amount`: payment amount for QR/transaction types
    - `pair`: FX pair for `forex_rate` (e.g. EURUSD)
    - `secret` / `payload`: HMAC key and message for `signature` type
    - `mask=true`: regulation-compliant masked output (PCI DSS · GDPR · KVKK…)
    """
    kw = _build_kwargs(
        locale, network, currency, carrier, algorithm, gender, prefix,
        min, max, amount, merchant, city, words, pattern, dims, nnz,
        secret, payload, color_format, start, end, pair, mask,
    )
    result = jutsu.generate(data_type, **kw)
    return {
        "type":   data_type,
        "result": result,
        "masked": mask,
        "status": "success" if "ERROR" not in str(result) else "error",
    }


@app.get("/bulk/{data_type}")
async def bulk_data(
    data_type: str,
    count:     int             = Query(default=10, ge=1, le=1000),
    locale:    Optional[str]   = None,
    network:   Optional[str]   = None,
    currency:  Optional[str]   = None,
    carrier:   Optional[str]   = None,
    algorithm: Optional[str]   = None,
    gender:    Optional[str]   = None,
    prefix:    Optional[str]   = None,
    min:       Optional[float] = None,
    max:       Optional[float] = None,
    amount:    Optional[float] = None,
    merchant:  Optional[str]   = None,
    city:      Optional[str]   = None,
    words:     Optional[int]   = None,
    pattern:   Optional[str]   = None,
    dims:      Optional[int]   = None,
    nnz:       Optional[int]   = None,
    secret:    Optional[str]   = None,
    payload:   Optional[str]   = None,
    color_format: Optional[str] = Query(None, alias="format"),
    start:     Optional[str]   = None,
    end:       Optional[str]   = None,
    pair:      Optional[str]   = None,
    mask:      bool            = False,
):
    """
    Generate *count* values for a single data type.
    Accepts the same optional parameters as `/generate/{data_type}`.
    - **mask=true** masks every generated value.
    """
    kw = _build_kwargs(
        locale, network, currency, carrier, algorithm, gender, prefix,
        min, max, amount, merchant, city, words, pattern, dims, nnz,
        secret, payload, color_format, start, end, pair, mask,
    )
    results = jutsu.bulk(data_type, count=count, **kw)
    return {
        "type":    data_type,
        "count":   len(results),
        "masked":  mask,
        "results": results,
    }


@app.get("/profile")
async def profile_data(
    locale: Optional[str] = None,
    count: int = Query(default=1, ge=1, le=100),
):
    """Generate one or more complete person profiles."""
    kw = {}
    if locale is not None:
        kw["locale"] = locale
    profiles = [jutsu.profile(**kw) for _ in range(count)]
    return {
        "count":   len(profiles),
        "results": profiles if count > 1 else profiles[0],
    }


@app.get("/company")
async def company_data(
    locale: Optional[str] = None,
    count: int = Query(default=1, ge=1, le=100),
):
    """Generate one or more complete company profiles."""
    kw = {}
    if locale is not None:
        kw["locale"] = locale
    companies = [jutsu.company(**kw) for _ in range(count)]
    return {
        "count":   len(companies),
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
    locale = body.get("locale")
    count  = int(body.get("count", 1))
    schema = body.get("schema") or body.get("types")
    if schema is None:
        return {"status": "error", "error": "Provide 'schema' (dict) or 'types' (list)"}
    kw = {"count": count}
    if locale is not None:
        kw["locale"] = str(locale).upper()
    records = jutsu.template(schema, **kw)
    return {
        "count":   len(records),
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
    schema = body.get("schema_map") or body.get("schema") or {}
    locale = body.get("locale")
    count  = int(body.get("count", 10))
    fmt    = str(body.get("format", "json")).lower()
    table  = str(body.get("table", "records"))
    if fmt not in ("json", "csv", "sql"):
        return {"status": "error", "error": "format must be json | csv | sql"}
    kw = {"count": count, "format": fmt, "table": table}
    if locale is not None:
        kw["locale"] = str(locale).upper()
    output = jutsu.export(schema, **kw)
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
        "total":      sum(len(v) for v in cats.values()),
        "categories": cats,
    }


@app.get("/health")
async def health():
    """Simple health check."""
    return {"status": "alive"}
