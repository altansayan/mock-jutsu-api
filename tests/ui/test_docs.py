"""
UI Tests for the generated HTML Documentation using Playwright.
Verifies that the generated HTML files load correctly and UI interactions work.
Target structure: HOW-TO/{LANG}/HOW-TO-MockJutsu-{LANG}.html (HOW-TO 2.0)
"""
import os
import re
import pytest
from playwright.sync_api import Page, expect

BASE_DIR   = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
HOW_TO_DIR = os.path.join(BASE_DIR, "HOW-TO")

LOCALES = ["TR", "EN", "UK", "DE", "FR", "RU"]


def _file_url(loc: str) -> str:
    path = os.path.join(HOW_TO_DIR, loc, f"HOW-TO-MockJutsu-{loc}.html")
    return f"file:///{path}".replace("\\", "/")


@pytest.fixture(scope="session", autouse=True)
def check_docs_exist():
    """Ensure the HTML docs exist before running UI tests."""
    for loc in LOCALES:
        path = os.path.join(HOW_TO_DIR, loc, f"HOW-TO-MockJutsu-{loc}.html")
        if not os.path.exists(path):
            pytest.skip(f"Documentation file {path} not found. Run generate_full_docs.py first.")


@pytest.mark.parametrize("loc", LOCALES)
def test_doc_loads_and_has_title(page: Page, loc: str):
    """Test that each locale's document loads and has the correct title format."""
    page.goto(_file_url(loc))
    expect(page).to_have_title(re.compile(r"Mock Jutsu"))
    header = page.locator("h1").first
    expect(header).to_contain_text("Mock Jutsu")


def test_search_filter(page: Page):
    """Test the search functionality in the Full Reference tab (TR locale)."""
    page.goto(_file_url("TR"))

    # Initially many cards should be visible
    cards = page.locator(".fn-card")
    initial_count = cards.count()
    assert initial_count > 100, f"Expected >100 cards, found {initial_count}"

    # Text search
    search_box = page.locator("#fn-search")
    search_box.fill("tckn")
    page.wait_for_timeout(150)

    visible = page.locator(".fn-card:visible")
    filtered_count = visible.count()
    assert filtered_count < initial_count, "Search filter did not reduce card count"
    assert filtered_count > 0, "Search for 'tckn' should find at least one card"

    # Clear and test category filter button
    search_box.fill("")
    page.wait_for_timeout(100)

    identity_btn = page.locator(".cat-btn", has_text="Identity")
    if identity_btn.count() == 0:
        identity_btn = page.locator(".cat-btn", has_text="Kimlik")
    identity_btn.first.click()
    page.wait_for_timeout(150)

    cat_filtered = page.locator(".fn-card:visible")
    assert cat_filtered.count() > 0, "Category filter should have results"


def test_tab_switching(page: Page):
    """Test switching between tabs: Full Reference, Quick Start, etc."""
    page.goto(_file_url("EN"))

    # Full Reference tab should be active initially
    expect(page.locator("#tab-ref")).to_be_visible()
    expect(page.locator("#tab-qs")).not_to_be_visible()

    # Click Quick Start tab (index 1)
    page.locator(".tab").nth(1).click()

    expect(page.locator("#tab-ref")).not_to_be_visible()
    expect(page.locator("#tab-qs")).to_be_visible()

    # Quick Start should have cards
    cards = page.locator("#tab-qs .qs-card")
    assert cards.count() > 0, "Quick Start tab should have cards"
