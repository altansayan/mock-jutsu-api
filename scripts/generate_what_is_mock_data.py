"""
Mock Data Nedir? / What is Mock Data? — 6 dil HOW-TO tab üretici
Gemini API ile SEO+GEO+AEO uyumlu içerik üretir, HOW-TO sayfalarına tab olarak ekler.
"""

import os, sys, re, json, time
from google import genai
from google.genai import types
from pathlib import Path
from mockjutsu.core import jutsu

# ── Config ────────────────────────────────────────────────────────────────────
ROOT      = Path(__file__).parent.parent
HOWTO_DIR = ROOT / "HOW-TO"
GENAI_KEY = os.environ.get("GEMINI_API_KEY", "")
GENAI_MDL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

client = genai.Client(api_key=GENAI_KEY)

# ── Locale tanımları ──────────────────────────────────────────────────────────
LOCALES = {
    "TR": {
        "dir": "TR", "file": "HOW-TO-MockJutsu-TR.html",
        "tab_label": "Mock Data Nedir?",
        "tab_id": "whatismock",
        "lang": "tr", "lang_name": "Türkçe",
        "title": "Mock Data Nedir? | Mock Jutsu TR Rehberi",
        "meta_desc": "Mock data nedir, neden kullanılır ve nasıl üretilir? Yazılım testlerinde algoritmik mock veri üretimini Mock Jutsu ile keşfedin.",
        "faq_q1": "Mock data nedir?",
        "faq_q2": "Mock data ile gerçek veri arasındaki fark nedir?",
        "faq_q3": "Mock data neden önemlidir?",
        "faq_q4": "Mock Jutsu nasıl mock data üretir?",
        "types": {"IBAN": "TR284991766282240240907775", "TCKN": "49137670120",
                  "SWIFT": "TVBATR2A", "Telefon": "+905068480445",
                  "E-posta": "ninja6209@deneme-posta.org", "Kart No": "4236722366884606"},
    },
    "EN": {
        "dir": "EN", "file": "HOW-TO-MockJutsu-EN.html",
        "tab_label": "What is Mock Data?",
        "tab_id": "whatismock",
        "lang": "en", "lang_name": "English (US)",
        "title": "What is Mock Data? | Mock Jutsu EN Guide",
        "meta_desc": "What is mock data, why do developers use it, and how is it generated algorithmically? Explore format-valid synthetic data with Mock Jutsu.",
        "faq_q1": "What is mock data?",
        "faq_q2": "What is the difference between mock data and real data?",
        "faq_q3": "Why is mock data important in software testing?",
        "faq_q4": "How does Mock Jutsu generate mock data?",
        "types": {"IBAN (US routing)": "RT:697664024 ACC:678586640082", "SSN": "260-49-2519",
                  "SWIFT": "WFBIUS6S", "Phone": "+13104867018",
                  "Email": "ninja3399@samplemail.org", "Card Number": "4007848425205082"},
    },
    "UK": {
        "dir": "UK", "file": "HOW-TO-MockJutsu-UK.html",
        "tab_label": "What is Mock Data?",
        "tab_id": "whatismock",
        "lang": "en-GB", "lang_name": "English (UK)",
        "title": "What is Mock Data? | Mock Jutsu UK Guide",
        "meta_desc": "What is mock data and how is it used in software testing? Generate format-valid synthetic data including NHS numbers, UK IBANs and more with Mock Jutsu.",
        "faq_q1": "What is mock data?",
        "faq_q2": "How is mock data different from anonymised data?",
        "faq_q3": "Why do QA engineers use mock data?",
        "faq_q4": "How does Mock Jutsu generate UK-specific mock data?",
        "types": {"IBAN (UK)": "GB94OFZX11069422939382", "NHS Number": "687 770 0651",
                  "SWIFT": "NWBKGB2L", "Phone": "+447712678585",
                  "Email": "user9650@mockpost.org.uk", "Card Number": "4751913702923332"},
    },
    "DE": {
        "dir": "DE", "file": "HOW-TO-MockJutsu-DE.html",
        "tab_label": "Was sind Mock-Daten?",
        "tab_id": "whatismock",
        "lang": "de", "lang_name": "Deutsch",
        "title": "Was sind Mock-Daten? | Mock Jutsu DE Leitfaden",
        "meta_desc": "Was sind Mock-Daten, warum werden sie eingesetzt und wie werden sie algorithmisch generiert? Entdecken Sie formatgültige Testdaten mit Mock Jutsu.",
        "faq_q1": "Was sind Mock-Daten?",
        "faq_q2": "Was ist der Unterschied zwischen Mock-Daten und echten Daten?",
        "faq_q3": "Warum sind Mock-Daten im Software-Testing wichtig?",
        "faq_q4": "Wie generiert Mock Jutsu Mock-Daten?",
        "types": {"IBAN (DE)": "DE07390534179107296400", "SWIFT": "HYVEDEMM",
                  "Telefon": "+491760788198", "E-Mail": "user4897@mustermail.de",
                  "Kartennummer": "4690523079962088"},
    },
    "FR": {
        "dir": "FR", "file": "HOW-TO-MockJutsu-FR.html",
        "tab_label": "Qu'est-ce que les Mock Data?",
        "tab_id": "whatismock",
        "lang": "fr", "lang_name": "Français",
        "title": "Qu'est-ce que les Mock Data? | Guide Mock Jutsu FR",
        "meta_desc": "Qu'est-ce que les mock data, pourquoi les utiliser et comment les générer algorithmiquement? Découvrez Mock Jutsu pour des données de test valides.",
        "faq_q1": "Qu'est-ce que les mock data?",
        "faq_q2": "Quelle est la différence entre mock data et données réelles?",
        "faq_q3": "Pourquoi les ingénieurs QA utilisent-ils des mock data?",
        "faq_q4": "Comment Mock Jutsu génère-t-il des mock data?",
        "types": {"IBAN (FR)": "FR961883519598MS3F8WNDEM474", "SWIFT": "BNPAFRPP",
                  "Téléphone": "+33612959737", "E-mail": "mock2163@exemple-mail.fr",
                  "Numéro de carte": "4282385676604933"},
    },
    "RU": {
        "dir": "RU", "file": "HOW-TO-MockJutsu-RU.html",
        "tab_label": "Что такое Mock Data?",
        "tab_id": "whatismock",
        "lang": "ru", "lang_name": "Русский",
        "title": "Что такое Mock Data? | Руководство Mock Jutsu RU",
        "meta_desc": "Что такое mock data, зачем они нужны и как генерируются алгоритмически? Узнайте о генерации тестовых данных с Mock Jutsu.",
        "faq_q1": "Что такое mock data?",
        "faq_q2": "В чём разница между mock data и реальными данными?",
        "faq_q3": "Почему mock data важны в тестировании ПО?",
        "faq_q4": "Как Mock Jutsu генерирует mock data?",
        "types": {"СНИЛС": "517-893-184 28", "SWIFT": "RZBSRUMM",
                  "Телефон": "+79261234567", "Email": "test@mockmail.ru",
                  "Номер карты": "4910085768278147"},
    },
}

