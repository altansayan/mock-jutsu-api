"""Generate placeholder HOW-TO content .txt files for types that are missing them."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mockjutsu.cli import _REFERENCE
from mockjutsu.core import jutsu

CONTENT_DIR = os.path.join(os.path.dirname(__file__), '..', 'HOW-TO', 'content')
LANGS = ['TR', 'EN', 'UK', 'DE', 'FR', 'RU']

LANG_META = {
    'TR': ('test verisi', 'mock veri', 'geliştiriciler'),
    'EN': ('test data', 'mock data', 'developers'),
    'UK': ('testovi dani', 'mock dani', 'rozrobnyky'),
    'DE': ('Testdaten', 'Mock-Daten', 'Entwickler'),
    'FR': ('données de test', 'données mock', 'développeurs'),
    'RU': ('тестовые данные', 'mock-данные', 'разработчики'),
}

missing = []
for r in _REFERENCE:
    fn = r[0].strip()
    if not fn or fn.startswith('--') or r[1] == 'Commands':
        continue
    for lang in LANGS:
        path = os.path.join(CONTENT_DIR, f'{fn}_{lang}.txt')
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            missing.append((fn, lang, r))

print(f'Missing: {len(missing)} files')

created = 0
for fn, lang, r in missing:
    _, cat, _, example, cli_cmd, desc, opts = r
    try:
        sample = str(jutsu.generate(fn))[:60]
    except Exception:
        sample = str(example)[:60]

    term1, term2, devs = LANG_META[lang]
    fn_label = fn.replace('_', ' ')

    content = (
        f'<p>The <strong>{fn}</strong> function in mock-jutsu generates {desc.lower()} '
        f'This generator belongs to the <em>{cat}</em> category and produces realistic '
        f'{term2} for testing purposes without touching production systems.</p>\n\n'
        f'<p>Use <code>jutsu.generate(\'{fn}\')</code> in Python or '
        f'<code>mockjutsu {cli_cmd}</code> from the CLI to get {fn_label} {term2}. '
        f'{devs.capitalize()} working with {cat} systems benefit from this mock generator '
        f'in unit tests, integration tests, and CI pipelines.</p>\n\n'
        f'<p>Sample output: <code>{sample}</code>. The mock-jutsu {fn} generator follows '
        f'real-world format specifications, ensuring that validation logic and downstream '
        f'parsers behave identically with synthetic {term1} as they would with real data.</p>\n\n'
        f'<p>For JMeter performance tests use '
        f'<code>${"{"}__mockjutsu({fn},){"}"}</code> to generate realistic {fn_label} '
        f'values at scale. mock-jutsu has zero runtime dependencies — all generation happens '
        f'locally in pure Python, making it safe and fast for any CI environment.</p>'
    )

    path = os.path.join(CONTENT_DIR, f'{fn}_{lang}.txt')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    created += 1

print(f'Created: {created} placeholder files')
