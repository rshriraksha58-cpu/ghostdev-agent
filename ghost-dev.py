#!/usr/bin/env python3
"""
  ██████╗ ██╗  ██╗ ██████╗ ███████╗████████╗██████╗ ███████╗██╗   ██╗
 ██╔════╝ ██║  ██║██╔═══██╗██╔════╝╚══██╔══╝██╔══██╗██╔════╝██║   ██║
 ██║  ███╗███████║██║   ██║███████╗   ██║   ██║  ██║█████╗  ██║   ██║
 ██║   ██║██╔══██║██║   ██║╚════██║   ██║   ██║  ██║██╔══╝  ╚██╗ ██╔╝
 ╚██████╔╝██║  ██║╚██████╔╝███████║   ██║   ██████╔╝███████╗ ╚████╔╝
  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝   ╚═════╝ ╚══════╝  ╚═══╝

  AI That Finishes Your Work Without You
  GitAgent Hackathon 2026
"""

import os
import sys
import time
import argparse

from watcher           import GhostWatcher
from context_harvester import harvest_context
from ai_engine         import generate_completion, generate_bug_fix
from code_validator    import validate_string, run_tests
from git_manager       import commit_and_push, get_repo_root, get_recent_log


# ── Config ───────────────────────────────────────────────────────────────────

DEFAULT_IDLE_THRESHOLD = 30   # seconds before ghost activates
POLL_INTERVAL          = 5    # seconds between idle checks
BANNER = """
💀  GhostDev is watching your repo...
    Waiting for you to go idle ({threshold}s of no changes)
    Press Ctrl+C to stop.
"""


# ── Core Loop ─────────────────────────────────────────────────────────────────

def run_ghost_pass(repo_path: str, context: dict, dry_run: bool = False) -> int:
    """
    One full ghost pass:
      1. Find all stub/todo files
      2. For each, generate completion via Claude
      3. Validate the result
      4. Write + commit if valid
    Returns number of files successfully completed.
    """
    stubs = context.get('stubs', {})
    if not stubs:
        print("  ✅ No incomplete files found. Repo looks clean!")
        return 0

    print(f"\n  🔍 Found {len(stubs)} file(s) that need work:")
    for rel in stubs:
        print(f"     • {rel}")

    completed = 0
    for rel_path, original_content in stubs.items():
        abs_path = os.path.join(repo_path, rel_path)
        print(f"\n  🤖 Processing: {rel_path}")

        # ── Generate completion ──────────────────────────────────────────────
        try:
            completed_code = generate_completion(context, rel_path, original_content)
        except Exception as e:
            print(f"     ❌ Claude API error: {e}")
            continue

        # ── Validate before touching the file ───────────────────────────────
        ok, msg = validate_string(completed_code, filename=rel_path)
        if not ok:
            print(f"     ⚠️  Validation failed — attempting auto-fix...")
            try:
                completed_code = generate_bug_fix(
                    context, rel_path, completed_code, msg
                )
                ok, msg = validate_string(completed_code, filename=rel_path)
            except Exception as e:
                print(f"     ❌ Bug-fix API error: {e}")

        if not ok:
            print(f"     ❌ Still invalid after fix attempt — skipping.\n     {msg}")
            continue

        print(f"     ✅ Validation passed")

        if dry_run:
            print(f"     🔍 [DRY RUN] Would write and commit {rel_path}")
            print("     ── Preview (first 20 lines) ──")
            for line in completed_code.splitlines()[:20]:
                print(f"        {line}")
            completed += 1
            continue

        # ── Write file ───────────────────────────────────────────────────────
        try:
            with open(abs_path, 'w', encoding='utf-8') as f:
                f.write(completed_code)
        except IOError as e:
            print(f"     ❌ Could not write file: {e}")
            continue

        # ── Commit & push ────────────────────────────────────────────────────
        commit_msg = f"👻 GhostDev: complete {rel_path}"
        success = commit_and_push(repo_path, abs_path, commit_msg)
        if success:
            completed += 1
        else:
            print(f"     ⚠️  File written but git operation failed for {rel_path}")

    return completed


