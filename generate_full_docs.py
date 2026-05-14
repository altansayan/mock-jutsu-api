"""
Mock Jutsu — HOW-TO 2.0 Static Site Generator
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)

Reads cached AI content from HOW-TO/content/{fn}_{lang}.txt
and generates a full static site:

  HOW-TO/{LANG}/HOW-TO-MockJutsu-{LANG}.html   ← listing page  (6 files)
  HOW-TO/{LANG}/FUNCTION/{fn}-{LANG}.html        ← detail page (1 per fn×lang)

Usage:
  python generate_full_docs.py           (all languages)
  python generate_full_docs.py --lang TR (single language)

Note: Run generate_ai_content.py first to populate HOW-TO/content/.
"""

import os
import sys
import re
import json
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))
from mockjutsu.cli import _REFERENCE

CONTENT_DIR = os.path.join(BASE_DIR, "HOW-TO", "content")
OUT_DIR     = os.path.join(BASE_DIR, "HOW-TO")
GITHUB_BASE = "https://altansayan.github.io/mock-jutsu-api/HOW-TO"

LANGS = ["TR", "EN", "UK", "DE", "FR", "RU"]

# ── Language UI strings ────────────────────────────────────────────────────────
UI = {
    "TR": {
        "lang_attr":    "tr",
        "flag":         "🇹🇷",
        "title_prefix": "Mock Jutsu",
        "listing_title":"Mock Jutsu HOW-TO — TR Rehberi",
        "listing_desc": "mock-jutsu ile Türkçe mock veri üretimi. TCKN, IBAN, Kredi Kartı ve 230+ tip için kapsamlı rehber.",
        "back_link":    "← Tüm Fonksiyonlar",
        "section_cli":  "CLI Kullanımı",
        "section_py":   "Python API",
        "section_jmeter":"JMeter",
        "section_api":  "REST API",
        "section_params":"Parametreler",
        "section_related":"İlgili Fonksiyonlar",
        "param_name":   "Parametre",
        "param_values": "Değerler",
        "param_desc":   "Açıklama",
        "badge_locale": "Locale Destekli",
        "copy_hint":    "Kopyalamak için tıkla",
        "cat_label":    "Kategori",
        "breadcrumb_home": "Mock Jutsu HOW-TO",
        "no_content":   "İçerik henüz üretilmedi. generate_ai_content.py çalıştırın.",
        "lang_switch":  "Diğer Diller",
        "listing_subtitle": "Tüm Fonksiyonlar",
    },
    "EN": {
        "lang_attr":    "en",
        "flag":         "🇺🇸",
        "title_prefix": "Mock Jutsu",
        "listing_title":"Mock Jutsu HOW-TO — EN Guide",
        "listing_desc": "Complete guide to generating mock data with mock-jutsu. SSN, IBAN, Credit Cards and 230+ types.",
        "back_link":    "← All Functions",
        "section_cli":  "CLI Usage",
        "section_py":   "Python API",
        "section_jmeter":"JMeter",
        "section_api":  "REST API",
        "section_params":"Parameters",
        "section_related":"Related Functions",
        "param_name":   "Parameter",
        "param_values": "Values",
        "param_desc":   "Description",
        "badge_locale": "Locale Aware",
        "copy_hint":    "Click to copy",
        "cat_label":    "Category",
        "breadcrumb_home": "Mock Jutsu HOW-TO",
        "no_content":   "Content not yet generated. Run generate_ai_content.py first.",
        "lang_switch":  "Other Languages",
        "listing_subtitle": "All Functions",
    },
    "UK": {
        "lang_attr":    "en-GB",
        "flag":         "🇬🇧",
        "title_prefix": "Mock Jutsu",
        "listing_title":"Mock Jutsu HOW-TO — UK Guide",
        "listing_desc": "Complete guide to generating mock data with mock-jutsu. NIN, IBAN, Credit Cards and 230+ types.",
        "back_link":    "← All Functions",
        "section_cli":  "CLI Usage",
        "section_py":   "Python API",
        "section_jmeter":"JMeter",
        "section_api":  "REST API",
        "section_params":"Parameters",
        "section_related":"Related Functions",
        "param_name":   "Parameter",
        "param_values": "Values",
        "param_desc":   "Description",
        "badge_locale": "Locale Aware",
        "copy_hint":    "Click to copy",
        "cat_label":    "Category",
        "breadcrumb_home": "Mock Jutsu HOW-TO",
        "no_content":   "Content not yet generated. Run generate_ai_content.py first.",
        "lang_switch":  "Other Languages",
        "listing_subtitle": "All Functions",
    },
    "DE": {
        "lang_attr":    "de",
        "flag":         "🇩🇪",
        "title_prefix": "Mock Jutsu",
        "listing_title":"Mock Jutsu HOW-TO — DE Handbuch",
        "listing_desc": "Vollständiges Handbuch zur Mock-Daten-Generierung mit mock-jutsu. IBAN, Steuernummern und 230+ Typen.",
        "back_link":    "← Alle Funktionen",
        "section_cli":  "CLI-Verwendung",
        "section_py":   "Python API",
        "section_jmeter":"JMeter",
        "section_api":  "REST API",
        "section_params":"Parameter",
        "section_related":"Verwandte Funktionen",
        "param_name":   "Parameter",
        "param_values": "Werte",
        "param_desc":   "Beschreibung",
        "badge_locale": "Locale-fähig",
        "copy_hint":    "Zum Kopieren klicken",
        "cat_label":    "Kategorie",
        "breadcrumb_home": "Mock Jutsu HOW-TO",
        "no_content":   "Inhalt noch nicht generiert. generate_ai_content.py ausführen.",
        "lang_switch":  "Andere Sprachen",
        "listing_subtitle": "Alle Funktionen",
    },
    "FR": {
        "lang_attr":    "fr",
        "flag":         "🇫🇷",
        "title_prefix": "Mock Jutsu",
        "listing_title":"Mock Jutsu HOW-TO — Guide FR",
        "listing_desc": "Guide complet pour générer des données fictives avec mock-jutsu. IBAN, numéros fiscaux et 230+ types.",
        "back_link":    "← Toutes les fonctions",
        "section_cli":  "Utilisation CLI",
        "section_py":   "API Python",
        "section_jmeter":"JMeter",
        "section_api":  "REST API",
        "section_params":"Paramètres",
        "section_related":"Fonctions associées",
        "param_name":   "Paramètre",
        "param_values": "Valeurs",
        "param_desc":   "Description",
        "badge_locale": "Locale supporté",
        "copy_hint":    "Cliquer pour copier",
        "cat_label":    "Catégorie",
        "breadcrumb_home": "Mock Jutsu HOW-TO",
        "no_content":   "Contenu non encore généré. Exécutez generate_ai_content.py.",
        "lang_switch":  "Autres langues",
        "listing_subtitle": "Toutes les fonctions",
    },
    "RU": {
        "lang_attr":    "ru",
        "flag":         "🇷🇺",
        "title_prefix": "Mock Jutsu",
        "listing_title":"Mock Jutsu HOW-TO — Руководство RU",
        "listing_desc": "Полное руководство по генерации фиктивных данных с mock-jutsu. ИНН, IBAN, банковские карты и 230+ типов.",
        "back_link":    "← Все функции",
        "section_cli":  "Использование CLI",
        "section_py":   "Python API",
        "section_jmeter":"JMeter",
        "section_api":  "REST API",
        "section_params":"Параметры",
        "section_related":"Похожие функции",
        "param_name":   "Параметр",
        "param_values": "Значения",
        "param_desc":   "Описание",
        "badge_locale": "Поддержка Locale",
        "copy_hint":    "Нажмите для копирования",
        "cat_label":    "Категория",
        "breadcrumb_home": "Mock Jutsu HOW-TO",
        "no_content":   "Контент ещё не сгенерирован. Запустите generate_ai_content.py.",
        "lang_switch":  "Другие языки",
        "listing_subtitle": "Все функции",
    },
}

