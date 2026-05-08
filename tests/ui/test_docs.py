"""
UI Tests for the generated HTML Documentation using Playwright.
Verifies that the generated HTML files load correctly, display the right parameters, and UI interactions work.
"""
import os
import re
import pytest
from playwright.sync_api import Page, expect

DOCS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

LOCALES = ["TR", "EN", "UK", "DE", "FR", "RU"]

@pytest.fixture(scope="session", autouse=True)
def check_docs_exist():
    """Ensure the HTML docs exist before running UI tests."""
    for loc in LOCALES:
        path = os.path.join(DOCS_DIR, f"HOW-TO-MockJutsu-{loc}.html")
        if not os.path.exists(path):
            pytest.skip(f"Documentation file {path} not found. Run generate_locale_docs.py first.")


@pytest.mark.parametrize("loc", LOCALES)
def test_doc_loads_and_has_title(page: Page, loc: str):
    """Test that each locale's document loads and has the correct title format."""
    file_path = f"file:///{DOCS_DIR}/HOW-TO-MockJutsu-{loc}.html".replace("\\", "/")
    page.goto(file_path)
    
    # Check title
    expect(page).to_have_title(re.compile(r"mock-jutsu — .*"))
    
    # Check header
    header = page.locator(".header h1")
    expect(header).to_contain_text("mock-jutsu")


def test_table_search_filter(page: Page):
    """Test the search and filter functionality in the Reference table (TR locale)."""
    file_path = f"file:///{DOCS_DIR}/HOW-TO-MockJutsu-TR.html".replace("\\", "/")
    page.goto(file_path)
    
    # Initially there should be many rows
    rows = page.locator("#refBody tr:visible")
    initial_count = rows.count()
    assert initial_count > 100, f"Expected >100 rows, found {initial_count}"
    
    # 1. Test Text Search
    search_box = page.locator("#searchBox")
    search_box.fill("tckn")
    
    # Wait for filter to apply
    page.wait_for_timeout(100)
    filtered_count = rows.count()
    assert filtered_count < initial_count, "Search filter did not reduce row count"
    assert filtered_count > 0, "Search for 'tckn' should find at least one row"
    
    # 2. Test Category Filter
    page.locator(".reset-btn").click()
    page.wait_for_timeout(100)
    
    cat_filter = page.locator("#catFilter")
    cat_filter.select_option("Kimlik")
    page.wait_for_timeout(100)
    
    cat_filtered_count = rows.count()
    assert cat_filtered_count > 0, "Category filter 'Kimlik' should have results"
    
    # Ensure all visible rows are indeed 'Kimlik'
    for i in range(cat_filtered_count):
        cat_text = rows.nth(i).locator(".col-cat").inner_text()
        assert "Kimlik" in cat_text, f"Row {i} category '{cat_text}' is not 'Kimlik'"


def test_tab_switching(page: Page):
    """Test switching between tabs: Reference, Quick Start, etc."""
    file_path = f"file:///{DOCS_DIR}/HOW-TO-MockJutsu-EN.html".replace("\\", "/")
    page.goto(file_path)
    
    # Reference should be active initially
    expect(page.locator("#tab-ref")).to_be_visible()
    expect(page.locator("#tab-qs")).not_to_be_visible()
    
    # Click Quick Start tab
    tabs = page.locator(".tab")
    # In EN, tabs are ['Full Reference', 'Quick Start', 'Advanced Features', 'REST API']
    tabs.nth(1).click()
    
    # Now Quick Start should be active
    expect(page.locator("#tab-ref")).not_to_be_visible()
    expect(page.locator("#tab-qs")).to_be_visible()
    
    # Verify Quick Start has cards
    cards = page.locator("#tab-qs .qs-card")
    assert cards.count() > 0, "Quick Start tab should have cards"