# ── Prompt üretici ────────────────────────────────────────────────────────────
def build_prompt(loc: dict) -> str:
    examples_str = "\n".join(f"  - {k}: {v}" for k, v in loc["types"].items())
    return f"""You are a senior software engineer and technical writer. Write an HTML tab section for a developer documentation page about "What is Mock Data?" in {loc["lang_name"]}.

STRICT REQUIREMENTS:
- Language: {loc["lang_name"]} ONLY. Every single word must be in {loc["lang_name"]}.
- Voice: Written by a practising QA/software engineer — opinionated, precise, no filler phrases
- NO AI tells: no "In conclusion", no "It is worth noting", no "This article explores", no bullet-point overload
- SEO: Use the primary keyword naturally 3-4 times. Secondary keywords: test data generation, synthetic data, software testing, format-valid data
- GEO: First paragraph must be a 40-50 word standalone definition (AI search engines quote this)
- AEO: Include a FAQ section at the end with 4 questions and direct answers (2-3 sentences each)
- Include real Mock Jutsu examples from the locale's data types:
{examples_str}
- Mention: 390 types, 49 categories, 6 locales (TR/UK/US/DE/FR/RU), PCI DSS / GDPR / KVKK masking, zero external dependencies
- Structure with these HTML sections (use these exact CSS classes):
  <div class="whatismock-hero"> — opening definition
  <div class="whatismock-section"> — why needed (problem/solution, no story)
  <div class="whatismock-section"> — who uses it (developer unit/integration tests, QA engineer performance/acceptance tests)
  <div class="whatismock-examples"> — real Mock Jutsu output examples (use <code> tags)
  <div class="whatismock-section"> — how Mock Jutsu solves it (4 channels: CLI, API server, PyPI/Maven, JMeter)
  <div class="whatismock-faq"> — FAQ with schema-ready structure

OUTPUT: Return ONLY the inner HTML content (no <html>, no <head>, no <style>, no <script>). Start directly with <div class="whatismock-hero">.
The content should be 800-1200 words. Dense, scannable, technically precise."""


