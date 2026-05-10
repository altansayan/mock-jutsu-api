import os
import sys
import subprocess
import importlib.util

# CI'da zorunlu olan test bağımlılıkları — eksikse push bloklanır
_REQUIRED_TEST_DEPS = ["pytest", "pytest_cov", "playwright", "pytest_playwright"]

def _check_test_deps():
    missing = [pkg for pkg in _REQUIRED_TEST_DEPS if importlib.util.find_spec(pkg) is None]
    if missing:
        print("\n[CI PARITY CHECK] Eksik test bağımlılıkları tespit edildi:")
        for pkg in missing:
            print(f"  ✗ {pkg}")
        print("\nCI'da da aynı hata oluşur. Önce şunu çalıştırın:")
        print("  pip install -e \".[test]\"")
        print("  playwright install chromium")
        return False
    return True

def run_checks():
    # 1. Path Management
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SRC_DIR = os.path.join(BASE_DIR, "src")

    # 2. Environment Setup (Root fix for PYTHONPATH)
    env = os.environ.copy()
    env["PYTHONPATH"] = SRC_DIR + os.pathsep + env.get("PYTHONPATH", "")

    print("Starting Mock Jutsu Master Compliance Check...")

    # 3. Step 0: CI parity — test bağımlılıkları kurulu mu?
    print("\nStep 0: CI Parity Check (test dependencies)...")
    if not _check_test_deps():
        return 1
    print("  All test dependencies present.")
    
    # 4. Step 1: Run Compliance Auditor
    print("\nStep 1: Running Compliance Auditor...")
    audit_script = os.path.join(BASE_DIR, "scripts", "audit_compliance.py")
    result = subprocess.run([sys.executable, audit_script], cwd=BASE_DIR, env=env, capture_output=True, text=True)
    if result.returncode != 0:
        print("Compliance Audit FAILED.")
        print(result.stdout)
        print(result.stderr)
        return 1

    # 5. Step 2: Run Pytest with Coverage
    print("\nStep 2: Running Pytest (Strict Coverage)...")
    # We use -p no:capture to avoid the I/O error on some environments
    pytest_cmd = [
        sys.executable, "-m", "pytest", 
        "tests/", 
        "--cov=mockjutsu", 
        "--cov-fail-under=85", 
        "-p", "no:capture"
    ]
    result = subprocess.run(pytest_cmd, cwd=BASE_DIR, env=env)
    if result.returncode != 0:
        print("Test Suite or Coverage FAILED.")
        return 1

    print("\nALL CHECKS PASSED. Ready for push.")
    return 0

if __name__ == "__main__":
    sys.exit(run_checks())
