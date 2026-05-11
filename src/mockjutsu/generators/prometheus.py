"""
mock-jutsu — Prometheus / OpenMetrics Exposition Format Generator
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)

Supported types:
  prometheus_metrics   — Classic Prometheus text exposition format.
                         Metric families: process (CPU/memory/fds), HTTP counter,
                         HTTP request duration histogram, Go runtime (optional).
                         Returns JSON with 'exposition' (raw text) + parsed metadata.
  openmetrics_snapshot — OpenMetrics format (OTLP-compatible superset of Prometheus).
                         Same metric families; ends with mandatory '# EOF' terminator.
                         Returns JSON with 'exposition' + metadata.

Prometheus / OpenMetrics exposition rules (zero external dependencies):
  # HELP metric_name description
  # TYPE metric_name counter|gauge|histogram|summary
  metric_name{label="value"} numeric_value
  Histogram: _bucket{le="N"} count (monotonically non-decreasing), _sum, _count
  Checksum: none (text format, no embedded checksum)
  OpenMetrics: must end with '# EOF\n' terminator

Zero external dependencies: datetime, json, math, random (stdlib only).
"""

import datetime
import json
import math
import random

# ── Constants ─────────────────────────────────────────────────────────────────

_HTTP_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']

_HTTP_PATHS = [
    '/', '/api/health', '/api/v1/users', '/api/v1/orders',
    '/api/v1/products', '/api/v1/data', '/api/v1/auth/token', '/metrics',
]

_HTTP_STATUS_OK  = ['200', '201', '204']
_HTTP_STATUS_ERR = ['400', '401', '403', '404', '500', '502']