# ── Gemini çağrısı ────────────────────────────────────────────────────────────
def generate_content(locale_key: str, loc: dict) -> str:
    print(f"  Generating {locale_key} ({loc['lang_name']})...")
    prompt = build_prompt(loc)
    response = client.models.generate_content(model=GENAI_MDL, contents=prompt)
    content = response.text.strip()
    # Markdown code fence temizle
    content = re.sub(r'^```html\s*', '', content, flags=re.MULTILINE)
    content = re.sub(r'^```\s*$', '', content, flags=re.MULTILINE)
    return content.strip()


# ── CSS (bir kez, ilk locale'e eklenir — diğerleri zaten paylaşıyor) ──────────
WHATISMOCK_CSS = """
/* ── What is Mock Data tab ── */
.whatismock-hero{background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 100%);color:#f8fafc;padding:2.5rem 2rem;border-radius:12px;margin-bottom:2rem}
.whatismock-hero h2{font-size:1.75rem;font-weight:700;margin-bottom:1rem;color:#fff}
.whatismock-hero p{font-size:1.05rem;line-height:1.75;color:#cbd5e1;max-width:760px}
.whatismock-section{margin-bottom:2rem}
.whatismock-section h3{font-size:1.2rem;font-weight:700;color:#1e40af;margin-bottom:.75rem;border-left:4px solid #3b82f6;padding-left:.75rem}
.whatismock-section p{color:#374151;line-height:1.75;margin-bottom:.75rem}
.whatismock-examples{background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:1.5rem 2rem;margin-bottom:2rem}
.whatismock-examples h3{font-size:1.1rem;font-weight:700;color:#1e40af;margin-bottom:1rem}
.whatismock-examples table{width:100%;border-collapse:collapse}
.whatismock-examples th{text-align:left;font-size:.8rem;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:.05em;padding:.5rem .75rem;border-bottom:2px solid #e2e8f0}
.whatismock-examples td{padding:.6rem .75rem;border-bottom:1px solid #f1f5f9;font-size:.9rem;color:#374151}
.whatismock-examples td code{background:#e0f2fe;color:#0369a1;padding:.15rem .4rem;border-radius:4px;font-size:.85rem;font-family:monospace}
.whatismock-faq{margin-bottom:2rem}
.whatismock-faq h3{font-size:1.2rem;font-weight:700;color:#1e40af;margin-bottom:1rem;border-left:4px solid #3b82f6;padding-left:.75rem}
.whatismock-faq details{border:1px solid #e2e8f0;border-radius:8px;padding:.75rem 1rem;margin-bottom:.6rem;background:#fff}
.whatismock-faq details[open]{border-color:#3b82f6}
.whatismock-faq summary{font-weight:600;color:#1e293b;cursor:pointer;font-size:.95rem}
.whatismock-faq details p{margin-top:.6rem;color:#475569;line-height:1.7;font-size:.92rem}
"""


