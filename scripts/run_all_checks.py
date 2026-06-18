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

    # Step 3: Auto-update README badge and HOW-TO pages
    print("\nStep 3: Updating README badge and HOW-TO pages...")
    docs_script = os.path.join(BASE_DIR, "generate_full_docs.py")
    docs_result = subprocess.run(
        [sys.executable, docs_script], cwd=BASE_DIR, env=env,
        capture_output=True, text=True,
    )
    if docs_result.returncode != 0:
        print("generate_full_docs.py FAILED:")
        print(docs_result.stdout[-2000:])
        return 1
    print(f"  {docs_result.stdout.strip().splitlines()[-1]}")

    # Check if README or HOW-TO changed
    diff_result = subprocess.run(
        ["git", "diff", "--name-only", "README.md", "HOW-TO/", "index.html"],
        cwd=BASE_DIR, capture_output=True, text=True,
    )
    changed = [f for f in diff_result.stdout.strip().splitlines() if f]
    if changed:
        print(f"\n  Badge updated — auto-committing: {', '.join(changed)}")
        subprocess.run(["git", "add", "README.md", "HOW-TO/", "index.html"],
                       cwd=BASE_DIR)
        commit_result = subprocess.run(
            ["git", "commit",
             "-m", f"chore(docs): auto-update badge to {counts['passed']} passed [skip ci]",
             "--no-verify"],
            cwd=BASE_DIR, capture_output=True, text=True,
        )
        if commit_result.returncode != 0:
            print("  Auto-commit failed (nothing to commit or git error).")
            print(commit_result.stderr)
        else:
            print("  Auto-commit created. Re-run git push to include it.")
            return 1  # abort current push so new commit is included next push
    else:
        print("  Badge already up to date — no commit needed.")

    print("\nALL CHECKS PASSED. Ready for push.")
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
