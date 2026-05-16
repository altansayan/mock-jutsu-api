"""
mock-jutsu — Causal Event-Sourcing & CDC Generator
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)

Supported types:
  event_stream — Markov Chain user-journey event sequence (Login → Browse → Cart → Checkout → Logout)
                 JSON array; each event carries event_id, correlation_id, session_id, user_id,
                 ISO-8601 timestamp, event_type, payload.  All events in a sequence share the
                 same correlation_id/session_id/user_id.  Timestamps strictly increase.
  cdc_event    — Debezium-style Change Data Capture event (INSERT / UPDATE / DELETE)
                 JSON object: op (c/u/d), ts_ms, source (db+table), before/after payloads.
                 INSERT → before=null; DELETE → after=null; UPDATE → both present.

Zero external dependencies: datetime, json, random, uuid (stdlib only).
"""

import datetime
import json
import random
import uuid


# ── Markov Chain — user journey ───────────────────────────────────────────────

_TRANSITIONS: dict = {
    'login':        [('page_view', 0.80), ('logout', 0.20)],
    'page_view':    [('page_view', 0.30), ('search', 0.30), ('add_to_cart', 0.20), ('checkout', 0.10), ('logout', 0.10)],
    'search':       [('page_view', 0.40), ('add_to_cart', 0.30), ('search', 0.20), ('logout', 0.10)],
    'add_to_cart':  [('page_view', 0.30), ('add_to_cart', 0.20), ('checkout', 0.40), ('logout', 0.10)],
    'checkout':     [('payment', 0.70), ('add_to_cart', 0.10), ('logout', 0.20)],
    'payment':      [('logout', 0.90), ('page_view', 0.10)],
    'logout':       [],
}

VALID_EVENT_TYPES = set(_TRANSITIONS.keys())

_PAGES        = ['/', '/products', '/category/electronics', '/category/clothing', '/about', '/deals']
_SEARCH_TERMS = ['laptop', 'shoes', 'headphones', 'keyboard', 'monitor', 'jacket', 'phone', 'tablet']
_PAY_METHODS_EVENT = ['credit_card', 'paypal', 'bank_transfer', 'crypto']


def _rand_uuid() -> str:
    return str(uuid.uuid4())


def _rand_ip() -> str:
    return f"{random.randint(1,254)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"


def _next_state(current: str):
    transitions = _TRANSITIONS.get(current, [])
    if not transitions:
        return None
    r = random.random()
    cumul = 0.0
    for state, prob in transitions:
        cumul += prob
        if r < cumul:
            return state
    return transitions[-1][0]


def _payload(event_type: str) -> dict:
    if event_type == 'login':
        return {'method': random.choice(['password', 'oauth', 'sso']), 'ip': _rand_ip()}
    if event_type == 'page_view':
        return {'url': random.choice(_PAGES), 'referrer': random.choice(['direct', 'google', 'email', 'social'])}
    if event_type == 'search':
        return {'query': random.choice(_SEARCH_TERMS), 'results': random.randint(0, 250)}
    if event_type == 'add_to_cart':
        return {'sku': f"SKU-{random.randint(10000,99999)}", 'quantity': random.randint(1, 5), 'price': round(random.uniform(9.99, 499.99), 2)}
    if event_type == 'checkout':
        return {'items': random.randint(1, 8), 'total': round(random.uniform(19.99, 1999.99), 2), 'currency': 'USD'}
    if event_type == 'payment':
        return {'method': random.choice(_PAY_METHODS_EVENT), 'status': 'success', 'amount': round(random.uniform(19.99, 1999.99), 2)}
    if event_type == 'logout':
        return {'reason': random.choice(['user_initiated', 'session_timeout', 'inactivity'])}
    return {}


def generate_event_stream(max_steps: int = 15) -> str:
    """Markov Chain user-journey sequence: Login → … → Logout, as a JSON array."""
    correlation_id = _rand_uuid()
    session_id     = _rand_uuid()
    user_id        = _rand_uuid()

    ts = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(
        days=random.randint(0, 6),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )

    events = []
    state  = 'login'

    for _ in range(max_steps):
        events.append({
            'event_id':       _rand_uuid(),
            'aggregate_id':   user_id,
            'aggregate_type': 'User',
            'correlation_id': correlation_id,
            'session_id':     session_id,
            'user_id':        user_id,
            'timestamp':      ts.strftime('%Y-%m-%dT%H:%M:%S.') + f"{random.randint(0, 999):03d}Z",
            'event_type':     state,
            'payload':        _payload(state),
        })
        ts += datetime.timedelta(seconds=random.randint(5, 120))

        if state == 'logout':
            break
        nxt = _next_state(state)
        if nxt is None:
            break
        state = nxt

    # Guarantee terminal logout when max_steps exhausted before hitting logout
    if events[-1]['event_type'] != 'logout':
        events.append({
            'event_id':       _rand_uuid(),
            'aggregate_id':   user_id,
            'aggregate_type': 'User',
            'correlation_id': correlation_id,
            'session_id':     session_id,
            'user_id':        user_id,
            'timestamp':      ts.strftime('%Y-%m-%dT%H:%M:%S.') + f"{random.randint(0, 999):03d}Z",
            'event_type':     'logout',
            'payload':        _payload('logout'),
        })

    return json.dumps(events, ensure_ascii=False)


