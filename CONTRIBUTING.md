# Contributing to mock-jutsu

First of all, thank you for considering contributing to `mock-jutsu`! 🥷
We welcome all contributions that align with our core philosophy: **"Stop mocking with random strings. Start generating cryptographically valid test data."**

To maintain the highest quality and performance standards, we have strict guidelines that every contributor must follow.

## 🚨 The Golden Rule: Test-Driven Development (TDD)

**Tests first. Then code.**
We do not accept Pull Requests that add or modify features without accompanying tests.

1. **Write the Test**: Before you write your algorithm, write a test in `tests/test_generators.py` that mathematically validates what the generated data *should* look like (e.g., passing a checksum or matching a regex).
2. **Watch it Fail**: Run the test. It must fail.
3. **Write the Code**: Implement the generator algorithm.
4. **Watch it Pass**: Run the test suite and ensure it passes successfully.

If you push code without tests, or if your code breaks existing tests, our **GitHub Actions CI Pipeline will automatically reject your Pull Request.**

## ⚡ Performance Mandate

`mock-jutsu` is designed for massive bulk generation. A generator must be fast.
- Do **not** use the `secrets` module for standard generation. Use the `random` module (e.g., `random.randrange`, `random.choice`) which is 2x-3x faster. Only use `secrets` for cryptographic functions (like `crypto.py`).
- Do **not** place `import` statements inside `while` or `for` loops.
- Your new generator must pass the baseline performance limits defined in `tests/test_performance.py`.

## 🛠️ Local Development Setup

To test your code locally before pushing:

1. Clone the repository and install it in editable mode:
   ```bash
   pip install -e .
   ```
2. Install test dependencies:
   ```bash
   pip install pytest
   ```
3. Run the test suite:
   ```bash
   pytest tests/
   ```

### Enforce Pre-Push Checks Locally
We highly recommend running our setup script to install a git `pre-push` hook. This will automatically run the test suite before you push, saving you from CI failures:
```bash
python scripts/setup-hooks.py
```

## Pull Request Process

1. Fork the repo and create your branch from `main`.
2. Ensure your code follows the performance and zero-dependency mandates.
3. Ensure all tests (`pytest tests/`) pass locally.
4. Open a Pull Request. The GitHub Actions bot will verify your code. Wait for the green checkmark (✅) before requesting a review.