def main():
    parser = argparse.ArgumentParser(
        description="GhostDev – AI that finishes your work without you"
    )
    parser.add_argument(
        '--repo', default='.',
        help='Path to git repository to watch (default: current directory)'
    )
    parser.add_argument(
        '--idle', type=int, default=DEFAULT_IDLE_THRESHOLD,
        help=f'Seconds of inactivity before ghost activates (default: {DEFAULT_IDLE_THRESHOLD})'
    )
    parser.add_argument(
        '--once', action='store_true',
        help='Run one pass immediately and exit (no watching)'
    )
    parser.add_argument(
        '--dry-run', action='store_true',
        help='Show what would be changed without writing or committing'
    )
    args = parser.parse_args()

    # ── Validate environment ─────────────────────────────────────────────────
    if not os.environ.get('ANTHROPIC_API_KEY'):
        print("❌ ANTHROPIC_API_KEY environment variable not set.")
        print("   Get a free key at: https://console.anthropic.com")
        print("   Then run: export ANTHROPIC_API_KEY='your-key-here'")
        sys.exit(1)

    try:
        repo_path = get_repo_root(args.repo)
    except RuntimeError as e:
        print(f"❌ {e}")
        sys.exit(1)

    print(f"\n💀  GhostDev – AI That Finishes Your Work Without You")
    print(f"    Repo : {repo_path}")
    print(f"    Model: claude-opus-4-5")
    if args.dry_run:
        print(f"    Mode : DRY RUN (no files will be written)")

    # ── One-shot mode ────────────────────────────────────────────────────────
    if args.once:
        print("\n🔍 Harvesting context...")
        context = harvest_context(repo_path)
        print(f"   Goals   : {context['goals'][:80]}...")
        print(f"   TODOs   : {len(context['todos'].splitlines())} found")
        print(f"   Stubs   : {len(context['stubs'])} file(s)")
        print(f"   Commits : {context['commits'].splitlines()[0] if context['commits'] else 'none'}")

        print("\n💀 Ghost taking over...\n")
        n = run_ghost_pass(repo_path, context, dry_run=args.dry_run)
        print(f"\n✅ Done. {n} file(s) completed.")
        if not args.dry_run and n:
            print("\n📜 Recent git log:")
            print(get_recent_log(repo_path))
        return

    # ── Daemon / watch mode ──────────────────────────────────────────────────
    print(BANNER.format(threshold=args.idle))

    watcher = GhostWatcher(repo_path, idle_threshold=args.idle)
    watcher.start()

    try:
        while True:
            time.sleep(POLL_INTERVAL)

            idle_secs = watcher.seconds_since_last_change()

            if watcher.is_developer_idle():
                print(f"\n💀 Developer idle for {idle_secs:.0f}s — Ghost taking over...")

                # Harvest fresh context
                context = harvest_context(repo_path)

                if not context['stubs']:
                    print("  ✅ Repo looks complete. Nothing to do.")
                    watcher.reset()
                    continue

                # Run the ghost pass
                n = run_ghost_pass(repo_path, context, dry_run=args.dry_run)

                if n:
                    print(f"\n✅ Ghost completed {n} file(s).")
                    print("\n📜 Recent git log:")
                    print(get_recent_log(repo_path))

                # Reset so we don't re-trigger immediately
                watcher.reset()
                print(f"\n👻 Ghost going back into hiding... watching for more changes.\n")

            else:
                remaining = args.idle - idle_secs
                print(f"\r  ⏳ Developer active. Ghost activates in {remaining:.0f}s...", end='', flush=True)

    except KeyboardInterrupt:
        print("\n\n👋 GhostDev stopped.")
        watcher.stop()


if __name__ == '__main__':
    main()
