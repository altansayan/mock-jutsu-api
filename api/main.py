"""
mock-jutsu — FastAPI Application
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)
Purpose: Provides a RESTful gateway for the mock-jutsu engine.
"""

from fastapi import FastAPI
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
    gender: str = None
):
    """
    Primary endpoint for data generation.
    Supports query parameters for filtering results.
    """
    result = jutsu.generate(
        data_type, 
        locale=locale, 
        network=network, 
        gender=gender
    )
    return {
        "type": data_type,
        "locale": locale,
        "result": result,
        "status": "success" if "ERROR" not in str(result) else "error"
    }

@app.get("/health")
async def health():
    """Simple health check."""
    return {"status": "alive"}
