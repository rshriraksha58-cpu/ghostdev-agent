import subprocess
import sys
import tempfile
import os


def validate_file(file_path: str) -> tuple[bool, str]:
    """
    Run syntax check + flake8 lint on a single file.
    Returns (passed: bool, message: str).
    """

    # 1. Syntax check via py_compile
    result = subprocess.run(
        [sys.executable, '-m', 'py_compile', file_path],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        return False, f"Syntax error:\n{result.stderr}"

    # 2. Flake8 lint (warnings are OK, only fail on errors E/F)
    result = subprocess.run(
        ['flake8', file_path,
         '--max-line-length=120',
         '--select=E,F',          # only errors, not style warnings
         '--extend-ignore=E501'], # ignore line-too-long
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        # filter out minor style issues, only show real problems
        issues = result.stdout.strip()
        # allow undefined name warnings for common ghost completions
        critical = [l for l in issues.splitlines()
                    if not l.endswith("undefined name 'self'")]
        if critical:
            return False, f"Lint errors:\n" + '\n'.join(critical)

    return True, "OK"


def validate_string(code: str, filename: str = "ghostdev_temp.py") -> tuple[bool, str]:
    """
    Validate a code string without writing to the target file yet.
    Writes to a temp file, validates, then deletes it.
    """
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.py', prefix='ghostdev_',
        delete=False, encoding='utf-8'
    ) as tmp:
        tmp.write(code)
        tmp_path = tmp.name

    try:
        ok, msg = validate_file(tmp_path)
        return ok, msg
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def run_tests(repo_path: str) -> tuple[bool, str]:
    """
    Run pytest in the repo (if tests exist).
    Returns (passed, output).
    """
    test_dirs = ['tests', 'test']
    has_tests = any(
        os.path.isdir(os.path.join(repo_path, d)) for d in test_dirs
    )
    # also check for test_*.py files
    if not has_tests:
        for f in os.listdir(repo_path):
            if f.startswith('test_') and f.endswith('.py'):
                has_tests = True
                break

    if not has_tests:
        return True, "No tests found — skipping pytest."

    result = subprocess.run(
        [sys.executable, '-m', 'pytest', '--tb=short', '-q'],
        cwd=repo_path,
        capture_output=True,
        text=True,
        timeout=60
    )
    passed = result.returncode == 0
    output = (result.stdout + result.stderr).strip()
    return passed, output
