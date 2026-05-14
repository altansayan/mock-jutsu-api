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

# ── Listing-page extras ────────────────────────────────────────────────────────

TAB_LABELS = {
    "TR": ("Tam Referans", "Hızlı Başlangıç", "Güçlü Özellikler", "REST API"),
    "EN": ("Full Reference", "Quick Start",    "Power Features",   "REST API"),
    "UK": ("Full Reference", "Quick Start",    "Power Features",   "REST API"),
    "DE": ("Vollständige Referenz", "Schnellstart", "Leistungsfunktionen", "REST API"),
    "FR": ("Référence complète", "Démarrage rapide", "Fonctionnalités", "REST API"),
    "RU": ("Полный справочник", "Быстрый старт", "Функции", "REST API"),
}

HEADER_ENGINE = {
    "TR": "Nihai Algoritmik Mock Veri Motoru",
    "EN": "The Ultimate Algorithmic Mock Data Engine",
    "UK": "The Ultimate Algorithmic Mock Data Engine",
    "DE": "Die Ultimative Mock-Daten-Engine",
    "FR": "Le Moteur de Données Fictives Algorithmiques",
    "RU": "Максимальный Движок Мок-Данных",
}

HEADER_LISTING_TITLE = {
    "TR": "Mock Jutsu &mdash; TR Rehberi",
    "EN": "Mock Jutsu &mdash; EN Guide",
    "UK": "Mock Jutsu &mdash; UK Guide",
    "DE": "Mock Jutsu &mdash; DE Handbuch",
    "FR": "Mock Jutsu &mdash; Guide FR",
    "RU": "Mock Jutsu &mdash; Руководство RU",
}

