"""
mock-jutsu -- CLI
Developer: Altan Sezer Ayan - A.S.A (https://github.com/altansayan)
"""

import io
import sys

import click
from mockjutsu.core import jutsu

# Force UTF-8 on Windows terminals that default to cp1254/cp1252
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def _print_banner() -> None:
    import os
    from pyfiglet import Figlet
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text

    # Read width from the real stdout fd — survives stdout wrapper and terminal resize
    try:
        term_w = os.get_terminal_size(sys.__stdout__.fileno()).columns
    except Exception:
        import shutil
        term_w = shutil.get_terminal_size((80, 24)).columns
    term_w = max(40, min(term_w, 220))

    console = Console(highlight=False, width=term_w)

    # Breakpoints: full / compact / text-only
    if term_w >= 88:
        font, padding = "standard", (1, 4)
    elif term_w >= 65:
        font, padding = "small", (1, 2)
    else:
        font, padding = None, (0, 1)

    body = Text(justify="center")

    if font:
        raw_art = Figlet(font=font).renderText("mock-jutsu").rstrip("\n")
        art_lines = [line.rstrip() for line in raw_art.splitlines()]
        min_i = min((len(l) - len(l.lstrip()) for l in art_lines if l.strip()), default=0)
        art_lines = [l[min_i:] for l in art_lines]
        mid = len(art_lines) // 2
        for i, line in enumerate(art_lines):
            if i == mid:
                body.append("⚔  ", style="bold yellow")
                body.append(line, style="bold bright_green")
                body.append("  ✦\n", style="bold yellow")
            else:
                body.append(line + "\n", style="bold bright_green")
    else:
        body.append("⚔  mock-jutsu  ✦\n", style="bold bright_green")

    body.append("\n")
    body.append("Algorithmic Mock Data Engine\n", style="bold white")
    body.append("95+ Types", style="cyan")
    body.append("  |  ", style="dim white")
    body.append("6 Locales", style="cyan")
    body.append("  |  ", style="dim white")
    body.append("689 Tests\n", style="cyan")
    body.append("\n")
    body.append("Developed by: Altan Sezer Ayan - A.S.A\n", style="dim white")
    body.append("https://github.com/altansayan\n", style="dim blue")
    body.append("MockJutsu - Api: ", style="dim white")
    body.append("https://github.com/altansayan/mock-jutsu-api\n", style="dim blue")
    body.append("MockJutsu JMeter: ", style="dim white")
    body.append("https://github.com/altansayan/mock-jutsu-jmeter\n", style="dim blue")
    body.append("MockJutsu Postman Collection:\n", style="dim white")
    body.append("https://github.com/altansayan/mock-jutsu-postman-collection\n", style="dim blue")
    body.append("\n")
    body.append("Licensed under the MIT License\n", style="dim white")
    body.append("Copyright (c) 2025 Altan Sezer Ayan - A.S.A", style="dim white")

    console.print(Panel(body, border_style="bright_green", padding=padding))

