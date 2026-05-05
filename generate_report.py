"""
mock-jutsu — Custom HTML Test Report Generator
Developer: Altan Sezer Ayan (https://github.com/altansayan)
"""

import json
import os
from datetime import datetime, timezone

REPORT_JSON = "reports/test_results.json"
REPORT_HTML = "reports/test_report.html"

CATEGORY_MAP = {
    "Identity":      ['tckn', 'ykn', 'taxid', 'nationalid', 'firstname', 'lastname',
                      'fullname', 'passport', 'license', 'age', 'gender', 'birthdate'],
    "Financial":     ['cardnum', 'cardnetwork', 'cardtype', 'cardstatus', 'cardowner',
                      'cvv3', 'cvv4', 'pin', 'expiry', 'expirymonth', 'expiryyear',
                      'issuer', 'balance', 'iban', 'cardcategory'],
    "Communication": ['phone', 'phone_country', 'phone_area', 'phone_local',
                      'address_city', 'address_street', 'address_full',
                      'postalcode', 'plate', 'email'],
    "Meta":          ['uuid', 'requestid', 'correlationid', 'sessionid', 'idempotencykey',
                      'deviceid', 'timestamp', 'timestamp_iso', 'bearertoken',
                      'clientversion', 'ipv4', 'ipv6', 'browser_name', 'browser_version',
                      'browser_engine', 'useragent', 'signature', 'apppassword'],
}

CATEGORY_COLORS = {
    "Identity":      ("#6366f1", "#eef2ff"),
    "Financial":     ("#0ea5e9", "#f0f9ff"),
    "Communication": ("#10b981", "#ecfdf5"),
    "Meta":          ("#f59e0b", "#fffbeb"),
    "Algorithm":     ("#e11d48", "#fff1f2"),
}

LOCALES = ["TR", "UK", "US", "DE", "FR", "RU"]
LOCALE_FLAGS = {"TR": "TR", "UK": "UK", "US": "US", "DE": "DE", "FR": "FR", "RU": "RU"}


# ── helpers ──────────────────────────────────────────────────────────────────

def load_json():
    with open(REPORT_JSON, encoding="utf-8") as f:
        return json.load(f)


def category_of(dt):
    for cat, types in CATEGORY_MAP.items():
        if dt in types:
            return cat
    return "Other"


def parse_tests(tests):
    """Return two lists: matrix_tests, specific_tests — each as dicts."""
    matrix, specific = [], []
    for t in tests:
        name = t["nodeid"].split("::")[-1]
        duration_ms = round((t.get("call", {}) or {}).get("duration", 0) * 1000, 2)
        outcome = t["outcome"]
        error_msg = ""
        call = t.get("call") or {}
        if outcome == "failed":
            error_msg = str(call.get("longrepr", ""))[:500]

        if name.startswith("test_comprehensive_matrix["):
            inner = name[len("test_comprehensive_matrix["):-1]
            parts = inner.split("-")
            locale = parts[-1]
            data_type = "-".join(parts[:-1])
            cat = category_of(data_type)
            matrix.append({
                "full_name": f"test_comprehensive_matrix[{data_type}-{locale}]",
                "data_type": data_type,
                "locale": locale,
                "category": cat,
                "outcome": outcome,
                "duration_ms": duration_ms,
                "error": error_msg,
            })
        else:
            specific.append({
                "full_name": name,
                "category": "Algorithm",
                "outcome": outcome,
                "duration_ms": duration_ms,
                "error": error_msg,
            })
    return matrix, specific


def parse_matrix_grid(matrix_tests):
    """Build {data_type: {locale: outcome}} for the visual grid."""
    grid = {}
    for t in matrix_tests:
        grid.setdefault(t["data_type"], {})[t["locale"]] = t["outcome"]
    return grid


# ── HTML builders ─────────────────────────────────────────────────────────────

def badge(outcome):
    cls = {"passed": "pass", "failed": "fail"}.get(outcome, "skip")
    lbl = {"passed": "PASS", "failed": "FAIL"}.get(outcome, outcome.upper())
    return f'<span class="badge {cls}">{lbl}</span>'


def cell(outcome):
    if outcome == "passed":
        return '<td class="cell-pass">✓</td>'
    if outcome == "failed":
        return '<td class="cell-fail">✗</td>'
    return '<td class="cell-na">—</td>'


