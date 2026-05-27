from collections import defaultdict, deque
from time import monotonic


class InMemoryRateLimiter:
    def __init__(self, limit: int, window_seconds: int):
        self.limit = max(1, limit)
        self.window_seconds = max(1, window_seconds)
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def is_allowed(self, key: str, now: float | None = None) -> tuple[bool, int]:
        current_time = monotonic() if now is None else now
        cutoff = current_time - self.window_seconds
        hits = self._hits[key]

        while hits and hits[0] <= cutoff:
            hits.popleft()

        if len(hits) >= self.limit:
            retry_after = max(1, int(self.window_seconds - (current_time - hits[0])))
            return False, retry_after

        hits.append(current_time)
        return True, 0