LANG_LABELS = {"TR": "TR", "EN": "EN", "UK": "UK", "DE": "DE", "FR": "FR", "RU": "RU"}

# ── Parameter descriptions (locale-agnostic — values vary per lang if needed) ─
PARAM_INFO = {
    "--locale":    ("TR|UK|US|DE|FR|RU",  "Region / locale for locale-aware output"),
    "--gender":    ("male|female",          "Filter output by gender"),
    "--prefix":    ("string",              "Custom prefix string"),
    "--network":   ("visa|mc|amex|troy|mir|jcb|discover|unionpay|maestro", "Card network"),
    "--algorithm": ("md5|sha1|sha224|sha256|sha384|sha512|sha3-224|sha3-256|sha3-384|sha3-512|crc32|adler32|crc16", "Hash algorithm"),
    "--min":       ("float",               "Minimum numeric value"),
    "--max":       ("float",               "Maximum numeric value"),
    "--amount":    ("float",               "Payment amount"),
    "--currency":  ("btc|eth",             "Cryptocurrency symbol"),
    "--carrier":   ("fedex|ups|usps|dhl",  "Logistics carrier"),
    "--words":     ("12|15|18|21|24",      "Word count for mnemonic"),
    "--pattern":   ("regex",               "Regex pattern to generate"),
    "--dims":      ("int",                 "Vector dimensions"),
    "--nnz":       ("int",                 "Non-zero entry count for sparse vector (default: 128)"),
    "--format":    ("hex|rgb|hsl|name",    "Color output format (default: hex)"),
    "--secret":    ("string",              "HMAC signing key (default: ninja)"),
    "--payload":   ("string",              "Message to sign with HMAC (default: mock)"),
    "--count":     ("int",                 "Number of records to generate (default: 10)"),
    "--table":     ("string",              "SQL table name for INSERT statements (default: records)"),
}

