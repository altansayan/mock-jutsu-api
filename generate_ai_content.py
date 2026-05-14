"""
Mock Jutsu — HOW-TO 2.0 AI Content Generator
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)

Generates SEO-optimized 300-400 word articles for each function × language
using Gemini API. Results are cached as plain .txt files.

Usage:
  1. Copy .env.example → .env and add your GEMINI_API_KEY
  2. python generate_ai_content.py           (all functions, all languages)
  3. python generate_ai_content.py --lang TR  (only Turkish)
  4. python generate_ai_content.py --fn tckn  (only one function)
  5. python generate_ai_content.py --force    (regenerate even if cached)

API key sources (checked in order):
  1. GEMINI_API_KEY  environment variable
  2. GOOGLE_API_KEY  environment variable
  3. .env file in project root

Get your free Gemini API key at: https://aistudio.google.com/
"""

import os
import sys
import json
import time
import argparse
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

# ── Path setup ────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))
from mockjutsu.cli import _REFERENCE

# ── Load .env manually (zero external deps) ───────────────────────────────────
def _load_dotenv():
    env_path = os.path.join(BASE_DIR, ".env")
    if not os.path.exists(env_path):
        return
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

_load_dotenv()

API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""
MODEL   = os.environ.get("GEMINI_MODEL", "gemini-3-flash-preview")

# ── Config ────────────────────────────────────────────────────────────────────
CONTENT_DIR = os.path.join(BASE_DIR, "HOW-TO", "content")
LANGS       = ["TR", "EN", "UK", "DE", "FR", "RU"]
MAX_WORKERS = 5   # concurrent Gemini requests

# ── Prompts per language ──────────────────────────────────────────────────────
_PROMPTS = {
    "TR": """\
Sen mock-jutsu Python kütüphanesini belgeleyen uzman bir teknik yazarsın.

Aşağıdaki mock veri üretme fonksiyonu için SEO uyumlu, akıcı Türkçe bir teknik makale yaz.

Fonksiyon  : {fn}
Kategori   : {cat}
Açıklama   : {desc}
Örnek çıktı: {example}
CLI        : mockjutsu generate {fn}
Python     : jutsu.generate('{fn}')
JMeter     : ${{__mockjutsu({fn},)}}

Kurallar:
- Dil: Türkçe (doğal ve akıcı, kelime kelime çeviri değil)
- Uzunluk: 300-400 kelime
- Format: Yalnızca <p>...</p> paragrafları, başka HTML tag kullanma
- SEO anahtar kelimeler: "{fn}", "mock data", "test verisi", "mock-jutsu" — doğal kullan
- İçerik: Fonksiyonun ne ürettiği, hangi algoritmayı / standardı kullandığı,
  hangi test senaryolarında kullanılacağı, geliştiriciye ne zaman faydalı olduğu
- Başlık YAZMA — sadece paragraf içeriği istiyorum
""",

    "EN": """\
You are an expert technical writer documenting mock-jutsu, a Python mock data library.

Write an SEO-optimized technical article for the function below.

Function   : {fn}
Category   : {cat}
Description: {desc}
Example    : {example}
CLI        : mockjutsu generate {fn}
Python     : jutsu.generate('{fn}')
JMeter     : ${{__mockjutsu({fn},)}}

Rules:
- Language: American English (natural, professional)
- Length: 300-400 words
- Format: Only <p>...</p> paragraphs, no other HTML tags
- SEO keywords: "{fn}", "mock data", "test data", "mock-jutsu" — use naturally
- Content: what the function generates, algorithm / standard used,
  testing scenarios, developer benefits
- Do NOT include a heading — paragraphs only
""",

    "UK": """\
You are an expert technical writer documenting mock-jutsu, a Python mock data library.

Write an SEO-optimised technical article for the function below.

Function   : {fn}
Category   : {cat}
Description: {desc}
Example    : {example}
CLI        : mockjutsu generate {fn}
Python     : jutsu.generate('{fn}')
JMeter     : ${{__mockjutsu({fn},)}}

Rules:
- Language: British English (natural, professional)
- Length: 300-400 words
- Format: Only <p>...</p> paragraphs, no other HTML tags
- SEO keywords: "{fn}", "mock data", "test data", "mock-jutsu" — use naturally
- Content: what the function generates, algorithm / standard used,
  testing scenarios, developer benefits
- Do NOT include a heading — paragraphs only
""",

    "DE": """\
Du bist ein erfahrener technischer Redakteur und dokumentierst mock-jutsu, eine Python-Bibliothek für Mock-Daten.

Schreibe einen SEO-optimierten technischen Artikel für die folgende Funktion.

Funktion    : {fn}
Kategorie   : {cat}
Beschreibung: {desc}
Beispiel    : {example}
CLI         : mockjutsu generate {fn}
Python      : jutsu.generate('{fn}')
JMeter      : ${{__mockjutsu({fn},)}}

Regeln:
- Sprache: Deutsch (natürlich und fließend, keine wörtliche Übersetzung)
- Länge: 300-400 Wörter
- Format: Nur <p>...</p>-Absätze, keine anderen HTML-Tags
- SEO-Keywords: "{fn}", "Mock-Daten", "Testdaten", "mock-jutsu" — natürlich einsetzen
- Inhalt: Was die Funktion generiert, welcher Algorithmus / Standard verwendet wird,
  Testszenarien und Entwicklervorteile
- KEINE Überschrift — nur Absätze
""",

    "FR": """\
Tu es un rédacteur technique expert documentant mock-jutsu, une bibliothèque Python de données fictives.

Écris un article technique optimisé SEO pour la fonction ci-dessous.

Fonction    : {fn}
Catégorie   : {cat}
Description : {desc}
Exemple     : {example}
CLI         : mockjutsu generate {fn}
Python      : jutsu.generate('{fn}')
JMeter      : ${{__mockjutsu({fn},)}}

Règles :
- Langue : Français (naturel et fluide, pas de traduction mot à mot)
- Longueur : 300-400 mots
- Format : Uniquement des balises <p>...</p>, pas d'autres balises HTML
- Mots-clés SEO : "{fn}", "données fictives", "données de test", "mock-jutsu" — usage naturel
- Contenu : ce que génère la fonction, l'algorithme / norme utilisé,
  scénarios de test et avantages pour le développeur
- PAS de titre — uniquement des paragraphes
""",

    "RU": """\
Ты опытный технический писатель, документирующий mock-jutsu — Python-библиотеку фиктивных данных.

Напиши SEO-оптимизированную техническую статью для функции ниже.

Функция    : {fn}
Категория  : {cat}
Описание   : {desc}
Пример     : {example}
CLI        : mockjutsu generate {fn}
Python     : jutsu.generate('{fn}')
JMeter     : ${{__mockjutsu({fn},)}}

Правила:
- Язык: Русский (естественный и плавный, не дословный перевод)
- Длина: 300-400 слов
- Формат: Только теги <p>...</p>, никаких других HTML-тегов
- SEO-ключевые слова: "{fn}", "мок-данные", "тестовые данные", "mock-jutsu" — использовать естественно
- Содержание: что генерирует функция, какой алгоритм / стандарт используется,
  сценарии тестирования и преимущества для разработчика
- БЕЗ заголовка — только абзацы
""",
}


