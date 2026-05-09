import os
import sys
import subprocess

def run_checks():
    # 1. Path Management
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SRC_DIR = os.path.join(BASE_DIR, "src")
    
    # 2. Environment Setup (Root fix for PYTHONPATH)
    env = os.environ.copy()
    env["PYTHONPATH"] = SRC_DIR + os.pathsep + env.get("PYTHONPATH", "")

    print(f"Files in BASE_DIR: {os.listdir(BASE_DIR)}")
    if os.path.exists(os.path.join(BASE_DIR, "tests")):
        print(f"Files in tests/: {os.listdir(os.path.join(BASE_DIR, 'tests'))}")
    print("Starting Mock Jutsu Master Compliance Check...")
    
    # 3. Step 1: Run Compliance Auditor
    print("\nStep 1: Running Compliance Auditor...")
    audit_script = os.path.join(BASE_DIR, "scripts", "audit_compliance.py")
    result = subprocess.run([sys.executable, audit_script], cwd=BASE_DIR, env=env)
    if result.returncode != 0:
        print("Compliance Audit FAILED.")
        return 1

    # 4. Step 2: Run Pytest with Coverage
    print("\nStep 2: Running Pytest (Strict Coverage)...")
    # We use -p no:capture to avoid the I/O error on some environments
    pytest_cmd = [
        sys.executable, "-m", "pytest", 
        "tests/", 
        "--cov=src", 
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
