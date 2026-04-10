import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class GhostWatcher(FileSystemEventHandler):
    """
    Watches a directory for file changes.
    Tracks the last time any .py file was modified.
    GhostDev activates once the developer goes idle.
    """

    def __init__(self, repo_path: str, idle_threshold: int = 30):
        super().__init__()
        self.repo_path      = repo_path
        self.idle_threshold = idle_threshold   # seconds of no activity
        self.last_change    = time.time()
        self._lock          = threading.Lock()
        self._observer      = Observer()

    # ── Watchdog event handlers ──────────────────────────────────────────────

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.py'):
            self._touch()

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.py'):
            self._touch()

    def _touch(self):
        with self._lock:
            self.last_change = time.time()

    # ── Public API ───────────────────────────────────────────────────────────

    def is_developer_idle(self) -> bool:
        """Return True when no .py file has changed for idle_threshold seconds."""
        with self._lock:
            return (time.time() - self.last_change) >= self.idle_threshold

    def seconds_since_last_change(self) -> float:
        with self._lock:
            return time.time() - self.last_change

    def reset(self):
        """Call after GhostDev finishes a pass so it doesn't re-trigger immediately."""
        with self._lock:
            self.last_change = time.time()

    def start(self):
        self._observer.schedule(self, self.repo_path, recursive=True)
        self._observer.start()
        print(f"  👁  Watching {self.repo_path}  (idle threshold: {self.idle_threshold}s)")

    def stop(self):
        self._observer.stop()
        self._observer.join()
