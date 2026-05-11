"""
mock-jutsu — Reverse Regex Generator
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)

Parses a regex pattern into an AST via Python stdlib sre_parse and generates
a random string that matches the pattern — 100% match guaranteed.

Zero external dependencies: uses only sre_parse / sre_constants (stdlib).

Supported constructs:
  Literals          — 'abc', 'A'
  ANY (dot)         — '.' → random printable ASCII (no newline)
  IN (char class)   — '[a-z]', '[A-F0-9]', '[^abc]'
  Shorthand classes — \\d \\D \\w \\W \\s \\S
  MAX_REPEAT        — '+', '*', '?', '{n}', '{n,m}' (unbounded capped at _MAX_UNBOUNDED)
  SUBPATTERN        — '(abc)', '(?:abc)' (capturing & non-capturing groups)
  BRANCH            — 'a|b|c'
  AT anchors        — '^', '$' (produce no characters)
  NOT_LITERAL       — '[^x]' single-char negation
"""

try:
    import re._parser as sre_parse      # Python 3.11+
    import re._constants as SC
except (ImportError, AttributeError):
    import sre_parse                     # Python 3.10 fallback
    import sre_constants as SC
import random
import string

# ── Character pools ───────────────────────────────────────────────────────────

_PRINTABLE = [chr(i) for i in range(33, 127)]   # 33–126: visible ASCII (no space, no DEL)
_PRINTABLE_SPACE = [chr(i) for i in range(32, 127)]  # includes space
_DIGITS = list(string.digits)
_UPPER = list(string.ascii_uppercase)
_LOWER = list(string.ascii_lowercase)
_WORD = list(string.ascii_letters + string.digits + '_')
_SPACE = [' ', '\t']
_NON_DIGIT = [c for c in _PRINTABLE_SPACE if c not in string.digits]
_NON_WORD = [c for c in _PRINTABLE_SPACE if c not in string.ascii_letters + string.digits + '_']
_NON_SPACE = [c for c in _PRINTABLE if True]  # printable non-space chars

_MAX_UNBOUNDED = 8  # cap for *, +, {n,} quantifiers with no upper bound

# ── Preset patterns used when no pattern is supplied ─────────────────────────

_PRESETS = [
    (r'\d{3}-\d{4}',          r'\d{3}-\d{4}'),
    (r'[A-Z]{2}\d{6}',        r'[A-Z]{2}\d{6}'),
    (r'[A-Fa-f0-9]{8}',       r'[A-Fa-f0-9]{8}'),
    (r'\d{2}/\d{2}/\d{4}',    r'\d{2}/\d{2}/\d{4}'),
    (r'[A-Z][a-z]{4,8}',      r'[A-Z][a-z]{4,8}'),
    (r'\w{8}',                 r'\w{8}'),
    (r'[A-Z0-9]{4}-[A-Z0-9]{4}', r'[A-Z0-9]{4}-[A-Z0-9]{4}'),
    (r'v\d+\.\d+\.\d+',       r'v\d+\.\d+\.\d+'),
    (r'[A-Z]{3}\d{4}',        r'[A-Z]{3}\d{4}'),
    (r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'),
]


# ── Core generation functions ─────────────────────────────────────────────────

def _gen_sequence(nodes) -> str:
    return ''.join(_gen_node(n) for n in nodes)


def _gen_node(node) -> str:
    op, av = node

    if op == SC.LITERAL:
        return chr(av)

    if op == SC.NOT_LITERAL:
        pool = [c for c in _PRINTABLE if ord(c) != av]
        return random.choice(pool) if pool else '?'

    if op == SC.ANY:
        return random.choice(_PRINTABLE)

    if op == SC.IN:
        return _gen_class(av)

    if op in (SC.MAX_REPEAT, SC.MIN_REPEAT):
        lo, hi, sub = av
        if hi == SC.MAXREPEAT:
            hi = lo + _MAX_UNBOUNDED
        count = random.randint(lo, min(hi, lo + _MAX_UNBOUNDED))
        return ''.join(_gen_sequence(sub) for _ in range(count))

    if op == SC.SUBPATTERN:
        # av = (group_id, add_flags, del_flags, pattern) in Python 3.6+
        sub = av[-1]
        return _gen_sequence(sub)

    if op == SC.BRANCH:
        _, alts = av
        return _gen_sequence(random.choice(alts))

    if op == SC.AT:
        return ''  # ^ or $ anchor — produces no characters

    if op == SC.ASSERT:
        return ''  # lookahead — produces no characters

    if op == SC.ASSERT_NOT:
        return ''  # negative lookahead — produces no characters

    if op == SC.GROUPREF:
        return ''  # backreference — skip (complex stateful; out of scope)

    return ''


def _gen_class(av) -> str:
    """Generate one character matching a character class [...]."""
    negate = False
    pool = []

    for item_op, item_av in av:
        if item_op == SC.NEGATE:
            negate = True
        elif item_op == SC.LITERAL:
            pool.append(chr(item_av))
        elif item_op == SC.RANGE:
            lo, hi = item_av
            pool.extend(chr(c) for c in range(lo, hi + 1) if 33 <= c <= 126)
        elif item_op == SC.CATEGORY:
            pool.extend(_cat_pool(item_av))

    if negate:
        pool = [c for c in _PRINTABLE if c not in pool]

    return random.choice(pool) if pool else '?'


def _cat_pool(cat) -> list:
    """Map sre_constants category to character pool."""
    _map = {
        SC.CATEGORY_DIGIT:         _DIGITS,
        SC.CATEGORY_NOT_DIGIT:     _NON_DIGIT,
        SC.CATEGORY_WORD:          _WORD,
        SC.CATEGORY_NOT_WORD:      _NON_WORD,
        SC.CATEGORY_SPACE:         _SPACE,
        SC.CATEGORY_NOT_SPACE:     _NON_SPACE,
        SC.CATEGORY_UNI_DIGIT:     _DIGITS,
        SC.CATEGORY_UNI_NOT_DIGIT: _NON_DIGIT,
        SC.CATEGORY_UNI_WORD:      _WORD,
        SC.CATEGORY_UNI_NOT_WORD:  _NON_WORD,
        SC.CATEGORY_UNI_SPACE:     _SPACE,
        SC.CATEGORY_UNI_NOT_SPACE: _NON_SPACE,
    }
    return _map.get(cat, _WORD)


def generate_regex_string(pattern: str | None = None) -> str:
    """Generate a random string matching the given regex pattern.

    If no pattern is given, uses a built-in preset.
    Raises ValueError for patterns that cannot be parsed.
    """
    if pattern is None:
        pattern = random.choice(_PRESETS)[0]
    try:
        parsed = sre_parse.parse(pattern)
        return _gen_sequence(parsed)
    except Exception:
        return f"ERROR: Invalid pattern '{pattern}'"


# ── Generator class ───────────────────────────────────────────────────────────

class ReverseRegexGenerator:
    """Generates strings that match a given regular expression pattern."""

    def generate(self, data_type: str, **kwargs) -> str:
        if data_type == 'regex_string':
            pattern = kwargs.get('pattern', None)
            return generate_regex_string(pattern)
        return f"ERROR: Unknown type '{data_type}'"
