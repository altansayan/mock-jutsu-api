"""
Tests for the newly industrialized CLI features: Extra Parameters and Flag processing.
"""
import pytest
from click.testing import CliRunner
from mockjutsu.cli import main
import re

@pytest.fixture
def runner():
    return CliRunner()

def test_cli_list_shows_extra_param_header(runner):
    """Verify that 'mockjutsu list' includes the new EXTRA PARAM column header."""
    result = runner.invoke(main, ['list'])
    assert result.exit_code == 0
    # Strip formatting or check case-insensitively
    output = result.output.upper()
    assert "EXTRA PARAM" in output

def test_cli_generate_with_prefix(runner):
    """Verify that --prefix flag works for supported types."""
    result = runner.invoke(main, ['generate', 'tckn', '--prefix', 'TR'])
    assert result.exit_code == 0
    assert result.output.strip().startswith('TR')

def test_cli_generate_with_gender(runner):
    """Verify that --gender flag works for name generation."""
    # We can't strictly verify if a name is male/female easily without a database, 
    # but we can ensure the command doesn't crash and returns a valid name.
    result = runner.invoke(main, ['generate', 'firstname', '--gender', 'male'])
    assert result.exit_code == 0
    assert len(result.output.strip()) > 1

def test_cli_generate_with_min_max(runner):
    """Verify that --min and --max flags work for balance/age."""
    result = runner.invoke(main, ['generate', 'age', '--min', '20', '--max', '25'])
    assert result.exit_code == 0
    val = int(result.output.strip())
    assert 20 <= val <= 25

def test_cli_generate_with_amount_merchant(runner):
    """Verify that --amount and --merchant flags work for QR codes (smoke test)."""
    result = runner.invoke(main, ['generate', 'emv_qr_pos', '--amount', '100.50', '--merchant', 'TESTPAY'])
    assert result.exit_code == 0
    assert len(result.output.strip()) > 10
