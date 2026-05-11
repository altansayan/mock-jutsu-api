"""
Tests for God Mode #22 — Borsa Grafiği Simülasyonu (GBM / OHLCV)
Types: ohlcv_candles, market_tick

Core invariants:
  ohlcv_candles:
    - h >= max(o, c)  for every candle
    - l <= min(o, c)  for every candle
    - l <= h          for every candle
    - All prices > 0
    - Volume > 0
    - Timestamps strictly increasing (ISO-8601)
    - Open[i] == Close[i-1]  (candles chain, price continuity)
    - 10-30 candles per series
    - GBM: prices never go to 0 or negative

  market_tick:
    - bid < ask  (positive spread)
    - bid <= price <= ask
    - price > 0
    - size > 0
    - side in ('buy', 'sell')
"""

import json
import pytest
from mockjutsu.core import MockJutsuCore

jutsu = MockJutsuCore()

_VALID_INTERVALS = {'1m', '5m', '15m', '1h', '4h', '1d'}
_VALID_SIDES     = {'buy', 'sell'}


# ── ohlcv_candles ─────────────────────────────────────────────────────────────

class TestOhlcvCandles:

    def test_no_error(self):
        assert not jutsu.generate('ohlcv_candles').startswith('ERROR')

    def test_returns_string(self):
        assert isinstance(jutsu.generate('ohlcv_candles'), str)

    def test_is_valid_json(self):
        json.loads(jutsu.generate('ohlcv_candles'))

    def test_is_dict(self):
        assert isinstance(json.loads(jutsu.generate('ohlcv_candles')), dict)

    def test_has_required_fields(self):
        data = json.loads(jutsu.generate('ohlcv_candles'))
        for field in ('symbol', 'interval', 'candles'):
            assert field in data, f"Missing field: {field}"

    def test_interval_is_valid(self):
        for _ in range(10):
            data = json.loads(jutsu.generate('ohlcv_candles'))
            assert data['interval'] in _VALID_INTERVALS, \
                f"Invalid interval: {data['interval']}"

    def test_candles_is_list(self):
        data = json.loads(jutsu.generate('ohlcv_candles'))
        assert isinstance(data['candles'], list)

    def test_candle_count_between_10_and_30(self):
        for _ in range(10):
            candles = json.loads(jutsu.generate('ohlcv_candles'))['candles']
            assert 10 <= len(candles) <= 30, \
                f"Candle count out of range: {len(candles)}"

    def test_each_candle_has_ohlcv_fields(self):
        candles = json.loads(jutsu.generate('ohlcv_candles'))['candles']
        for i, c in enumerate(candles):
            for f in ('t', 'o', 'h', 'l', 'c', 'v'):
                assert f in c, f"Candle {i} missing field '{f}'"

    def test_high_ge_max_open_close(self):
        """h >= max(o, c) for every candle."""
        for _ in range(20):
            candles = json.loads(jutsu.generate('ohlcv_candles'))['candles']
            for i, c in enumerate(candles):
                assert c['h'] >= max(c['o'], c['c']) - 1e-9, \
                    f"Candle {i}: h={c['h']} < max(o={c['o']}, c={c['c']})"

    def test_low_le_min_open_close(self):
        """l <= min(o, c) for every candle."""
        for _ in range(20):
            candles = json.loads(jutsu.generate('ohlcv_candles'))['candles']
            for i, c in enumerate(candles):
                assert c['l'] <= min(c['o'], c['c']) + 1e-9, \
                    f"Candle {i}: l={c['l']} > min(o={c['o']}, c={c['c']})"

    def test_low_le_high(self):
        """l <= h for every candle."""
        for _ in range(20):
            candles = json.loads(jutsu.generate('ohlcv_candles'))['candles']
            for i, c in enumerate(candles):
                assert c['l'] <= c['h'] + 1e-9, \
                    f"Candle {i}: l={c['l']} > h={c['h']}"

    def test_all_prices_positive(self):
        for _ in range(20):
            candles = json.loads(jutsu.generate('ohlcv_candles'))['candles']
            for i, c in enumerate(candles):
                for field in ('o', 'h', 'l', 'c'):
                    assert c[field] > 0, \
                        f"Candle {i} {field}={c[field]} is not positive"

    def test_volume_positive(self):
        for _ in range(10):
            candles = json.loads(jutsu.generate('ohlcv_candles'))['candles']
            for i, c in enumerate(candles):
                assert c['v'] > 0, f"Candle {i} volume={c['v']} is not positive"

    def test_timestamps_strictly_increasing(self):
        """t[i] > t[i-1] for all consecutive candles."""
        for _ in range(10):
            candles = json.loads(jutsu.generate('ohlcv_candles'))['candles']
            for i in range(1, len(candles)):
                assert candles[i]['t'] > candles[i - 1]['t'], \
                    f"Timestamp not increasing at index {i}"

    def test_open_equals_prev_close(self):
        """Open of candle[i] must equal Close of candle[i-1] (price continuity)."""
        for _ in range(10):
            candles = json.loads(jutsu.generate('ohlcv_candles'))['candles']
            for i in range(1, len(candles)):
                assert abs(candles[i]['o'] - candles[i - 1]['c']) < 1e-9, \
                    f"Open[{i}]={candles[i]['o']} != Close[{i-1}]={candles[i-1]['c']}"

    def test_prices_are_floats_rounded_2dp(self):
        """OHLC prices should have at most 2 decimal places."""
        candles = json.loads(jutsu.generate('ohlcv_candles'))['candles']
        for i, c in enumerate(candles):
            for field in ('o', 'h', 'l', 'c'):
                val = c[field]
                assert round(val, 2) == val, \
                    f"Candle {i} {field}={val} not rounded to 2dp"

    def test_symbol_is_nonempty_string(self):
        for _ in range(10):
            symbol = json.loads(jutsu.generate('ohlcv_candles'))['symbol']
            assert isinstance(symbol, str) and len(symbol) > 0

    def test_bulk_variety_across_runs(self):
        """Multiple runs produce different symbols or different close prices."""
        closes = {json.loads(r)['candles'][-1]['c'] for r in jutsu.bulk('ohlcv_candles', 5)}
        assert len(closes) > 1

    def test_prices_in_reasonable_range(self):
        """Start price between 0.01 and 70000.00 (crypto can go up to 70K)."""
        for _ in range(10):
            candles = json.loads(jutsu.generate('ohlcv_candles'))['candles']
            first_open = candles[0]['o']
            assert 0.01 <= first_open <= 70000.0, \
                f"First open {first_open} out of reasonable range"


