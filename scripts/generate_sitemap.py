#!/usr/bin/env python3
"""
Mock Jutsu — Dynamic Sitemap Generator
=======================================
Reads all registered types from cli.py _REFERENCE and generates
a complete sitemap.xml covering every page on the static site.

Usage:
  python scripts/generate_sitemap.py            # writes sitemap.xml
  python scripts/generate_sitemap.py --dry-run  # print stats only

Output files:
  sitemap.xml               ← root (what robots.txt points to)
  HOW-TO/sitemap-howto.xml  ← copy (for HOW-TO directory access)

Priority scheme:
  1.0  homepage
  0.9  language listing pages  (6 locales)
  0.8  function detail pages   (N functions × 6 locales)
  0.6  CLI command pages       (Commands category)

The script is also called automatically at the end of generate_full_docs.py
so that both HTML pages and sitemaps stay in sync.
"""

import sys
import os
import argparse
import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

try:
    from mockjutsu.cli import _REFERENCE
except ImportError as e:
    print(f"ERROR: Could not import _REFERENCE from mockjutsu.cli: {e}")
    sys.exit(1)

# ── Constants ──────────────────────────────────────────────────────────────────

LANGS    = ["TR", "EN", "UK", "DE", "FR", "RU"]
BASE_URL = "https://altansayan.github.io/mock-jutsu-api"
TODAY    = datetime.date.today().isoformat()

# ── URL helpers ────────────────────────────────────────────────────────────────

def homepage_url() -> str:
    return f"{BASE_URL}/"

def listing_url(lang: str) -> str:
    return f"{BASE_URL}/HOW-TO/{lang}/HOW-TO-MockJutsu-{lang}.html"

def detail_url(fn: str, lang: str) -> str:
    return f"{BASE_URL}/HOW-TO/{lang}/FUNCTION/{fn}-{lang}.html"

# ── Sitemap builder ────────────────────────────────────────────────────────────

def _entry(loc: str, priority: str, changefreq: str, lastmod: str = TODAY) -> str:
    return (
        f"  <url>\n"
        f"    <loc>{loc}</loc>\n"
        f"    <lastmod>{lastmod}</lastmod>\n"
        f"    <changefreq>{changefreq}</changefreq>\n"
        f"    <priority>{priority}</priority>\n"
        f"  </url>"
    )


def get_functions():
    """Return all _REFERENCE rows that represent data types (not CLI flags)."""
    return [
        r for r in _REFERENCE
        if r[0].strip() and not r[0].strip().startswith("--")
    ]


def build_sitemap(funcs: list) -> str:
    entries = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
        '        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
        '        xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9',
        '          http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">',
        "",
        "  <!-- Homepage -->",
        _entry(homepage_url(), "1.0", "weekly"),
        "",
        "  <!-- Language listing pages -->",
    ]

    for lang in LANGS:
        entries.append(_entry(listing_url(lang), "0.9", "weekly"))

    entries.append("")
    entries.append("  <!-- Function detail pages -->")

    for r in funcs:
        fn  = r[0].strip()
        cat = r[1] if len(r) > 1 else ""
        pri = "0.6" if cat == "Commands" else "0.8"
        for lang in LANGS:
            entries.append(_entry(detail_url(fn, lang), pri, "monthly"))

    entries.append("</urlset>")
    return "\n".join(entries)


def write_sitemaps(xml: str, dry_run: bool = False) -> dict:
    paths = {
        "root":  os.path.join(BASE_DIR, "sitemap.xml"),
        "howto": os.path.join(BASE_DIR, "HOW-TO", "sitemap-howto.xml"),
    }
    if not dry_run:
        for key, path in paths.items():
            with open(path, "w", encoding="utf-8") as f:
                f.write(xml)
    return paths


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Mock Jutsu — Dynamic Sitemap Generator"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print stats only; do not write any files"
    )
    args = parser.parse_args()

    funcs = get_functions()

    # Count breakdown
    cmd_count  = sum(1 for r in funcs if len(r) > 1 and r[1] == "Commands")
    fn_count   = len(funcs) - cmd_count
    total_urls = 1 + len(LANGS) + len(funcs) * len(LANGS)

    xml = build_sitemap(funcs)

    paths = write_sitemaps(xml, dry_run=args.dry_run)

    tag = "[DRY-RUN]" if args.dry_run else "[OK]"
    print(f"Mock Jutsu Sitemap Generator")
    print("-" * 40)
    print(f"  Date         : {TODAY}")
    print(f"  Functions    : {fn_count}  (data types)")
    print(f"  Commands     : {cmd_count}  (CLI commands)")
    print(f"  Locales      : {len(LANGS)}")
    print("-" * 40)
    print(f"  1            homepage        priority=1.0")
    print(f"  {len(LANGS):<12}   listing pages   priority=0.9")
    print(f"  {fn_count * len(LANGS):<12}   function pages  priority=0.8")
    print(f"  {cmd_count * len(LANGS):<12}   command pages   priority=0.6")
    print("-" * 40)
    print(f"  Total URLs   : {total_urls}")
    print("-" * 40)
    for key, path in paths.items():
        rel = os.path.relpath(path, BASE_DIR)
        print(f"  {tag} {rel}")

    if args.dry_run:
        print("\n  (no files written — remove --dry-run to write)")


if __name__ == "__main__":
    main()
