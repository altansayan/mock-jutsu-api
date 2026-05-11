"""
Tests for God Mode #18 — Causal Event-Sourcing & CDC Generator
Types: event_stream, cdc_event

Core invariants:
  - event_stream : JSON array, first='login', last='logout', all events share
                   correlation_id/session_id/user_id, timestamps strictly increasing,
                   event_ids unique, event_type in valid Markov states
  - cdc_event    : op in {c,u,d}, INSERT→before=None, DELETE→after=None,
                   UPDATE→both dicts, source has db+table
"""

import json
import re
import pytest
from mockjutsu.core import MockJutsuCore

jutsu = MockJutsuCore()

_VALID_EVENT_TYPES = {'login', 'page_view', 'search', 'add_to_cart', 'checkout', 'payment', 'logout'}
_TS_RE = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$')
_REQUIRED_FIELDS = {'event_id', 'correlation_id', 'session_id', 'user_id', 'timestamp', 'event_type', 'payload'}


# ── event_stream ──────────────────────────────────────────────────────────────

class TestEventStream:

    def test_no_error(self):
        assert not jutsu.generate('event_stream').startswith('ERROR')

    def test_returns_string(self):
        assert isinstance(jutsu.generate('event_stream'), str)

    def test_is_valid_json(self):
        json.loads(jutsu.generate('event_stream'))

    def test_is_list(self):
        assert isinstance(json.loads(jutsu.generate('event_stream')), list)

    def test_has_at_least_two_events(self):
        assert len(json.loads(jutsu.generate('event_stream'))) >= 2

    def test_max_16_events(self):
        for _ in range(20):
            assert len(json.loads(jutsu.generate('event_stream'))) <= 16

    def test_first_event_is_login(self):
        events = json.loads(jutsu.generate('event_stream'))
        assert events[0]['event_type'] == 'login'

    def test_last_event_is_logout(self):
        for _ in range(20):
            events = json.loads(jutsu.generate('event_stream'))
            assert events[-1]['event_type'] == 'logout', f"Last event: {events[-1]['event_type']}"

    def test_all_events_share_correlation_id(self):
        events = json.loads(jutsu.generate('event_stream'))
        corr_ids = {e['correlation_id'] for e in events}
        assert len(corr_ids) == 1

    def test_all_events_share_session_id(self):
        events = json.loads(jutsu.generate('event_stream'))
        sess_ids = {e['session_id'] for e in events}
        assert len(sess_ids) == 1

    def test_all_events_share_user_id(self):
        events = json.loads(jutsu.generate('event_stream'))
        user_ids = {e['user_id'] for e in events}
        assert len(user_ids) == 1

    def test_event_ids_are_unique(self):
        events = json.loads(jutsu.generate('event_stream'))
        ids = [e['event_id'] for e in events]
        assert len(set(ids)) == len(ids)

    def test_timestamps_are_monotonically_increasing(self):
        events = json.loads(jutsu.generate('event_stream'))
        for i in range(1, len(events)):
            assert events[i]['timestamp'] > events[i-1]['timestamp'], (
                f"Timestamp regression at index {i}: {events[i]['timestamp']} <= {events[i-1]['timestamp']}"
            )

    def test_event_type_from_valid_set(self):
        events = json.loads(jutsu.generate('event_stream'))
        for e in events:
            assert e['event_type'] in _VALID_EVENT_TYPES, f"Unknown event_type: {e['event_type']}"

    def test_each_event_has_required_fields(self):
        events = json.loads(jutsu.generate('event_stream'))
        for e in events:
            missing = _REQUIRED_FIELDS - set(e.keys())
            assert not missing, f"Missing fields: {missing}"

    def test_each_event_has_dict_payload(self):
        events = json.loads(jutsu.generate('event_stream'))
        for e in events:
            assert isinstance(e['payload'], dict), f"payload is not dict for {e['event_type']}"

    def test_timestamp_format(self):
        """Timestamps must be ISO 8601 with milliseconds: 2026-05-11T20:15:30.123Z"""
        events = json.loads(jutsu.generate('event_stream'))
        for e in events:
            assert _TS_RE.match(e['timestamp']), f"Bad timestamp format: {e['timestamp']!r}"

    def test_bulk_unique_correlation_ids(self):
        results = jutsu.bulk('event_stream', 5)
        corr_ids = set()
        for r in results:
            events = json.loads(r)
            corr_ids.add(events[0]['correlation_id'])
        assert len(corr_ids) == 5


# ── cdc_event ─────────────────────────────────────────────────────────────────

class TestCdcEvent:

    def test_no_error(self):
        assert not jutsu.generate('cdc_event').startswith('ERROR')

    def test_returns_string(self):
        assert isinstance(jutsu.generate('cdc_event'), str)

    def test_is_valid_json(self):
        json.loads(jutsu.generate('cdc_event'))

    def test_is_dict(self):
        assert isinstance(json.loads(jutsu.generate('cdc_event')), dict)

    def test_has_op_field(self):
        assert 'op' in json.loads(jutsu.generate('cdc_event'))

    def test_op_is_valid(self):
        for _ in range(20):
            assert json.loads(jutsu.generate('cdc_event'))['op'] in {'c', 'u', 'd'}

    def test_has_ts_ms_field(self):
        assert 'ts_ms' in json.loads(jutsu.generate('cdc_event'))

    def test_ts_ms_is_int(self):
        assert isinstance(json.loads(jutsu.generate('cdc_event'))['ts_ms'], int)

    def test_has_source_field(self):
        assert 'source' in json.loads(jutsu.generate('cdc_event'))

    def test_source_has_db_and_table(self):
        source = json.loads(jutsu.generate('cdc_event'))['source']
        assert 'db' in source and 'table' in source

    def test_has_before_and_after_fields(self):
        data = json.loads(jutsu.generate('cdc_event'))
        assert 'before' in data and 'after' in data

    def test_operation_before_after_consistency(self):
        """INSERT→before=None, DELETE→after=None, UPDATE→both dicts (30 iterations)."""
        for _ in range(30):
            data = json.loads(jutsu.generate('cdc_event'))
            op = data['op']
            if op == 'c':
                assert data['before'] is None, "INSERT must have before=None"
                assert isinstance(data['after'], dict), "INSERT must have after=dict"
            elif op == 'd':
                assert isinstance(data['before'], dict), "DELETE must have before=dict"
                assert data['after'] is None, "DELETE must have after=None"
            else:  # 'u'
                assert isinstance(data['before'], dict), "UPDATE must have before=dict"
                assert isinstance(data['after'], dict), "UPDATE must have after=dict"

    def test_bulk_op_distribution(self):
        """Multiple operation types appear across 30 runs."""
        ops = {json.loads(jutsu.generate('cdc_event'))['op'] for _ in range(30)}
        assert len(ops) > 1

    def test_bulk_table_distribution(self):
        """Multiple tables appear across 20 runs."""
        tables = {json.loads(jutsu.generate('cdc_event'))['source']['table'] for _ in range(20)}
        assert len(tables) > 1
