import logging
import math
import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import FastAPI
from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger("app.performance")
SLOW_MS = 2000.0
KEEP = 500


def percentile(sorted_values: list[float], pct: float) -> float:
    """Nearest-rank percentile of an already sorted list."""
    if not sorted_values:
        return 0.0
    rank = max(1, math.ceil(pct / 100 * len(sorted_values)))
    return sorted_values[rank - 1]


class RouteStats:
    def __init__(self) -> None:
        self._samples: dict[tuple[str, str], deque[float]] = defaultdict(lambda: deque(maxlen=KEEP))
        self._slow: dict[tuple[str, str], int] = defaultdict(int)
        self._lock = Lock()

    def record(self, method: str, route: str, ms: float) -> None:
        with self._lock:
            self._samples[(method, route)].append(ms)
            if ms > SLOW_MS:
                self._slow[(method, route)] += 1

    def reset(self) -> None:
        with self._lock:
            self._samples.clear()
            self._slow.clear()

    def snapshot(self) -> dict:
        with self._lock:
            rows = []
            for (method, route), samples in self._samples.items():
                ordered = sorted(samples)
                rows.append(
                    {
                        "method": method,
                        "route": route,
                        "count": len(ordered),
                        "p50_ms": round(percentile(ordered, 50), 1),
                        "p95_ms": round(percentile(ordered, 95), 1),
                        "max_ms": round(ordered[-1], 1),
                        "slow": self._slow[(method, route)],
                    }
                )
        rows.sort(key=lambda r: r["p95_ms"], reverse=True)
        return {"slow_threshold_ms": SLOW_MS, "routes": rows}


STATS = RouteStats()


class TimingMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        started = time.perf_counter()
        state = {"ms": None}

        async def send_with_timing(message: Message) -> None:
            if message["type"] == "http.response.start":
                state["ms"] = (time.perf_counter() - started) * 1000
                MutableHeaders(scope=message)["X-Response-Time-Ms"] = f"{state['ms']:.1f}"
            await send(message)

        try:
            await self.app(scope, receive, send_with_timing)
        finally:
            if state["ms"] is not None:
                route = getattr(scope.get("route"), "path", None) or "unmatched"  # template, so ids never become labels
                STATS.record(scope["method"], route, state["ms"])
                if state["ms"] > SLOW_MS:
                    logger.warning("slow_request method=%s route=%s ms=%.0f", scope["method"], route, state["ms"])


def install(app: FastAPI) -> None:
    app.add_middleware(TimingMiddleware)
