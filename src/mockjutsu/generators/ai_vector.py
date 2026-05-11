"""
mock-jutsu — AI & Vector Database Mock Generator
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)

L2-normalized float vectors for AI/ML and vector database testing.

Supported types:
  ai_embedding     — 1536-dim unit vector (OpenAI Ada-002 / Pinecone compatible)
  ai_vector        — N-dim unit vector, configurable via dims kwarg (default: 384)
  ai_sparse_vector — sparse {indices, values} for hybrid search (Pinecone / Qdrant)
"""

import json
import math
import random


def _unit_vector(dims: int) -> list:
    """Gaussian random vector normalized to L2 unit length."""
    vec  = [random.gauss(0.0, 1.0) for _ in range(dims)]
    norm = math.sqrt(sum(x * x for x in vec))
    if norm == 0.0:
        vec[0] = 1.0
        return vec
    inv = 1.0 / norm
    return [x * inv for x in vec]


def generate_ai_embedding(dims: int = 1536) -> str:
    """1536-dim (Ada-002 compatible) L2-normalized float vector."""
    return json.dumps(_unit_vector(dims), separators=(',', ':'))


def generate_ai_vector(dims: int = 384) -> str:
    """N-dim L2-normalized unit vector — general-purpose embedding mock."""
    return json.dumps(_unit_vector(dims), separators=(',', ':'))


def generate_ai_sparse_vector(dims: int = 10000, nnz: int = 128) -> str:
    """Sparse {indices, values} vector with L2-normalized positive weights."""
    k       = min(nnz, dims)
    indices = sorted(random.sample(range(dims), k))
    raw     = [random.uniform(0.001, 1.0) for _ in indices]
    norm    = math.sqrt(sum(x * x for x in raw))
    values  = [x / norm for x in raw]
    return json.dumps({"indices": indices, "values": values}, separators=(',', ':'))


class AiVectorGenerator:
    """L2-normalized AI/ML embedding and sparse vector generator."""

    def generate(self, data_type: str, **kwargs) -> str:
        if data_type == 'ai_embedding':
            return generate_ai_embedding(dims=int(kwargs.get('dims', 1536)))
        if data_type == 'ai_vector':
            return generate_ai_vector(dims=int(kwargs.get('dims', 384)))
        if data_type == 'ai_sparse_vector':
            return generate_ai_sparse_vector(
                dims=int(kwargs.get('dims', 10000)),
                nnz=int(kwargs.get('nnz', 128)),
            )
        return f"ERROR: Unknown type '{data_type}'"
