"""
Generates 6 locale-specific HOW-TO HTML files dynamically from CLI REFERENCE.
"""
import os
import sys

# Ensure src is in PYTHONPATH if run locally
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from mockjutsu.cli import _REFERENCE

BASE_CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
background:#f8fafc;color:#1e293b;line-height:1.6}
.header{background:#0f172a;color:#fff;padding:2rem 2rem 3rem;text-align:center}
.header h1{font-size:1.8rem;margin-bottom:.5rem;font-weight:700}
.header .sub{font-size:.9rem;color:#94a3b8}
.tabs{display:flex;justify-content:center;background:#fff;border-bottom:1px solid #e2e8f0;margin-top:-1rem;padding:0 1rem;gap:1rem}
.tab{padding:1rem 1.5rem;cursor:pointer;font-weight:500;color:#64748b;border-bottom:3px solid transparent;transition:all .2s ease;font-size:.95rem}
.tab:hover{color:#3b82f6}
.tab.active{color:#3b82f6;border-bottom-color:#3b82f6}
.section{display:none;padding:2rem;max-width:1200px;margin:0 auto}
.section.active{display:block;animation:fadeIn .3s ease}
@keyframes fadeIn{from{opacity:0;transform:translateY(5px)}to{opacity:1;transform:translateY(0)}}
.stitle{font-size:1.25rem;font-weight:600;margin-bottom:1.5rem;color:#0f172a;padding-left:10px;border-left:4px solid #3b82f6}
.toolbar{display:flex;gap:1rem;margin-bottom:1.5rem;flex-wrap:wrap;align-items:center;background:#fff;padding:1rem;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,.05)}
.toolbar input,.toolbar select{padding:.6rem 1rem;border:1px solid #cbd5e1;border-radius:6px;font-size:.9rem;outline:none;transition:border-color .2s}
.toolbar input:focus,.toolbar select:focus{border-color:#3b82f6;box-shadow:0 0 0 3px rgba(59,130,246,.1)}
.toolbar input{flex:1;min-width:250px}
.reset-btn{padding:.6rem 1.2rem;background:#f1f5f9;border:1px solid #cbd5e1;border-radius:6px;cursor:pointer;font-size:.9rem;font-weight:500;color:#475569;transition:all .2s}
.reset-btn:hover{background:#e2e8f0}
.row-count{font-size:.85rem;color:#64748b;font-weight:500;margin-left:auto}
.table-wrap{background:#fff;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,.05);overflow-x:auto}
table{width:100%;border-collapse:collapse;text-align:left;font-size:.9rem}
th,td{padding:1rem;border-bottom:1px solid #e2e8f0;vertical-align:middle}
th{background:#f8fafc;font-weight:600;color:#475569;text-transform:uppercase;font-size:.75rem;letter-spacing:.05em;white-space:nowrap}
tr:hover td{background:#f1f5f9}
code{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace;font-size:.85rem;padding:.2rem .4rem;background:#f1f5f9;border-radius:4px;color:#0f172a}
.pill{display:inline-block;padding:.25rem .6rem;border-radius:9999px;font-size:.75rem;font-weight:600;white-space:nowrap}
.lc{display:inline-block;padding:.15rem .4rem;border-radius:4px;font-size:.7rem;font-weight:700;margin:1px;font-family:monospace}
.badge-no{color:#94a3b8;font-size:.8rem}
.cat-kimlik{background:#eff6ff;color:#1d4ed8}
.cat-vergi{background:#fdf4ff;color:#86198f}
.cat-isveren{background:#f0fdf4;color:#15803d}
.cat-sigorta{background:#fffbeb;color:#b45309}
.cat-isim{background:#f0f9ff;color:#0369a1}
.cat-belge{background:#f8fafc;color:#475569}
.cat-demografik{background:#faf5ff;color:#6b21a8}
.cat-finansal{background:#ecfdf5;color:#047857}
.cat-iletisim{background:#fff1f2;color:#be123c}
.cat-meta{background:#f1f5f9;color:#334155}
.cat-bankacilik{background:#eef2ff;color:#4338ca}
.cat-kurumsal{background:#fdf2f8;color:#be185d}
.cat-saglik{background:#f0fdfa;color:#0f766e}
.cat-ticaret{background:#fff7ed;color:#c2410c}
.cat-guvenlik{background:#fee2e2;color:#b91c1c}
.cat-rfid,.cat-nfc{background:#e0e7ff;color:#3730a3}
.cat-ir{background:#ffe4e6;color:#e11d48}
.cat-barkod{background:#f1f5f9;color:#0f172a}
.cat-telecom{background:#fdf4ff;color:#a21caf}
.cat-securities{background:#ecfccb;color:#3f6212}
.cat-crypto{background:#fef3c7;color:#b45309}
.cat-ecommerce{background:#fae8ff;color:#86198f}
.cat-location{background:#e0f2fe;color:#0369a1}
.cat-social{background:#dbeafe;color:#1e40af}
.lc-TR{background:#fee2e2;color:#991b1b}
.lc-US{background:#e0e7ff;color:#3730a3}
.lc-UK{background:#dbeafe;color:#1e40af}
.lc-FR{background:#ecfdf5;color:#065f46}
.lc-RU{background:#ffedd5;color:#9a3412}
.lc-DE{background:#fce7f3;color:#9d174d}
.col-fn{width:15%}
.col-cat{width:12%}
.col-locale{width:12%}
.col-extra{width:15%}
.col-output{width:20%}
.col-cli{width:26%}
.qs-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:1.5rem}
.qs-card{background:#fff;border-radius:8px;padding:1.5rem;box-shadow:0 1px 3px rgba(0,0,0,.05);border:1px solid #e2e8f0}
.qs-card h3{font-size:1rem;color:#0f172a;margin-bottom:1rem;display:flex;align-items:center;gap:.5rem}
.qs-card h3::before{content:"";display:block;width:8px;height:8px;background:#3b82f6;border-radius:50%}
.qs-card pre{background:#0f172a;color:#f8fafc;padding:1rem;border-radius:6px;font-size:.85rem;overflow-x:auto;line-height:1.5}
.qs-card pre .kw{color:#38bdf8}
.qs-card pre .st{color:#a3e635}
.qs-card pre .cm{color:#64748b}
.qs-card pre .fn{color:#f472b6}
.footer{text-align:center;padding:2rem;color:#64748b;font-size:.85rem;margin-top:2rem}
.locale-card{background:#fff;padding:1rem 1.5rem;border-radius:8px;border:1px solid #e2e8f0;display:flex;align-items:center;gap:1.5rem}
.locale-card h3{font-size:1rem;color:#0f172a;margin:0}
.locale-card ul{list-style:none;display:flex;gap:.5rem;flex-wrap:wrap;margin:0}
"""

def build_rows_js():
    # Construct ROWS array from _REFERENCE
    rows = []
    for r in _REFERENCE:
        fn = r[0].strip()
        if not fn or fn.startswith("--"):
            continue
        cat = r[1]
        catCls = cat.split("/")[0].lower()
        if "kimlik" in catCls: catCls = "kimlik"
        elif "vergi" in catCls: catCls = "vergi"
        elif "bank" in catCls: catCls = "bankacilik"
        # simplifications
        localeAware = r[2]
        out = r[3]
        cli = r[4]
        if not cli.startswith("mockjutsu "):
            cli = "mockjutsu " + cli
        extra = "—"
        if "--network" in cli: extra = "--network"
        elif "--algorithm" in cli: extra = "--algorithm"
        elif "currency" in cli and "--" in cli: extra = "..."
        
        locales = "TR US UK DE FR RU" if localeAware else ""
        
        row_str = '  ["{fn}","{cat}","{catCls}",{localeAware_str},"{extra}","{out_safe}","{cli}","{locales}"]'.format(
            fn=fn, cat=cat, catCls=catCls, localeAware_str=str(localeAware).lower(),
            extra=extra, out_safe=out.replace('"', '\\"'), cli=cli, locales=locales
        )
        rows.append(row_str)
        
    return "const ROWS = [\n" + ",\n".join(rows) + "\n];"

ROWS_JS = build_rows_js()

# ── Category translations per locale ─────────────────────────────────────────
CAT_TRANSLATIONS = {
    'TR': {},
    'EN': {
        'Kimlik': 'Identity', 'Kimlik/TR': 'Identity/TR', 'Kimlik/US': 'Identity/US',
        'Kimlik/UK': 'Identity/UK', 'Kimlik/DE': 'Identity/DE',
        'Kimlik/FR': 'Identity/FR', 'Kimlik/RU': 'Identity/RU',
        'Kimlik/Vergi': 'Identity/Tax', 'İşveren': 'Employer', 'Sigorta': 'Insurance',
        'İsim': 'Name', 'Belge': 'Document', 'Demografik': 'Demographic',
        'Finansal': 'Financial', 'İletişim': 'Contact', 'Meta': 'Meta',
        'Bankacılık': 'Banking', 'Kurumsal': 'Corporate', 'Sağlık': 'Health',
        'Ticaret': 'Commerce', 'Güvenlik': 'Security',
        'Hardware': 'Hardware',
        'IR (Kızılötesi)': 'IR (Infrared)', 'Barkod': 'Barcode',
    },
    'UK': {
        'Kimlik': 'Identity', 'Kimlik/TR': 'Identity/TR', 'Kimlik/US': 'Identity/US',
        'Kimlik/UK': 'Identity/UK', 'Kimlik/DE': 'Identity/DE',
        'Kimlik/FR': 'Identity/FR', 'Kimlik/RU': 'Identity/RU',
        'Kimlik/Vergi': 'Identity/Tax', 'İşveren': 'Employer', 'Sigorta': 'Insurance',
        'İsim': 'Name', 'Belge': 'Document', 'Demografik': 'Demographic',
        'Finansal': 'Financial', 'İletişim': 'Contact', 'Meta': 'Meta',
        'Bankacılık': 'Banking', 'Kurumsal': 'Corporate', 'Sağlık': 'Health',
        'Ticaret': 'Commerce', 'Güvenlik': 'Security',
        'Hardware': 'Hardware',
        'IR (Kızılötesi)': 'IR (Infrared)', 'Barkod': 'Barcode',
    },
    'DE': {
        'Kimlik': 'Identität', 'Kimlik/TR': 'Identität/TR', 'Kimlik/US': 'Identität/US',
        'Kimlik/UK': 'Identität/UK', 'Kimlik/DE': 'Identität/DE',
        'Kimlik/FR': 'Identität/FR', 'Kimlik/RU': 'Identität/RU',
        'Kimlik/Vergi': 'Identität/Steuer', 'İşveren': 'Arbeitgeber',
        'Sigorta': 'Versicherung', 'İsim': 'Name', 'Belge': 'Dokument',
        'Demografik': 'Demografisch', 'Finansal': 'Finanziell',
        'İletişim': 'Kontakt', 'Meta': 'Meta', 'Bankacılık': 'Bankwesen',
        'Kurumsal': 'Unternehmen', 'Sağlık': 'Gesundheit',
        'Ticaret': 'Handel', 'Güvenlik': 'Sicherheit',
        'Hardware': 'Hardware',
        'IR (Kızılötesi)': 'IR (Infrarot)', 'Barkod': 'Barcode',
    },
    'FR': {
        'Kimlik': 'Identité', 'Kimlik/TR': 'Identité/TR', 'Kimlik/US': 'Identité/US',
        'Kimlik/UK': 'Identité/UK', 'Kimlik/DE': 'Identité/DE',
        'Kimlik/FR': 'Identité/FR', 'Kimlik/RU': 'Identité/RU',
        'Kimlik/Vergi': 'Identité/Fiscal', 'İşveren': 'Employeur',
        'Sigorta': 'Assurance', 'İsim': 'Nom', 'Belge': 'Document',
        'Demografik': 'Démographique', 'Finansal': 'Financier',
        'İletişim': 'Contact', 'Meta': 'Méta', 'Bankacılık': 'Banque',
        'Kurumsal': 'Entreprise', 'Sağlık': 'Santé',
        'Ticaret': 'Commerce', 'Güvenlik': 'Sécurité',
        'Hardware': 'Matériel',
        'IR (Kızılötesi)': 'IR (Infrarouge)', 'Barkod': 'Code-barres',
    },
    'RU': {
        'Kimlik': 'Идентификация', 'Kimlik/TR': 'Идент./TR',
        'Kimlik/US': 'Идент./US', 'Kimlik/UK': 'Идент./UK',
        'Kimlik/DE': 'Идент./DE', 'Kimlik/FR': 'Идент./FR',
        'Kimlik/RU': 'Идент./RU', 'Kimlik/Vergi': 'Идент./Налог',
        'İşveren': 'Работодатель', 'Sigorta': 'Страхование',
        'İsim': 'Имя', 'Belge': 'Документ', 'Demografik': 'Демографический',
        'Finansal': 'Финансовый', 'İletişim': 'Контакт', 'Meta': 'Мета',
        'Bankacılık': 'Банковское дело', 'Kurumsal': 'Корпоративный',
        'Sağlık': 'Здоровье', 'Ticaret': 'Торговля', 'Güvenlik': 'Безопасность',
        'Hardware': 'Аппаратное обеспечение',
        'IR (Kızılötesi)': 'ИК (Инфракрасный)', 'Barkod': 'Штрихкод',
    },
}

def translate_rows(rows_js, loc_key):
    trans = CAT_TRANSLATIONS.get(loc_key, {})
    if not trans:
        return rows_js
    result = rows_js
    for tr_key in sorted(trans, key=len, reverse=True):
        result = result.replace(f'"{tr_key}"', f'"{trans[tr_key]}"')
    return result

TOTAL_PARAMS = len([r for r in _REFERENCE if r[0].strip() and not r[0].strip().startswith("--")])

LOCALES = {
    'TR': {
        'lang': 'tr',
        'flag': '🇹🇷',
        'title': 'mock-jutsu — TR Referans Kılavuzu',
        'header_title': 'mock-jutsu &mdash; TR Referans Kılavuzu',
        'header_sub': f'6 locale &nbsp;&bull;&nbsp; {TOTAL_PARAMS} parametre tipi &nbsp;&bull;&nbsp; Yasal algoritmalar &nbsp;&bull;&nbsp; Developer: Altan Sezer Ayan - A.S.A',
        'tabs': ['Tam Referans', 'Hızlı Başlangıç', 'Güçlü Özellikler', 'REST API'],
        'section_ref': f'Tüm Parametreler ({TOTAL_PARAMS})',
        'search_placeholder': 'Fonksiyon, CLI komutu veya örnek çıktı ara...',
        'cat_label': 'Tüm Kategoriler',
        'locale_label': 'Locale Filtresi',
        'reset_btn': 'Sıfırla',
        'col_fn': 'FONKSİYON', 'col_cat': 'KATEGORİ', 'col_loc': 'LOCALE',
        'col_extra': 'EK PARAMETRE', 'col_out': 'ÖRNEK ÇIKTI', 'col_cli': 'CLI KOMUTU',
        'badge_yes': 'Evet', 'badge_no': '—',
        'section_qs': 'Hızlı Başlangıç',
        'section_power': 'Güçlü Özellikler',
        'section_api': 'REST API',
        'locale_code': 'TR',
        'id_types': ['tckn', 'ykn', 'vkn', 'sgk', 'mersis'],
        'id_label': 'Türkiye Kimlik Tipleri',
        'qs_cards': [
            ('Python API', '''<span class="cm"># Tek değer</span>\njutsu.generate(<span class="st">'tckn'</span>)           <span class="cm"># → '45678901234'</span>\njutsu.generate(<span class="st">'iban'</span>, locale=<span class="st">'TR'</span>)   <span class="cm"># → 'TR33000610…'</span>\njutsu.generate(<span class="st">'phone'</span>, locale=<span class="st">'TR'</span>)  <span class="cm"># → '+905321234567'</span>\njutsu.generate(<span class="st">'cardnum'</span>, network=<span class="st">'troy'</span>)'''),
            ('CLI', '''mockjutsu generate tckn\nmockjutsu generate iban --locale TR\nmockjutsu generate phone --locale TR\nmockjutsu generate cardnum --network troy\nmockjutsu bulk tckn --count 1000\nmockjutsu template tckn fullname phone iban --locale TR\nmockjutsu start-api --port 8000'''),
            ('TR Kimlik Profili', '''p = jutsu.profile(locale=<span class="st">'TR'</span>)\n<span class="cm"># tckn, firstname, lastname,</span>\n<span class="cm"># phone (+90...), email,</span>\n<span class="cm"># iban (TR...), address</span>\n\n<span class="cm"># CLI</span>\nmockjutsu profile --locale TR --count 3'''),
            ('TR Fintech Örneği', '''jutsu.generate(<span class="st">'tckn'</span>)          <span class="cm"># 34521876543</span>\njutsu.generate(<span class="st">'vkn'</span>)           <span class="cm"># 1234567890</span>\njutsu.generate(<span class="st">'sgk'</span>)           <span class="cm"># 34-0012345-1.01-02</span>\njutsu.generate(<span class="st">'mersis'</span>)        <span class="cm"># 1234567890012345</span>\njutsu.generate(<span class="st">'iban'</span>, locale=<span class="st">'TR'</span>)\njutsu.generate(<span class="st">'plate'</span>, locale=<span class="st">'TR'</span>) <span class="cm"># 34 ABC 123</span>'''),
        ],
    },
    'EN': {
        'lang': 'en',
        'flag': '🇺🇸',
        'title': 'mock-jutsu — US Reference Guide',
        'header_title': 'mock-jutsu &mdash; US Reference Guide',
        'header_sub': f'6 locales &nbsp;&bull;&nbsp; {TOTAL_PARAMS} data types &nbsp;&bull;&nbsp; Legal algorithms &nbsp;&bull;&nbsp; Developer: Altan Sezer Ayan - A.S.A',
        'tabs': ['Full Reference', 'Quick Start', 'Advanced Features', 'REST API'],
        'section_ref': f'All Parameters ({TOTAL_PARAMS})',
        'search_placeholder': 'Search function, CLI command or example output...',
        'cat_label': 'All Categories',
        'locale_label': 'Locale Filter',
        'reset_btn': 'Reset',
        'col_fn': 'FUNCTION', 'col_cat': 'CATEGORY', 'col_loc': 'LOCALE',
        'col_extra': 'EXTRA PARAM', 'col_out': 'EXAMPLE OUTPUT', 'col_cli': 'CLI COMMAND',
        'badge_yes': 'Yes', 'badge_no': '—',
        'section_qs': 'Quick Start',
        'section_power': 'Advanced Features',
        'section_api': 'REST API',
        'locale_code': 'US',
        'id_types': ['ssn', 'ein', 'ssn_masked'],
        'id_label': 'US Identity Types',
        'qs_cards': [
            ('Python API', '''<span class="cm"># Single value</span>\njutsu.generate(<span class="st">'ssn'</span>)             <span class="cm"># → '234-56-7890'</span>\njutsu.generate(<span class="st">'ein'</span>)             <span class="cm"># → '12-3456789'</span>\njutsu.generate(<span class="st">'phone'</span>, locale=<span class="st">'US'</span>)  <span class="cm"># → '+15551234567'</span>\njutsu.generate(<span class="st">'cardnum'</span>, network=<span class="st">'visa'</span>)'''),
            ('CLI', '''mockjutsu generate ssn\nmockjutsu generate ein\nmockjutsu generate phone --locale US\nmockjutsu generate iban --locale US\nmockjutsu bulk ssn --count 500\nmockjutsu template ssn firstname lastname phone --locale US\nmockjutsu start-api --port 8000'''),
            ('US Person Profile', '''p = jutsu.profile(locale=<span class="st">'US'</span>)\n<span class="cm"># ssn, firstname, lastname,</span>\n<span class="cm"># phone (+1...), email,</span>\n<span class="cm"># routing+account (US IBAN)</span>\n\n<span class="cm"># CLI</span>\nmockjutsu profile --locale US --count 3'''),
            ('US Fintech Example', '''jutsu.generate(<span class="st">'ssn'</span>)            <span class="cm"># 234-56-7890</span>\njutsu.generate(<span class="st">'ein'</span>)            <span class="cm"># 12-3456789</span>\njutsu.generate(<span class="st">'routing_number'</span>) <span class="cm"># 021000021</span>\njutsu.generate(<span class="st">'credit_score'</span>)   <span class="cm"># 720</span>\njutsu.generate(<span class="st">'isin'</span>, locale=<span class="st">'US'</span>)<span class="cm"># US0378331005</span>\njutsu.generate(<span class="st">'zip'</span>, locale=<span class="st">'US'</span>) <span class="cm"># postalcode</span>'''),
        ],
    },
    'UK': {
        'lang': 'en-GB',
        'flag': '🇬🇧',
        'title': 'mock-jutsu — UK Reference Guide',
        'header_title': 'mock-jutsu &mdash; UK Reference Guide',
        'header_sub': f'6 locales &nbsp;&bull;&nbsp; {TOTAL_PARAMS} data types &nbsp;&bull;&nbsp; Legal algorithms &nbsp;&bull;&nbsp; Developer: Altan Sezer Ayan - A.S.A',
        'tabs': ['Full Reference', 'Quick Start', 'Advanced Features', 'REST API'],
        'section_ref': f'All Parameters ({TOTAL_PARAMS})',
        'search_placeholder': 'Search function, CLI command or example output...',
        'cat_label': 'All Categories',
        'locale_label': 'Locale Filter',
        'reset_btn': 'Reset',
        'col_fn': 'FUNCTION', 'col_cat': 'CATEGORY', 'col_loc': 'LOCALE',
        'col_extra': 'EXTRA PARAM', 'col_out': 'EXAMPLE OUTPUT', 'col_cli': 'CLI COMMAND',
        'badge_yes': 'Yes', 'badge_no': '—',
        'section_qs': 'Quick Start',
        'section_power': 'Advanced Features',
        'section_api': 'REST API',
        'locale_code': 'UK',
        'id_types': ['nin', 'utr', 'crn', 'paye', 'nhs_number'],
        'id_label': 'UK Identity Types',
        'qs_cards': [
            ('Python API', '''<span class="cm"># Single value</span>\njutsu.generate(<span class="st">'nin'</span>)               <span class="cm"># → 'AB 12 34 56 C'</span>\njutsu.generate(<span class="st">'utr'</span>)               <span class="cm"># → '1234567890'</span>\njutsu.generate(<span class="st">'nhs_number'</span>)        <span class="cm"># → '943 476 5919'</span>\njutsu.generate(<span class="st">'phone'</span>, locale=<span class="st">'UK'</span>)  <span class="cm"># → '+441234567890'</span>'''),
            ('CLI', '''mockjutsu generate nin\nmockjutsu generate utr\nmockjutsu generate crn\nmockjutsu generate nhs_number\nmockjutsu generate iban --locale UK\nmockjutsu bulk nin --count 500\nmockjutsu template nin utr nhs_number phone --locale UK\nmockjutsu start-api --port 8000'''),
            ('UK Person Profile', '''p = jutsu.profile(locale=<span class="st">'UK'</span>)\n<span class="cm"># nin, firstname, lastname,</span>\n<span class="cm"># phone (+44...), email,</span>\n<span class="cm"># iban (GB...)  </span>\n\n<span class="cm"># CLI</span>\nmockjutsu profile --locale UK --count 3'''),
            ('UK Fintech Example', '''jutsu.generate(<span class="st">'nin'</span>)          <span class="cm"># AB 12 34 56 C</span>\njutsu.generate(<span class="st">'sort_code'</span>)   <span class="cm"># 20-00-00</span>\njutsu.generate(<span class="st">'utr'</span>)          <span class="cm"># 1234567890</span>\njutsu.generate(<span class="st">'crn'</span>)          <span class="cm"># 12345678</span>\njutsu.generate(<span class="st">'paye'</span>)         <span class="cm"># 123/AB4567</span>\njutsu.generate(<span class="st">'iban'</span>, locale=<span class="st">'UK'</span>)  <span class="cm"># GB82WEST…</span>'''),
        ],
    },
    'DE': {
        'lang': 'de',
        'flag': '🇩🇪',
        'title': 'mock-jutsu — DE Referenzhandbuch',
        'header_title': 'mock-jutsu &mdash; DE Referenzhandbuch',
        'header_sub': f'6 Sprachräume &nbsp;&bull;&nbsp; {TOTAL_PARAMS} Datentypen &nbsp;&bull;&nbsp; Rechtskonforme Algorithmen &nbsp;&bull;&nbsp; Entwickler: Altan Sezer Ayan - A.S.A',
        'tabs': ['Vollreferenz', 'Schnellstart', 'Erweiterte Funktionen', 'REST API'],
        'section_ref': f'Alle Parameter ({TOTAL_PARAMS})',
        'search_placeholder': 'Funktion, CLI-Befehl oder Beispielausgabe suchen...',
        'cat_label': 'Alle Kategorien',
        'locale_label': 'Locale-Filter',
        'reset_btn': 'Zurücksetzen',
        'col_fn': 'FUNKTION', 'col_cat': 'KATEGORIE', 'col_loc': 'LOCALE',
        'col_extra': 'EXTRA-PARAM', 'col_out': 'BEISPIELAUSGABE', 'col_cli': 'CLI-BEFEHL',
        'badge_yes': 'Ja', 'badge_no': '—',
        'section_qs': 'Schnellstart',
        'section_power': 'Erweiterte Funktionen',
        'section_api': 'REST API',
        'locale_code': 'DE',
        'id_types': ['ust_id', 'ustid', 'hrb', 'siren'],
        'id_label': 'Deutsche Identitätstypen',
        'qs_cards': [
            ('Python API', '''<span class="cm"># Einzelwert</span>\njutsu.generate(<span class="st">'ust_id'</span>)           <span class="cm"># → 'DE123456789'</span>\njutsu.generate(<span class="st">'hrb'</span>)              <span class="cm"># → 'HRB 123456'</span>\njutsu.generate(<span class="st">'iban'</span>, locale=<span class="st">'DE'</span>)  <span class="cm"># → 'DE89370400…'</span>\njutsu.generate(<span class="st">'phone'</span>, locale=<span class="st">'DE'</span>) <span class="cm"># → '+4989123456'</span>'''),
            ('CLI', '''mockjutsu generate ust_id\nmockjutsu generate hrb\nmockjutsu generate iban --locale DE\nmockjutsu generate phone --locale DE\nmockjutsu bulk ust_id --count 500\nmockjutsu template ust_id hrb iban company_name --locale DE\nmockjutsu start-api --port 8000'''),
            ('DE Personenprofil', '''p = jutsu.profile(locale=<span class="st">'DE'</span>)\n<span class="cm"># ust_id, Vorname, Nachname,</span>\n<span class="cm"># Telefon (+49...), E-Mail,</span>\n<span class="cm"># IBAN (DE...)</span>\n\n<span class="cm"># CLI</span>\nmockjutsu profile --locale DE --count 3'''),
            ('DE Fintech-Beispiel', '''jutsu.generate(<span class="st">'ust_id'</span>)         <span class="cm"># DE123456789</span>\njutsu.generate(<span class="st">'hrb'</span>)            <span class="cm"># HRB 123456</span>\njutsu.generate(<span class="st">'rvn'</span>)            <span class="cm"># 65 070892 W 1235</span>\njutsu.generate(<span class="st">'bic'</span>, locale=<span class="st">'DE'</span>)<span class="cm"># DEUTDEDB</span>\njutsu.generate(<span class="st">'iban'</span>, locale=<span class="st">'DE'</span>)\njutsu.company(locale=<span class="st">'DE'</span>)       <span class="cm"># tam şirket</span>'''),
        ],
    },
    'FR': {
        'lang': 'fr',
        'flag': '🇫🇷',
        'title': 'mock-jutsu — Guide de Référence FR',
        'header_title': 'mock-jutsu &mdash; Guide de Référence FR',
        'header_sub': f'6 régions &nbsp;&bull;&nbsp; {TOTAL_PARAMS} types de données &nbsp;&bull;&nbsp; Algorithmes légaux &nbsp;&bull;&nbsp; Développeur: Altan Sezer Ayan - A.S.A',
        'tabs': ['Référence Complète', 'Démarrage Rapide', 'Fonctionnalités Avancées', 'REST API'],
        'section_ref': f'Tous les Paramètres ({TOTAL_PARAMS})',
        'search_placeholder': 'Rechercher une fonction, commande CLI ou exemple...',
        'cat_label': 'Toutes Catégories',
        'locale_label': 'Filtre Locale',
        'reset_btn': 'Réinitialiser',
        'col_fn': 'FONCTION', 'col_cat': 'CATÉGORIE', 'col_loc': 'LOCALE',
        'col_extra': 'PARAM EXTRA', 'col_out': 'EXEMPLE DE SORTIE', 'col_cli': 'COMMANDE CLI',
        'badge_yes': 'Oui', 'badge_no': '—',
        'section_qs': 'Démarrage Rapide',
        'section_power': 'Fonctionnalités Avancées',
        'section_api': 'REST API',
        'locale_code': 'FR',
        'id_types': ['siren', 'siret', 'tva'],
        'id_label': "Types d'identité français",
        'qs_cards': [
            ('Python API', '''<span class="cm"># Valeur unique</span>\njutsu.generate(<span class="st">'siren'</span>)            <span class="cm"># → '732829320'</span>\njutsu.generate(<span class="st">'siret'</span>)            <span class="cm"># → '73282932000074'</span>\njutsu.generate(<span class="st">'tva'</span>)              <span class="cm"># → 'FR73732829320'</span>\njutsu.generate(<span class="st">'iban'</span>, locale=<span class="st">'FR'</span>)  <span class="cm"># → 'FR7614508…'</span>'''),
            ('CLI', '''mockjutsu generate siren\nmockjutsu generate siret\nmockjutsu generate tva\nmockjutsu generate iban --locale FR\nmockjutsu bulk siren --count 500\nmockjutsu template siren siret tva iban company_name --locale FR\nmockjutsu start-api --port 8000'''),
            ('Profil Personne FR', '''p = jutsu.profile(locale=<span class="st">'FR'</span>)\n<span class="cm"># siren, prénom, nom,</span>\n<span class="cm"># téléphone (+33...), e-mail,</span>\n<span class="cm"># IBAN (FR...)</span>\n\n<span class="cm"># CLI</span>\nmockjutsu profile --locale FR --count 3'''),
            ('Exemple Fintech FR', '''jutsu.generate(<span class="st">'siren'</span>)        <span class="cm"># 732829320</span>\njutsu.generate(<span class="st">'siret'</span>)        <span class="cm"># 73282932000074</span>\njutsu.generate(<span class="st">'tva'</span>)          <span class="cm"># FR73732829320</span>\njutsu.generate(<span class="st">'bic'</span>, locale=<span class="st">'FR'</span>)\njutsu.generate(<span class="st">'iban'</span>, locale=<span class="st">'FR'</span>)\njutsu.company(locale=<span class="st">'FR'</span>)'''),
        ],
    },
    'RU': {
        'lang': 'ru',
        'flag': '🇷🇺',
        'title': 'mock-jutsu — Справочник RU',
        'header_title': 'mock-jutsu &mdash; Справочник RU',
        'header_sub': f'6 регионов &nbsp;&bull;&nbsp; {TOTAL_PARAMS} типа данных &nbsp;&bull;&nbsp; Правовые алгоритмы &nbsp;&bull;&nbsp; Разработчик: Altan Sezer Ayan - A.S.A',
        'tabs': ['Полный Справочник', 'Быстрый Старт', 'Расширенные Возможности', 'REST API'],
        'section_ref': f'Все Параметры ({TOTAL_PARAMS})',
        'search_placeholder': 'Поиск функции, CLI команды или примера вывода...',
        'cat_label': 'Все Категории',
        'locale_label': 'Фильтр Locale',
        'reset_btn': 'Сбросить',
        'col_fn': 'ФУНКЦИЯ', 'col_cat': 'КАТЕГОРИЯ', 'col_loc': 'LOCALE',
        'col_extra': 'ДОП. ПАРАМЕТР', 'col_out': 'ПРИМЕР ВЫВОДА', 'col_cli': 'CLI КОМАНДА',
        'badge_yes': 'Да', 'badge_no': '—',
        'section_qs': 'Быстрый Старт',
        'section_power': 'Расширенные Возможности',
        'section_api': 'REST API',
        'locale_code': 'RU',
        'id_types': ['inn', 'snils', 'ogrn', 'kpp', 'patronymic'],
        'id_label': 'Российские типы идентификации',
        'qs_cards': [
            ('Python API', '''<span class="cm"># Одно значение</span>\njutsu.generate(<span class="st">'inn'</span>)             <span class="cm"># → '7707083893'</span>\njutsu.generate(<span class="st">'snils'</span>)           <span class="cm"># → '112-233-445 95'</span>\njutsu.generate(<span class="st">'ogrn'</span>)            <span class="cm"># → '1027700132195'</span>\njutsu.generate(<span class="st">'phone'</span>, locale=<span class="st">'RU'</span>) <span class="cm"># → '+79161234567'</span>'''),
            ('CLI', '''mockjutsu generate inn\nmockjutsu generate snils\nmockjutsu generate ogrn\nmockjutsu generate kpp\nmockjutsu generate patronymic --locale RU\nmockjutsu bulk inn --count 500\nmockjutsu template inn snils ogrn phone --locale RU\nmockjutsu start-api --port 8000'''),
            ('Профиль Персоны RU', '''p = jutsu.profile(locale=<span class="st">'RU'</span>)\n<span class="cm"># inn, имя, отчество, фамилия,</span>\n<span class="cm"># телефон (+7...), email,</span>\n<span class="cm"># bik_code + счёт</span>\n\n<span class="cm"># CLI</span>\nmockjutsu profile --locale RU --count 3'''),
            ('Финтех-пример RU', '''jutsu.generate(<span class="st">'inn'</span>)          <span class="cm"># 7707083893</span>\njutsu.generate(<span class="st">'snils'</span>)        <span class="cm"># 112-233-445 95</span>\njutsu.generate(<span class="st">'ogrn'</span>)         <span class="cm"># 1027700132195</span>\njutsu.generate(<span class="st">'kpp'</span>)          <span class="cm"># 770701001</span>\njutsu.generate(<span class="st">'bik_code'</span>)     <span class="cm"># 044525225</span>\njutsu.company(locale=<span class="st">'RU'</span>)'''),
        ],
    },
}

def build_qs_cards(cards):
    html = ''
    for title, code in cards:
        html += f'''    <div class="qs-card">
      <h3>{title}</h3>
      <pre>{code}</pre>
    </div>\n'''
    return html

def build_html(loc_key, cfg):
    lc = cfg['locale_code']
    locale_rows_js = translate_rows(ROWS_JS, loc_key)
    tabs_html = ''.join(
        f'  <div class="tab{{" active" if i==0 else ""}}" onclick="showTab(\'{tid}\')">{name}</div>\n'
        for i, (tid, name) in enumerate(zip(['ref','qs','power','api'], cfg['tabs']))
    )
    id_badges = ''.join(f'<li><code>{t}</code></li>' for t in cfg['id_types'])

    return f'''<!DOCTYPE html>
<html lang="{cfg['lang']}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{cfg['title']}</title>
<style>
{BASE_CSS}
</style>
</head>
<body>

<div class="header">
  <h1>{cfg['header_title']}</h1>
  <div class="sub">{cfg['header_sub']}</div>
</div>

<div class="tabs">
{tabs_html}</div>

<!-- REFERENCE -->
<div class="section active" id="tab-ref">
  <div class="stitle">{cfg['section_ref']}</div>

  <div class="toolbar">
    <input id="searchBox" type="text" placeholder="{cfg['search_placeholder']}" oninput="filterTable()">
    <select id="catFilter" onchange="filterTable()">
      <option value="">{cfg['cat_label']}</option>
    </select>
    <select id="locFilter" onchange="filterTable()">
      <option value="">{cfg['locale_label']}</option>
      <option value="TR">TR</option>
      <option value="US">US</option>
      <option value="UK">UK</option>
      <option value="DE">DE</option>
      <option value="FR">FR</option>
      <option value="RU">RU</option>
    </select>
    <button class="reset-btn" onclick="resetFilters()">{cfg['reset_btn']}</button>
    <span class="row-count" id="rowCount">— {cfg['section_ref'].split("(")[0].strip()}</span>
  </div>

  <div class="locale-grid" style="margin-bottom:18px">
    <div class="locale-card">
      <h3>{cfg['flag']} {cfg['id_label']}</h3>
      <ul>{id_badges}</ul>
    </div>
  </div>

  <div class="table-wrap">
    <table id="refTable">
      <thead>
        <tr>
          <th class="col-fn">{cfg['col_fn']}</th>
          <th class="col-cat">{cfg['col_cat']}</th>
          <th class="col-locale">{cfg['col_loc']}</th>
          <th class="col-extra">{cfg['col_extra']}</th>
          <th class="col-output">{cfg['col_out']}</th>
          <th class="col-cli">{cfg['col_cli']}</th>
        </tr>
      </thead>
      <tbody id="refBody"></tbody>
    </table>
  </div>
</div>

<!-- QUICK START -->
<div class="section" id="tab-qs">
  <div class="stitle">{cfg['section_qs']}</div>
  <div class="qs-grid">
{build_qs_cards(cfg['qs_cards'])}  </div>
</div>

<!-- ADVANCED -->
<div class="section" id="tab-power">
  <div class="stitle">{cfg['section_power']}</div>
  <div class="qs-grid">

    <div class="qs-card">
      <h3>profile()</h3>
      <pre><span class="cm"># Python</span>
jutsu.profile(locale=<span class="st">'{lc}'</span>)

<span class="cm"># CLI</span>
<span class="kw">mockjutsu profile</span> <span class="st">--locale {lc}</span>
<span class="kw">mockjutsu profile</span> <span class="st">--locale {lc} --count 5</span></pre>
    </div>

    <div class="qs-card">
      <h3>company()</h3>
      <pre><span class="cm"># Python</span>
jutsu.company(locale=<span class="st">'{lc}'</span>)

<span class="cm"># CLI</span>
<span class="kw">mockjutsu company</span> <span class="st">--locale {lc}</span>
<span class="kw">mockjutsu company</span> <span class="st">--locale {lc} --count 3</span></pre>
    </div>

    <div class="qs-card">
      <h3>bulk()</h3>
      <pre><span class="cm"># Python</span>
jutsu.bulk(<span class="st">'phone'</span>, count=<span class="fn">100</span>, locale=<span class="st">'{lc}'</span>)
jutsu.bulk(<span class="st">'iban'</span>,  count=<span class="fn">500</span>, locale=<span class="st">'{lc}'</span>)

<span class="cm"># CLI</span>
<span class="kw">mockjutsu bulk</span> phone <span class="st">--count 100 --locale {lc}</span>
<span class="kw">mockjutsu bulk</span> iban  <span class="st">--count 500 --locale {lc}</span></pre>
    </div>

    <div class="qs-card">
      <h3>template()</h3>
      <pre><span class="cm"># Python — list</span>
jutsu.template(
  [<span class="st">'uuid'</span>, <span class="st">'phone'</span>, <span class="st">'iban'</span>],
  count=<span class="fn">10</span>, locale=<span class="st">'{lc}'</span>)

<span class="cm"># CLI</span>
<span class="kw">mockjutsu template</span> uuid phone iban <span class="st">--locale {lc} --count 10</span>
<span class="kw">mockjutsu template</span> uuid phone iban <span class="st">--format csv</span>
<span class="kw">mockjutsu template</span> uuid phone iban <span class="st">--format sql --table users</span></pre>
    </div>

    <div class="qs-card">
      <h3>export()</h3>
      <pre><span class="cm"># Python</span>
jutsu.export(
  {{'id':'uuid','phone':'phone','iban':'iban'}},
  count=<span class="fn">1000</span>, format=<span class="st">'sql'</span>,
  table=<span class="st">'users'</span>, locale=<span class="st">'{lc}'</span>)

<span class="cm"># CLI</span>
<span class="kw">mockjutsu export</span> uuid phone iban <span class="st">--count 1000 --format sql --table users --locale {lc}</span></pre>
    </div>

    <div class="qs-card">
      <h3>REST API</h3>
      <pre><span class="cm"># Start server</span>
<span class="kw">mockjutsu start-api</span> <span class="st">--port 8000</span>

GET /generate/phone?locale=<span class="st">{lc}</span>
GET /bulk/iban?count=<span class="fn">10</span>&amp;locale=<span class="st">{lc}</span>
GET /profile?locale=<span class="st">{lc}</span>&amp;count=<span class="fn">1</span>
POST /template
  {{"types":["uuid","phone","iban"],"locale":"{lc}","count":1}}

<span class="cm"># Swagger UI</span>
<span class="cm"># http://localhost:8000/docs</span></pre>
    </div>

  </div>
</div>

<!-- REST API -->
<div class="section" id="tab-api">
  <div class="stitle">{cfg['section_api']}</div>
  <div class="qs-grid">

    <div class="qs-card">
      <h3>GET /generate/{{type}}</h3>
      <pre>GET /generate/phone?locale=<span class="st">{lc}</span>
GET /generate/iban?locale=<span class="st">{lc}</span>
GET /generate/cardnum?network=<span class="st">visa</span>
GET /generate/hash?algorithm=<span class="st">sha256</span>

<span class="cm"># Response</span>
{{"type":"phone","locale":"{lc}",
  "result":"...","status":"success"}}</pre>
    </div>

    <div class="qs-card">
      <h3>GET /bulk/{{type}}</h3>
      <pre>GET /bulk/phone?count=<span class="fn">10</span>&amp;locale=<span class="st">{lc}</span>
GET /bulk/iban?count=<span class="fn">5</span>&amp;locale=<span class="st">{lc}</span>

<span class="cm"># Response</span>
{{"type":"phone","count":10,
  "results":["...","..."]}}</pre>
    </div>

    <div class="qs-card">
      <h3>POST /template</h3>
      <pre>{{"types":["uuid","phone","iban"],
 "count":1,"locale":"{lc}"}}

<span class="cm"># count=1 → single {{}}</span>
<span class="cm"># count>1 → [{{}},...] array</span></pre>
    </div>

    <div class="qs-card">
      <h3>GET /profile &amp; /company</h3>
      <pre>GET /profile?locale=<span class="st">{lc}</span>&amp;count=<span class="fn">1</span>
GET /company?locale=<span class="st">{lc}</span>&amp;count=<span class="fn">1</span></pre>
    </div>

    <div class="qs-card">
      <h3>POST /export</h3>
      <pre>{{"schema_map":{{"id":"uuid","p":"phone"}},
 "count":10,"locale":"{lc}",
 "format":"csv","table":"users"}}</pre>
    </div>

    <div class="qs-card">
      <h3>GET /list</h3>
      <pre>GET /list
GET /list?cat=<span class="st">Financial</span>
GET /health  <span class="cm">→ {{"status":"ok"}}</span>

<span class="cm"># Swagger UI</span>
<span class="cm"># http://localhost:8000/docs</span></pre>
    </div>

  </div>
</div>

<div class="footer">
  mock-jutsu &mdash; Developed by <strong>Altan Sezer Ayan - A.S.A</strong>
  &nbsp;&bull;&nbsp; <a href="https://github.com/altansayan/mock-jutsu-api" style="color:#6366f1">GitHub</a>
</div>

<script>
{locale_rows_js}

const CAT_CLS = {{
  kimlik:"cat-kimlik", vergi:"cat-vergi", isveren:"cat-isveren",
  sigorta:"cat-sigorta", isim:"cat-isim", belge:"cat-belge",
  demografik:"cat-demografik", finansal:"cat-finansal",
  iletisim:"cat-iletisim", meta:"cat-meta",
  bankacilik:"cat-bankacilik", kurumsal:"cat-kurumsal",
  saglik:"cat-saglik", ticaret:"cat-ticaret",
  rfid:"cat-rfid", nfc:"cat-nfc", ir:"cat-ir",
  barkod:"cat-barkod", telecom:"cat-telecom",
  securities:"cat-securities", crypto:"cat-crypto",
  ecommerce:"cat-ecommerce", location:"cat-location",
  social:"cat-social", guvenlik:"cat-guvenlik",
}};

function buildTable() {{
  const cats = new Set(); const sel = document.getElementById('catFilter');
  const tbody = document.getElementById('refBody');
  tbody.innerHTML = '';
  ROWS.forEach(([fn,cat,catCls,loc,extra,out,cli,locales]) => {{
    cats.add(cat);
    const lc_badges = locales ? locales.split(' ').map(l=>`<span class="lc lc-${{l}}">${{l}}</span>`).join('') : '<span class="col-locale"><span class="badge-no">—</span></span>';
    const tr = document.createElement('tr');
    tr.dataset.fn = fn; tr.dataset.cat = cat; tr.dataset.locales = locales||'';
    tr.innerHTML = `
      <td class="col-fn"><code>${{fn}}</code></td>
      <td class="col-cat"><span class="pill ${{CAT_CLS[catCls]||''}}">${{cat}}</span></td>
      <td class="col-locale">${{lc_badges}}</td>
      <td class="col-extra">${{extra!=='—'?`<code>${{extra}}</code>`:'—'}}</td>
      <td class="col-output"><code>${{out}}</code></td>
      <td class="col-cli"><code>${{cli}}</code></td>`;
    tbody.appendChild(tr);
  }});
  [...cats].sort().forEach(c => {{
    const o = document.createElement('option'); o.value=c; o.textContent=c; sel.appendChild(o);
  }});
  updateCount(ROWS.length);
}}

function filterTable() {{
  const q   = document.getElementById('searchBox').value.toLowerCase();
  const cat = document.getElementById('catFilter').value;
  const loc = document.getElementById('locFilter').value;
  let vis = 0;
  document.querySelectorAll('#refBody tr').forEach(tr => {{
    const match =
      (!q   || tr.dataset.fn.includes(q) || tr.innerHTML.toLowerCase().includes(q)) &&
      (!cat || tr.dataset.cat === cat) &&
      (!loc || tr.dataset.locales.includes(loc));
    tr.style.display = match ? '' : 'none';
    if (match) vis++;
  }});
  updateCount(vis);
}}

function resetFilters() {{
  document.getElementById('searchBox').value='';
  document.getElementById('catFilter').value='';
  document.getElementById('locFilter').value='';
  filterTable();
}}

function updateCount(n) {{
  document.getElementById('rowCount').textContent = `${{n}} / ${{ROWS.length}} parameters`;
}}

function showTab(id) {{
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.getElementById('tab-' + id).classList.add('active');
  event.target.classList.add('active');
}}

buildTable();
</script>
</body>
</html>'''

# ── Generate files ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    for loc_key, cfg in LOCALES.items():
        filename = f'HOW-TO-MockJutsu-{loc_key}.html'
        html = build_html(loc_key, cfg)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'Generated: {filename}')
    print('Done.')