QS_LOCALE_INFO = {
    "TR": {
        "locale": "TR", "card_net": "troy",
        "profile_title": "TR Kimlik Profili",
        "fintech_title": "TR Fintech Örneği",
        "profile_code": (
            "p = jutsu.profile(locale='TR')\n"
            "# tckn, firstname, lastname,\n"
            "# phone (+90...), email,\n"
            "# iban (TR...), address\n\n"
            "# CLI\n"
            "mockjutsu profile --locale TR --count 3"
        ),
        "fintech_code": (
            "jutsu.generate('tckn')          # 34521876543\n"
            "jutsu.generate('vkn')           # 1234567890\n"
            "jutsu.generate('sgk')           # 34-0012345-1.01-02\n"
            "jutsu.generate('mersis')        # 1234567890012345\n"
            "jutsu.generate('iban', locale='TR')\n"
            "jutsu.generate('plate', locale='TR')  # 34 ABC 123"
        ),
    },
    "EN": {
        "locale": "US", "card_net": "visa",
        "profile_title": "US Identity Profile",
        "fintech_title": "US Fintech Example",
        "profile_code": (
            "p = jutsu.profile(locale='US')\n"
            "# ssn, firstname, lastname,\n"
            "# phone (+1...), email,\n"
            "# iban (US...), address\n\n"
            "# CLI\n"
            "mockjutsu profile --locale US --count 3"
        ),
        "fintech_code": (
            "jutsu.generate('ssn')           # 234-56-7890\n"
            "jutsu.generate('ein')           # 12-3456789\n"
            "jutsu.generate('routing_number') # 021000021\n"
            "jutsu.generate('aba')           # 021000021\n"
            "jutsu.generate('iban', locale='US')\n"
            "jutsu.generate('cardnum', network='visa')"
        ),
    },
    "UK": {
        "locale": "UK", "card_net": "visa",
        "profile_title": "UK Identity Profile",
        "fintech_title": "UK Fintech Example",
        "profile_code": (
            "p = jutsu.profile(locale='UK')\n"
            "# nin, firstname, lastname,\n"
            "# phone (+44...), email,\n"
            "# iban (GB...), address\n\n"
            "# CLI\n"
            "mockjutsu profile --locale UK --count 3"
        ),
        "fintech_code": (
            "jutsu.generate('nin')           # AB 12 34 56 C\n"
            "jutsu.generate('utr')           # 1234567890\n"
            "jutsu.generate('crn')           # 12345678\n"
            "jutsu.generate('sort_code')     # 40-47-84\n"
            "jutsu.generate('iban', locale='UK')\n"
            "jutsu.generate('cardnum', network='visa')"
        ),
    },
    "DE": {
        "locale": "DE", "card_net": "visa",
        "profile_title": "DE Identitätsprofil",
        "fintech_title": "DE Fintech-Beispiel",
        "profile_code": (
            "p = jutsu.profile(locale='DE')\n"
            "# steuer_id, firstname, lastname,\n"
            "# phone (+49...), email,\n"
            "# iban (DE...), address\n\n"
            "# CLI\n"
            "mockjutsu profile --locale DE --count 3"
        ),
        "fintech_code": (
            "jutsu.generate('steuer_id')     # 86094599602\n"
            "jutsu.generate('ust_id')        # DE123456789\n"
            "jutsu.generate('hrb')           # HRB 123456\n"
            "jutsu.generate('rvn')           # 65 070892 W 1235\n"
            "jutsu.generate('iban', locale='DE')\n"
            "jutsu.generate('cardnum', network='visa')"
        ),
    },
    "FR": {
        "locale": "FR", "card_net": "visa",
        "profile_title": "Profil identité FR",
        "fintech_title": "Exemple Fintech FR",
        "profile_code": (
            "p = jutsu.profile(locale='FR')\n"
            "# siren, firstname, lastname,\n"
            "# phone (+33...), email,\n"
            "# iban (FR...), address\n\n"
            "# CLI\n"
            "mockjutsu profile --locale FR --count 3"
        ),
        "fintech_code": (
            "jutsu.generate('siren')         # 732829320\n"
            "jutsu.generate('siret')         # 73282932000074\n"
            "jutsu.generate('tva')           # FR73732829320\n"
            "jutsu.generate('iban', locale='FR')\n"
            "jutsu.generate('cardnum', network='visa')"
        ),
    },
    "RU": {
        "locale": "RU", "card_net": "mir",
        "profile_title": "Профиль идентификации RU",
        "fintech_title": "Пример Fintech RU",
        "profile_code": (
            "p = jutsu.profile(locale='RU')\n"
            "# inn, firstname, lastname,\n"
            "# phone (+7...), email,\n"
            "# iban (RU...), address\n\n"
            "# CLI\n"
            "mockjutsu profile --locale RU --count 3"
        ),
        "fintech_code": (
            "jutsu.generate('inn')           # 7707083893\n"
            "jutsu.generate('snils')         # 112-233-445 95\n"
            "jutsu.generate('ogrn')          # 1027700132195\n"
            "jutsu.generate('kpp')           # 770701001\n"
            "jutsu.generate('iban', locale='RU')\n"
            "jutsu.generate('cardnum', network='mir')"
        ),
    },
}

