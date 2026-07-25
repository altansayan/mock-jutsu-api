"""Replace 'pip install mock-jutsu' with 'pip install mockjutsu' in all HOW-TO HTML files."""
import pathlib

root = pathlib.Path(__file__).parent.parent / "HOW-TO"
old = "pip install mock-jutsu"
new = "pip install mockjutsu"

count = 0
for f in root.rglob("*.html"):
    text = f.read_text(encoding="utf-8")
    if old in text:
        f.write_text(text.replace(old, new), encoding="utf-8")
        count += 1

print(f"Fixed {count} files.")
