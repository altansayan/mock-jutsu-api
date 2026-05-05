"""
mock-jutsu — Enhanced CLI with Multi-Locale Info
Developer: Altan Sayan (https://github.com/altansayan)
"""

import click
from mockjutsu.core import jutsu
import uvicorn

@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """
    🥷 mock-jutsu — Atomic Mock Data Tool (Multi-Locale)
    Developed by: Altan Sayan (https://github.com/altansayan)
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())

@main.command()
@click.argument('data_type', required=False)
@click.option('--locale', default='TR', help='Locale (TR, UK, DE, FR, RU, US)')
@click.option('--network', default='visa', help='Card network (visa, mc, amex, troy, mir)')
def generate(data_type, locale, network):
    """Generate mock data. Example: mockjutsu generate tckn --locale TR"""
    if not data_type:
        click.echo("Error: Specify a type. See 'mockjutsu list'")
        return
    result = jutsu.generate(data_type, locale=locale, network=network)
    color = 'red' if "ERROR" in str(result) else 'green'
    click.echo(f"[{locale.upper()}] {data_type}: {click.style(str(result), fg=color, bold=True)}")

@main.command()
def list():
    """List all supported locales and atomic data types."""
    click.echo(click.style("\n🌍 SUPPORTED LOCALES", fg='cyan', bold=True))
    click.echo("TR (Turkey), UK (United Kingdom), US (USA), DE (Germany), FR (France), RU (Russia)")

    click.echo(click.style("\n🥷 ATOMIC DATA TYPES", fg='cyan', bold=True))
    
    categories = {
        "Identity": ["tckn/ssn/nin", "firstname", "lastname", "fullname", "patronymic (RU)", "passport", "age", "gender"],
        "Financial": ["cardnum", "cvv3", "cvv4", "expiry", "issuer", "iban"],
        "Communication": ["phone", "address_city", "address_full", "email"],
        "Meta & System": ["uuid", "requestid", "timestamp", "bearertoken", "browser_name", "ipv4"]
    }
    
    for cat, types in categories.items():
        click.echo(click.style(f"\n[{cat}]", fg='yellow'))
        click.echo("  " + ", ".join(types))
    
    click.echo(click.style("\nExample: mockjutsu generate ssn --locale US", fg='white', dim=True))

@main.command()
@click.option('--port', default=8000, help='Port for API.')
def serve(port):
    """Start the Ninja API server."""
    click.echo(click.style(f"\n🚀 Ninja API active on port {port}...", fg='green', bold=True))
    from api.main import app
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