# ── Related functions by category ─────────────────────────────────────────────
def build_related_map():
    cat_map: dict[str, list[str]] = {}
    for r in _REFERENCE:
        fn = r[0].strip()
        if not fn or fn.startswith("--"):
            continue
        cat = r[1]
        cat_map.setdefault(cat, []).append(fn)
    return cat_map

CAT_RELATED = build_related_map()


# ── Helpers ───────────────────────────────────────────────────────────────────
def get_functions():
    return [r for r in _REFERENCE if r[0].strip() and not r[0].strip().startswith("--")]


def read_content(fn: str, lang: str) -> str:
    p = os.path.join(CONTENT_DIR, f"{fn}_{lang}.txt")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return f.read().strip()
    return ""


def parse_extra_params(extra: str) -> list[tuple[str, str | None]]:
    """Returns [(flag, inline_values_or_None), ...]
    e.g. '--format (json|csv|sql)' → [('--format', 'json|csv|sql')]
         '--count (int)'           → [('--count',  'int')]
         '--locale'                → [('--locale',  None)]
    """
    if not extra or extra == "-":
        return []
    result = []
    for part in extra.split(","):
        part = part.strip()
        if part.startswith("--"):
            flag = part.split()[0]
            m = re.search(r'\(([^)]+)\)', part)
            result.append((flag, m.group(1) if m else None))
    return result


def listing_url(lang: str) -> str:
    return f"{GITHUB_BASE}/{lang}/HOW-TO-MockJutsu-{lang}.html"


def detail_url(fn: str, lang: str) -> str:
    return f"{GITHUB_BASE}/{lang}/FUNCTION/{fn}-{lang}.html"


def detail_rel_path(fn: str, lang: str) -> str:
    return os.path.join(OUT_DIR, lang, "FUNCTION", f"{fn}-{lang}.html")


def listing_rel_path(lang: str) -> str:
    return os.path.join(OUT_DIR, lang, f"HOW-TO-MockJutsu-{lang}.html")


# ── CSS (shared across all pages) ─────────────────────────────────────────────
BASE_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Inter',-apple-system,sans-serif;background:#f8fafc;color:#1e293b;line-height:1.6;-webkit-font-smoothing:antialiased}

