import sys
import os
import re

# Add src to path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

try:
    import mockjutsu.core as mc
    from mockjutsu.cli import _REFERENCE
except ImportError as e:
    print(f"Error importing project modules: {e}")
    sys.exit(1)

def audit():
    print("Mock Jutsu Compliance Audit starting...")
    
    # 1. Get all types from core
    core_types = set()
    for attr in dir(mc):
        if attr.endswith('_TYPES'):
            core_types.update(getattr(mc, attr))
    
    # 2. Get all types from CLI reference
    ref_types = set([r[0].strip() for r in _REFERENCE if r[0].strip() and not r[0].strip().startswith('--')])
    
    # 3. Read all test files content
    test_dir = os.path.join(BASE_DIR, "tests")
    combined_test_content = ""
    for filename in os.listdir(test_dir):
        if filename.startswith("test_") and filename.endswith(".py"):
            with open(os.path.join(test_dir, filename), "r", encoding="utf-8") as f:
                combined_test_content += f.read()

    errors = []

    print(f"Auditing {len(core_types)} core types against test suites...")

    for dt in sorted(list(core_types)):
        # Check CLI Reference
        if dt not in ref_types:
            errors.append(f"[CLI/Docs] Type '{dt}' is registered in core but missing in cli.py (_REFERENCE).")
            
        # Check if type is tested (mention in test files)
        if dt not in combined_test_content:
            errors.append(f"[Test Missing] No mention of '{dt}' found in tests/. Every type must have unit and api tests.")

    # Check for orphans (types in reference but not in core)
    # cardowner is a known alias
    for rt in ref_types:
        if rt not in core_types and rt != "cardowner":
            errors.append(f"[Orphan] Type '{rt}' is in CLI reference but NOT in core registries.")

    print("-" * 50)
    if errors:
        print(f"COMPLIANCE FAILURE: Found {len(errors)} issues!")
        for err in errors:
            print(err)
        print("\nFix these issues before pushing. Stay professional.")
        sys.exit(1)
    else:
        print("COMPLIANCE PASSED: All types are registered, tested, and documented.")
        sys.exit(0)

if __name__ == "__main__":
    audit()