def build_tab_html(locale_key: str, loc: dict, content: str) -> str:
    """Tab-section div'ini oluşturur."""
    faq_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": loc["faq_q1"],
             "acceptedAnswer": {"@type": "Answer", "text": f"Mock data, {loc['lang_name']} dilinde yazılım testleri için kullanılan sentetik, format-geçerli veridir."}},
            {"@type": "Question", "name": loc["faq_q2"],
             "acceptedAnswer": {"@type": "Answer", "text": "Mock data algoritmik olarak üretilir ve gerçek kullanıcı bilgisi içermez; format ve checksum kurallarına uyar."}},
            {"@type": "Question", "name": loc["faq_q3"],
             "acceptedAnswer": {"@type": "Answer", "text": "Gerçek veriye erişim olmadan sistemlerin doğrulanmasını sağlar; GDPR ve PCI DSS uyumlu test ortamları kurulur."}},
            {"@type": "Question", "name": loc["faq_q4"],
             "acceptedAnswer": {"@type": "Answer", "text": "Mock Jutsu 390 tip, 49 kategori ve 6 lokasyon desteğiyle CLI, API, PyPI/Maven ve JMeter Plugin üzerinden algoritmik veri üretir."}},
        ]
    }, ensure_ascii=False, indent=2)

    return f"""<div class="tab-section" id="tab-whatismock">
<div style="max-width:900px;margin:0 auto;padding:1.75rem 1.5rem">
<script type="application/ld+json">
{faq_schema}
</script>
{content}
</div>
</div>"""


def inject_tab_into_html(html_path: Path, loc: dict, tab_html: str, css: str):
    """HOW-TO HTML dosyasına tab butonu ve içeriği ekler."""
    text = html_path.read_text(encoding="utf-8")

    # Zaten eklenmiş mi?
    if 'tab-whatismock' in text:
        print(f"    SKIP {html_path.name}: tab already exists, skipping")
        return

    # 1. CSS ekle (</style> öncesine)
    if css and css not in text:
        text = text.replace("</style>", css + "\n</style>", 1)

    # 2. Tab butonu ekle (Maskeleme sekmesinden sonra)
    mask_tab_pattern = r'(<div class="tab"[^>]*onclick="showTab\(\'mask\'[^"]*"\)[^>]*>[^<]*</div>)'
    tab_button = f'\n  <div class="tab" onclick="showTab(\'whatismock\', this)">{loc["tab_label"]}</div>'
    text = re.sub(mask_tab_pattern, r'\1' + tab_button, text)

    # 3. Tab içeriği ekle (</main> öncesine)
    text = text.replace("</main>", tab_html + "\n</main>", 1)

    html_path.write_text(text, encoding="utf-8")
    print(f"    OK {html_path.name}: tab injected")


# ── Ana akış ─────────────────────────────────────────────────────────────────
def main():
    if not GENAI_KEY:
        print("ERROR: GEMINI_API_KEY not set")
        sys.exit(1)

    print(f"Model: {GENAI_MDL}")
    print(f"Locales: {list(LOCALES.keys())}\n")

    first = True
    for locale_key, loc in LOCALES.items():
        print(f"[{locale_key}] {loc['lang_name']}")
        html_path = HOWTO_DIR / loc["dir"] / loc["file"]

        if not html_path.exists():
            print(f"  ✗ File not found: {html_path}")
            continue

        # Gemini ile içerik üret
        content = generate_content(locale_key, loc)

        # Tab HTML'i oluştur
        tab_html = build_tab_html(locale_key, loc, content)

        # CSS sadece ilk locale'de eklenir (tüm dosyalar aynı CSS'i paylaşmaz ama her birinde olması gerek)
        inject_tab_into_html(html_path, loc, tab_html, WHATISMOCK_CSS)

        # Rate limit için bekle
        if not first:
            time.sleep(3)
        first = False

    print("\nDone.")


if __name__ == "__main__":
    main()