# ---------------------------------------------------------------------------
# Reference table
# (type, category, locale_aware, example_output, cli_cmd)
# cli_cmd: command string shown in the CLI COMMAND column (no "mockjutsu" prefix)
# ---------------------------------------------------------------------------
_REFERENCE = [
    # Identity
    ("tckn",          "Identity",    False, "45678901234",            "generate tckn"),
    ("ykn",           "Identity",    False, "99012345678",            "generate ykn"),
    ("nationalid",    "Identity",    True,  "(by locale)",            "generate nationalid --locale TR"),
    ("vkn",           "Identity",    False, "1234567890",             "generate vkn"),
    ("taxid",         "Identity",    True,  "(by locale)",            "generate taxid --locale TR"),
    ("employer_id",   "Identity",    True,  "(by locale)",            "generate employer_id --locale TR"),
    ("insurance_id",  "Identity",    True,  "(by locale)",            "generate insurance_id --locale TR"),
    ("sgk",           "Identity",    False, "34-0012345-1.01-02",     "generate sgk"),
    ("mersis",        "Identity",    False, "1234567890012345",        "generate mersis"),
    ("ssn",           "Identity",    False, "234-56-7890",            "generate ssn"),
    ("ein",           "Identity",    False, "12-3456789",             "generate ein"),
    ("nin",           "Identity",    False, "AB 12 34 56 C",          "generate nin"),
    ("utr",           "Identity",    False, "1234567890",             "generate utr"),
    ("crn",           "Identity",    False, "12345678",               "generate crn"),
    ("paye",          "Identity",    False, "123/AB4567",             "generate paye"),
    ("ust_id",        "Identity",    False, "DE123456789",            "generate ust_id"),
    ("hrb",           "Identity",    False, "HRB 123456",             "generate hrb"),
    ("rvn",           "Identity",    False, "65 070892 W 1235",       "generate rvn"),
    ("siren",         "Identity",    False, "732829320",              "generate siren"),
    ("siret",         "Identity",    False, "73282932000074",         "generate siret"),
    ("tva",           "Identity",    False, "FR73732829320",          "generate tva"),
    ("inn",           "Identity",    False, "7707083893",             "generate inn"),
    ("snils",         "Identity",    False, "112-233-445 95",         "generate snils"),
    ("ogrn",          "Identity",    False, "1027700132195",          "generate ogrn"),
    ("kpp",           "Identity",    False, "770701001",              "generate kpp"),
    # Name
    ("firstname",     "Name",        True,  "Emre",                   "generate firstname --locale TR"),
    ("lastname",      "Name",        True,  "Yilmaz",                 "generate lastname --locale TR"),
    ("fullname",      "Name",        True,  "Emre Kaya",              "generate fullname --locale TR"),
    ("patronymic",    "Name",        True,  "Ivanovich",              "generate patronymic --locale RU"),
    # Document
    ("passport",      "Document",    False, "P1234567",               "generate passport"),
    ("license",       "Document",    False, "654321",                 "generate license"),
    # Demographic
    ("age",           "Demographic", False, "34",                     "generate age"),
    ("gender",        "Demographic", False, "Male",                   "generate gender"),
    ("birthdate",     "Demographic", False, "1990-05-14",             "generate birthdate"),
    # Financial
    ("cardnum",       "Financial",   False, "4532015112830366",       "generate cardnum --network visa"),
    ("cardnetwork",   "Financial",   False, "VISA",                   "generate cardnetwork"),
    ("cardtype",      "Financial",   False, "Credit",                 "generate cardtype"),
    ("cardstatus",    "Financial",   False, "Active",                 "generate cardstatus"),
    ("cardcategory",  "Financial",   False, "Gold",                   "generate cardcategory"),
    ("cardowner",     "Financial",   True,  "JOHN SMITH",             "generate cardowner --locale TR"),
    ("cvv3",          "Financial",   False, "847",                    "generate cvv3"),
    ("cvv4",          "Financial",   False, "1234",                   "generate cvv4"),
    ("pin",           "Financial",   False, "7291",                   "generate pin"),
    ("expiry",        "Financial",   False, "09/27",                  "generate expiry"),
    ("expirymonth",   "Financial",   False, "09",                     "generate expirymonth"),
    ("expiryyear",    "Financial",   False, "27",                     "generate expiryyear"),
    ("issuer",        "Financial",   True,  "BosphorusBank A.S.",     "generate issuer --locale TR"),
    ("balance",       "Financial",   False, "12450.75",               "generate balance"),
    ("iban",          "Financial",   True,  "TR330006100519...",      "generate iban --locale TR"),
    # Contact
    ("phone",         "Contact",     True,  "+905325551234",          "generate phone --locale TR"),
    ("phone_country", "Contact",     True,  "+90",                    "generate phone_country --locale TR"),
    ("phone_area",    "Contact",     True,  "532",                    "generate phone_area --locale TR"),
    ("phone_local",   "Contact",     True,  "5551234",                "generate phone_local --locale TR"),
    ("address_city",  "Contact",     True,  "Istanbul",               "generate address_city --locale TR"),
    ("address_street","Contact",     True,  "Bagdat Caddesi",         "generate address_street --locale TR"),
    ("address_full",  "Contact",     True,  "Istanbul, Bagdat Cad.",  "generate address_full --locale TR"),
    ("postalcode",    "Contact",     True,  "34500",                  "generate postalcode --locale TR"),
    ("plate",         "Contact",     True,  "34 ABC 123",             "generate plate --locale TR"),
    ("email",         "Contact",     True,  "user42@gmail.com",       "generate email --locale TR"),
    # Banking
    ("swift",         "Banking",     True,  "DEUTDEDB",               "generate swift --locale TR"),
    ("sort_code",     "Banking",     False, "20-00-00",               "generate sort_code"),
    ("routing_number","Banking",     False, "021000021",              "generate routing_number"),
    ("bik_code",      "Banking",     False, "044525225",              "generate bik_code"),
    ("bank_name",     "Banking",     True,  "Berliner Finanzbank",    "generate bank_name --locale TR"),
    ("transaction",   "Banking",     True,  "{ref, iban*2, amount}",  "generate transaction --locale TR"),
    # Corporate
    ("company_name",  "Corporate",   True,  "Fischer Tech. GmbH",    "generate company_name --locale TR"),
    ("job_title",     "Corporate",   True,  "Software Engineer",      "generate job_title --locale TR"),
    # Health
    ("blood_type",    "Health",      False, "A+",                     "generate blood_type"),
    ("nhs_number",    "Health",      False, "943 476 5919",           "generate nhs_number"),
    ("icd10",         "Health",      False, "J18.9",                  "generate icd10"),
    ("height",        "Health",      True,  "178 cm / 5'10\"",        "generate height --locale TR"),
    ("weight",        "Health",      True,  "74 kg / 163 lbs",        "generate weight --locale TR"),
    # Commerce
    ("currency",      "Commerce",    True,  "{code:TRY, symbol:TL}",  "generate currency --locale TR"),
    ("tax_rate",      "Commerce",    True,  "{name:KDV, rate:20}",    "generate tax_rate --locale TR"),
    ("invoice_number","Commerce",    True,  "INV-2024-001234",        "generate invoice_number --locale TR"),
    ("vin",           "Commerce",    True,  "WBA3A5C5XMD123456",      "generate vin --locale TR"),
    ("vehicle",       "Commerce",    True,  "{make,model,year,vin}",  "generate vehicle --locale TR"),
    # Meta
    ("uuid",          "Meta",        False, "550e8400-e29b-41d4-...", "generate uuid"),
    ("requestid",     "Meta",        False, "550e8400-e29b-41d4-...", "generate requestid"),
    ("correlationid", "Meta",        False, "550e8400-e29b-41d4-...", "generate correlationid"),
    ("sessionid",     "Meta",        False, "550e8400-e29b-41d4-...", "generate sessionid"),
    ("idempotencykey","Meta",        False, "550e8400-e29b-41d4-...", "generate idempotencykey"),
    ("deviceid",      "Meta",        False, "550E8400-E29B-41D4-...", "generate deviceid"),
    ("timestamp",     "Meta",        False, "1714900000",             "generate timestamp"),
    ("timestamp_iso", "Meta",        False, "2024-05-05T14:30:00",    "generate timestamp_iso"),
    ("ipv4",          "Meta",        False, "192.168.1.42",           "generate ipv4"),
    ("ipv6",          "Meta",        False, "fe80:0000:0000:...",     "generate ipv6"),
    ("browser_name",  "Meta",        False, "Chrome",                 "generate browser_name"),
    ("browser_version","Meta",       False, "124.0.6367.78",          "generate browser_version"),
    ("browser_engine","Meta",        False, "Blink",                  "generate browser_engine"),
    ("useragent",     "Meta",        False, "Mozilla/5.0 ...",        "generate useragent"),
    ("jwt",           "Meta",        False, "eyJ....eyJ....sig",      "generate jwt"),
    ("bearertoken",   "Meta",        False, "Bearer eyJ....sig",      "generate bearertoken"),
    ("hash",          "Meta",        False, "e3b0c44298fc...",        "generate hash"),
    ("mac_address",   "Meta",        False, "A4:C3:F0:3D:8E:21",     "generate mac_address"),
    ("url",           "Meta",        True,  "https://api-42.co.uk/..", "generate url --locale TR"),
    ("domain",        "Meta",        True,  "test-77.com.tr",         "generate domain --locale TR"),
    ("color",         "Meta",        False, "#3A7BF0",                "generate color"),
    ("clientversion", "Meta",        False, "2.4.1",                  "generate clientversion"),
    ("signature",     "Meta",        False, "a1b2c3d4... (hex)",      "generate signature"),
    ("apppassword",   "Meta",        False, "481302",                 "generate apppassword"),
    # RFID
    ("rfid_uid",      "RFID",        False, "04:A3:B2:C1:D0:E5:F6",  "generate rfid_uid"),
    ("epc",           "RFID",        False, "3034257BF400B718...",    "generate epc"),
    ("rfid_tag",      "RFID",        False, "{uid,standard,freq,mem}","generate rfid_tag"),
    # NFC
    ("nfc_uid",       "NFC",         False, "04:A3:B2:C1:D0:E5:F6",  "generate nfc_uid"),
    ("nfc_atqa",      "NFC",         False, "00:44",                  "generate nfc_atqa"),
    ("nfc_sak",       "NFC",         False, "20",                     "generate nfc_sak"),
    ("ndef_uri",      "NFC",         False, "{raw_hex, decoded url}", "generate ndef_uri"),
    ("ndef_text",     "NFC",         True,  "{raw_hex, decoded txt}", "generate ndef_text --locale TR"),
    ("apdu",          "NFC",         False, "{cla,ins,p1,p2,hex}",   "generate apdu"),
    ("nfc_tag",       "NFC",         False, "{uid,atqa,sak,ndef}",   "generate nfc_tag"),
    # IR
    ("ir_nec",        "IR",          False, "{addr,cmd,hex:20DF10EF}","generate ir_nec"),
    ("ir_rc5",        "IR",          False, "{system,cmd,frame_bits}","generate ir_rc5"),
    ("ir_pronto",     "IR",          False, "0000 006D 0022 0000 ..", "generate ir_pronto"),
    ("ir_raw",        "IR",          False, "{carrier_hz,pulses:[]}","generate ir_raw"),
]