def build_html(data):
    tests_raw = data.get("tests", [])
    summary   = data.get("summary", {})
    duration  = data.get("duration", 0)
    created   = data.get("created", 0)
    env       = data.get("environment", {})

    total    = summary.get("total",   len(tests_raw))
    passed   = summary.get("passed",  0)
    failed   = summary.get("failed",  0)
    pass_rate = round(passed / total * 100, 1) if total else 0

    created_str = datetime.fromtimestamp(created, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC") if created else datetime.now().strftime("%Y-%m-%d %H:%M")

    matrix_tests, specific_tests = parse_tests(tests_raw)
    grid = parse_matrix_grid(matrix_tests)

    # ── category stats ──────────────────────────────────────────────────────
    cat_stats = {}
    for cat, types in CATEGORY_MAP.items():
        t_total = len(types) * len(LOCALES)
        t_pass  = sum(1 for dt in types for loc in LOCALES if grid.get(dt, {}).get(loc) == "passed")
        cat_stats[cat] = {"total": t_total, "passed": t_pass}
    spec_pass = sum(1 for t in specific_tests if t["outcome"] == "passed")
    cat_stats["Algorithm"] = {"total": len(specific_tests), "passed": spec_pass}

    # ── category cards ───────────────────────────────────────────────────────
    cat_cards_html = ""
    for cat, st in cat_stats.items():
        color, bg = CATEGORY_COLORS.get(cat, ("#6366f1", "#eef2ff"))
        rate = round(st["passed"] / st["total"] * 100, 1) if st["total"] else 0
        cat_cards_html += f"""
        <div class="cat-card" style="border-top:4px solid {color};background:{bg}">
          <div class="cat-label" style="color:{color}">{cat}</div>
          <div class="cat-nums"><span style="color:{color}">{st['passed']}</span> / {st['total']}</div>
          <div class="cat-rate">{rate}% pass rate</div>
          <div class="bar-wrap"><div class="bar-fill" style="width:{rate}%;background:{color}"></div></div>
        </div>"""

    # ── visual matrix sections ───────────────────────────────────────────────
    matrix_sections_html = ""
    for cat, types in CATEGORY_MAP.items():
        color, bg = CATEGORY_COLORS[cat]
        rows = ""
        for dt in types:
            row_fail = any(grid.get(dt, {}).get(loc) == "failed" for loc in LOCALES)
            row_cls  = "rrow-fail" if row_fail else ""
            cells    = "".join(cell(grid.get(dt, {}).get(loc)) for loc in LOCALES)
            rows += f'<tr class="{row_cls}"><td class="dt-col"><code>{dt}</code></td>{cells}</tr>\n'
        matrix_sections_html += f"""
        <div class="matrix-block">
          <div class="matrix-hdr" style="color:{color};background:{bg};border-left:4px solid {color}">
            {cat} &mdash; {len(types)} parameters x {len(LOCALES)} locales = {len(types)*len(LOCALES)} tests
          </div>
          <table class="mtable">
            <thead><tr>
              <th style="text-align:left">Parameter</th>
              {"".join(f'<th>{LOCALE_FLAGS[l]}<br><small>{l}</small></th>' for l in LOCALES)}
            </tr></thead>
            <tbody>{rows}</tbody>
          </table>
        </div>"""

    # ── full test list (all 369) ─────────────────────────────────────────────
    all_rows_html = ""
    row_idx = 0

    # matrix tests grouped — show every row
    for t in matrix_tests:
        color, _ = CATEGORY_COLORS.get(t["category"], ("#6366f1", "#eef2ff"))
        err_html = ""
        if t["error"]:
            safe = t["error"].replace("<","&lt;").replace(">","&gt;")
            err_html = f'<details><summary>Error</summary><pre>{safe}</pre></details>'
        all_rows_html += f"""
        <tr class="trow {'fail-row' if t['outcome']=='failed' else ''}"
            data-cat="{t['category']}" data-outcome="{t['outcome']}"
            data-locale="{t['locale']}" data-type="{t['data_type']}">
          <td class="idx">{row_idx + 1}</td>
          <td><span class="cat-pill" style="background:{color}20;color:{color}">{t['category']}</span></td>
          <td><code class="test-name">{t['full_name']}</code></td>
          <td><span class="locale-pill">{t['locale']}</span></td>
          <td><code>{t['data_type']}</code></td>
          <td>{badge(t['outcome'])}</td>
          <td class="dur">{t['duration_ms']} ms</td>
          <td>{err_html}</td>
        </tr>"""
        row_idx += 1

    # specific / algorithmic tests
    for t in specific_tests:
        color, _ = CATEGORY_COLORS["Algorithm"]
        err_html = ""
        if t["error"]:
            safe = t["error"].replace("<","&lt;").replace(">","&gt;")
            err_html = f'<details><summary>Error</summary><pre>{safe}</pre></details>'
        all_rows_html += f"""
        <tr class="trow {'fail-row' if t['outcome']=='failed' else ''}"
            data-cat="Algorithm" data-outcome="{t['outcome']}"
            data-locale="" data-type="">
          <td class="idx">{row_idx + 1}</td>
          <td><span class="cat-pill" style="background:{color}20;color:{color}">Algorithm</span></td>
          <td><code class="test-name">{t['full_name']}</code></td>
          <td><span class="locale-pill" style="background:#f1f5f9;color:#64748b">—</span></td>
          <td><code style="color:#94a3b8">—</code></td>
          <td>{badge(t['outcome'])}</td>
          <td class="dur">{t['duration_ms']} ms</td>
          <td>{err_html}</td>
        </tr>"""
        row_idx += 1

    # ── assemble ─────────────────────────────────────────────────────────────
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>mock-jutsu Test Report</title>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f8fafc;color:#1e293b;font-size:14px}}
a{{color:#6366f1;text-decoration:none}}
code{{font-family:'JetBrains Mono','Cascadia Code','Fira Code',monospace}}

/* Header */
.header{{background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 100%);color:#fff;padding:28px 40px}}
.header h1{{font-size:24px;font-weight:700;letter-spacing:-.5px}}
.header .meta{{font-size:12px;color:#94a3b8;margin-top:6px;line-height:1.8}}

/* Nav */
.nav{{background:#fff;border-bottom:1px solid #e2e8f0;padding:0 40px;display:flex;gap:0;position:sticky;top:0;z-index:100}}
.nav a{{display:inline-block;padding:12px 18px;font-size:13px;font-weight:500;color:#64748b;border-bottom:2px solid transparent;text-decoration:none}}
.nav a:hover{{color:#6366f1;border-bottom-color:#c7d2fe}}

/* Container */
.container{{max-width:1400px;margin:0 auto;padding:28px 40px}}

/* Summary cards */
.summary-row{{display:grid;grid-template-columns:repeat(5,1fr);gap:16px;margin-bottom:28px}}
.scard{{background:#fff;border-radius:10px;padding:20px 24px;box-shadow:0 1px 3px rgba(0,0,0,.07);border-top:4px solid}}
.scard .lbl{{font-size:11px;text-transform:uppercase;letter-spacing:.8px;color:#64748b}}
.scard .val{{font-size:30px;font-weight:700;margin-top:4px}}
.c-total{{border-color:#6366f1}} .c-total .val{{color:#6366f1}}
.c-pass {{border-color:#10b981}} .c-pass  .val{{color:#10b981}}
.c-fail {{border-color:#ef4444}} .c-fail  .val{{color:#ef4444}}
.c-rate {{border-color:#f59e0b}} .c-rate  .val{{color:#f59e0b}}
.c-dur  {{border-color:#0ea5e9}} .c-dur   .val{{color:#0ea5e9;font-size:20px}}

/* Section title */
.stitle{{font-size:17px;font-weight:700;margin:28px 0 14px;display:flex;align-items:center;gap:8px}}
.stitle::before{{content:'';display:inline-block;width:4px;height:20px;background:#6366f1;border-radius:2px}}

/* Category cards */
.cat-grid{{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;margin-bottom:28px}}
.cat-card{{background:#fff;border-radius:10px;padding:16px 18px;box-shadow:0 1px 3px rgba(0,0,0,.07)}}
.cat-label{{font-size:12px;font-weight:700;margin-bottom:4px}}
.cat-nums{{font-size:20px;font-weight:700;color:#1e293b}}
.cat-rate{{font-size:11px;color:#64748b;margin:2px 0 8px}}
.bar-wrap{{height:5px;background:#e2e8f0;border-radius:3px;overflow:hidden}}
.bar-fill{{height:100%;border-radius:3px}}

/* Matrix */
.matrix-block{{margin-bottom:24px}}
.matrix-hdr{{font-size:12px;font-weight:600;padding:7px 12px;border-radius:6px 6px 0 0}}
.mtable{{width:100%;border-collapse:collapse;background:#fff;font-size:12px;
         box-shadow:0 1px 3px rgba(0,0,0,.06)}}
.mtable th{{background:#f1f5f9;color:#475569;font-weight:600;font-size:10px;
            text-transform:uppercase;letter-spacing:.5px;padding:7px 10px;
            text-align:center;border-bottom:1px solid #e2e8f0}}
.mtable th:first-child{{text-align:left}}
.mtable td{{padding:6px 10px;border-bottom:1px solid #f1f5f9;text-align:center}}
.mtable tr:last-child td{{border-bottom:none}}
.dt-col{{text-align:left!important}} .dt-col code{{background:#f8fafc;padding:1px 5px;border-radius:3px;font-size:11px}}
.cell-pass{{color:#10b981;font-weight:700;font-size:15px}}
.cell-fail{{color:#ef4444;font-weight:700;font-size:15px;background:#fef2f2}}
.cell-na{{color:#cbd5e1}}
.rrow-fail{{background:#fef2f2!important}}

/* Test list toolbar */
.toolbar{{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-bottom:12px}}
.toolbar input{{flex:1;min-width:200px;padding:8px 12px;border:1px solid #e2e8f0;border-radius:7px;
                font-size:13px;outline:none}}
.toolbar input:focus{{border-color:#6366f1;box-shadow:0 0 0 3px #eef2ff}}
.toolbar select{{padding:8px 12px;border:1px solid #e2e8f0;border-radius:7px;font-size:13px;
                 background:#fff;outline:none;cursor:pointer}}
.filter-btn{{padding:7px 14px;border:1px solid #e2e8f0;border-radius:7px;font-size:12px;
             background:#fff;cursor:pointer;font-weight:500;color:#475569}}
.filter-btn:hover,.filter-btn.active{{background:#6366f1;color:#fff;border-color:#6366f1}}
.row-count{{font-size:12px;color:#64748b;white-space:nowrap}}

/* Full test table */
.ttable-wrap{{overflow-x:auto;border-radius:10px;box-shadow:0 1px 3px rgba(0,0,0,.07)}}
.ttable{{width:100%;border-collapse:collapse;background:#fff;font-size:12px}}
.ttable thead th{{background:#f1f5f9;color:#475569;font-weight:600;font-size:10px;
                  text-transform:uppercase;letter-spacing:.5px;padding:9px 12px;
                  text-align:left;border-bottom:1px solid #e2e8f0;white-space:nowrap}}
.ttable tbody tr{{border-bottom:1px solid #f8fafc}}
.ttable tbody tr:hover{{background:#f8fafc}}
.ttable tbody tr:last-child{{border-bottom:none}}
.ttable td{{padding:8px 12px;vertical-align:middle}}
.fail-row{{background:#fef2f2!important}}
.idx{{color:#94a3b8;width:40px;text-align:right;font-size:11px}}
.test-name{{font-size:11.5px;color:#1e293b}}
.dur{{color:#64748b;white-space:nowrap;text-align:right}}
.cat-pill{{font-size:10px;font-weight:600;padding:2px 8px;border-radius:10px;white-space:nowrap}}
.locale-pill{{font-size:10px;font-weight:700;padding:2px 7px;border-radius:5px;
              background:#e2e8f0;color:#475569;display:inline-block}}
.ttable pre{{font-size:10px;color:#b91c1c;white-space:pre-wrap;word-break:break-all;
             background:#fff1f2;padding:6px 8px;border-radius:4px;margin-top:4px;max-width:400px}}
.ttable details summary{{cursor:pointer;color:#ef4444;font-size:11px;font-weight:600}}

/* Badges */
.badge{{display:inline-block;font-size:10px;font-weight:700;padding:2px 8px;
        border-radius:10px;letter-spacing:.5px;text-transform:uppercase;white-space:nowrap}}
.badge.pass{{background:#dcfce7;color:#15803d}}
.badge.fail{{background:#fee2e2;color:#b91c1c}}
.badge.skip{{background:#fef9c3;color:#a16207}}

/* Footer */
.footer{{text-align:center;font-size:11px;color:#94a3b8;padding:28px 0;
         border-top:1px solid #e2e8f0;margin-top:40px}}
</style>
</head>
<body>

<div class="header">
  <h1>mock-jutsu &mdash; Test Report</h1>
  <div class="meta">
    Generated: {created_str} &nbsp;&bull;&nbsp;
    Python: {env.get('Python','&mdash;')} &nbsp;&bull;&nbsp;
    pytest: {env.get('pytest','&mdash;')} &nbsp;&bull;&nbsp;
    Duration: {duration:.2f}s
  </div>
</div>

<nav class="nav">
  <a href="#summary">Summary</a>
  <a href="#categories">Categories</a>
  <a href="#matrix">Matrix</a>
  <a href="#allTests">All Tests ({total})</a>
</nav>

<div class="container">

  <!-- ── Summary ── -->
  <div id="summary"></div>
  <div class="stitle">Summary</div>
  <div class="summary-row">
    <div class="scard c-total"><div class="lbl">Total Tests</div><div class="val">{total}</div></div>
    <div class="scard c-pass"> <div class="lbl">Passed</div>    <div class="val">{passed}</div></div>
    <div class="scard c-fail"> <div class="lbl">Failed</div>    <div class="val">{failed}</div></div>
    <div class="scard c-rate"> <div class="lbl">Pass Rate</div> <div class="val">{pass_rate}%</div></div>
    <div class="scard c-dur">  <div class="lbl">Duration</div>  <div class="val">{duration:.2f}s</div></div>
  </div>

  <!-- ── Categories ── -->
  <div id="categories"></div>
  <div class="stitle">Categories</div>
  <div class="cat-grid">{cat_cards_html}</div>

  <!-- ── Matrix ── -->
  <div id="matrix"></div>
  <div class="stitle">Locale x Type Matrix</div>
  {matrix_sections_html}

  <!-- ── All Tests ── -->
  <div id="allTests"></div>
  <div class="stitle">All Test Scenarios ({total})</div>

  <div class="toolbar">
    <input type="text" id="searchInput" placeholder="Search test name, type, locale..." oninput="filterTable()">
    <select id="catFilter" onchange="filterTable()">
      <option value="">All Categories</option>
      <option value="Identity">Identity</option>
      <option value="Financial">Financial</option>
      <option value="Communication">Communication</option>
      <option value="Meta">Meta</option>
      <option value="Algorithm">Algorithm</option>
    </select>
    <select id="localeFilter" onchange="filterTable()">
      <option value="">All Locales</option>
      <option value="TR">TR</option>
      <option value="UK">UK</option>
      <option value="US">US</option>
      <option value="DE">DE</option>
      <option value="FR">FR</option>
      <option value="RU">RU</option>
    </select>
    <select id="outcomeFilter" onchange="filterTable()">
      <option value="">All Results</option>
      <option value="passed">Passed</option>
      <option value="failed">Failed</option>
    </select>
    <button class="filter-btn" onclick="resetFilters()">Reset</button>
    <span class="row-count" id="rowCount">Showing {total} tests</span>
  </div>

  <div class="ttable-wrap">
    <table class="ttable" id="testTable">
      <thead>
        <tr>
          <th>#</th>
          <th>Category</th>
          <th>Test Name</th>
          <th>Locale</th>
          <th>Type</th>
          <th>Result</th>
          <th>Duration</th>
          <th>Details</th>
        </tr>
      </thead>
      <tbody id="testBody">
        {all_rows_html}
      </tbody>
    </table>
  </div>

</div>

<div class="footer">
  mock-jutsu-api &nbsp;&bull;&nbsp; Developed by Altan Sezer Ayan &nbsp;&bull;&nbsp;
  <a href="https://github.com/altansayan">github.com/altansayan</a>
</div>

<script>
function filterTable() {{
  const search  = document.getElementById('searchInput').value.toLowerCase();
  const cat     = document.getElementById('catFilter').value;
  const locale  = document.getElementById('localeFilter').value;
  const outcome = document.getElementById('outcomeFilter').value;
  const rows    = document.querySelectorAll('#testBody tr.trow');
  let visible = 0;
  rows.forEach(row => {{
    const name    = row.querySelector('.test-name')?.textContent.toLowerCase() || '';
    const rowCat  = row.dataset.cat || '';
    const rowLoc  = row.dataset.locale || '';
    const rowType = row.dataset.type || '';
    const rowOut  = row.dataset.outcome || '';
    const matchSearch  = !search  || name.includes(search) || rowType.includes(search) || rowLoc.toLowerCase().includes(search);
    const matchCat     = !cat     || rowCat === cat;
    const matchLocale  = !locale  || rowLoc === locale;
    const matchOutcome = !outcome || rowOut === outcome;
    const show = matchSearch && matchCat && matchLocale && matchOutcome;
    row.style.display = show ? '' : 'none';
    if (show) visible++;
  }});
  document.getElementById('rowCount').textContent = `Showing ${{visible}} / {total} tests`;
}}

function resetFilters() {{
  document.getElementById('searchInput').value = '';
  document.getElementById('catFilter').value = '';
  document.getElementById('localeFilter').value = '';
  document.getElementById('outcomeFilter').value = '';
  filterTable();
}}
</script>
</body>
</html>"""

    return html


def main():
    os.makedirs("reports", exist_ok=True)
    data = load_json()
    html = build_html(data)
    with open(REPORT_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    size_kb = os.path.getsize(REPORT_HTML) // 1024
    print(f"Report generated: {os.path.abspath(REPORT_HTML)} ({size_kb} KB)")


if __name__ == "__main__":
    main()
