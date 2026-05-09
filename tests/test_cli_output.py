"""
Verifies the actual terminal output of CLI commands.
Checks the banner, counts, and specific parameter existence in 'list' output.
"""
import subprocess
import sys
import os

def run_cli(*args):
    # Use python -m to ensure we use the current source, setting PYTHONPATH to src
    env = os.environ.copy()
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    env["PYTHONPATH"] = os.path.join(base_dir, "src")
    # Set TERM to dumb to reduce colors, but Rich might still add them
    env["TERM"] = "dumb"
    cmd = [sys.executable, "-m", "mockjutsu.cli"] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', env=env)
    return result

def strip_ansi(text):
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def test_cli_list_output_contains_expected_count():
    """Asserts that 'mockjutsu list' shows the correct total count."""
    res = run_cli("list")
    assert res.returncode == 0
    
    output = strip_ansi(res.stdout)
    
    # Check for the key phrase and the numeric value separately
    assert "types listed" in output
    
    import sys
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, os.path.join(base_dir, "src"))
    from mockjutsu.cli import _REFERENCE
    types_count = len([r for r in _REFERENCE if r[0].strip() and not r[0].strip().startswith("--")])
    
    assert str(types_count) in output
    
    # 2. Check for specific new/important parameters
    assert "track2_data" in output
    assert "tckn" in output
    assert "iban" in output
    assert "credit_score" in output
    assert "3ds_cavv" in output
    assert "3ds_eci" in output

def test_cli_generate_smoke():
    """Smoke test for generation output."""
    res = run_cli("generate", "tckn")
    assert res.returncode == 0
    assert len(res.stdout.strip()) == 11
    assert res.stdout.strip().isdigit()

def test_cli_help():
    """Ensure help works and shows the main commands."""
    res = run_cli("--help")
    assert res.returncode == 0
    # Check for the banner/engine name instead of hardcoded usage path
    assert "Mock Jutsu - The Ultimate Algorithmic Mock Data Engine" in res.stdout
    assert "generate" in res.stdout
    assert "bulk" in res.stdout
    assert "template" in res.stdout
    assert "list" in res.stdout
