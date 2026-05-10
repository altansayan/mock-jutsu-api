"""
mock-jutsu — Sync & Consistency Tests
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)

Guard: Every type registered in core.py MUST appear in:
  1. mockjutsu list  (CLI output)
  2. HOW-TO-MockJutsu-TR.html  (documentation)

If either check fails after adding a new type, the developer forgot to:
  - Add the type to cli.py _REFERENCE  (causes list failure)
  - Re-run generate_locale_docs.py     (causes HTML failure)

These tests run in pre-push hook and CI — push is blocked until both pass.
"""

import os
import pytest
from click.testing import CliRunner

import mockjutsu.core as mc
from mockjutsu.cli import main, _REFERENCE

DOCS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOCALES  = ["TR", "EN", "UK", "DE", "FR", "RU"]

# ── Collect all registered types from core ───────────────────────────────────

def _all_core_types() -> set:
    types = set()
    for attr in dir(mc):
        if attr.endswith('_TYPES'):
            types.update(getattr(mc, attr))
    return types

ALL_CORE_TYPES = _all_core_types()

# ── Collect all types visible in CLI _REFERENCE ──────────────────────────────

_REF_TYPES = {
    r[0].strip()
    for r in _REFERENCE
    if r[0].strip() and not r[0].strip().startswith('--')
}

# ── 1. CLI list sync ─────────────────────────────────────────────────────────

def test_cli_list_runs_without_error():
    runner = CliRunner()
    result = runner.invoke(main, ['list'])
    assert result.exit_code == 0, f"mockjutsu list failed:\n{result.output}"


@pytest.mark.parametrize("data_type", sorted(ALL_CORE_TYPES))
def test_core_type_visible_in_cli_list(data_type):
    """Every core type must appear in `mockjutsu list` output."""
    runner = CliRunner()
    result = runner.invoke(main, ['list'])
    assert data_type in result.output, (
        f"Type '{data_type}' is registered in core.py but MISSING from `mockjutsu list`.\n"
        f"Fix: add it to _REFERENCE in cli.py."
    )


@pytest.mark.parametrize("data_type", sorted(ALL_CORE_TYPES))
def test_core_type_in_reference_table(data_type):
    """Every core type must have an entry in cli.py _REFERENCE."""
    # cardowner is a known display alias, not a standalone core type
    if data_type == 'cardowner':
        return
    assert data_type in _REF_TYPES, (
        f"Type '{data_type}' is in core.py but missing from cli.py _REFERENCE.\n"
        f"Fix: add a row for '{data_type}' to the _REFERENCE list in cli.py."
    )


# ── 2. HOW-TO HTML sync ──────────────────────────────────────────────────────

def _html_content(locale: str) -> str:
    path = os.path.join(DOCS_DIR, f"HOW-TO-MockJutsu-{locale}.html")
    if not os.path.exists(path):
        pytest.skip(f"HOW-TO-MockJutsu-{locale}.html not found — run generate_locale_docs.py")
    with open(path, encoding="utf-8") as f:
        return f.read()


@pytest.mark.parametrize("data_type", sorted(ALL_CORE_TYPES))
def test_core_type_visible_in_html_tr(data_type):
    """Every core type must appear in HOW-TO-MockJutsu-TR.html."""
    html = _html_content("TR")
    assert data_type in html, (
        f"Type '{data_type}' is registered in core.py but MISSING from HOW-TO-MockJutsu-TR.html.\n"
        f"Fix: re-run `python generate_locale_docs.py` and commit the updated HTML files."
    )


@pytest.mark.parametrize("locale", LOCALES)
def test_html_type_count_matches_core(locale):
    """Every type in _REFERENCE must have a data-fn row in the HTML."""
    import re
    html = _html_content(locale)
    html_types = set(re.findall(r'data-fn="([^"]+)"', html))
    core_count = len(_REF_TYPES)
    html_count = len(html_types)
    assert html_count == core_count, (
        f"HOW-TO-MockJutsu-{locale}.html has {html_count} data-fn rows "
        f"but core has {core_count}.\n"
        f"Missing: {_REF_TYPES - html_types}"
    )


# ── 3. No orphan types in _REFERENCE ────────────────────────────────────────

def test_no_orphan_types_in_reference():
    """_REFERENCE must not list types that don't exist in core.py."""
    known_aliases = {'cardowner'}
    orphans = _REF_TYPES - ALL_CORE_TYPES - known_aliases
    assert not orphans, (
        f"Types in _REFERENCE but NOT in core.py: {orphans}\n"
        f"Fix: remove or move these entries."
    )
