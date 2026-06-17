import os
import re
import sys
import json
import subprocess
import importlib.util

_REQUIRED_TEST_DEPS = ["pytest", "pytest_cov", "playwright", "pytest_playwright"]

def _check_test_deps():
    missing = [pkg for pkg in _REQUIRED_TEST_DEPS if importlib.util.find_spec(pkg) is None]
    if missing:
        print("\n[CI PARITY CHECK] Eksik test bağımlılıkları tespit edildi:")
        for pkg in missing:
            print(f"  x {pkg}")
        print("\nCI'da da aynı hata oluşur. Önce şunu çalıştırın:")
        print("  pip install -e \".[test]\"")
        print("  playwright install chromium")
        return False
    return True


def _stream_pytest(cmd, cwd, env):
    """Run pytest, stream output to terminal, return (returncode, full_output)."""
    proc = subprocess.Popen(
        cmd, cwd=cwd, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1, encoding="utf-8", errors="replace",
    )
    lines = []
    for line in proc.stdout:
        sys.stdout.write(line)
        sys.stdout.flush()
        lines.append(line)
    proc.wait()
    return proc.returncode, "".join(lines)


def _parse_counts(output: str) -> dict:
    passed = skipped = failed = 0
    m = re.search(r"(\d+) passed", output)
    if m:
        passed = int(m.group(1))
    m = re.search(r"(\d+) skipped", output)
    if m:
        skipped = int(m.group(1))
    m = re.search(r"(\d+) failed", output)
    if m:
        failed = int(m.group(1))
    return {"passed": passed, "skipped": skipped, "failed": failed}


def run_checks():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SRC_DIR  = os.path.join(BASE_DIR, "src")

    env = os.environ.copy()
    env["PYTHONPATH"] = SRC_DIR + os.pathsep + env.get("PYTHONPATH", "")

    print("Starting Mock Jutsu Master Compliance Check...")

    # Step 0: CI parity
    print("\nStep 0: CI Parity Check (test dependencies)...")
    if not _check_test_deps():
        return 1
    print("  All test dependencies present.")

    # Step 1: Compliance Audit
    print("\nStep 1: Running Compliance Auditor...")
    audit_script = os.path.join(BASE_DIR, "scripts", "audit_compliance.py")
    result = subprocess.run(
        [sys.executable, audit_script], cwd=BASE_DIR, env=env,
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print("Compliance Audit FAILED.")
        print(result.stdout)
        print(result.stderr)
        return 1

    # Step 2: Pytest (streaming — output shown in real-time)
    print("\nStep 2: Running Pytest (Strict Coverage)...")
    pytest_cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "--cov=mockjutsu",
        "--cov-fail-under=85",
        "--ignore=tests/test_external_validators.py",
        "-p", "no:capture",
    ]
    rc, output = _stream_pytest(pytest_cmd, BASE_DIR, env)
    if rc != 0:
        print("Test Suite or Coverage FAILED.")
        return 1

    # Parse and persist test counts
    counts = _parse_counts(output)
    stats_path = os.path.join(BASE_DIR, "compliance", "test_stats.json")
    os.makedirs(os.path.dirname(stats_path), exist_ok=True)
    with open(stats_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(counts, f, indent=2)
    print(f"\n  Test stats saved: {counts['passed']} passed, "
          f"{counts['skipped']} skipped, {counts['failed']} failed")
    print("  Run 'python generate_full_docs.py' to update HOW-TO + README badge.")

    print("\nALL CHECKS PASSED. Ready for push.")
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
