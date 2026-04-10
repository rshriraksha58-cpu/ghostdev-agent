import subprocess
import os


def get_repo_root(path: str = '.') -> str:
    """Return the root of the git repo containing `path`."""
    result = subprocess.run(
        ['git', 'rev-parse', '--show-toplevel'],
        cwd=path, capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"Not a git repo: {path}")
    return result.stdout.strip()


def stage_file(repo_path: str, file_path: str) -> bool:
    """git add a specific file. Returns True on success."""
    result = subprocess.run(
        ['git', 'add', file_path],
        cwd=repo_path, capture_output=True, text=True
    )
    return result.returncode == 0


def commit(repo_path: str, message: str) -> tuple[bool, str]:
    """
    Create a git commit with the ghost developer identity.
    Returns (success, output).
    """
    env = os.environ.copy()
    env['GIT_AUTHOR_NAME']     = 'GhostDev'
    env['GIT_AUTHOR_EMAIL']    = 'ghost@ghostdev.ai'
    env['GIT_COMMITTER_NAME']  = 'GhostDev'
    env['GIT_COMMITTER_EMAIL'] = 'ghost@ghostdev.ai'

    result = subprocess.run(
        ['git', 'commit', '-m', message],
        cwd=repo_path, capture_output=True, text=True, env=env
    )
    return result.returncode == 0, (result.stdout + result.stderr).strip()


def push(repo_path: str) -> tuple[bool, str]:
    """
    Push current branch to origin.
    Returns (success, output).
    Silently skips if no remote is configured.
    """
    # Check if remote exists
    result = subprocess.run(
        ['git', 'remote'],
        cwd=repo_path, capture_output=True, text=True
    )
    if not result.stdout.strip():
        return True, "No remote configured — skipping push."

    result = subprocess.run(
        ['git', 'push'],
        cwd=repo_path, capture_output=True, text=True
    )
    return result.returncode == 0, (result.stdout + result.stderr).strip()


def has_uncommitted_changes(repo_path: str) -> bool:
    """Return True if there are staged or unstaged changes."""
    result = subprocess.run(
        ['git', 'status', '--porcelain'],
        cwd=repo_path, capture_output=True, text=True
    )
    return bool(result.stdout.strip())


def commit_and_push(repo_path: str, file_path: str, message: str) -> bool:
    """
    Full pipeline: stage → commit → push.
    Returns True if everything succeeded.
    """
    if not stage_file(repo_path, file_path):
        print(f"    ⚠️  Could not stage {file_path}")
        return False

    ok, out = commit(repo_path, message)
    if not ok:
        print(f"    ⚠️  Commit failed: {out}")
        return False
    print(f"    💾 Committed: {message}")

    ok, out = push(repo_path)
    if ok:
        print(f"    🚀 Pushed to origin")
    else:
        print(f"    ⚠️  Push failed (commit saved locally): {out}")

    return True


def get_recent_log(repo_path: str, n: int = 5) -> str:
    result = subprocess.run(
        ['git', 'log', f'-{n}', '--oneline', '--decorate'],
        cwd=repo_path, capture_output=True, text=True
    )
    return result.stdout.strip()