LISTING_EXTRA_CSS = """
/* ── Listing header extras ── */
.lhdr-engine{font-size:1.1rem;color:#cbd5e1;font-weight:500;margin-bottom:.75rem}
.lhdr-stats{font-size:.95rem;color:#94a3b8;display:flex;align-items:center;justify-content:center;gap:.5rem;flex-wrap:wrap;margin:.25rem 0 1.25rem}
.lhdr-devinfo{font-size:.85rem;color:#64748b;margin-top:1.25rem}
.linkedin-link{display:flex;align-items:center;gap:.5rem;color:#f8fafc;text-decoration:none;font-weight:600;background:rgba(255,255,255,.05);padding:.55rem 1.1rem;border-radius:99px;transition:all .2s;border:1px solid rgba(255,255,255,.1);font-size:.9rem}
.linkedin-link:hover{background:rgba(10,102,194,.25);transform:translateY(-2px);border-color:rgba(10,102,194,.4)}
/* ── Tabs ── */
.tabs{display:flex;justify-content:center;background:#fff;border-bottom:1px solid #e2e8f0;padding:0 1rem;gap:1.25rem;position:sticky;top:0;z-index:100;box-shadow:0 4px 6px -1px rgba(0,0,0,.05);flex-wrap:wrap}
.tab{padding:1rem .9rem;cursor:pointer;font-weight:600;color:#64748b;border-bottom:3px solid transparent;transition:all .2s;font-size:.92rem;white-space:nowrap}
.tab:hover{color:#3b82f6}
.tab.active{color:#3b82f6;border-bottom-color:#3b82f6}
.tab-section{display:none}
.tab-section.active{display:block;animation:fadeIn .35s ease-out}
@keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
/* ── QS / Power cards ── */
.stitle{font-size:1.4rem;font-weight:700;margin-bottom:2rem;color:#0f172a;padding-left:14px;border-left:5px solid #3b82f6;letter-spacing:-.02em}
.qs-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:1.75rem;margin-bottom:2rem}
.qs-card{background:#fff;border-radius:12px;padding:1.75rem;box-shadow:0 1px 3px rgba(0,0,0,.05);border:1px solid #e2e8f0;transition:transform .2s,box-shadow .2s}
.qs-card:hover{transform:translateY(-3px);box-shadow:0 10px 20px -5px rgba(0,0,0,.1)}
.qs-card h3{font-size:.95rem;color:#0f172a;margin-bottom:1rem;display:flex;align-items:center;gap:.65rem;font-weight:700}
.qs-card h3::before{content:"";display:block;width:7px;height:7px;background:#3b82f6;border-radius:50%;flex-shrink:0}
.qs-card pre{background:#0f172a;color:#f8fafc;padding:.9rem 1rem;border-radius:6px;font-size:.81rem;overflow-x:auto;line-height:1.65;white-space:pre-wrap;font-family:'JetBrains Mono',monospace;margin:0}
"""

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
    ui    = UI[lang]
    funcs = get_functions()
    qs    = QS_LOCALE_INFO[lang]
    loc   = qs["locale"]
    net   = qs["card_net"]
    t_ref, t_qs, t_power, t_api = TAB_LABELS[lang]

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

    # Skip Commands in the card grid
    non_cmd_cats = [c for c in cats if c != "Commands"]

    # Category filter buttons (numeric catid avoids special-char issues)
    cat_filter_btns = '<button class="cat-btn active" data-catid="all">All</button>\n'
    for cat_idx, cat in enumerate(non_cmd_cats):
        cat_filter_btns += f'<button class="cat-btn" data-catid="{cat_idx}">{cat}</button>\n'

    cards_html = ""
    total_fn = 0
    for cat_idx, cat in enumerate(non_cmd_cats):
        rows = cat_map[cat]
        cards = ""
        for r in rows:
            fn            = r[0]
            locale_aware  = r[2]
            example       = r[3].replace('"', "&quot;")
            cli_cmd       = r[4].replace('"', "&quot;")
            desc          = r[5]
            short_desc    = desc[:90] + "…" if len(desc) > 90 else desc
            safe_desc     = desc[:120].replace('"', "&quot;")
            locale_badge  = (
                f'<span class="badge-locale" style="font-size:.65rem">{ui["badge_locale"]}</span>'
                if locale_aware else ""
            )
            url = detail_url(fn, lang)
            cards += (
                f'<a href="{url}" class="fn-card"'
                f' data-fn="{fn}" data-catid="{cat_idx}" data-cat="{cat.lower()}"'
                f' data-desc="{safe_desc}"'
                f' data-example="{example}"'
                f' data-cli="{cli_cmd}">\n'
                f'  <div class="fn-name">{fn}</div>\n'
                f'  <div class="fn-desc">{short_desc}</div>\n'
                f'  <div class="fn-locale">{locale_badge}</div>\n'
                f'</a>\n'
            )
            total_fn += 1
        cards_html += (
            f'<div class="cat-section" id="cat-{cat_idx}"'
            f' data-catid="{cat_idx}" data-cattotal="{len(rows)}">\n'
            f'  <div class="cat-header">{cat}'
            f' <small style="font-weight:400;color:#64748b">'
            f'(<span class="cat-count">{len(rows)}</span>)</small></div>\n'
            f'  <div class="fn-grid">{cards}</div>\n'
            f'</div>\n'
        )

    lang_pills = ""
    for l in LANGS:
        active = "active" if l == lang else ""
        url = listing_url(l)
        lang_pills += f'<a href="{url}" class="lang-pill {active}">{UI[l]["flag"]} {l}</a>\n'

    canonical = listing_url(lang)
    head = html_head(
        ui["listing_title"], ui["listing_desc"], canonical,
        lang, ui, None, json_ld_listing(lang, ui),
    )

    # SVG icons
    gh_svg = (
        '<svg height="18" viewBox="0 0 16 16" width="18" fill="currentColor">'
        '<path d="M8 0c4.42 0 8 3.58 8 8a8.013 8.013 0 0 1-5.45 7.59c-.4.08-.55-.17-.55-.38'
        ' 0-.27.01-1.13.01-2.2 0-.75-.25-1.23-.54-1.48 1.78-.2 3.65-.88 3.65-3.95'
        ' 0-.88-.31-1.59-.82-2.15.08-.2.36-1.02-.08-2.12 0 0-.67-.22-2.2.82-.64-.18-1.32-.27'
        '-2-.27-.68 0-1.36.09-2 .27-1.53-1.03-2.2-.82-2.2-.82-.44 1.1-.16 1.92-.08 2.12'
        '-.51.56-.82 1.28-.82 2.15 0 3.06 1.86 3.75 3.64 3.95-.23.2-.44.55-.51 1.07'
        '-.46.21-1.61.55-2.33-.66-.15-.24-.6-.83-1.23-.82-.67.01-.27.38.01.53.34.19.73.9.82 1.13'
        '.16.45.68 1.31 2.69.94 0 .67.01 1.3.01 1.49 0 .21-.15.46-.55.38A7.995 7.995 0 0 1 0 8'
        'c0-4.42 3.58-8 8-8Z"/></svg>'
    )
    li_svg = (
        '<svg height="18" viewBox="0 0 24 24" width="18" fill="currentColor">'
        '<path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239'
        ' 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79'
        '-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5'
        ' 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777'
        ' 7 2.476v6.759z"/></svg>'
    )

    # ── Custom listing header ─────────────────────────────────────────────────
    listing_header = (
        '<div class="header">\n'
        f'  <h1>{HEADER_LISTING_TITLE[lang]}</h1>\n'
        f'  <div class="lhdr-engine">{HEADER_ENGINE[lang]}</div>\n'
        '  <div class="lhdr-stats">\n'
        f'    <span>6 locale</span> &bull; <span>{total_fn} types</span>'
        ' &bull; <span>4008 tests</span>\n'
        '  </div>\n'
        '  <div class="header-links">\n'
        '    <a href="https://github.com/altansayan/mock-jutsu-api"'
        f' target="_blank" class="hlink">{gh_svg} GitHub</a>\n'
        '    <a href="https://www.linkedin.com/in/altansezerayan/"'
        f' target="_blank" class="linkedin-link">{li_svg} LinkedIn</a>\n'
        '  </div>\n'
        '  <div class="lhdr-devinfo">Developer: Altan Sezer Ayan (A.S.A)</div>\n'
        '</div>\n'
    )

    # ── Tab navigation ────────────────────────────────────────────────────────
    tab_nav = (
        '<div class="tabs">\n'
        f'  <div class="tab active" onclick="showTab(\'ref\', this)">{t_ref}</div>\n'
        f'  <div class="tab" onclick="showTab(\'qs\', this)">{t_qs}</div>\n'
        f'  <div class="tab" onclick="showTab(\'power\', this)">{t_power}</div>\n'
        f'  <div class="tab" onclick="showTab(\'api\', this)">{t_api}</div>\n'
        '</div>\n'
    )

    # ── Reference tab content ─────────────────────────────────────────────────
    ref_section = (
        '<div class="tab-section active" id="tab-ref">\n'
        '<div style="max-width:1100px;margin:0 auto;padding:1.75rem 1.5rem">\n'
        '<div class="lang-switch" style="margin-bottom:1.5rem">'
        f'<h3>{ui["lang_switch"]}</h3>'
        f'<div class="lang-pills">{lang_pills}</div></div>\n'
        '<div class="list-controls">\n'
        '  <div class="search-wrap">\n'
        '    <svg class="search-icon" viewBox="0 0 24 24" fill="none"'
        ' stroke="currentColor" stroke-width="2">'
        '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>\n'
        f'    <input type="text" id="fn-search" placeholder="Search {total_fn} functions&hellip;"'
        ' autocomplete="off" spellcheck="false">\n'
        '    <span id="search-count" style="display:none"></span>\n'
        '  </div>\n'
        f'  <div class="cat-filters" id="cat-filters">{cat_filter_btns}</div>\n'
        '</div>\n'
        '<div id="no-results" style="display:none;text-align:center;padding:3rem;'
        'color:#64748b;font-size:.95rem">'
        'No functions found. Try a different search term.</div>\n'
        + cards_html +
        '</div></div>\n'
    )

    # ── Pre-build QS/Power/API content blocks (avoids f-string { } escaping) ──
    qs_py = (
        "jutsu.generate('iban', locale='" + loc + "')\n"
        "jutsu.generate('phone', locale='" + loc + "')\n"
        "jutsu.generate('cardnum', network='" + net + "')\n"
        "jutsu.generate('fullname', locale='" + loc + "')"
    )
    qs_cli = (
        "mockjutsu generate iban --locale " + loc + "\n"
        "mockjutsu generate phone --locale " + loc + "\n"
        "mockjutsu generate cardnum --network " + net + "\n"
        "mockjutsu bulk phone --count 1000 --locale " + loc + "\n"
        "mockjutsu template uuid fullname phone iban --locale " + loc + "\n"
        "mockjutsu start-api --port 8000"
    )
    pwr_profile = (
        "# Python\n"
        "jutsu.profile(locale='" + loc + "')\n\n"
        "# CLI\n"
        "mockjutsu profile --locale " + loc + "\n"
        "mockjutsu profile --locale " + loc + " --count 5"
    )
    pwr_company = (
        "# Python\n"
        "jutsu.company(locale='" + loc + "')\n\n"
        "# CLI\n"
        "mockjutsu company --locale " + loc + "\n"
        "mockjutsu company --locale " + loc + " --count 3"
    )
    pwr_bulk = (
        "# Python\n"
        "jutsu.bulk('phone', count=100, locale='" + loc + "')\n"
        "jutsu.bulk('iban',  count=500, locale='" + loc + "')\n\n"
        "# CLI\n"
        "mockjutsu bulk phone --count 100 --locale " + loc + "\n"
        "mockjutsu bulk iban  --count 500 --locale " + loc
    )
    pwr_template = (
        "# Python\n"
        "jutsu.template(\n"
        "  ['uuid', 'phone', 'iban'],\n"
        "  count=10, locale='" + loc + "')\n\n"
        "# CLI\n"
        "mockjutsu template uuid phone iban --locale " + loc + " --count 10\n"
        "mockjutsu template uuid phone iban --format csv\n"
        "mockjutsu template uuid phone iban --format sql --table users"
    )
    pwr_export = (
        "# Python\n"
        "jutsu.export(\n"
        "  {'id':'uuid','phone':'phone','iban':'iban'},\n"
        "  count=1000, format='sql',\n"
        "  table='users', locale='" + loc + "')\n\n"
        "# CLI\n"
        "mockjutsu export uuid phone iban"
        " --count 1000 --format sql --table users --locale " + loc
    )
    pwr_rest = (
        "# Start server\n"
        "mockjutsu start-api --port 8000\n\n"
        "GET /generate/phone?locale=" + loc + "\n"
        "GET /bulk/iban?count=10&locale=" + loc + "\n"
        "GET /profile?locale=" + loc + "&count=1\n"
        'POST /template\n'
        '  {"types":["uuid","phone","iban"],"locale":"' + loc + '","count":1}\n\n'
        "# Swagger UI\n"
        "# http://localhost:8000/docs"
    )
    api_generate = (
        "GET /generate/phone?locale=" + loc + "\n"
        "GET /generate/iban?locale=" + loc + "\n"
        "GET /generate/cardnum?network=" + net + "\n"
        "GET /generate/hash?algorithm=sha256\n\n"
        "# Response\n"
        '{"type":"phone","locale":"' + loc + '",\n'
        '  "result":"...","status":"success"}'
    )
    api_bulk = (
        "GET /bulk/phone?count=10&locale=" + loc + "\n"
        "GET /bulk/iban?count=5&locale=" + loc + "\n\n"
        "# Response\n"
        '{"type":"phone","count":10,\n'
        '  "results":["...","..."]}'
    )
    api_template = (
        '{"types":["uuid","phone","iban"],\n'
        ' "count":1,"locale":"' + loc + '"}\n\n'
        "# count=1 -> single object\n"
        "# count>1 -> array"
    )
    api_profile = (
        "GET /profile?locale=" + loc + "&count=1\n"
        "GET /company?locale=" + loc + "&count=1"
    )
    api_export = (
        '{"schema_map":{"id":"uuid","p":"phone"},\n'
        ' "count":10,"locale":"' + loc + '",\n'
        ' "format":"csv","table":"users"}'
    )
    api_list = (
        "GET /list\n"
        "GET /list?cat=Financial\n"
        'GET /health  -> {"status":"ok"}\n\n'
        "# Swagger UI\n"
        "# http://localhost:8000/docs"
    )

    def qs_card(title: str, code: str) -> str:
        return (
            '<div class="qs-card">'
            f'<h3>{title}</h3>'
            f'<pre>{code}</pre>'
            '</div>\n'
        )

    # ── Quick Start tab ───────────────────────────────────────────────────────
    qs_section = (
        '<div class="tab-section" id="tab-qs">\n'
        '<div style="max-width:1100px;margin:0 auto;padding:1.75rem 1.5rem">\n'
        f'<div class="stitle">{t_qs}</div>\n'
        '<div class="qs-grid">\n'
        + qs_card("Python API", qs_py)
        + qs_card("CLI", qs_cli)
        + qs_card(qs["profile_title"], qs["profile_code"])
        + qs_card(qs["fintech_title"], qs["fintech_code"])
        + '</div></div></div>\n'
    )

    # ── Power Features tab ────────────────────────────────────────────────────
    power_section = (
        '<div class="tab-section" id="tab-power">\n'
        '<div style="max-width:1100px;margin:0 auto;padding:1.75rem 1.5rem">\n'
        f'<div class="stitle">{t_power}</div>\n'
        '<div class="qs-grid">\n'
        + qs_card("profile()", pwr_profile)
        + qs_card("company()", pwr_company)
        + qs_card("bulk()", pwr_bulk)
        + qs_card("template()", pwr_template)
        + qs_card("export()", pwr_export)
        + qs_card("REST API", pwr_rest)
        + '</div></div></div>\n'
    )

    # ── REST API tab ──────────────────────────────────────────────────────────
    api_section = (
        '<div class="tab-section" id="tab-api">\n'
        '<div style="max-width:1100px;margin:0 auto;padding:1.75rem 1.5rem">\n'
        f'<div class="stitle">{t_api}</div>\n'
        '<div class="qs-grid">\n'
        + qs_card("GET /generate/{type}", api_generate)
        + qs_card("GET /bulk/{type}", api_bulk)
        + qs_card("POST /template", api_template)
        + qs_card("GET /profile &amp; /company", api_profile)
        + qs_card("POST /export", api_export)
        + qs_card("GET /list", api_list)
        + '</div></div></div>\n'
    )

    search_css = """<style>
.list-controls{background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:1.25rem 1.5rem;margin-bottom:1.75rem;box-shadow:0 1px 3px rgba(0,0,0,.05)}
.search-wrap{position:relative;margin-bottom:1rem}
.search-icon{position:absolute;left:.85rem;top:50%;transform:translateY(-50%);width:16px;height:16px;color:#94a3b8;pointer-events:none}
#fn-search{width:100%;padding:.65rem 1rem .65rem 2.5rem;border:1px solid #e2e8f0;border-radius:8px;font-size:.9rem;color:#0f172a;background:#f8fafc;outline:none;box-sizing:border-box;transition:border-color .15s,box-shadow .15s}
#fn-search:focus{border-color:#3b82f6;box-shadow:0 0 0 3px rgba(59,130,246,.12);background:#fff}
#search-count{position:absolute;right:.85rem;top:50%;transform:translateY(-50%);font-size:.78rem;color:#64748b;background:#f1f5f9;padding:.15rem .5rem;border-radius:20px}
.cat-filters{display:flex;flex-wrap:wrap;gap:.4rem}
.cat-btn{background:#f1f5f9;border:1px solid #e2e8f0;color:#475569;font-size:.78rem;padding:.3rem .75rem;border-radius:20px;cursor:pointer;transition:all .15s;font-family:inherit}
.cat-btn:hover{border-color:#3b82f6;color:#3b82f6}
.cat-btn.active{background:#3b82f6;border-color:#3b82f6;color:#fff}
</style>"""

    search_js = """<script>
(function(){
  var search   = document.getElementById('fn-search');
  var countEl  = document.getElementById('search-count');
  var noRes    = document.getElementById('no-results');
  var cards    = Array.from(document.querySelectorAll('.fn-card'));
  var catBtns  = Array.from(document.querySelectorAll('.cat-btn'));
  var sections = Array.from(document.querySelectorAll('.cat-section[data-catid]'));
  var activeCatId = 'all';

  function update(){
    var q = search.value.trim().toLowerCase();
    var totalVisible = 0;
    var matched = {};
    cards.forEach(function(c){
      var fn      = (c.dataset.fn      || '').toLowerCase();
      var desc    = (c.dataset.desc    || '').toLowerCase();
      var example = (c.dataset.example || '').toLowerCase();
      var cli     = (c.dataset.cli     || '').toLowerCase();
      var cat     = (c.dataset.cat     || '').toLowerCase();
      var catid   = c.dataset.catid    || '';
      var matchQ   = !q || fn.indexOf(q)!=-1 || desc.indexOf(q)!=-1
                       || example.indexOf(q)!=-1 || cli.indexOf(q)!=-1
                       || cat.indexOf(q)!=-1;
      var matchCat = activeCatId==='all' || catid===activeCatId;
      var show = matchQ && matchCat;
      c.style.display = show ? '' : 'none';
      if(show){ totalVisible++; matched[catid]=(matched[catid]||0)+1; }
    });
    sections.forEach(function(sec){
      var catid = sec.dataset.catid;
      var total = parseInt(sec.dataset.cattotal,10);
      var cnt   = matched[catid]||0;
      sec.style.display = cnt>0 ? '' : 'none';
      var span = sec.querySelector('.cat-count');
      if(span){ span.textContent = (q&&cnt<total) ? cnt+'/'+total : total; }
    });
    noRes.style.display = totalVisible===0 ? '' : 'none';
    if(q){
      countEl.textContent = totalVisible+' result'+(totalVisible!==1?'s':'');
      countEl.style.display = '';
    } else { countEl.style.display='none'; }
  }

  search.addEventListener('input', update);
  catBtns.forEach(function(btn){
    btn.addEventListener('click', function(){
      activeCatId = btn.dataset.catid;
      catBtns.forEach(function(b){ b.classList.toggle('active',b===btn); });
      update();
    });
  });
})();
</script>"""

    tab_js = """<script>
function showTab(id, el) {
  document.querySelectorAll('.tab').forEach(function(t){ t.classList.remove('active'); });
  document.querySelectorAll('.tab-section').forEach(function(s){ s.classList.remove('active'); });
  el.classList.add('active');
  document.getElementById('tab-' + id).classList.add('active');
}
</script>"""

    copy_js = """<script>
function copyTerm(id) {
  var el = document.getElementById(id);
  var txt = Array.from(el.querySelectorAll('code')).map(function(c){ return c.textContent; }).join('\n');
  navigator.clipboard.writeText(txt).then(function(){
    var btn = el.previousElementSibling.querySelector('.copy-btn');
    btn.textContent = 'copied!';
    setTimeout(function(){ btn.textContent = 'copy'; }, 1500);
  });
}
</script>"""

    footer = (
        '<div class="footer">\n'
        '  mock-jutsu &mdash; Developed by <strong>Altan Sezer Ayan - A.S.A</strong>\n'
        '  &nbsp;&bull;&nbsp; <a href="https://github.com/altansayan/mock-jutsu-api">GitHub</a>\n'
        '</div>\n'
    )

    return (
        head + '\n'
        '<style>' + LISTING_EXTRA_CSS + '</style>\n'
        + search_css + '\n'
        '<body>\n'
        + listing_header
        + tab_nav
        + ref_section
        + qs_section
        + power_section
        + api_section
        + footer
        + tab_js + '\n'
        + search_js + '\n'
        + copy_js + '\n'
        '</body>\n</html>'
    )


