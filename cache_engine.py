"""
Majestic AI v1.0 – In-Memory State Engine
LRU Cache with TTL, active-process registry, error history
"""
import time
import threading
from collections import OrderedDict

# ─── LRU Cache with TTL ────────────────────────────────────────────────────
class TTLLRUCache:
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.max_size = max_size
        self.ttl      = ttl
        self._store   = OrderedDict()   # key -> (value, expire_at)
        self._lock    = threading.RLock()
        # Background cleanup thread
        self._cleaner = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._cleaner.start()

    # public API ─────────────────────────────────────────────────────────────
    def get(self, key):
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            value, exp = entry
            if time.time() > exp:
                del self._store[key]
                return None
            self._store.move_to_end(key)
            return value

    def set(self, key, value, ttl: int = None):
        ttl = ttl or self.ttl
        with self._lock:
            if key in self._store:
                self._store.move_to_end(key)
            self._store[key] = (value, time.time() + ttl)
            if len(self._store) > self.max_size:
                self._store.popitem(last=False)

    def delete(self, key):
        with self._lock:
            self._store.pop(key, None)

    def clear(self):
        with self._lock:
            self._store.clear()

    def stats(self):
        with self._lock:
            now = time.time()
            live = sum(1 for _, (_, e) in self._store.items() if e > now)
            return {
                "total_entries": len(self._store),
                "live_entries":  live,
                "expired":       len(self._store) - live,
                "max_size":      self.max_size,
                "ttl_seconds":   self.ttl,
            }

    # internals ──────────────────────────────────────────────────────────────
    def _cleanup_loop(self):
        while True:
            time.sleep(300)
            with self._lock:
                now = time.time()
                dead = [k for k, (_, e) in self._store.items() if e <= now]
                for k in dead:
                    del self._store[k]


# ─── Active Process Registry ────────────────────────────────────────────────
class ProcessRegistry:
    def __init__(self):
        self._procs = {}          # pid -> metadata dict
        self._lock  = threading.RLock()

    def register(self, pid: int, meta: dict):
        with self._lock:
            self._procs[pid] = {**meta, "pid": pid, "registered_at": time.time()}

    def update(self, pid: int, **kwargs):
        with self._lock:
            if pid in self._procs:
                self._procs[pid].update(kwargs)

    def remove(self, pid: int):
        with self._lock:
            return self._procs.pop(pid, None)

    def get(self, pid: int):
        with self._lock:
            return dict(self._procs.get(pid, {}))

    def all(self):
        with self._lock:
            return [dict(v) for v in self._procs.values()]


# ─── Error History (capped) ─────────────────────────────────────────────────
class ErrorHistory:
    def __init__(self, max_len: int = 1000):
        self._hist = []
        self._max  = max_len
        self._lock = threading.Lock()

    def record(self, error_type: str, detail: str, context: dict = None):
        with self._lock:
            entry = {
                "timestamp":  time.time(),
                "error_type": error_type,
                "detail":     detail,
                "context":    context or {},
            }
            self._hist.append(entry)
            if len(self._hist) > self._max:
                self._hist.pop(0)

    def recent(self, n: int = 50):
        with self._lock:
            return list(self._hist[-n:])

    def clear(self):
        with self._lock:
            self._hist.clear()


# ─── Singleton instances (imported by server.py) ────────────────────────────
cache    = TTLLRUCache(max_size=1000, ttl=3600)
procs    = ProcessRegistry()
err_hist = ErrorHistory(max_len=1000)