/* ── Header ── */
.header{background:linear-gradient(135deg,#0f172a 0%,#1e293b 100%);color:#fff;padding:3.5rem 2rem 4rem;text-align:center;position:relative;overflow:hidden}
.header::before{content:"";position:absolute;top:0;left:0;right:0;height:4px;background:linear-gradient(90deg,#3b82f6,#8b5cf6,#ec4899)}
.header h1{font-size:2.2rem;font-weight:800;letter-spacing:-0.025em;background:linear-gradient(to right,#fff,#cbd5e1);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:.4rem}
.header .subtitle{font-size:1rem;color:#94a3b8;margin-bottom:1.2rem}
.header-links{display:flex;justify-content:center;gap:.75rem;flex-wrap:wrap;margin-top:1.2rem}
.hlink{display:flex;align-items:center;gap:.4rem;color:#f8fafc;text-decoration:none;font-weight:600;background:rgba(255,255,255,.05);padding:.5rem 1rem;border-radius:99px;transition:all .2s;border:1px solid rgba(255,255,255,.1);font-size:.9rem}
.hlink:hover{background:rgba(255,255,255,.15);transform:translateY(-2px)}
.badge-cat{display:inline-block;padding:.25rem .75rem;border-radius:6px;font-size:.75rem;font-weight:700;background:#1e40af;color:#bfdbfe;margin-left:.5rem;vertical-align:middle}
.badge-locale{display:inline-block;padding:.2rem .6rem;border-radius:6px;font-size:.72rem;font-weight:700;background:#065f46;color:#a7f3d0;margin-left:.4rem;vertical-align:middle}

/* ── Layout ── */
.container{max-width:960px;margin:0 auto;padding:2rem 1.5rem}

/* ── Breadcrumb ── */
.breadcrumb{font-size:.85rem;color:#64748b;margin-bottom:1.75rem;display:flex;align-items:center;gap:.4rem;flex-wrap:wrap}
.breadcrumb a{color:#3b82f6;text-decoration:none}
.breadcrumb a:hover{text-decoration:underline}
.breadcrumb span{color:#94a3b8}

/* ── Article ── */
.article{background:#fff;border-radius:12px;padding:2rem;border:1px solid #e2e8f0;margin-bottom:2rem;box-shadow:0 1px 3px rgba(0,0,0,.05)}
.article p{margin-bottom:1rem;color:#334155;line-height:1.75;font-size:.97rem}
.article p:last-child{margin-bottom:0}

/* ── Terminal windows ── */
.terminals{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:1.25rem;margin-bottom:2rem}
.term{border-radius:12px;overflow:hidden;border:1px solid #30363d;box-shadow:0 4px 12px rgba(0,0,0,.15);display:flex;flex-direction:column;background:#0d1117}
.term-header{background:#161b22;padding:.65rem 1rem;display:flex;align-items:center;gap:.5rem;border-bottom:1px solid #30363d;flex-shrink:0}
.dot{width:12px;height:12px;border-radius:50%;flex-shrink:0}
.dot.r{background:#ff5f56}.dot.y{background:#ffbd2e}.dot.g{background:#27c93f}
.term-title{color:#8b949e;font-size:.78rem;font-family:'JetBrains Mono',monospace;margin-left:.35rem;flex:1}
.copy-btn{background:transparent;border:1px solid #30363d;color:#8b949e;font-size:.7rem;padding:.2rem .5rem;border-radius:4px;cursor:pointer;font-family:'JetBrains Mono',monospace;transition:all .15s}
.copy-btn:hover{border-color:#3b82f6;color:#60a5fa}
.term-body{background:#0d1117;padding:1.1rem 1.25rem;font-family:'JetBrains Mono',monospace;font-size:.82rem;line-height:1.9;overflow-x:auto;flex:1}
.term-body code{display:block;white-space:pre}
.p{color:#e6edf3}.p::before{content:"$ ";color:#3fb950}
.o{color:#7ee787;padding-left:1.4rem}.jm{color:#7ee787}
.c{color:#8b949e}
.py{color:#e6edf3}.py::before{content:">>> ";color:#79c0ff}
.kw{color:#ff7b72}.st{color:#a5d6ff}.fn{color:#d2a8ff}.nb{color:#ffa657}

/* ── Params table ── */
.params-section{background:#fff;border-radius:12px;border:1px solid #e2e8f0;margin-bottom:2rem;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.05)}
.params-section h2{font-size:1rem;font-weight:700;color:#0f172a;padding:1rem 1.5rem;border-bottom:1px solid #f1f5f9;background:#f8fafc}
.params-section table{width:100%;border-collapse:collapse}
.params-section th{background:#f8fafc;padding:.65rem 1.25rem;text-align:left;font-size:.75rem;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.04em;border-bottom:1px solid #f1f5f9}
.params-section td{padding:.7rem 1.25rem;font-size:.875rem;border-bottom:1px solid #f8fafc;color:#334155}
.params-section tr:last-child td{border-bottom:none}
.param-flag{font-family:'JetBrains Mono',monospace;color:#0ea5e9;font-size:.8rem}
.param-vals{font-family:'JetBrains Mono',monospace;color:#7c3aed;font-size:.78rem}

/* ── Related ── */
.related{background:#fff;border-radius:12px;border:1px solid #e2e8f0;padding:1.25rem 1.5rem;margin-bottom:2rem;box-shadow:0 1px 3px rgba(0,0,0,.05)}
.related h2{font-size:1rem;font-weight:700;color:#0f172a;margin-bottom:.85rem}
.related-grid{display:flex;flex-wrap:wrap;gap:.5rem}
.rel-link{display:inline-block;padding:.3rem .75rem;background:#f1f5f9;border:1px solid #e2e8f0;border-radius:8px;font-family:'JetBrains Mono',monospace;font-size:.78rem;color:#0f172a;text-decoration:none;transition:all .15s}
.rel-link:hover{background:#dbeafe;border-color:#93c5fd;color:#1d4ed8}

/* ── Language switcher ── */
.lang-switch{background:#fff;border-radius:12px;border:1px solid #e2e8f0;padding:1rem 1.5rem;margin-bottom:2rem;box-shadow:0 1px 3px rgba(0,0,0,.05)}
.lang-switch h3{font-size:.85rem;font-weight:600;color:#64748b;margin-bottom:.65rem}
.lang-pills{display:flex;gap:.5rem;flex-wrap:wrap}
.lang-pill{display:inline-block;padding:.3rem .85rem;border-radius:99px;font-size:.8rem;font-weight:700;text-decoration:none;transition:all .15s;border:1px solid #e2e8f0;background:#f8fafc;color:#475569}
.lang-pill:hover{border-color:#3b82f6;color:#1d4ed8;background:#eff6ff}
.lang-pill.active{background:#1d4ed8;color:#fff;border-color:#1d4ed8}

/* ── Listing page ── */
.cat-section{margin-bottom:2.5rem}
.cat-header{font-size:1rem;font-weight:700;color:#0f172a;margin-bottom:.85rem;padding-left:12px;border-left:4px solid #3b82f6}
.fn-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:.75rem}
.fn-card{background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:1rem 1.25rem;transition:all .2s;text-decoration:none;display:block;box-shadow:0 1px 2px rgba(0,0,0,.04)}
.fn-card:hover{border-color:#3b82f6;box-shadow:0 4px 12px rgba(59,130,246,.12);transform:translateY(-2px)}
.fn-card .fn-name{font-family:'JetBrains Mono',monospace;font-size:.88rem;font-weight:700;color:#0f172a;margin-bottom:.3rem}
.fn-card .fn-desc{font-size:.78rem;color:#64748b;line-height:1.5;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.fn-card .fn-locale{margin-top:.4rem}

/* ── Footer ── */
.footer{text-align:center;padding:2rem;color:#94a3b8;font-size:.82rem;margin-top:1rem}
.footer a{color:#6366f1;text-decoration:none}
.footer a:hover{text-decoration:underline}
"""


# ── SEO helpers ───────────────────────────────────────────────────────────────
def hreflang_tags(fn: str | None = None) -> str:
    tags = []
    for lang in LANGS:
        lc = UI[lang]["lang_attr"]
        url = detail_url(fn, lang) if fn else listing_url(lang)
        tags.append(f'<link rel="alternate" hreflang="{lc}" href="{url}">')
    default_url = detail_url(fn, "EN") if fn else listing_url("EN")
    tags.append(f'<link rel="alternate" hreflang="x-default" href="{default_url}">')
    return "\n".join(tags)


def json_ld_detail(fn: str, cat: str, desc: str, lang: str, ui: dict) -> str:
    page_url = detail_url(fn, lang)
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "TechArticle",
                "headline": f"Mock Jutsu — {fn} — {lang}",
                "description": desc[:160],
                "url": page_url,
                "inLanguage": ui["lang_attr"],
                "author": {"@type": "Person", "name": "Altan Sezer Ayan"},
                "publisher": {"@type": "Organization", "name": "mock-jutsu"},
                "keywords": f"{fn}, mock data, test data, mock-jutsu, {cat}",
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Mock Jutsu HOW-TO",
                     "item": listing_url(lang)},
                    {"@type": "ListItem", "position": 2, "name": fn,
                     "item": page_url},
                ],
            },
            {
                "@type": "HowTo",
                "name": f"How to use {fn} in mock-jutsu",
                "step": [
                    {"@type": "HowToStep", "name": "Install", "text": "pip install mock-jutsu"},
                    {"@type": "HowToStep", "name": "Generate",
                     "text": f"mockjutsu generate {fn}"},
                ],
            },
        ],
    }
    return json.dumps(schema, ensure_ascii=False, indent=2)


def json_ld_listing(lang: str, ui: dict) -> str:
    schema = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "mock-jutsu",
        "applicationCategory": "DeveloperApplication",
        "description": ui["listing_desc"],
        "inLanguage": ui["lang_attr"],
        "author": {"@type": "Person", "name": "Altan Sezer Ayan"},
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        "url": listing_url(lang),
    }
    return json.dumps(schema, ensure_ascii=False, indent=2)


# ── Head template ─────────────────────────────────────────────────────────────
def html_head(title: str, desc: str, canonical: str, lang: str, ui: dict,
              fn: str | None, extra_ld: str) -> str:
    og_img = "https://altansayan.github.io/mock-jutsu-api/assets/banner.png"
    return f"""<!DOCTYPE html>
<html lang="{ui['lang_attr']}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="author" content="Altan Sezer Ayan (A.S.A)">
<meta name="keywords" content="mock data, fake data, test data, mockjutsu, mock-jutsu{', ' + fn if fn else ''}">
<link rel="icon" type="image/png" href="https://altansayan.github.io/mock-jutsu-api/assets/favicon.png">
<link rel="canonical" href="{canonical}">
{hreflang_tags(fn)}
<meta property="og:type" content="article">
<meta property="og:url" content="{canonical}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{og_img}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:url" content="{canonical}">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{og_img}">
<script type="application/ld+json">{extra_ld}</script>
<style>{BASE_CSS}</style>
</head>"""


# ── Header block ──────────────────────────────────────────────────────────────
def html_header(h1: str, subtitle: str, back_url: str, back_label: str) -> str:
    gh_svg = '<svg height="18" viewBox="0 0 16 16" width="18" fill="currentColor"><path d="M8 0c4.42 0 8 3.58 8 8a8.013 8.013 0 0 1-5.45 7.59c-.4.08-.55-.17-.55-.38 0-.27.01-1.13.01-2.2 0-.75-.25-1.23-.54-1.48 1.78-.2 3.65-.88 3.65-3.95 0-.88-.31-1.59-.82-2.15.08-.2.36-1.02-.08-2.12 0 0-.67-.22-2.2.82-.64-.18-1.32-.27-2-.27-.68 0-1.36.09-2 .27-1.53-1.03-2.2-.82-2.2-.82-.44 1.1-.16 1.92-.08 2.12-.51.56-.82 1.28-.82 2.15 0 3.06 1.86 3.75 3.64 3.95-.23.2-.44.55-.51 1.07-.46.21-1.61.55-2.33-.66-.15-.24-.6-.83-1.23-.82-.67.01-.27.38.01.53.34.19.73.9.82 1.13.16.45.68 1.31 2.69.94 0 .67.01 1.3.01 1.49 0 .21-.15.46-.55.38A7.995 7.995 0 0 1 0 8c0-4.42 3.58-8 8-8Z"/></svg>'
    return f"""<div class="header">
  <h1>{h1}</h1>
  <div class="subtitle">{subtitle}</div>
  <div class="header-links">
    <a href="{back_url}" class="hlink">{back_label}</a>
    <a href="https://github.com/altansayan/mock-jutsu-api" target="_blank" class="hlink">{gh_svg} GitHub</a>
  </div>
</div>"""


# ── Terminal window ───────────────────────────────────────────────────────────
def terminal_window(title: str, content_html: str, window_id: str) -> str:
    return f"""<div class="term">
  <div class="term-header">
    <span class="dot r"></span><span class="dot y"></span><span class="dot g"></span>
    <span class="term-title">{title}</span>
    <button class="copy-btn" onclick="copyTerm('{window_id}')">copy</button>
  </div>
  <div class="term-body" id="{window_id}">{content_html}</div>
</div>"""


def code(line: str, cls: str = "p") -> str:
    return f'<code class="{cls}">{line}</code>'


# ── Detail page builder ───────────────────────────────────────────────────────
def build_detail_page(r: tuple, lang: str) -> str:
    fn, cat, locale_aware, example, cli_cmd, desc = r[0], r[1], r[2], r[3], r[4], r[5]
    extra_params = r[6] if len(r) > 6 else "-"
    ui = UI[lang]

    # Article content
    article_html = read_content(fn, lang)
    if not article_html:
        article_html = f"<p>{ui['no_content']}</p>"

    # Title & meta
    page_title = f"Mock Jutsu — {fn} | {lang}"
    meta_desc  = desc[:155] if len(desc) > 155 else desc
    canonical  = detail_url(fn, lang)

    # Determine CLI flags for this function
    param_pairs = parse_extra_params(extra_params)   # [(flag, inline_val_or_None)]
    param_flags = [f for f, _ in param_pairs]
    has_locale  = locale_aware

    # Build CLI terminal
    cli_full = f"mockjutsu {cli_cmd}" if not cli_cmd.startswith("mockjutsu") else cli_cmd
    cli_content  = code(cli_full)
    if cat == "Commands":
        # For command pages: show a locale variant and a --count variant where relevant
        if has_locale:
            alt = cli_full.replace("--locale TR", "--locale DE").replace("--locale UK", "--locale DE")
            if alt != cli_full:
                cli_content += code(alt)
        if "--count" in cli_full:
            cli_content += code(cli_full.replace("--count 10", "--count 50"))
    else:
        if has_locale:
            cli_content += code(f"mockjutsu generate {fn} --locale DE")
        cli_content += code(f"mockjutsu bulk {fn} --count 10" + (" --locale TR" if has_locale else ""))
        locale_export = " --locale TR" if has_locale else ""
        cli_content += code(f"mockjutsu export {fn} --count 10 --format json{locale_export}", "o")
        cli_content += code(f"mockjutsu export {fn} --count 10 --format csv{locale_export}", "o")
        cli_content += code(f"mockjutsu export {fn} --count 10 --format sql{locale_export}", "o")
        if param_pairs:
            first_flag, first_inline = param_pairs[0]
            vals = first_inline or PARAM_INFO.get(first_flag, ("value", ""))[0]
            extra_cmd = f"mockjutsu generate {fn} {first_flag} {vals.split('|')[0]}"
            if extra_cmd != cli_full:
                cli_content += code(extra_cmd)

    # Python terminal
    locale_arg = ", locale='TR'" if has_locale else ""
    py_content  = code(f"from mockjutsu import jutsu", "c")
    py_content += code("", "c")
    py_content += code(f"jutsu.generate('{fn}'{locale_arg})", "py")
    py_content += code(f"jutsu.bulk('{fn}', count=10{locale_arg})", "py")
    py_content += code("", "c")
    py_content += code(f"jutsu.template(['{fn}'], count=5{locale_arg})", "py")

    # JMeter terminal
    if has_locale:
        jm_basic  = f"${{__mockjutsu({fn},TR)}}"
        jm_alt    = f"${{__mockjutsu({fn},DE)}}"
        jm_p2     = "# Parameter 2: locale (TR/UK/US/DE/FR/RU)"
    else:
        jm_basic  = f"${{__mockjutsu({fn})}}"
        jm_alt    = None
        jm_p2     = "# Parameter 2: (not required for this function)"
    jm_content  = code(jm_basic, "jm")
    jm_content += code("", "c")
    jm_content += code(f"# JMeter Function: __mockjutsu", "c")
    jm_content += code(f"# Parameter 1: {fn}", "c")
    jm_content += code(jm_p2, "c")
    if jm_alt:
        jm_content += code(jm_alt, "jm")

    # REST API terminal
    locale_qs = "?locale=TR" if has_locale else ""
    api_content  = code(f"GET /generate/{fn}{locale_qs}")
    api_content  += code(f'# → {{"type":"{fn}","result":"...","status":"ok"}}', "c")
    api_content  += code("")
    api_content  += code(f"GET /bulk/{fn}?count=10{('&locale=TR' if has_locale else '')}")
    locale_part  = ',"locale":"TR"' if has_locale else ""
    api_content  += code(f"POST /template")
    api_content  += code('     {"types":["' + fn + '"],"count":1' + locale_part + '}')

    # Language switcher
    lang_pills = ""
    for l in LANGS:
        active = "active" if l == lang else ""
        url = detail_url(fn, l)
        lang_pills += f'<a href="{url}" class="lang-pill {active}">{UI[l]["flag"]} {l}</a>\n'

    # Parameters table
    params_html = ""
    locale_pair  = [("--locale", None)] if has_locale else []
    all_pairs    = locale_pair + param_pairs
    if all_pairs:
        rows = ""
        for flag, inline_val in all_pairs:
            info   = PARAM_INFO.get(flag, ("value", flag.lstrip("-")))
            values = inline_val if inline_val else info[0]
            rows += f"""<tr>
              <td><span class="param-flag">{flag}</span></td>
              <td><span class="param-vals">{values}</span></td>
              <td>{info[1]}</td>
            </tr>"""
        params_html = f"""<div class="params-section">
  <h2>{ui['section_params']}</h2>
  <table>
    <thead><tr>
      <th>{ui['param_name']}</th>
      <th>{ui['param_values']}</th>
      <th>{ui['param_desc']}</th>
    </tr></thead>
    <tbody>{rows}</tbody>
  </table>
</div>"""

    # Related functions (same category, exclude self, max 12)
    related_fns = [f for f in CAT_RELATED.get(cat, []) if f != fn][:12]
    related_html = ""
    if related_fns:
        links = ""
        for rf in related_fns:
            links += f'<a href="{detail_url(rf, lang)}" class="rel-link"><code>{rf}</code></a>\n'
        related_html = f"""<div class="related">
  <h2>{ui['section_related']}</h2>
  <div class="related-grid">{links}</div>
</div>"""

    if cat == "Commands":
        locale_badge = ""
        cat_badge    = ""
    else:
        locale_badge = f'<span class="badge-locale">{ui["badge_locale"]}</span>' if has_locale else ""
        cat_badge    = f'<span class="badge-cat">{cat}</span>'
    listing_back = listing_url(lang)

    head = html_head(
        page_title, meta_desc, canonical, lang, ui, fn,
        json_ld_detail(fn, cat, desc, lang, ui)
    )
    header = html_header(
        f"<code style='font-size:1.6rem'>{fn}</code>"
        f'{cat_badge}{locale_badge}',
        f"Mock Jutsu HOW-TO | {lang}",
        listing_back,
        ui["back_link"],
    )

    return f"""{head}
<body>
{header}
<div class="container">
  <nav class="breadcrumb">
    <a href="{listing_back}">{ui['breadcrumb_home']}</a>
    <span>›</span>
    <a href="{listing_back}#{cat}">{cat}</a>
    <span>›</span>
    <strong>{fn}</strong>
  </nav>

  <div class="article">{article_html}</div>

  <div class="terminals">
    {terminal_window(ui['section_cli'], cli_content, f'term-cli-{fn}')}
    {terminal_window(ui['section_py'],  py_content,  f'term-py-{fn}')}
    {terminal_window(ui['section_jmeter'], jm_content, f'term-jm-{fn}')}
    {terminal_window(ui['section_api'], api_content, f'term-api-{fn}')}
  </div>

  {params_html}
  {related_html}

  <div class="lang-switch">
    <h3>{ui['lang_switch']}</h3>
    <div class="lang-pills">{lang_pills}</div>
  </div>
</div>

<div class="footer">
  mock-jutsu &mdash; Developed by <strong>Altan Sezer Ayan - A.S.A</strong>
  &nbsp;&bull;&nbsp; <a href="https://github.com/altansayan/mock-jutsu-api">GitHub</a>
  &nbsp;&bull;&nbsp; <a href="{listing_back}">{ui['breadcrumb_home']}</a>
</div>

<script>
function copyTerm(id) {{
  const el = document.getElementById(id);
  const txt = [...el.querySelectorAll('code')].map(c => c.textContent).join('\n');
  navigator.clipboard.writeText(txt).then(() => {{
    const btn = el.previousElementSibling.querySelector('.copy-btn');
    btn.textContent = 'copied!';
    setTimeout(() => btn.textContent = 'copy', 1500);
  }});
}}
</script>
</body>
</html>"""


# ── Listing page builder ──────────────────────────────────────────────────────
def build_listing_page(lang: str) -> str:
    ui  = UI[lang]
    funcs = get_functions()

    # Group by category (preserve _CAT_ORDER if available)
    try:
        from mockjutsu.cli import _CAT_ORDER
        order = _CAT_ORDER
    except ImportError:
        order = []
    cat_map: dict[str, list] = {}
    for r in funcs:
        cat_map.setdefault(r[1], []).append(r)
    cats = [c for c in order if c in cat_map] + [c for c in cat_map if c not in order]

    cards_html = ""
    for cat in cats:
        rows = cat_map[cat]
        cards = ""
        for r in rows:
            fn, _, locale_aware, _, _, desc = r[0], r[1], r[2], r[3], r[4], r[5]
            locale_badge = f'<span class="badge-locale" style="font-size:.65rem">{ui["badge_locale"]}</span>' if locale_aware else ""
            url = detail_url(fn, lang)
            short_desc = desc[:90] + "…" if len(desc) > 90 else desc
            cards += f"""<a href="{url}" class="fn-card">
  <div class="fn-name">{fn}</div>
  <div class="fn-desc">{short_desc}</div>
  <div class="fn-locale">{locale_badge}</div>
</a>"""
        cards_html += f"""<div class="cat-section" id="{cat}">
  <div class="cat-header">{cat} <small style="font-weight:400;color:#64748b">({len(rows)})</small></div>
  <div class="fn-grid">{cards}</div>
</div>"""

    lang_pills = ""
    for l in LANGS:
        active = "active" if l == lang else ""
        url = listing_url(l)
        lang_pills += f'<a href="{url}" class="lang-pill {active}">{UI[l]["flag"]} {l}</a>\n'

    canonical = listing_url(lang)
    head = html_head(
        ui["listing_title"],
        ui["listing_desc"],
        canonical,
        lang, ui, None,
        json_ld_listing(lang, ui),
    )
    header = html_header(
        "Mock Jutsu HOW-TO",
        ui["listing_subtitle"],
        "https://altansayan.github.io/mock-jutsu-api/",
        "← mock-jutsu",
    )

    return f"""{head}
<body>
{header}
<div class="container" style="max-width:1100px">
  <div class="lang-switch" style="margin-bottom:1.5rem">
    <h3>{ui['lang_switch']}</h3>
    <div class="lang-pills">{lang_pills}</div>
  </div>
  {cards_html}
</div>
<div class="footer">
  mock-jutsu &mdash; Developed by <strong>Altan Sezer Ayan - A.S.A</strong>
  &nbsp;&bull;&nbsp; <a href="https://github.com/altansayan/mock-jutsu-api">GitHub</a>
</div>
</body>
</html>"""


# ── Sitemap ───────────────────────────────────────────────────────────────────
def build_sitemap(funcs: list) -> str:
    urls = ['<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    urls.append('  <url><loc>https://altansayan.github.io/mock-jutsu-api/</loc><priority>1.0</priority></url>')
    for lang in LANGS:
        urls.append(f'  <url><loc>{listing_url(lang)}</loc><priority>0.9</priority></url>')
    for r in funcs:
        fn = r[0]
        for lang in LANGS:
            urls.append(f'  <url><loc>{detail_url(fn, lang)}</loc><priority>0.7</priority></url>')
    urls.append('</urlset>')
    return "\n".join(urls)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Mock Jutsu HOW-TO 2.0 generator")
    parser.add_argument("--lang", default="", help="Only this language (TR/EN/UK/DE/FR/RU)")
    args = parser.parse_args()

    langs = [args.lang.upper()] if args.lang else LANGS
    funcs = get_functions()

    total_pages = len(langs) + len(langs) * len(funcs)
    print(f"Generating HOW-TO 2.0 — {len(funcs)} functions × {len(langs)} languages")
    print(f"Total HTML pages: {total_pages}")
    print()

    done = 0
    for lang in langs:
        # Create dirs
        fn_dir = os.path.join(OUT_DIR, lang, "FUNCTION")
        os.makedirs(fn_dir, exist_ok=True)

        # Listing page
        path = listing_rel_path(lang)
        with open(path, "w", encoding="utf-8") as f:
            f.write(build_listing_page(lang))
        done += 1
        print(f"[{done:>4}] {os.path.relpath(path, BASE_DIR)}")

        # Detail pages
        for r in funcs:
            fn = r[0]
            path = detail_rel_path(fn, lang)
            with open(path, "w", encoding="utf-8") as f:
                f.write(build_detail_page(r, lang))
            done += 1
            if done % 50 == 0:
                print(f"[{done:>4}/{total_pages}] {lang}/FUNCTION/{fn}-{lang}.html")

    # Sitemap
    sitemap_path = os.path.join(OUT_DIR, "sitemap-howto.xml")
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(build_sitemap(funcs))
    print(f"\nSitemap: {os.path.relpath(sitemap_path, BASE_DIR)}")
    print(f"\nDone — {done} pages generated.")
    print("Open:  HOW-TO/TR/HOW-TO-MockJutsu-TR.html")


if __name__ == "__main__":
    main()
