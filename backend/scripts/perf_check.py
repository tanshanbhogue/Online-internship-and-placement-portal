import argparse
import math
import sys
import time

import httpx

ENDPOINTS = [
    "/api/internships",
    "/api/question-bank/categories",
    "/api/practice/history",
    "/api/mock-tests",
    "/api/mock-results",
    "/api/analytics/summary",
    "/api/analytics/trends",
    "/api/analytics/strengths-weaknesses",
    "/api/analytics/attempts",
]


def nearest_rank(values: list[float], pct: float) -> float:
    ordered = sorted(values)
    return ordered[max(1, math.ceil(pct / 100 * len(ordered))) - 1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--runs", type=int, default=30)
    parser.add_argument("--budget-ms", type=float, default=2000.0)
    args = parser.parse_args()

    failed = False
    with httpx.Client(base_url=args.base_url, timeout=15) as client:
        started = time.perf_counter()
        login = client.post("/api/auth/login", json={"email": args.email, "password": args.password})
        login_ms = (time.perf_counter() - started) * 1000
        if login.status_code != 200:
            print(f"Login failed (HTTP {login.status_code}).")
            return 2
        print(f"{'endpoint':42} {'runs':>5} {'p50 ms':>8} {'p95 ms':>8} {'max ms':>8}  result")
        print(f"{'POST /api/auth/login (once)':42} {1:>5} {login_ms:>8.0f} {login_ms:>8.0f} {login_ms:>8.0f}  {'ok' if login_ms <= args.budget_ms else 'SLOW'}")
        for path in ENDPOINTS:
            times = []
            for _ in range(args.runs):
                t0 = time.perf_counter()
                response = client.get(path)
                times.append((time.perf_counter() - t0) * 1000)
                if response.status_code != 200:
                    print(f"{path}: HTTP {response.status_code}")
                    failed = True
                    break
            else:
                p95 = nearest_rank(times, 95)
                ok = p95 <= args.budget_ms
                failed = failed or not ok
                print(f"{'GET ' + path:42} {len(times):>5} {nearest_rank(times, 50):>8.0f} {p95:>8.0f} {max(times):>8.0f}  {'ok' if ok else 'SLOW'}")
    print("PASS: every p95 within budget" if not failed else "FAIL")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