# Prometheus default histogram bucket boundaries
_HIST_LE = [
    ('0.005', 0.005), ('0.01', 0.01), ('0.025', 0.025), ('0.05', 0.05),
    ('0.1',   0.1),   ('0.25', 0.25), ('0.5',   0.5),   ('1',    1.0),
    ('2.5',   2.5),   ('5',    5.0),  ('10',    10.0),
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _fmt(v: float) -> str:
    """Prometheus-compatible number formatting."""
    if isinstance(v, int) or (v == int(v) and abs(v) < 1e15):
        return str(int(v))
    if abs(v) < 1e-3 or abs(v) >= 1e10:
        return f"{v:.6e}"
    s = f"{v:.4f}".rstrip('0')
    return s.rstrip('.')


def _mono_buckets(total_count: int) -> list[tuple[str, int]]:
    """
    Generate monotonically non-decreasing histogram bucket counts.
    The final (+Inf) bucket equals total_count exactly.
    """
    fracs = sorted(random.uniform(0.05, 1.0) for _ in range(len(_HIST_LE)))
    top = fracs[-1]
    counts = [int(total_count * (f / top)) for f in fracs]
    # Guarantee non-decreasing after int() truncation
    for i in range(1, len(counts)):
        counts[i] = max(counts[i], counts[i - 1])
    # Clamp top bucket to total_count (float rounding)
    counts[-1] = min(counts[-1], total_count)
    result = [(le_str, counts[i]) for i, (le_str, _) in enumerate(_HIST_LE)]
    result.append(('+Inf', total_count))
    return result


# ── Metric family builders ────────────────────────────────────────────────────

def _build_process_metrics() -> list[str]:
    cpu     = round(random.uniform(0.5, 100000.0), 2)
    rss     = random.randint(10 * 1024 * 1024, 4 * 1024 * 1024 * 1024)
    vms     = rss + random.randint(50 * 1024 * 1024, 512 * 1024 * 1024)
    fds     = random.randint(5, 512)
    age_s   = random.randint(3600, 86400 * 30)
    start_t = round(
        datetime.datetime.now(datetime.timezone.utc).timestamp() - age_s, 3
    )

    lines = []
    for name, typ, val, help_txt in [
        ('process_cpu_seconds_total',    'counter', cpu,     'Total user and system CPU time spent in seconds.'),
        ('process_resident_memory_bytes','gauge',   rss,     'Resident memory size in bytes.'),
        ('process_virtual_memory_bytes', 'gauge',   vms,     'Virtual memory size in bytes.'),
        ('process_open_fds',             'gauge',   fds,     'Number of open file descriptors.'),
        ('process_start_time_seconds',   'gauge',   start_t, 'Start time of the process since unix epoch in seconds.'),
    ]:
        lines += [
            f'# HELP {name} {help_txt}',
            f'# TYPE {name} {typ}',
            f'{name} {_fmt(val)}',
        ]
    return lines


def _build_http_counter() -> list[str]:
    name  = 'http_requests_total'
    lines = [
        f'# HELP {name} Total number of HTTP requests received.',
        f'# TYPE {name} counter',
    ]
    methods  = random.sample(_HTTP_METHODS, random.randint(2, 4))
    paths    = random.sample(_HTTP_PATHS,   random.randint(2, 4))
    for method in methods:
        for path in paths:
            status = random.choice(_HTTP_STATUS_OK * 3 + _HTTP_STATUS_ERR)
            count  = random.randint(1, 100_000)
            lines.append(
                f'{name}{{method="{method}",path="{path}",status="{status}"}} {count}'
            )
    return lines


def _build_http_histogram() -> list[str]:
    name        = 'http_request_duration_seconds'
    total_count = random.randint(200, 50_000)
    avg_dur     = random.uniform(0.01, 1.0)
    total_sum   = round(total_count * avg_dur * random.uniform(0.8, 1.2), 3)

    lines = [
        f'# HELP {name} HTTP request latency in seconds.',
        f'# TYPE {name} histogram',
    ]
    for le_str, bucket_count in _mono_buckets(total_count):
        lines.append(f'{name}_bucket{{le="{le_str}"}} {bucket_count}')
    lines.append(f'{name}_sum {_fmt(total_sum)}')
    lines.append(f'{name}_count {total_count}')
    return lines


def _build_go_metrics() -> list[str]:
    goroutines = random.randint(5, 200)
    alloc      = random.randint(1 * 1024 * 1024, 500 * 1024 * 1024)
    gc_count   = random.randint(1, 2000)
    gc_sum     = round(gc_count * random.uniform(1e-5, 5e-4), 6)

    lines = []
    for name, typ, val, help_txt in [
        ('go_goroutines',           'gauge', goroutines, 'Number of goroutines that currently exist.'),
        ('go_memstats_alloc_bytes', 'gauge', alloc,      'Number of bytes allocated and still in use.'),
    ]:
        lines += [
            f'# HELP {name} {help_txt}',
            f'# TYPE {name} {typ}',
            f'{name} {_fmt(val)}',
        ]

    # GC summary
    name    = 'go_gc_duration_seconds'
    quants  = [0, 0.25, 0.5, 0.75, 1]
    q_vals  = sorted(random.uniform(1e-6, 1e-3) for _ in range(5))
    lines  += [
        f'# HELP {name} A summary of GC invocation durations.',
        f'# TYPE {name} summary',
    ]
    for q, v in zip(quants, q_vals):
        lines.append(f'{name}{{quantile="{q}"}} {_fmt(v)}')
    lines.append(f'{name}_sum {_fmt(gc_sum)}')
    lines.append(f'{name}_count {gc_count}')
    return lines


def _assemble(blocks: list[list[str]], terminator: str | None = None) -> str:
    """Join metric blocks with blank-line separators."""
    sections = []
    for block in blocks:
        if block:
            sections.append('\n'.join(block))
    body = '\n\n'.join(sections) + '\n'
    if terminator:
        body += terminator + '\n'
    return body


def _metadata(exposition: str) -> tuple[list[str], int]:
    """Return (metric_families_list, total_sample_count)."""
    families = [
        line.split()[2]
        for line in exposition.splitlines()
        if line.startswith('# TYPE ')
    ]
    samples = sum(
        1 for line in exposition.splitlines()
        if line and not line.startswith('#')
    )
    return families, samples


# ── Public generators ─────────────────────────────────────────────────────────

def generate_prometheus_metrics() -> str:
    """Classic Prometheus text exposition format."""
    blocks = [
        _build_process_metrics(),
        _build_http_counter(),
        _build_http_histogram(),
    ]
    if random.random() < 0.7:
        blocks.append(_build_go_metrics())

    exposition = _assemble(blocks)
    families, samples = _metadata(exposition)

    return json.dumps({
        'exposition':      exposition,
        'format':          'prometheus',
        'metric_families': families,
        'total_samples':   samples,
    }, ensure_ascii=False)


def generate_openmetrics_snapshot() -> str:
    """OpenMetrics exposition format — identical content, mandatory '# EOF' terminator."""
    blocks = [
        _build_process_metrics(),
        _build_http_counter(),
        _build_http_histogram(),
    ]
    if random.random() < 0.7:
        blocks.append(_build_go_metrics())

    exposition = _assemble(blocks, terminator='# EOF')
    families, samples = _metadata(exposition)

    return json.dumps({
        'exposition':      exposition,
        'format':          'openmetrics',
        'metric_families': families,
        'total_samples':   samples,
    }, ensure_ascii=False)


# ── Generator class ────────────────────────────────────────────────────────────

class PrometheusGenerator:
    """Prometheus / OpenMetrics exposition format generator."""

    def generate(self, data_type: str, **kwargs) -> str:
        if data_type == 'prometheus_metrics':
            return generate_prometheus_metrics()
        if data_type == 'openmetrics_snapshot':
            return generate_openmetrics_snapshot()
        return f"ERROR: Unknown type '{data_type}'"