# Category display order
_CAT_ORDER = [
    "Identity", "Name", "Document", "Demographic",
    "Financial", "Contact", "Banking", "Corporate",
    "Health", "Commerce", "Meta", "RFID", "NFC", "IR",
]

_CAT_COLORS = {
    "Identity":    "bright_blue",
    "Name":        "green",
    "Document":    "cyan",
    "Demographic": "magenta",
    "Financial":   "bright_blue",
    "Contact":     "green",
    "Banking":     "cyan",
    "Corporate":   "yellow",
    "Health":      "green",
    "Commerce":    "magenta",
    "Meta":        "yellow",
    "RFID":        "cyan",
    "NFC":         "bright_blue",
    "IR":          "red",
}


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """mock-jutsu -- Algorithmic Mock Data Engine (6 Locales, 95+ Types)"""
    if ctx.invoked_subcommand is None:
        _print_banner()
        click.echo(ctx.get_help())


@main.command()
@click.argument('data_type', required=False)
@click.option('--locale',  default='TR',   help='Locale: TR UK US DE FR RU')
@click.option('--network', default='visa', help='Card network: visa mc amex troy mir')
def generate(data_type, locale, network):
    """Generate mock data.  Example: mockjutsu generate tckn --locale TR"""
    if not data_type:
        click.echo("Error: specify a type. Run 'mockjutsu list' to see all types.")
        return
    result = jutsu.generate(data_type, locale=locale, network=network)
    color  = 'red' if "ERROR" in str(result) else 'green'
    click.echo(f"[{locale.upper()}] {data_type}: {click.style(str(result), fg=color, bold=True)}")


