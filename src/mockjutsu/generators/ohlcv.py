"""
mock-jutsu — OHLCV & Market Tick Generator (Geometric Brownian Motion)
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)

Supported types:
  ohlcv_candles — OHLCV candlestick series via Geometric Brownian Motion.
                  H >= max(O,C), L <= min(O,C), Open[i] = Close[i-1].
                  Intervals: 1m, 5m, 15m, 1h, 4h, 1d.
  market_tick   — Individual exchange trade tick.
                  bid < price <= ask, positive spread, side buy/sell.

GBM price model (zero external dependencies):
  S(t+dt) = S(t) × exp((μ - σ²/2)×dt + σ×√dt×Z)
  where Z ~ N(0,1) via random.gauss (stdlib).

Zero external dependencies: datetime, json, math, random, uuid (stdlib only).
"""

import datetime
import json
import math
import random
import uuid


# ── Symbols ───────────────────────────────────────────────────────────────────

_SYMBOLS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'NFLX',
    'BABA', 'BRK', 'JPM', 'GS', 'BAC', 'C', 'WMT', 'COST', 'XOM',
    'CVX', 'JNJ', 'PFE', 'AMD', 'INTC', 'ORCL', 'SAP', 'ASML',
    'THYAO', 'EREGL', 'AKBNK', 'GARAN', 'SISE',
    'BTC-USD', 'ETH-USD', 'SOL-USD', 'XRP-USD',
]

_INTERVALS = ['1m', '5m', '15m', '1h', '4h', '1d']

# Interval → seconds (for timestamp stepping)
_INTERVAL_SECS = {
    '1m':  60,
    '5m':  300,
    '15m': 900,
    '1h':  3600,
    '4h':  14400,
    '1d':  86400,
}

# Per-interval GBM σ (daily vol ~25%, scaled by √(dt/86400))
_BASE_DAILY_VOL = 0.25


# ── Helpers ───────────────────────────────────────────────────────────────────

def _now_minus(days: int = 0) -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days)


def _iso(dt: datetime.datetime) -> str:
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


def _gbm_step(price: float, mu: float, sigma: float, dt_frac: float) -> float:
    """One GBM step. Returns new price > 0."""
    z = random.gauss(0.0, 1.0)
    log_return = (mu - 0.5 * sigma * sigma) * dt_frac + sigma * math.sqrt(dt_frac) * z
    return round(max(0.01, price * math.exp(log_return)), 2)


# ── OHLCV candles ─────────────────────────────────────────────────────────────

def generate_ohlcv_candles() -> str:
    """
    OHLCV candlestick time series via Geometric Brownian Motion.

    Each candle:
      - Open  = previous Close (price continuity)
      - Close = GBM step from Open
      - High  = max(Open, Close) × (1 + uniform(0, intra_range))
      - Low   = min(Open, Close) × (1 - uniform(0, intra_range))
      - Volume = lognormal random (lot-sized)
    """
    symbol   = random.choice(_SYMBOLS)
    interval = random.choice(_INTERVALS)
    n        = random.randint(10, 30)

    interval_secs = _INTERVAL_SECS[interval]
    dt_frac       = interval_secs / 86400.0      # fraction of a trading day
    sigma         = _BASE_DAILY_VOL * math.sqrt(dt_frac)
    mu            = random.uniform(-0.0005, 0.0005)  # slight drift

    # Starting price: realistic range per symbol type
    if '-USD' in symbol:
        start_price = round(random.uniform(100.0, 70000.0), 2)
    else:
        start_price = round(random.uniform(5.0, 2000.0), 2)

    # Start timestamp: go back n intervals from now
    start_dt   = _now_minus(days=0)
    start_dt  -= datetime.timedelta(seconds=interval_secs * n)
    start_dt   = start_dt.replace(second=0, microsecond=0)

    # Base volume (avg trade size per interval)
    base_vol = random.randint(10_000, 5_000_000)

    candles   = []
    prev_close = start_price

    for i in range(n):
        o = prev_close
        c = _gbm_step(o, mu, sigma, dt_frac)

        # Intra-candle high/low: O and C define the body; wicks extend ±0-3%
        intra_range = random.uniform(0.0, 0.03)
        body_hi     = max(o, c)
        body_lo     = min(o, c)
        h = round(body_hi * (1.0 + random.uniform(0.0, intra_range)), 2)
        l = round(body_lo * (1.0 - random.uniform(0.0, intra_range)), 2)
        l = max(0.01, l)

        # Volume: lognormal around base, integer lot
        v = max(1, int(random.lognormvariate(math.log(base_vol), 0.5)))

        ts = _iso(start_dt + datetime.timedelta(seconds=interval_secs * i))

        candles.append({'t': ts, 'o': o, 'h': h, 'l': l, 'c': c, 'v': v})
        prev_close = c

    return json.dumps({
        'symbol':   symbol,
        'interval': interval,
        'candles':  candles,
    }, ensure_ascii=False)


# ── Market Tick ───────────────────────────────────────────────────────────────

def generate_market_tick() -> str:
    """
    Individual exchange trade tick.

    Invariants:
      - bid < ask   (positive spread, typically 0.01–0.05 for liquid equities)
      - bid <= price <= ask
      - side: 'buy' if price closer to ask, else 'sell' (Lee-Ready heuristic)
    """
    symbol    = random.choice(_SYMBOLS)
    mid_price = round(random.uniform(5.0, 2000.0), 2)

    # Spread: 0.01–0.10 for equities; wider for crypto
    spread  = round(random.uniform(0.01, 0.10), 2)
    half    = round(spread / 2, 2)
    bid     = round(max(0.01, mid_price - half), 2)
    ask     = round(bid + spread, 2)

    # Trade price: strictly bid < price <= ask
    price = round(random.uniform(bid, ask), 2)
    price = round(max(bid, min(ask, price)), 2)
    if price <= bid:
        price = round(min(ask, bid + 0.01), 2)

    # Side: Lee-Ready rule — above midpoint = buy, below = sell
    midpoint = round((bid + ask) / 2, 2)
    side = 'buy' if price >= midpoint else 'sell'

    size = random.randint(1, 10000) * random.choice([1, 10, 100])
    seq  = random.randint(1, 999_999_999)

    now_ms = datetime.datetime.now(datetime.timezone.utc)
    ts     = now_ms.strftime('%Y-%m-%dT%H:%M:%S.') + f"{now_ms.microsecond // 1000:03d}Z"

    return json.dumps({
        'symbol':    symbol,
        'timestamp': ts,
        'price':     price,
        'size':      size,
        'bid':       bid,
        'ask':       ask,
        'side':      side,
        'seq':       seq,
    }, ensure_ascii=False)


# ── Generator class ────────────────────────────────────────────────────────────

class OhlcvGenerator:
    """OHLCV candlestick (GBM) and market tick generator."""

    def generate(self, data_type: str, **kwargs) -> str:
        if data_type == 'ohlcv_candles':
            return generate_ohlcv_candles()
        if data_type == 'market_tick':
            return generate_market_tick()
        return f"ERROR: Unknown type '{data_type}'"
