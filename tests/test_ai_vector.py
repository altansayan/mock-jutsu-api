"""
Tests for God Mode #14 — AI & Vector Database Mocks
Types: ai_embedding, ai_vector, ai_sparse_vector

Core invariants:
  - ai_embedding     : 1536-dim (OpenAI Ada-002) L2-normalized float vector
  - ai_vector        : N-dim configurable L2-normalized float vector (default 384)
  - ai_sparse_vector : sparse {indices, values} with L2-normalized positive weights
  - All vectors satisfy |v|₂ = 1.0 ± 1e-6
  - Zero external dependencies (stdlib math + random only)
"""

import json
import math
import pytest
from mockjutsu.core import MockJutsuCore

jutsu = MockJutsuCore()
_TOL = 1e-6


def _parse(t, **kwargs):
    return json.loads(jutsu.generate(t, **kwargs))


def _l2_norm(vec: list) -> float:
    return math.sqrt(sum(x * x for x in vec))


# ── ai_embedding ──────────────────────────────────────────────────────────────

class TestAiEmbedding:

    def test_no_error(self):
        assert not jutsu.generate('ai_embedding').startswith('ERROR')

    def test_returns_list(self):
        assert isinstance(_parse('ai_embedding'), list)

    def test_default_dims_1536(self):
        assert len(_parse('ai_embedding')) == 1536

    def test_all_floats(self):
        vec = _parse('ai_embedding')
        assert all(isinstance(x, float) for x in vec)

    def test_l2_normalized(self):
        assert abs(_l2_norm(_parse('ai_embedding')) - 1.0) < _TOL

    def test_values_in_unit_range(self):
        vec = _parse('ai_embedding')
        assert all(-1.0 <= x <= 1.0 for x in vec)

    def test_custom_dims_768(self):
        assert len(_parse('ai_embedding', dims=768)) == 768

    def test_custom_dims_l2_normalized(self):
        assert abs(_l2_norm(_parse('ai_embedding', dims=768)) - 1.0) < _TOL

    def test_custom_dims_small(self):
        vec = _parse('ai_embedding', dims=8)
        assert len(vec) == 8
        assert abs(_l2_norm(vec) - 1.0) < _TOL

    def test_bulk_unique(self):
        results = jutsu.bulk('ai_embedding', 5)
        vecs = [json.loads(r) for r in results]
        first3 = [tuple(round(x, 8) for x in v[:3]) for v in vecs]
        assert len(set(first3)) == 5


# ── ai_vector ─────────────────────────────────────────────────────────────────

class TestAiVector:

    def test_no_error(self):
        assert not jutsu.generate('ai_vector').startswith('ERROR')

    def test_returns_list(self):
        assert isinstance(_parse('ai_vector'), list)

    def test_default_dims_384(self):
        assert len(_parse('ai_vector')) == 384

    def test_all_floats(self):
        vec = _parse('ai_vector')
        assert all(isinstance(x, float) for x in vec)

    def test_l2_normalized(self):
        assert abs(_l2_norm(_parse('ai_vector')) - 1.0) < _TOL

    def test_custom_dims_128(self):
        vec = _parse('ai_vector', dims=128)
        assert len(vec) == 128

    def test_custom_dims_l2_normalized(self):
        assert abs(_l2_norm(_parse('ai_vector', dims=128)) - 1.0) < _TOL

    def test_custom_dims_small(self):
        vec = _parse('ai_vector', dims=4)
        assert len(vec) == 4
        assert abs(_l2_norm(vec) - 1.0) < _TOL

    def test_bulk_unique(self):
        results = jutsu.bulk('ai_vector', 5)
        vecs = [json.loads(r) for r in results]
        first3 = [tuple(round(x, 8) for x in v[:3]) for v in vecs]
        assert len(set(first3)) == 5


# ── ai_sparse_vector ──────────────────────────────────────────────────────────

class TestAiSparseVector:

    def test_no_error(self):
        assert not jutsu.generate('ai_sparse_vector').startswith('ERROR')

    def test_returns_dict(self):
        assert isinstance(_parse('ai_sparse_vector'), dict)

    def test_required_keys(self):
        data = _parse('ai_sparse_vector')
        assert 'indices' in data and 'values' in data

    def test_indices_sorted(self):
        data = _parse('ai_sparse_vector')
        assert data['indices'] == sorted(data['indices'])

    def test_indices_unique(self):
        data = _parse('ai_sparse_vector')
        assert len(set(data['indices'])) == len(data['indices'])

    def test_indices_in_range(self):
        data = _parse('ai_sparse_vector')
        assert all(0 <= i < 10000 for i in data['indices'])

    def test_indices_values_same_length(self):
        data = _parse('ai_sparse_vector')
        assert len(data['indices']) == len(data['values'])

    def test_values_all_positive(self):
        data = _parse('ai_sparse_vector')
        assert all(v > 0 for v in data['values'])

    def test_l2_normalized(self):
        data = _parse('ai_sparse_vector')
        assert abs(_l2_norm(data['values']) - 1.0) < _TOL

    def test_default_nnz_128(self):
        data = _parse('ai_sparse_vector')
        assert len(data['indices']) == 128

    def test_bulk_unique(self):
        results = jutsu.bulk('ai_sparse_vector', 5)
        vecs = [json.loads(r) for r in results]
        first3 = [tuple(v['indices'][:3]) for v in vecs]
        assert len(set(first3)) == 5
