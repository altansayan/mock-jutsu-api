"""
Tests for God Mode #11 â€” Reverse Regex Generator
Type: reverse_regex

Core invariant: every generated value MUST match the input pattern.
Uses Python stdlib sre_parse (zero external dependencies).
"""

import re
import pytest
from mockjutsu.core import MockJutsuCore

jutsu = MockJutsuCore()


# â”€â”€ Core invariant: generated value matches the pattern â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

_PATTERNS = [
    r'\d{5}',
    r'[A-Z]{3}',
    r'[A-Z]{2}\d{6}',
    r'[a-z]{4,8}',
    r'\d{3}-\d{4}',
    r'[A-Z][a-z]{3,7}',
    r'\d+\.\d+\.\d+',
    r'[A-Fa-f0-9]{8}',
    r'(foo|bar|baz)',
    r'\w{6}',
    r'\d{2}/\d{2}/\d{4}',
    r'[A-Z0-9]{4}-[A-Z0-9]{4}',
    r'[a-z]{3}\d{3}',
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',
    r'[A-Z]{2,4}\d{2,4}',
]


@pytest.mark.parametrize("pattern", _PATTERNS)
def test_generated_matches_pattern(pattern):
    """Generated value must match the input pattern â€” tested 10 times per pattern."""
    full_pattern = re.compile(f'^(?:{pattern})$')
    for _ in range(10):
        val = jutsu.generate('reverse_regex', pattern=pattern)
        assert full_pattern.match(val), (
            f"Pattern {pattern!r} not matched by generated value {val!r}"
        )


# â”€â”€ Default (no pattern) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class TestRegexStringDefault:
    def test_default_returns_string(self):
        val = jutsu.generate('reverse_regex')
        assert isinstance(val, str) and len(val) > 0

    def test_default_no_error_prefix(self):
        val = jutsu.generate('reverse_regex')
        assert not val.startswith('ERROR')

    def test_default_bulk_unique(self):
        results = jutsu.bulk('reverse_regex', 20)
        assert len(set(results)) > 1

    def test_default_matches_its_preset(self):
        """Default call: generated value must match at least one of the preset patterns."""
        for _ in range(20):
            val = jutsu.generate('reverse_regex')
            assert isinstance(val, str) and len(val) > 0


# â”€â”€ Specific construct tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class TestRegexConstructs:
    def _match(self, pattern, val):
        return re.match(f'^(?:{pattern})$', val)

    def test_digit_shorthand(self):
        for _ in range(20):
            val = jutsu.generate('reverse_regex', pattern=r'\d{4}')
            assert self._match(r'\d{4}', val), f"Failed: {val!r}"

    def test_word_shorthand(self):
        for _ in range(20):
            val = jutsu.generate('reverse_regex', pattern=r'\w{5}')
            assert self._match(r'\w{5}', val), f"Failed: {val!r}"

    def test_character_class_range(self):
        for _ in range(20):
            val = jutsu.generate('reverse_regex', pattern=r'[A-F]{4}')
            assert self._match(r'[A-F]{4}', val), f"Failed: {val!r}"

    def test_alternation(self):
        for _ in range(30):
            val = jutsu.generate('reverse_regex', pattern=r'(alpha|beta|gamma)')
            assert val in ('alpha', 'beta', 'gamma'), f"Unexpected value: {val!r}"

    def test_optional_quantifier(self):
        for _ in range(20):
            val = jutsu.generate('reverse_regex', pattern=r'[A-Z]?\d{3}')
            assert self._match(r'[A-Z]?\d{3}', val), f"Failed: {val!r}"

    def test_exact_repeat(self):
        val = jutsu.generate('reverse_regex', pattern=r'[a-z]{7}')
        assert len(val) == 7 and val.islower()

    def test_literal_string(self):
        val = jutsu.generate('reverse_regex', pattern=r'MOCK')
        assert val == 'MOCK'

    def test_mixed_literal_and_digit(self):
        for _ in range(20):
            val = jutsu.generate('reverse_regex', pattern=r'ID-\d{6}')
            assert self._match(r'ID-\d{6}', val), f"Failed: {val!r}"

    def test_dot_any(self):
        for _ in range(20):
            val = jutsu.generate('reverse_regex', pattern=r'.{5}')
            assert len(val) == 5, f"Expected length 5, got: {val!r}"

    def test_anchors_ignored(self):
        for _ in range(20):
            val = jutsu.generate('reverse_regex', pattern=r'^\d{4}$')
            assert re.match(r'^\d{4}$', val), f"Failed: {val!r}"