# ── Helpers ───────────────────────────────────────────────────────────────────
def get_functions():
    return [r for r in _REFERENCE if r[0].strip() and not r[0].strip().startswith("--")]


def txt_path(fn: str, lang: str) -> str:
    return os.path.join(CONTENT_DIR, f"{fn}_{lang}.txt")


def is_cached(fn: str, lang: str) -> bool:
    p = txt_path(fn, lang)
    return os.path.exists(p) and os.path.getsize(p) > 100


def call_gemini(prompt: str) -> str:
    url  = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7},
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 5 * (attempt + 1)
                print(f"  Rate limited, waiting {wait}s…")
                time.sleep(wait)
            elif attempt == 2:
                raise
            else:
                time.sleep(2 ** attempt)
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)
    return ""


def generate_one(fn: str, cat: str, desc: str, example: str, lang: str, force: bool) -> str:
    if not force and is_cached(fn, lang):
        return f"SKIP {fn}_{lang}"
    tmpl   = _PROMPTS[lang]
    prompt = tmpl.format(fn=fn, cat=cat, desc=desc, example=str(example)[:200])
    text   = call_gemini(prompt)
    with open(txt_path(fn, lang), "w", encoding="utf-8") as f:
        f.write(text)
    return f"OK   {fn}_{lang}"


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Mock Jutsu HOW-TO content generator")
    parser.add_argument("--lang",  default="", help="Only this language (TR/EN/UK/DE/FR/RU)")
    parser.add_argument("--fn",    default="", help="Only this function name")
    parser.add_argument("--force", action="store_true", help="Regenerate even if cached")
    parser.add_argument("--workers", type=int, default=MAX_WORKERS)
    args = parser.parse_args()

    if not API_KEY:
        print("ERROR: GEMINI_API_KEY not found.")
        print("  → Copy .env.example to .env and add your key.")
        print("  → Get a free key at: https://aistudio.google.com/")
        sys.exit(1)

    os.makedirs(CONTENT_DIR, exist_ok=True)

    langs = [args.lang.upper()] if args.lang else LANGS
    funcs = get_functions()
    if args.fn:
        funcs = [r for r in funcs if r[0] == args.fn]
        if not funcs:
            print(f"Function '{args.fn}' not found.")
            sys.exit(1)

    tasks = []
    for r in funcs:
        fn, cat, _, example, _, desc = r[0], r[1], r[2], r[3], r[4], r[5]
        for lang in langs:
            tasks.append((fn, cat, desc, example, lang))

    total  = len(tasks)
    cached = sum(1 for fn, cat, desc, ex, lang in tasks if not args.force and is_cached(fn, lang))
    to_gen = total - cached

    print(f"Model     : {MODEL}")
    print(f"Functions : {len(funcs)}")
    print(f"Languages : {', '.join(langs)}")
    print(f"Total     : {total}  |  Cached: {cached}  |  To generate: {to_gen}")
    print()

    if to_gen == 0:
        print("All content cached. Run generate_full_docs.py to build HTML pages.")
        return

    done = errors = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = {
            ex.submit(generate_one, fn, cat, desc, example, lang, args.force): (fn, lang)
            for fn, cat, desc, example, lang in tasks
        }
        for fut in as_completed(futures):
            fn, lang = futures[fut]
            try:
                msg = fut.result()
                print(f"[{done+errors+1:>4}/{total}] {msg}")
                done += 1
            except Exception as e:
                print(f"[{done+errors+1:>4}/{total}] ERR  {fn}_{lang}: {e}")
                errors += 1
            time.sleep(0.05)

    print()
    print(f"Generated: {done}  |  Errors: {errors}")
    if errors == 0:
        print("Run  python generate_full_docs.py  to build HTML pages.")


if __name__ == "__main__":
    main()
