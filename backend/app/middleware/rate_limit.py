import os
import re
import time
from collections import deque
from dataclasses import dataclass
from threading import Lock

from fastapi import FastAPI
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send


@dataclass(frozen=True)
class Rule:
    method: str
    pattern: re.Pattern
    limit: int
    window: int  # seconds


def _env_limit(name: str, default_limit: int, default_window: int) -> tuple[int, int]:
    raw = os.environ.get(f"RATE_LIMIT_{name.upper()}", "")
    try:
        limit, window = raw.split("/")
        return max(1, int(limit)), max(1, int(window))
    except ValueError:
        return default_limit, default_window


def _rule(name, method, regex, limit, window) -> Rule:
    limit, window = _env_limit(name, limit, window)
    return Rule(method, re.compile(regex), limit, window)


RULES: dict[str, Rule] = {
    "login": _rule("login", "POST", r"^/api/auth/login$", 20, 60),
    "apply": _rule("apply", "POST", r"^/api/applications$", 20, 60),
    "submit_test": _rule("submit_test", "POST", r"^/api/mock-attempts/\d+/(submit|auto-submit)$", 30, 60),
    "search": _rule("search", "GET", r"^/api/internships$", 120, 60),
}


class SlidingWindowLimiter:
    def __init__(self) -> None:
        self._hits: dict[tuple[str, str], deque[float]] = {}
        self._lock = Lock()
        self.force = False
        self.clock = time.monotonic  # tests replace it

    def active(self) -> bool:
        if os.environ.get("RATE_LIMIT_ENABLED", "true").lower() == "false":
            return False
        return self.force or "PYTEST_CURRENT_TEST" not in os.environ

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()

    def check(self, client: str, name: str, rule: Rule) -> int:
        """Return 0 when the request is allowed, else the seconds to wait."""
        now = self.clock()
        key = (client, name)
        with self._lock:
            hits = self._hits.setdefault(key, deque())
            while hits and now - hits[0] >= rule.window:
                hits.popleft()
            if len(hits) >= rule.limit:
                return max(1, int(rule.window - (now - hits[0])) + 1)
            hits.append(now)
            if len(self._hits) > 10000:  # keep memory bounded: drop idle keys
                for k in [k for k, v in self._hits.items() if not v or now - v[-1] >= 3600]:
                    self._hits.pop(k, None)
            return 0


limiter = SlidingWindowLimiter()


class RateLimitMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http" and limiter.active():
            method, path = scope["method"], scope["path"]
            for name, rule in RULES.items():
                if rule.method == method and rule.pattern.match(path):
                    client = scope["client"][0] if scope.get("client") else "unknown"  # direct peer, never a forwarded header
                    wait = limiter.check(client, name, rule)
                    if wait:
                        response = JSONResponse(
                            status_code=429,
                            content={"detail": "Too many requests. Try again shortly.", "code": "rate_limited"},
                            headers={"Retry-After": str(wait)},
                        )
                        await response(scope, receive, send)
                        return
                    break
        await self.app(scope, receive, send)


def install(app: FastAPI) -> None:
    app.add_middleware(RateLimitMiddleware)