# ── Sitemap ───────────────────────────────────────────────────────────────────
def _sitemap_entry(loc: str, priority: str, changefreq: str) -> str:
    import datetime
    today = datetime.date.today().isoformat()
    return (
        f"  <url>\n"
        f"    <loc>{loc}</loc>\n"
        f"    <lastmod>{today}</lastmod>\n"
        f"    <changefreq>{changefreq}</changefreq>\n"
        f"    <priority>{priority}</priority>\n"
        f"  </url>"
    )


def build_sitemap(funcs: list) -> str:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
        '        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
        '        xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9',
        '          http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">',
        "",
        "  <!-- Homepage -->",
        _sitemap_entry("https://altansayan.github.io/mock-jutsu-api/", "1.0", "weekly"),
        "",
        "  <!-- Language listing pages -->",
    ]
    for lang in LANGS:
        lines.append(_sitemap_entry(listing_url(lang), "0.9", "weekly"))
    lines.append("")
    lines.append("  <!-- Function detail pages -->")
    for r in funcs:
        fn  = r[0]
        cat = r[1] if len(r) > 1 else ""
        pri = "0.6" if cat == "Commands" else "0.8"
        for lang in LANGS:
            lines.append(_sitemap_entry(detail_url(fn, lang), pri, "monthly"))
    lines.append("</urlset>")
    return "\n".join(lines)


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

    # Sitemap — write to both root and HOW-TO/
    sitemap_xml = build_sitemap(funcs)
    for sm_path in [
        os.path.join(BASE_DIR, "sitemap.xml"),
        os.path.join(OUT_DIR, "sitemap-howto.xml"),
    ]:
        with open(sm_path, "w", encoding="utf-8") as f:
            f.write(sitemap_xml)
        print(f"Sitemap: {os.path.relpath(sm_path, BASE_DIR)}")

    total_urls = 1 + len(langs) + len(funcs) * len(langs)
    print(f"\nDone — {done} pages + {total_urls} sitemap URLs generated.")
    print("Open:  HOW-TO/TR/HOW-TO-MockJutsu-TR.html")


if __name__ == "__main__":
    main()
