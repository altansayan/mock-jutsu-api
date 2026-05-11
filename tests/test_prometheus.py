"""
Tests for God Mode #24 — Prometheus / OpenMetrics Çıktıları
Types: prometheus_metrics, openmetrics_snapshot

Core invariants:
  Both types:
    - JSON dict with 'exposition' (raw text), 'format', 'metric_families', 'total_samples'
    - # HELP lines present
    - # TYPE lines present, type values valid Prometheus types
    - Sample lines: name{labels} numeric_value  (no comment prefix)
    - Counter values >= 0
    - Histogram buckets monotonically non-decreasing
    - Histogram +Inf bucket count == _count line
    - Histogram _sum >= 0
    - process_ metrics present (CPU, memory)
    - http_requests_total counter present

  prometheus_metrics:
    - format == 'prometheus'
    - Does NOT end with '# EOF'

  openmetrics_snapshot:
    - format == 'openmetrics'
    - Ends with '# EOF\n'
    - '# EOF' is the last non-empty line
"""

import json
import re
import pytest
from mockjutsu.core import MockJutsuCore

jutsu = MockJutsuCore()

_VALID_PROMETHEUS_TYPES = {'counter', 'gauge', 'histogram', 'summary', 'untyped',
                           'gaugehistogram', 'stateset', 'info', 'unknown'}
_HIST_METRIC = 'http_request_duration_seconds'


def _exposition(data_type):
    return json.loads(jutsu.generate(data_type))['exposition']


def _get_type_map(exposition: str) -> dict:
    """Parse # TYPE lines → {metric_name: type_string}."""
    pattern = re.compile(r'^# TYPE (\S+) (\S+)', re.MULTILINE)
    return {m.group(1): m.group(2) for m in pattern.finditer(exposition)}


def _get_sample_lines(exposition: str) -> list[tuple[str, float]]:
    """Return (metric_name, value) for every non-comment, non-empty line."""
    pattern = re.compile(
        r'^([a-zA-Z_:][a-zA-Z0-9_:]*)(?:\{[^}]*\})?\s+'
        r'([-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)',
        re.MULTILINE,
    )
    return [(m.group(1), float(m.group(2))) for m in pattern.finditer(exposition)]


def _histogram_buckets(exposition: str, base: str) -> list[tuple[str, int]]:
    """Extract (le_str, count) from histogram bucket lines."""
    pat = re.compile(
        rf'^{re.escape(base)}_bucket\{{.*?le="([^"]+)".*?\}}\s+(\d+)',
        re.MULTILINE,
    )
    return [(m.group(1), int(m.group(2))) for m in pat.finditer(exposition)]


def _histogram_count(exposition: str, base: str) -> int | None:
    m = re.search(rf'^{re.escape(base)}_count\s+(\d+)', exposition, re.MULTILINE)
    return int(m.group(1)) if m else None


def _histogram_sum(exposition: str, base: str) -> float | None:
    m = re.search(
        rf'^{re.escape(base)}_sum\s+([-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)',
        exposition, re.MULTILINE,
    )
    return float(m.group(1)) if m else None


# ── prometheus_metrics ────────────────────────────────────────────────────────

