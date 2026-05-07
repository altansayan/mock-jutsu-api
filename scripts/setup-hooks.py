import os
import sys
import stat

def main():
    repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    hooks_dir = os.path.join(repo_dir, ".git", "hooks")
    
    if not os.path.exists(hooks_dir):
        print("Error: Could not find .git/hooks directory. Are you in the repository root?")
        sys.exit(1)
        
    pre_push_path = os.path.join(hooks_dir, "pre-push")
    
    hook_script = """#!/bin/sh
# Enforce tests before pushing

echo "🥷 mock-jutsu pre-push hook: Running tests..."

# Ensure we are in the root directory
cd "$(dirname "$0")/../../"

# Run pytest
pytest tests/
if [ $? -ne 0 ]; then
    echo "❌ Tests failed! Push rejected."
    echo "Please fix the failing tests before pushing."
    exit 1
fi

echo "✅ All tests passed! Proceeding with push..."
exit 0
"""

    with open(pre_push_path, "w", encoding="utf-8") as f:
        f.write(hook_script)
        
    # Make executable on Unix-like systems
    if os.name == 'posix':
        st = os.stat(pre_push_path)
        os.chmod(pre_push_path, st.st_mode | stat.S_IEXEC)
        
    print(f"Successfully installed pre-push hook at {pre_push_path}")
    print("From now on, git will automatically run 'pytest tests/' before every push.")
    print("If the tests fail, the push will be aborted.")

if __name__ == "__main__":
    main()
