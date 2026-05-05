"""
mock-jutsu -- CLI
Developer: Altan Sayan (https://github.com/altansayan)
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

# -- Reference table ----------------------------------------------------------
# (type, category, locale_aware, example_output, extra_param, locales)
_REFERENCE = [
    # Kimlik
    ("tckn",          "Kimlik",      False, "45678901234",           "—",              ""),
    ("ykn",           "Kimlik",      False, "99012345678",           "—",              ""),
    ("nationalid",    "Kimlik",      True,  "(locale'e göre)",       "—",              "TR US UK DE FR RU"),
    ("vkn",           "Kimlik",      False, "1234567890",            "—",              "TR"),
    ("taxid",         "Kimlik",      True,  "(locale'e göre)",       "—",              "TR US UK DE FR RU"),
    ("employer_id",   "Kimlik",      True,  "(locale'e göre)",       "—",              "TR US UK DE FR RU"),
    ("insurance_id",  "Kimlik",      True,  "(locale'e göre)",       "—",              "TR US UK DE FR RU"),
    ("sgk",           "Kimlik",      False, "34-0012345-1.01-02",    "—",              "TR"),
    ("mersis",        "Kimlik",      False, "1234567890012345",       "—",              "TR"),
    ("ssn",           "Kimlik",      False, "234-56-7890",           "—",              "US"),
    ("ein",           "Kimlik",      False, "12-3456789",            "—",              "US"),
    ("nin",           "Kimlik",      False, "AB 12 34 56 C",         "—",              "UK"),
    ("utr",           "Kimlik",      False, "1234567890",            "—",              "UK"),
    ("crn",           "Kimlik",      False, "12345678",              "—",              "UK"),
    ("paye",          "Kimlik",      False, "123/AB4567",            "—",              "UK"),
    ("ust_id",        "Kimlik",      False, "DE123456789",           "—",              "DE"),
    ("hrb",           "Kimlik",      False, "HRB 123456",            "—",              "DE"),
    ("rvn",           "Kimlik",      False, "65 070892 W 1235",      "—",              "DE"),
    ("siren",         "Kimlik",      False, "732829320",             "—",              "FR"),
    ("siret",         "Kimlik",      False, "73282932000074",        "—",              "FR"),
    ("tva",           "Kimlik",      False, "FR73732829320",         "—",              "FR"),
    ("inn",           "Kimlik",      False, "7707083893",            "—",              "RU"),
    ("snils",         "Kimlik",      False, "112-233-445 95",        "—",              "RU"),
    ("ogrn",          "Kimlik",      False, "1027700132195",         "—",              "RU"),
    ("kpp",           "Kimlik",      False, "770701001",             "—",              "RU"),
    # İsim
    ("firstname",     "İsim",        True,  "Emre",                  "gender",         "TR US UK DE FR RU"),
    ("lastname",      "İsim",        True,  "Yılmaz",                "gender (RU)",    "TR US UK DE FR RU"),
    ("fullname",      "İsim",        True,  "Emre Kaya",             "gender",         "TR US UK DE FR RU"),
    ("patronymic",    "İsim",        True,  "Иванович",              "gender",         "RU"),
    ("passport",      "Belge",       False, "P1234567",              "—",              ""),
    ("license",       "Belge",       False, "654321",                "—",              ""),
    ("age",           "Demografik",  False, "34",                    "—",              ""),
    ("gender",        "Demografik",  False, "Male",                  "—",              ""),
    ("birthdate",     "Demografik",  False, "1990-05-14",            "—",              ""),
    # Finansal
    ("cardnum",       "Finansal",    False, "4532015112830366",      "--network",      ""),
    ("cardnetwork",   "Finansal",    False, "VISA",                  "—",              ""),
    ("cardtype",      "Finansal",    False, "Credit",                "—",              ""),
    ("cardstatus",    "Finansal",    False, "Active",                "—",              ""),
    ("cardcategory",  "Finansal",    False, "Gold",                  "—",              ""),
    ("cardowner",     "Finansal",    True,  "JOHN SMITH",            "gender",         "TR US UK DE FR RU"),
    ("cvv3",          "Finansal",    False, "847",                   "—",              ""),
    ("cvv4",          "Finansal",    False, "1234",                  "—",              ""),
    ("pin",           "Finansal",    False, "7291",                  "—",              ""),
    ("expiry",        "Finansal",    False, "09/27",                 "—",              ""),
    ("expirymonth",   "Finansal",    False, "09",                    "—",              ""),
    ("expiryyear",    "Finansal",    False, "27",                    "—",              ""),
    ("issuer",        "Finansal",    True,  "BosphorusBank A.S.",    "—",              "TR US UK DE FR RU"),
    ("balance",       "Finansal",    False, "12450.75",              "min max",        ""),
    ("iban",          "Finansal",    True,  "TR330006100519...",     "—",              "TR US UK DE FR RU"),
    # İletişim
    ("phone",         "İletişim",    True,  "+905325551234",         "—",              "TR US UK DE FR RU"),
    ("phone_country", "İletişim",    True,  "+90",                   "—",              "TR US UK DE FR RU"),
    ("phone_area",    "İletişim",    True,  "532",                   "—",              "TR US UK DE FR RU"),
    ("phone_local",   "İletişim",    True,  "5551234",               "—",              "TR US UK DE FR RU"),
    ("address_city",  "İletişim",    True,  "Istanbul",              "—",              "TR US UK DE FR RU"),
    ("address_street","İletişim",    True,  "Bagdat Caddesi",        "—",              "TR US UK DE FR RU"),
    ("address_full",  "İletişim",    True,  "Istanbul, Bagdat Cad.", "—",              "TR US UK DE FR RU"),
    ("postalcode",    "İletişim",    True,  "34500",                 "—",              "TR US UK DE FR RU"),
    ("plate",         "İletişim",    True,  "34 ABC 123",            "—",              "TR US UK DE FR RU"),
    ("email",         "İletişim",    True,  "user42@gmail.com",      "—",              "TR US UK DE FR RU"),
    # Bankacılık
    ("swift",         "Bankacılık",  True,  "DEUTDEDB",              "—",              "TR US UK DE FR RU"),
    ("sort_code",     "Bankacılık",  False, "20-00-00",              "—",              "UK"),
    ("routing_number","Bankacılık",  False, "021000021",             "—",              "US"),
    ("bik_code",      "Bankacılık",  False, "044525225",             "—",              "RU"),
    ("bank_name",     "Bankacılık",  True,  "Berliner Finanzbank",   "—",              "TR US UK DE FR RU"),
    ("transaction",   "Bankacılık",  True,  "{ref, iban*2, amount}", "—",              "TR US UK DE FR RU"),
    # Kurumsal
    ("company_name",  "Kurumsal",    True,  "Fischer Tech. GmbH",    "—",              "TR US UK DE FR RU"),
    ("job_title",     "Kurumsal",    True,  "Yazilim Muhendisi",     "—",              "TR US UK DE FR RU"),
    # Sağlık
    ("blood_type",    "Sağlık",      False, "A+",                    "—",              ""),
    ("nhs_number",    "Sağlık",      False, "943 476 5919",          "—",              "UK"),
    ("icd10",         "Sağlık",      False, "J18.9",                 "—",              ""),
    ("height",        "Sağlık",      True,  "178 cm / 5'10\"",       "—",              "TR US UK DE FR RU"),
    ("weight",        "Sağlık",      True,  "74 kg / 163 lbs",       "—",              "TR US UK DE FR RU"),
    # Ticaret
    ("currency",      "Ticaret",     True,  "{code:TRY, symbol:TL}", "—",              "TR US UK DE FR RU"),
    ("tax_rate",      "Ticaret",     True,  "{name:KDV, rate:20}",   "—",              "TR US UK DE FR RU"),
    ("invoice_number","Ticaret",     True,  "INV-2024-001234",       "—",              "TR US UK DE FR RU"),
    ("vin",           "Ticaret",     True,  "WBA3A5C5XMD123456",     "—",              "TR US UK DE FR RU"),
    ("vehicle",       "Ticaret",     True,  "{make,model,year,vin}", "—",              "TR US UK DE FR RU"),
    # Meta & Sistem
    ("uuid",          "Meta",        False, "550e8400-e29b-41d4-...", "—",             ""),
    ("requestid",     "Meta",        False, "550e8400-e29b-41d4-...", "—",             ""),
    ("correlationid", "Meta",        False, "550e8400-e29b-41d4-...", "—",             ""),
    ("sessionid",     "Meta",        False, "550e8400-e29b-41d4-...", "—",             ""),
    ("idempotencykey","Meta",        False, "550e8400-e29b-41d4-...", "—",             ""),
    ("deviceid",      "Meta",        False, "550E8400-E29B-41D4-...", "—",             ""),
    ("timestamp",     "Meta",        False, "1714900000",            "—",              ""),
    ("timestamp_iso", "Meta",        False, "2024-05-05T14:30:00",   "—",              ""),
    ("ipv4",          "Meta",        False, "192.168.1.42",          "—",              ""),
    ("ipv6",          "Meta",        False, "fe80:0000:0000:...",    "—",              ""),
    ("browser_name",  "Meta",        False, "Chrome",                "—",              ""),
    ("browser_version","Meta",       False, "124.0.6367.78",         "—",              ""),
    ("browser_engine","Meta",        False, "Blink",                 "—",              ""),
    ("useragent",     "Meta",        False, "Mozilla/5.0 ...",       "—",              ""),
    ("jwt",           "Meta",        False, "eyJ....eyJ....sig",     "—",              ""),
    ("bearertoken",   "Meta",        False, "Bearer eyJ....sig",     "—",              ""),
    ("hash",          "Meta",        False, "e3b0c44298fc...",       "algorithm",      ""),
    ("mac_address",   "Meta",        False, "A4:C3:F0:3D:8E:21",    "—",              ""),
    ("url",           "Meta",        True,  "https://api-42.co.uk/..","—",             "TR US UK DE FR RU"),
    ("domain",        "Meta",        True,  "test-77.com.tr",        "—",              "TR US UK DE FR RU"),
    ("color",         "Meta",        False, "#3A7BF0",               "format",         ""),
    ("clientversion", "Meta",        False, "2.4.1",                 "—",              ""),
    ("signature",     "Meta",        False, "a1b2c3d4... (hex)",     "secret payload", ""),
    ("apppassword",   "Meta",        False, "481302",                "—",              ""),
    # RFID
    ("rfid_uid",      "RFID",        False, "04:A3:B2:C1:D0:E5:F6", "—",              ""),
    ("epc",           "RFID",        False, "3034257BF400B71800...", "—",              ""),
    ("rfid_tag",      "RFID",        False, "{uid,standard,freq,mem}","—",             ""),
    # NFC
    ("nfc_uid",       "NFC",         False, "04:A3:B2:C1:D0:E5:F6", "—",              ""),
    ("nfc_atqa",      "NFC",         False, "00:44",                 "—",              ""),
    ("nfc_sak",       "NFC",         False, "20",                    "—",              ""),
    ("ndef_uri",      "NFC",         False, "{raw_hex, decoded url}","—",              ""),
    ("ndef_text",     "NFC",         True,  "{raw_hex, decoded txt}","—",              "TR US UK DE FR RU"),
    ("apdu",          "NFC",         False, "{cla,ins,p1,p2,hex}",   "—",              ""),
    ("nfc_tag",       "NFC",         False, "{uid,atqa,sak,ndef}",   "—",              ""),
    # IR
    ("ir_nec",        "IR",          False, "{addr,cmd,hex:20DF10EF}","—",             ""),
    ("ir_rc5",        "IR",          False, "{system,cmd,frame_bits}","—",             ""),
    ("ir_pronto",     "IR",          False, "0000 006D 0022 0000 ..","—",              ""),
    ("ir_raw",        "IR",          False, "{carrier_hz,pulses:[]}","—",              ""),
]

# Category display order and colors
_CAT_ORDER = [
    "Kimlik", "İsim", "Belge", "Demografik",
    "Finansal", "İletişim", "Bankacılık", "Kurumsal",
    "Sağlık", "Ticaret", "Meta", "RFID", "NFC", "IR",
]
_CAT_COLORS = {
    "Kimlik":     "bright_blue",
    "İsim":       "green",
    "Belge":      "cyan",
    "Demografik": "magenta",
    "Finansal":   "bright_blue",
    "İletişim":   "green",
    "Bankacılık": "cyan",
    "Kurumsal":   "yellow",
    "Sağlık":     "green",
    "Ticaret":    "magenta",
    "Meta":       "yellow",
    "RFID":       "cyan",
    "NFC":        "bright_blue",
    "IR":         "red",
}


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """
    🥷 mock-jutsu — Algorithmic Mock Data Engine (6 Locale, 95+ Type)
    Developed by: Altan Sayan (https://github.com/altansayan)
    """
    if ctx.invoked_subcommand is None:
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
@click.option('--cat', default='', help='Filter by category (e.g. Finansal, NFC, RFID, IR)')
def list_types(cat):
    """List all 95+ data types grouped by category."""
    W = 76

    # -- Header ----------------------------------------------------------------
    click.echo(click.style("-" * W, fg='bright_black'))
    click.echo(click.style(
        "  mock-jutsu  --  95+ Veri Tipi  |  6 Locale  |  689 Test",
        bold=True
    ))
    click.echo(click.style("-" * W, fg='bright_black'))
    click.echo()
    click.echo(click.style(
        "  Locale'ler: TR (Turkey) | US (United States) | UK (United Kingdom)\n"
        "              DE (Germany) | FR (France)        | RU (Russia)",
        fg='bright_black'
    ))
    click.echo()

    # -- Column headers --------------------------------------------------------
    h_type    = click.style(f"  {'TUR':<22}", fg='bright_black', bold=True)
    h_example = click.style(f"{'ORNEK CIKTI':<30}", fg='bright_black', bold=True)
    h_loc     = click.style(f"{'LOC':^5}", fg='bright_black', bold=True)
    h_extra   = click.style("EK / LOCALE", fg='bright_black', bold=True)
    click.echo(h_type + h_example + h_loc + h_extra)
    click.echo(click.style("  " + "-" * (W - 2), fg='bright_black'))

    # -- Group and print -------------------------------------------------------
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
            f"  >> {category.upper()} ({len(rows)} tip)",
            fg=color, bold=True
        ))

        for (typ, _cat, locale_aware, example, extra, locales) in rows:
            loc_flag = click.style("v", fg="green") if locale_aware else click.style("-", fg='bright_black')
            right    = locales if locales else (extra if extra != "—" else "")
            right_s  = click.style(right, fg='bright_black')
            typ_s    = click.style(f"  {typ:<22}", fg='white', bold=True)
            ex_s     = click.style(f"{example:<30}", fg='bright_yellow')
            click.echo(f"{typ_s}{ex_s} {loc_flag}   {right_s}")
            printed += 1

    # -- Footer ----------------------------------------------------------------
    click.echo()
    click.echo(click.style("-" * W, fg='bright_black'))
    click.echo(click.style(
        f"  {printed} tip gösteriliyor  "
        "· LOC=✓ → --locale parametresi destekler",
        fg='bright_black'
    ))
    click.echo(click.style(
        "  Örnek : mockjutsu generate tckn\n"
        "  Örnek : mockjutsu generate cardnum --network amex\n"
        "  Örnek : mockjutsu generate iban --locale DE\n"
        "  Filtre: mockjutsu list --cat NFC",
        fg='bright_black'
    ))
    click.echo(click.style("-" * W, fg='bright_black'))


@main.command()
@click.option('--port', default=8000, help='Port for the API server.')
def serve(port):
    """Start the FastAPI mock server."""
    import uvicorn
    click.echo(click.style(f"\n🚀 mock-jutsu API — port {port}", fg='green', bold=True))
    from api.main import app
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