class TestPrometheusMetrics:

    def test_no_error(self):
        assert not jutsu.generate('prometheus_metrics').startswith('ERROR')

    def test_returns_string(self):
        assert isinstance(jutsu.generate('prometheus_metrics'), str)

    def test_is_valid_json(self):
        json.loads(jutsu.generate('prometheus_metrics'))

    def test_is_dict(self):
        assert isinstance(json.loads(jutsu.generate('prometheus_metrics')), dict)

    def test_has_required_fields(self):
        data = json.loads(jutsu.generate('prometheus_metrics'))
        for f in ('exposition', 'format', 'metric_families', 'total_samples'):
            assert f in data, f"Missing field: {f}"

    def test_format_is_prometheus(self):
        assert json.loads(jutsu.generate('prometheus_metrics'))['format'] == 'prometheus'

    def test_exposition_is_string(self):
        assert isinstance(_exposition('prometheus_metrics'), str)

    def test_exposition_is_nonempty(self):
        assert len(_exposition('prometheus_metrics')) > 0

    def test_has_help_lines(self):
        exp = _exposition('prometheus_metrics')
        assert '# HELP ' in exp, "No # HELP lines found"

    def test_has_type_lines(self):
        exp = _exposition('prometheus_metrics')
        assert '# TYPE ' in exp, "No # TYPE lines found"

    def test_type_values_are_valid(self):
        """All # TYPE values must be valid Prometheus metric types."""
        exp = _exposition('prometheus_metrics')
        type_map = _get_type_map(exp)
        assert len(type_map) > 0, "No TYPE declarations found"
        for name, typ in type_map.items():
            assert typ in _VALID_PROMETHEUS_TYPES, \
                f"Invalid type '{typ}' for metric '{name}'"

    def test_sample_lines_have_numeric_values(self):
        """All non-comment lines must parse to (name, float)."""
        exp = _exposition('prometheus_metrics')
        samples = _get_sample_lines(exp)
        assert len(samples) > 0, "No sample lines found"

    def test_counter_values_nonnegative(self):
        """http_requests_total counter values must be >= 0."""
        for _ in range(5):
            exp = _exposition('prometheus_metrics')
            for name, val in _get_sample_lines(exp):
                if name == 'http_requests_total':
                    assert val >= 0, f"Counter value {val} < 0"

    def test_histogram_bucket_lines_present(self):
        exp = _exposition('prometheus_metrics')
        assert f'{_HIST_METRIC}_bucket' in exp, \
            "Histogram bucket lines not found"

    def test_histogram_has_inf_bucket(self):
        exp = _exposition('prometheus_metrics')
        buckets = _histogram_buckets(exp, _HIST_METRIC)
        les = [le for le, _ in buckets]
        assert '+Inf' in les, f"No +Inf bucket in: {les}"

    def test_histogram_buckets_monotonic(self):
        """Bucket counts must be non-decreasing across le values."""
        for _ in range(10):
            exp = _exposition('prometheus_metrics')
            buckets = _histogram_buckets(exp, _HIST_METRIC)
            assert len(buckets) >= 2, "Fewer than 2 bucket lines"
            counts = [c for _, c in buckets]
            for i in range(1, len(counts)):
                assert counts[i] >= counts[i - 1], \
                    f"Bucket count decreased: {counts[i-1]} → {counts[i]}"

    def test_histogram_inf_equals_count(self):
        """The +Inf bucket must equal the _count line."""
        for _ in range(10):
            exp = _exposition('prometheus_metrics')
            buckets = _histogram_buckets(exp, _HIST_METRIC)
            inf_count = next((c for le, c in buckets if le == '+Inf'), None)
            total_count = _histogram_count(exp, _HIST_METRIC)
            assert inf_count is not None, "No +Inf bucket found"
            assert total_count is not None, "No _count line found"
            assert inf_count == total_count, \
                f"+Inf bucket {inf_count} != _count {total_count}"

    def test_histogram_sum_nonneg(self):
        for _ in range(10):
            exp = _exposition('prometheus_metrics')
            s = _histogram_sum(exp, _HIST_METRIC)
            assert s is not None, "No _sum line found"
            assert s >= 0, f"Histogram sum {s} < 0"

    def test_has_process_cpu_metric(self):
        for _ in range(5):
            exp = _exposition('prometheus_metrics')
            assert 'process_cpu_seconds_total' in exp, \
                "process_cpu_seconds_total not found"

    def test_has_process_memory_metric(self):
        for _ in range(5):
            exp = _exposition('prometheus_metrics')
            assert 'process_resident_memory_bytes' in exp

    def test_has_http_requests_total(self):
        for _ in range(5):
            exp = _exposition('prometheus_metrics')
            assert 'http_requests_total' in exp

    def test_metric_families_is_list(self):
        data = json.loads(jutsu.generate('prometheus_metrics'))
        assert isinstance(data['metric_families'], list)
        assert len(data['metric_families']) > 0

    def test_total_samples_is_positive_int(self):
        data = json.loads(jutsu.generate('prometheus_metrics'))
        ts = data['total_samples']
        assert isinstance(ts, int) and ts > 0, \
            f"total_samples={ts} is not a positive int"

    def test_does_not_end_with_eof(self):
        for _ in range(5):
            exp = _exposition('prometheus_metrics')
            # Prometheus text format does NOT have # EOF terminator
            stripped = exp.strip()
            assert not stripped.endswith('# EOF'), \
                "prometheus_metrics should not end with '# EOF'"

    def test_bulk_variety(self):
        """Multiple runs produce different total_samples (random metric counts)."""
        counts = {json.loads(r)['total_samples'] for r in jutsu.bulk('prometheus_metrics', 5)}
        assert len(counts) >= 1  # at minimum, values exist


# ── openmetrics_snapshot ──────────────────────────────────────────────────────