# ── market_tick ───────────────────────────────────────────────────────────────

class TestMarketTick:

    def test_no_error(self):
        assert not jutsu.generate('market_tick').startswith('ERROR')

    def test_returns_string(self):
        assert isinstance(jutsu.generate('market_tick'), str)

    def test_is_valid_json(self):
        json.loads(jutsu.generate('market_tick'))

    def test_is_dict(self):
        assert isinstance(json.loads(jutsu.generate('market_tick')), dict)

    def test_has_required_fields(self):
        data = json.loads(jutsu.generate('market_tick'))
        for field in ('symbol', 'timestamp', 'price', 'size', 'bid', 'ask', 'side', 'seq'):
            assert field in data, f"Missing field: {field}"

    def test_bid_lt_ask(self):
        """bid must be strictly less than ask (positive spread)."""
        for _ in range(20):
            data = json.loads(jutsu.generate('market_tick'))
            assert data['bid'] < data['ask'], \
                f"bid={data['bid']} >= ask={data['ask']}"

    def test_price_between_bid_and_ask(self):
        """bid <= price <= ask."""
        for _ in range(20):
            data = json.loads(jutsu.generate('market_tick'))
            assert data['bid'] <= data['price'] <= data['ask'], \
                f"price={data['price']} not in [{data['bid']}, {data['ask']}]"

    def test_price_positive(self):
        for _ in range(20):
            assert json.loads(jutsu.generate('market_tick'))['price'] > 0

    def test_size_positive(self):
        for _ in range(20):
            assert json.loads(jutsu.generate('market_tick'))['size'] > 0

    def test_size_is_integer(self):
        for _ in range(10):
            size = json.loads(jutsu.generate('market_tick'))['size']
            assert isinstance(size, int)

    def test_side_valid(self):
        for _ in range(20):
            assert json.loads(jutsu.generate('market_tick'))['side'] in _VALID_SIDES

    def test_side_distribution(self):
        """Both buy and sell appear across 20 ticks."""
        sides = {json.loads(jutsu.generate('market_tick'))['side'] for _ in range(20)}
        assert len(sides) == 2

    def test_bid_ask_prices_rounded_2dp(self):
        for _ in range(10):
            data = json.loads(jutsu.generate('market_tick'))
            for field in ('bid', 'ask', 'price'):
                val = data[field]
                assert round(val, 2) == val, \
                    f"{field}={val} not rounded to 2dp"

    def test_seq_is_positive_int(self):
        for _ in range(10):
            seq = json.loads(jutsu.generate('market_tick'))['seq']
            assert isinstance(seq, int) and seq > 0

    def test_bulk_unique_ticks(self):
        prices = {json.loads(r)['price'] for r in jutsu.bulk('market_tick', 5)}
        assert len(prices) >= 3