@main.command(name='list')
@click.option('--cat', default='', help='Filter by category  e.g. Financial, NFC, RFID, IR')
def list_types(cat):
    """List all 95+ data types with CLI usage examples."""
    # Column widths
    W_TYPE = 20
    W_EX   = 24
    W_CLI  = 48
    W      = 2 + W_TYPE + W_EX + W_CLI + 2   # ~86

    sep = click.style("-" * W, fg='bright_black')

    # Banner
    _print_banner()
    click.echo()
    click.echo(click.style(
        "  Locales:  TR (Turkey)  |  US (United States)  |  UK (United Kingdom)\n"
        "            DE (Germany) |  FR (France)          |  RU (Russia)",
        fg='bright_black'
    ))
    click.echo()

    # Column headers
    h_type = click.style(f"  {'TYPE':<{W_TYPE}}", fg='bright_black', bold=True)
    h_ex   = click.style(f"{'EXAMPLE OUTPUT':<{W_EX}}", fg='bright_black', bold=True)
    h_cli  = click.style(f"{'CLI COMMAND':<{W_CLI}}", fg='bright_black', bold=True)
    h_loc  = click.style("L", fg='bright_black', bold=True)
    click.echo(h_type + h_ex + h_cli + h_loc)
    click.echo(click.style("  " + "-" * (W - 2), fg='bright_black'))

    # Group rows by category
    cat_filter = cat.strip().lower()
    groups: dict[str, list] = {c: [] for c in _CAT_ORDER}
    for row in _REFERENCE:
        groups.setdefault(row[1], []).append(row)

    printed = 0
    for category in _CAT_ORDER:
        rows = groups.get(category, [])
        if not rows:
            continue
        if cat_filter and cat_filter not in category.lower():
            continue

        color = _CAT_COLORS.get(category, "white")
        click.echo()
        click.echo(click.style(
            f"  >> {category.upper()} ({len(rows)} types)",
            fg=color, bold=True
        ))

        for (typ, _cat, locale_aware, example, cli_cmd) in rows:
            loc_flag = click.style("v", fg="green") if locale_aware else click.style("-", fg='bright_black')
            typ_s    = click.style(f"  {typ:<{W_TYPE}}", fg='white', bold=True)
            ex_s     = click.style(f"{example:<{W_EX}}", fg='bright_yellow')
            full_cmd = f"mockjutsu {cli_cmd}"
            cli_s    = click.style(f"{full_cmd:<{W_CLI}}", fg='cyan')
            click.echo(f"{typ_s}{ex_s}{cli_s} {loc_flag}")
            printed += 1

    # Footer
    click.echo()
    click.echo(sep)
    click.echo(click.style(
        f"  {printed} types listed  "
        "|  L=v -> supports --locale flag",
        fg='bright_black'
    ))
    click.echo(click.style(
        "  Filter:  mockjutsu list --cat Financial\n"
        "  Filter:  mockjutsu list --cat NFC",
        fg='bright_black'
    ))
    click.echo(sep)


@main.command()
@click.option('--port', default=8000, help='Port for the API server.')
def serve(port):
    """Start the FastAPI mock server."""
    import uvicorn
    click.echo(click.style(f"\nmock-jutsu API -- port {port}", fg='green', bold=True))
    from api.main import app
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
