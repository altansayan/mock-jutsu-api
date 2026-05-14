"""
Mock Jutsu — Function Validator
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)

Her _REFERENCE girişi için şunları doğrular:
  1. generators/ altında generate_{fn}() fonksiyonu var mı?
  2. 6 dilde .txt içerik dosyası mevcut mu?
  3. 6 dilde .html sayfası oluşturulmuş mu?

Kullanım:
  python validate_functions.py            (tüm fonksiyonlar)
  python validate_functions.py tckn       (tek fonksiyon)
"""

import os
import sys

BASE_DIR       = os.path.dirname(os.path.abspath(__file__))
GENERATORS_DIR = os.path.join(BASE_DIR, "src", "mockjutsu", "generators")
CONTENT_DIR    = os.path.join(BASE_DIR, "HOW-TO", "content")
HTML_DIR       = os.path.join(BASE_DIR, "HOW-TO")
LANGS          = ["TR", "EN", "UK", "DE", "FR", "RU"]

sys.path.insert(0, os.path.join(BASE_DIR, "src"))
from mockjutsu.cli import _REFERENCE


def get_funcs(filter_fn: str = "") -> list:
    rows = [
        r for r in _REFERENCE
        if r[0].strip()
        and not r[0].strip().startswith("--")
        and r[1] != "Commands"
    ]
    if filter_fn:
        rows = [r for r in rows if r[0] == filter_fn]
    return rows


def validate(filter_fn: str = "") -> int:
    from mockjutsu.core import MockJutsuCore
    jutsu  = MockJutsuCore()
    funcs  = get_funcs(filter_fn)
    errors = []

    if filter_fn and not funcs:
        print(f"HATA: '{filter_fn}' _REFERENCE'da bulunamadi.")
        return 1

    for r in funcs:
        fn = r[0]

        # 1 — Core'da kayıtlı mı? (ERROR dönüyorsa tip setinde yok demektir)
        result = str(jutsu.generate(fn))
        if result.startswith("ERROR"):
            errors.append(f"[CORE YOK]       {fn} — core.py tip setinde kayitli degil ({result})")

        # 2 — İçerik dosyaları (.txt)
        for lang in LANGS:
            path = os.path.join(CONTENT_DIR, f"{fn}_{lang}.txt")
            if not os.path.exists(path) or os.path.getsize(path) < 100:
                errors.append(f"[İÇERİK EKSİK]   {fn}_{lang}.txt — eksik veya boş")

        # 3 — HTML sayfaları
        for lang in LANGS:
            path = os.path.join(HTML_DIR, lang, "FUNCTION", f"{fn}-{lang}.html")
            if not os.path.exists(path):
                errors.append(f"[HTML EKSİK]     {fn}-{lang}.html — oluşturulmamış")

    if errors:
        print()
        print("mock-jutsu validate_functions: HATALAR BULUNDU")
        print("=" * 52)
        for e in errors:
            print(f"  {e}")
        print()
        print(f"Toplam {len(errors)} hata.")
        print()
        print("Düzeltmek için:")
        fn_hint = filter_fn or "<fn_adi>"
        print(f"  python generate_ai_content.py --fn {fn_hint}")
        print(f"  python generate_full_docs.py")
        return 1

    scope = f"'{filter_fn}'" if filter_fn else f"{len(funcs)} fonksiyon"
    print(
        f"mock-jutsu validate_functions: OK "
        f"({scope}, {len(funcs)*6} HTML sayfa, {len(funcs)*6} içerik dosyası)"
    )
    return 0


if __name__ == "__main__":
    fn_arg = sys.argv[1] if len(sys.argv) > 1 else ""
    sys.exit(validate(fn_arg))