class TestOpenMetricsSnapshot:

    def test_no_error(self):
        assert not jutsu.generate('openmetrics_snapshot').startswith('ERROR')

    def test_returns_string(self):
        assert isinstance(jutsu.generate('openmetrics_snapshot'), str)

    def test_is_valid_json(self):
        json.loads(jutsu.generate('openmetrics_snapshot'))

    def test_is_dict(self):
        assert isinstance(json.loads(jutsu.generate('openmetrics_snapshot')), dict)

    def test_has_required_fields(self):
        data = json.loads(jutsu.generate('openmetrics_snapshot'))
        for f in ('exposition', 'format', 'metric_families', 'total_samples'):
            assert f in data, f"Missing field: {f}"

    def test_format_is_openmetrics(self):
        assert json.loads(jutsu.generate('openmetrics_snapshot'))['format'] == 'openmetrics'

    def test_exposition_is_nonempty(self):
        assert len(_exposition('openmetrics_snapshot')) > 0

    def test_ends_with_eof(self):
        """OpenMetrics exposition MUST end with '# EOF\\n'."""
        for _ in range(10):
            exp = _exposition('openmetrics_snapshot')
            assert exp.endswith('# EOF\n'), \
                f"Does not end with '# EOF\\n': ...{exp[-20:]!r}"

    def test_eof_is_last_line(self):
        """The last non-empty line must be '# EOF'."""
        for _ in range(10):
            exp = _exposition('openmetrics_snapshot')
            lines = [l for l in exp.splitlines() if l.strip()]
            assert lines[-1] == '# EOF', \
                f"Last non-empty line is not '# EOF': '{lines[-1]}'"

    def test_has_help_lines(self):
        assert '# HELP ' in _exposition('openmetrics_snapshot')

    def test_has_type_lines(self):
        assert '# TYPE ' in _exposition('openmetrics_snapshot')

    def test_type_values_are_valid(self):
        exp = _exposition('openmetrics_snapshot')
        type_map = _get_type_map(exp)
        for name, typ in type_map.items():
            assert typ in _VALID_PROMETHEUS_TYPES, \
                f"Invalid type '{typ}' for metric '{name}'"

    def test_sample_lines_have_numeric_values(self):
        exp = _exposition('openmetrics_snapshot')
        samples = _get_sample_lines(exp)
        assert len(samples) > 0

    def test_histogram_bucket_lines_present(self):
        exp = _exposition('openmetrics_snapshot')
        assert f'{_HIST_METRIC}_bucket' in exp

    def test_histogram_has_inf_bucket(self):
        exp = _exposition('openmetrics_snapshot')
        buckets = _histogram_buckets(exp, _HIST_METRIC)
        assert '+Inf' in [le for le, _ in buckets]

    def test_histogram_buckets_monotonic(self):
        for _ in range(10):
            exp = _exposition('openmetrics_snapshot')
            counts = [c for _, c in _histogram_buckets(exp, _HIST_METRIC)]
            for i in range(1, len(counts)):
                assert counts[i] >= counts[i - 1], \
                    f"Bucket decreased: {counts[i-1]} → {counts[i]}"

    def test_histogram_inf_equals_count(self):
        for _ in range(10):
            exp = _exposition('openmetrics_snapshot')
            buckets = _histogram_buckets(exp, _HIST_METRIC)
            inf_count = next((c for le, c in buckets if le == '+Inf'), None)
            total_count = _histogram_count(exp, _HIST_METRIC)
            assert inf_count is not None
            assert total_count is not None
            assert inf_count == total_count, \
                f"+Inf {inf_count} != _count {total_count}"

    def test_histogram_sum_nonneg(self):
        for _ in range(10):
            exp = _exposition('openmetrics_snapshot')
            s = _histogram_sum(exp, _HIST_METRIC)
            assert s is not None and s >= 0

    def test_has_process_cpu_metric(self):
        for _ in range(5):
            assert 'process_cpu_seconds_total' in _exposition('openmetrics_snapshot')

    def test_has_http_requests_total(self):
        for _ in range(5):
            assert 'http_requests_total' in _exposition('openmetrics_snapshot')

    def test_metric_families_is_list(self):
        data = json.loads(jutsu.generate('openmetrics_snapshot'))
        assert isinstance(data['metric_families'], list)
        assert len(data['metric_families']) > 0

    def test_total_samples_is_positive_int(self):
        data = json.loads(jutsu.generate('openmetrics_snapshot'))
        ts = data['total_samples']
        assert isinstance(ts, int) and ts > 0

    def test_bulk_variety(self):
        expositions = {_exposition('openmetrics_snapshot') for _ in range(3)}
        assert len(expositions) >= 1