# ── CDC Event (Debezium-style) ─────────────────────────────────────────────────

_CDC_TABLES: dict = {
    'orders':   {'order_id': 'uuid', 'user_id': 'uuid', 'total': 'decimal',
                 'status': 'order_status', 'created_at': 'ts'},
    'users':    {'user_id': 'uuid', 'email': 'email', 'full_name': 'name', 'created_at': 'ts'},
    'products': {'product_id': 'uuid', 'name': 'product_name', 'price': 'decimal', 'stock': 'pos_int'},
    'payments': {'payment_id': 'uuid', 'order_id': 'uuid', 'amount': 'decimal',
                 'method': 'pay_method', 'status': 'pay_status'},
}

_ORDER_STATUSES = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
_PAY_STATUSES   = ['pending', 'authorized', 'captured', 'failed', 'refunded']
_PAY_METHODS    = ['credit_card', 'debit_card', 'paypal', 'bank_transfer', 'crypto']
_PRODUCT_NAMES  = ['Laptop Pro 15"', 'Wireless Headset', 'USB-C Hub 7-in-1', 'Mechanical Keyboard', 'Monitor 27" 4K']
_FULL_NAMES     = ['Alice Smith', 'Bob Johnson', 'Carol Lee', 'David Park', 'Emma Wilson']


def _gen_field(ftype: str):
    if ftype == 'uuid':         return _rand_uuid()
    if ftype == 'decimal':      return round(random.uniform(1.0, 9999.99), 2)
    if ftype == 'pos_int':      return random.randint(0, 1000)
    if ftype == 'email':        return f"user{random.randint(1000, 9999)}@example.com"
    if ftype == 'name':         return random.choice(_FULL_NAMES)
    if ftype == 'ts':           return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    if ftype == 'order_status': return random.choice(_ORDER_STATUSES)
    if ftype == 'pay_status':   return random.choice(_PAY_STATUSES)
    if ftype == 'pay_method':   return random.choice(_PAY_METHODS)
    if ftype == 'product_name': return random.choice(_PRODUCT_NAMES)
    return None


def _gen_row(schema: dict) -> dict:
    return {field: _gen_field(ftype) for field, ftype in schema.items()}


def generate_cdc_event() -> str:
    """Debezium-style CDC event: INSERT(c), UPDATE(u), or DELETE(d) as a JSON object."""
    table  = random.choice(list(_CDC_TABLES.keys()))
    schema = _CDC_TABLES[table]
    op     = random.choices(['c', 'u', 'd'], weights=[0.30, 0.50, 0.20])[0]

    ts_ms = int(datetime.datetime.now(datetime.timezone.utc).timestamp() * 1000) + random.randint(-86_400_000, 0)

    before_row = _gen_row(schema)
    after_row  = _gen_row(schema)
    # Keep primary key consistent across before/after for UPDATE
    pk_field = next(iter(schema))
    after_row[pk_field] = before_row[pk_field]

    if op == 'c':      # INSERT — no previous state
        before, after = None, after_row
    elif op == 'd':    # DELETE — no subsequent state
        before, after = before_row, None
    else:              # UPDATE — both states present
        before, after = before_row, after_row

    return json.dumps({
        'op':     op,
        'ts_ms':  ts_ms,
        'source': {
            'version':   '2.3.0',
            'connector': 'postgresql',
            'db':        'mockdb',
            'table':     table,
        },
        'before': before,
        'after':  after,
    }, ensure_ascii=False)


# ── Generator class ────────────────────────────────────────────────────────────

class EventSourcingGenerator:
    """Markov Chain event stream and Debezium-style CDC event generator."""

    def generate(self, data_type: str, **kwargs) -> str:
        if data_type == 'event_stream':
            return generate_event_stream()
        if data_type == 'cdc_event':
            return generate_cdc_event()
        return f"ERROR: Unknown type '{data_type}'"
