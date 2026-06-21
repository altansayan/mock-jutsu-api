"""
Gemini API kullanarak tüm tip açıklamalarını 6 dile lokalize eder.
Çıktı: HOW-TO/content/descriptions.json

Kullanım:
    python scripts/generate_descriptions.py
    python scripts/generate_descriptions.py --langs TR FR  (sadece belirtilen diller)
    python scripts/generate_descriptions.py --resume       (mevcut JSON'u koruyarak eksikleri tamamla)
"""

import json
import os
import pathlib
import sys
import time
import argparse
import urllib.request
import urllib.error

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "src"))
from mockjutsu.cli import _REFERENCE

# ── Config ────────────────────────────────────────────────────────────────────

OUT_FILE = pathlib.Path(__file__).parent.parent / "HOW-TO" / "content" / "descriptions.json"

LANGS = {
    "TR": "Turkish",
    "EN": "English",
    "UK": "British English",
    "DE": "German",
    "FR": "French",
    "RU": "Russian",
}

LANG_SEO_NOTES = {
    "TR": "Türkçe, SEO uyumlu, doğal ve akıcı",
    "EN": "English, SEO-friendly, clear and concise",
    "UK": "British English, SEO-friendly, clear and concise",
    "DE": "Deutsch, SEO-optimiert, klar und prägnant",
    "FR": "Français, optimisé pour le SEO, clair et concis",
    "RU": "Русский, SEO-оптимизированный, чёткий и лаконичный",
}

BATCH_SIZE = 50  # Gemini'ye tek seferde gönderilen tip sayısı


def load_env():
    env_path = pathlib.Path(__file__).parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def get_all_types():
    return [
        (r[0], r[5])
        for r in _REFERENCE
        if r[0] and not r[0].startswith("--")
    ]


def call_gemini(prompt: str, api_key: str, model: str) -> str:
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.3,
            "responseMimeType": "application/json",
        },
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    return data["candidates"][0]["content"]["parts"][0]["text"]


def build_prompt(lang: str, lang_name: str, seo_note: str, batch: list[tuple]) -> str:
    types_block = "\n".join(
        f'  "{t}": "{desc}"' for t, desc in batch
    )
    return f"""You are a technical copywriter generating SEO-friendly descriptions for a developer mock data tool called MockJutsu.

For each type below, write a SHORT description (1-2 sentences, max 120 characters) in {lang_name}.
Rules:
- Language: {seo_note}
- Mention what kind of data is generated and its use case
- Do NOT mention "MockJutsu" in the description
- Keep technical terms (TCKN, IBAN, PAN, CVV, etc.) as-is — do not translate them
- Return ONLY a valid JSON object with type name as key and description as value
- No markdown, no code blocks, no extra text — raw JSON only

Types (key: English description):
{{
{types_block}
}}

Return format:
{{
  "type_name": "localized description here",
  ...
}}"""


def generate_for_lang(lang: str, types: list[tuple], api_key: str, model: str,
                      all_desc: dict, out_file: pathlib.Path) -> dict:
    lang_name = LANGS[lang]
    seo_note = LANG_SEO_NOTES[lang]
    results = {}

    missing = [(t, d) for t, d in types if t not in all_desc.get(t, {}) or lang not in all_desc.get(t, {})]
    if not missing:
        print(f"  [{lang}] Tum tipler mevcut, atlaniyor.")
        return {t: all_desc[t][lang] for t in all_desc if lang in all_desc.get(t, {})}

    print(f"  [{lang}] {len(missing)} tip islenecek ({len(types) - len(missing)} mevcut)...")

    batches = [missing[i:i + BATCH_SIZE] for i in range(0, len(missing), BATCH_SIZE)]
    for i, batch in enumerate(batches):
        print(f"    Batch {i+1}/{len(batches)} ({len(batch)} tip)...", end=" ", flush=True)
        prompt = build_prompt(lang, lang_name, seo_note, batch)

        retries = 4
        for attempt in range(retries):
            try:
                raw = call_gemini(prompt, api_key, model)
                parsed = json.loads(raw)
                results.update(parsed)
                print(f"OK ({len(parsed)} dondu)")
                break
            except (urllib.error.URLError, json.JSONDecodeError, KeyError,
                    TimeoutError, OSError) as e:
                if attempt < retries - 1:
                    wait = 10 * (attempt + 1)
                    print(f"HATA ({type(e).__name__}), {wait}s sonra tekrar...")
                    time.sleep(wait)
                else:
                    print(f"BASARISIZ: {e}")

        # Her batch sonrası kaydet (crash koruması)
        for t, desc in results.items():
            if t not in all_desc:
                all_desc[t] = {}
            all_desc[t][lang] = desc
        out_file.write_text(
            json.dumps(all_desc, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        time.sleep(2)

    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--langs", nargs="+", choices=list(LANGS.keys()),
                        default=list(LANGS.keys()), help="İşlenecek diller")
    parser.add_argument("--resume", action="store_true",
                        help="Mevcut descriptions.json'u koruyarak eksikleri tamamla")
    args = parser.parse_args()

    load_env()
    api_key = os.environ.get("GEMINI_API_KEY", "")
    model = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
    if not api_key:
        print("HATA: GEMINI_API_KEY bulunamadı (.env dosyasını kontrol et)")
        sys.exit(1)

    print(f"Model: {model}")
    print(f"Diller: {args.langs}")

    types = get_all_types()
    print(f"Toplam tip: {len(types)}")

    # Mevcut dosyayı yükle (resume modu veya güncelleme)
    existing = {}
    if OUT_FILE.exists() and (args.resume or True):
        existing = json.loads(OUT_FILE.read_text(encoding="utf-8"))
        print(f"Mevcut descriptions.json yüklendi ({sum(len(v) for v in existing.values())} entry)")

    all_descriptions = dict(existing)

    for lang in args.langs:
        print(f"\n[{lang}] {LANGS[lang]} işleniyor...")
        generate_for_lang(lang, types, api_key, model, all_descriptions, OUT_FILE)

        count = sum(1 for t in all_descriptions if lang in all_descriptions.get(t, {}))
        print(f"  [{lang}] tamamlandi -> {count} tip")

    # Özet
    total = sum(1 for t in all_descriptions for _ in all_descriptions[t])
    print(f"\nTamamlandi: {len(all_descriptions)} tip, {total} toplam description")
    print(f"Cikti: {OUT_FILE}")


if __name__ == "__main__":
    main()
