# NFR-001 Performance test runner - Test Plan cases PT-N01_01 .. PT-N01_08
# File: backend/perf/run_nfr01.py
#
# Requirement (SRS NFR-001): the portal responds to user actions within 2 seconds under normal load (95th percentile).
#
# What it does (default "managed" mode, nothing to set up by hand):
#   1. creates a throw-away SQLite database in a temp folder and seeds it with dummy data
#      (questions, mock tests, internships, N dummy students with some practice and mock-test history, one admin);
#   2. starts the portal (uvicorn) against that database, with the per-IP rate limiter switched off, because every
#      virtual user comes from 127.0.0.1 and the limiter (SEC-21) would answer 429 instead of measuring speed;
#   3. runs the eight cases with N concurrent virtual users, each sending requests back to back (no think time);
#   4. writes perf/results/nfr01_results.json (read by update_test_plan.py) and perf/results/nfr01_report.md.
#
# Run from backend/ with the portal's virtual environment active:
#       python -m perf.run_nfr01                      (defaults: 10 users, 30 requests per user per case)
#       python -m perf.run_nfr01 --users 20 --iterations 50
#
# Exit code 0 = every case passed, 1 = at least one case failed, 2 = setup problem.
import argparse
import json
import math
import os
import platform
import random
import socket
import statistics
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import httpx

BACKEND = Path(__file__).resolve().parent.parent
RESULTS = Path(__file__).resolve().parent / "results"
BUDGET_MS = 2000.0          # SRS NFR-001
REQUIRED_SHARE = 95.0       # 95% of requests inside the budget
CLIENT_TIMEOUT_S = 10.0     # a request slower than this counts as a timeout
PASSWORD = "Perf@12345"     # dummy password for the dummy students
ADMIN_EMAIL, ADMIN_PASSWORD = "perf.admin@example.com", "PerfAdmin@123"
MOCK_TITLE = "Full Aptitude Mock - 30 min"
MINIMAL_PDF = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 200 200]>>endobj\ntrailer<</Root 1 0 R>>\n%%EOF\n"

CASE_NAMES = {
    "PT-N01_01": "Login response time",
    "PT-N01_02": "Internship listings page load",
    "PT-N01_03": "Listings filter and search",
    "PT-N01_04": "Application submission",
    "PT-N01_05": "Start a mock test",
    "PT-N01_06": "Mock test submission",
    "PT-N01_07": "Analytics dashboard load",
    "PT-N01_08": "Overall 95th percentile under normal load",
}
FILTERS = [{"domain": "Backend"}, {"domain": "Data Analytics"}, {"q": "intern"}, {"location": "Remote"}, {"min_stipend": 15000, "open_only": "true"}]
DASHBOARD = ["/api/analytics/summary", "/api/analytics/trends", "/api/analytics/strengths-weaknesses", "/api/analytics/attempts"]


def nearest_rank(values, pct):
    ordered = sorted(values)
    return ordered[max(1, math.ceil(pct / 100 * len(ordered))) - 1] if ordered else 0.0


# ---------------------------------------------------------------- server handling
def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class ManagedServer:
    """Temp database + uvicorn subprocess. restart() gives a fresh process (and fresh server-side statistics)."""

    def __init__(self, users: int, iterations: int):
        self.tmp = tempfile.TemporaryDirectory(prefix="nfr01_")
        self.port = free_port()
        self.base_url = f"http://127.0.0.1:{self.port}"
        self.env = {
            **os.environ,
            "APP_ENV": "development",
            "DATABASE_URL": f"sqlite:///{Path(self.tmp.name, 'perf.db').as_posix()}",
            "SECRET_KEY": "nfr01-performance-run-key-not-a-real-secret",
            "RESUME_STORAGE_DIR": str(Path(self.tmp.name, "resumes")),
            "COOKIE_SECURE": "false",
            "RATE_LIMIT_ENABLED": "false",
        }
        self.proc = None
        self._seed(users, iterations)

    def _seed(self, users: int, iterations: int) -> None:
        code = (
            "import sys; sys.path.insert(0, r'%s');"
            "from perf.seed_nfr01 import seed; seed(%d, %d, %r, %r, %r)"
            % (BACKEND, users, iterations, PASSWORD, ADMIN_EMAIL, ADMIN_PASSWORD)
        )
        done = subprocess.run([sys.executable, "-c", code], cwd=BACKEND, env=self.env, capture_output=True, text=True)
        if done.returncode != 0:
            raise SystemExit(f"Seeding failed:\n{done.stdout}\n{done.stderr}")

    def start(self) -> None:
        self.proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(self.port), "--log-level", "warning"],
            cwd=BACKEND, env=self.env,
        )
        for _ in range(100):
            try:
                if httpx.get(self.base_url + "/api/health", timeout=1).status_code == 200:
                    return
            except httpx.HTTPError:
                time.sleep(0.2)
        self.stop()
        raise SystemExit("The portal did not start within 20 seconds.")

    def stop(self) -> None:
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.proc.kill()
        self.proc = None

    def restart(self) -> None:
        self.stop()
        self.start()

    def close(self) -> None:
        self.stop()
        try:
            self.tmp.cleanup()
        except OSError:
            pass


# ---------------------------------------------------------------- measuring
class Sample:
    __slots__ = ("label", "ms", "ok", "timeout", "detail")

    def __init__(self, label, ms, ok, timeout=False, detail=""):
        self.label, self.ms, self.ok, self.timeout, self.detail = label, ms, ok, timeout, detail


def timed(client: httpx.Client, label: str, method: str, url: str, expect: tuple, **kw) -> Sample:
    t0 = time.perf_counter()
    try:
        response = client.request(method, url, **kw)
    except httpx.TimeoutException:
        return Sample(label, CLIENT_TIMEOUT_S * 1000, False, True, "timeout")
    except httpx.HTTPError as exc:
        return Sample(label, (time.perf_counter() - t0) * 1000, False, False, type(exc).__name__)
    ms = (time.perf_counter() - t0) * 1000
    ok = response.status_code in expect
    return Sample(label, ms, ok, False, "" if ok else f"HTTP {response.status_code}")


def new_client(base_url: str) -> httpx.Client:
    return httpx.Client(base_url=base_url, timeout=CLIENT_TIMEOUT_S)


def login_client(base_url: str, email: str, password: str) -> httpx.Client:
    client = new_client(base_url)
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    if response.status_code != 200:
        raise SystemExit(f"Setup: login of {email} failed (HTTP {response.status_code}). Is the database seeded?")
    return client


def run_users(base_url: str, users: int, worker, login: bool = True) -> list[Sample]:
    """worker(user_index, client) -> list[Sample]; all virtual users start together."""
    clients = [login_client(base_url, f"perf.student{i}@example.com", PASSWORD) if login else new_client(base_url) for i in range(users)]
    barrier = threading.Barrier(users)

    def go(i):
        barrier.wait()
        try:
            return worker(i, clients[i])
        except Exception as exc:  # one broken virtual user must not abort the whole run
            return [Sample("virtual user crashed", 0.0, False, False, f"{type(exc).__name__}: {exc}"[:200])]

    try:
        with ThreadPoolExecutor(max_workers=users) as pool:
            return [s for chunk in pool.map(go, range(users)) for s in chunk]
    finally:
        for c in clients:
            c.close()


def summarise(samples: list[Sample]) -> dict:
    times = [s.ms for s in samples]
    within = sum(1 for s in samples if s.ok and s.ms <= BUDGET_MS)
    return {
        "requests": len(samples),
        "errors": sum(1 for s in samples if not s.ok),
        "timeouts": sum(1 for s in samples if s.timeout),
        "p50_ms": round(nearest_rank(times, 50), 1),
        "p95_ms": round(nearest_rank(times, 95), 1),
        "p99_ms": round(nearest_rank(times, 99), 1),
        "max_ms": round(max(times), 1) if times else 0.0,
        "mean_ms": round(statistics.fmean(times), 1) if times else 0.0,
        "within_budget_percent": round(100.0 * within / len(samples), 2) if samples else 0.0,
        "first_error": next((s.detail for s in samples if not s.ok), ""),
    }


def verdict(stats: dict) -> bool:
    return stats["requests"] > 0 and stats["errors"] == 0 and stats["timeouts"] == 0 and stats["within_budget_percent"] >= REQUIRED_SHARE and stats["p95_ms"] <= BUDGET_MS


def server_stats(base_url: str) -> list[dict]:
    """Per-route statistics recorded by the portal itself (GET /api/admin/performance)."""
    admin = login_client(base_url, ADMIN_EMAIL, ADMIN_PASSWORD)
    try:
        return admin.get("/api/admin/performance").json().get("routes", [])
    finally:
        admin.close()


def core_routes(rows):
    return [r for r in rows if r["route"] not in ("/api/health", "/api/admin/performance", "unmatched")]


# ---------------------------------------------------------------- workers
def first_mock_test_id(client: httpx.Client) -> int:
    items = client.get("/api/mock-tests").json()["items"]
    return next((t["id"] for t in items if t["title"] == MOCK_TITLE), items[0]["id"])


def start_attempt(client, test_id, label="start"):
    t0 = time.perf_counter()
    try:
        response = client.post(f"/api/mock-tests/{test_id}/attempts")
    except httpx.TimeoutException:
        return None, Sample(label, CLIENT_TIMEOUT_S * 1000, False, True, "timeout")
    except httpx.HTTPError as exc:  # e.g. the connection was dropped by the server
        return None, Sample(label, (time.perf_counter() - t0) * 1000, False, False, type(exc).__name__)
    ms = (time.perf_counter() - t0) * 1000
    ok = response.status_code in (200, 201)
    return (response.json() if ok else None), Sample(label, ms, ok, False, "" if ok else f"HTTP {response.status_code}")


def final_answers(state: dict) -> list[dict]:
    return [{"question_id": q["id"], "selected_option_id": q["options"][0]["id"]} for q in state["questions"] if q.get("options")]


def w_login(iterations):
    def work(i, _client):
        out = []
        with new_client(BASE) as client:
            for _ in range(iterations):
                out.append(timed(client, "POST /api/auth/login", "POST", "/api/auth/login", (200,), json={"email": f"perf.student{i}@example.com", "password": PASSWORD}))
        return out
    return work


def w_listings(iterations):
    return lambda i, c: [timed(c, "GET /api/internships", "GET", "/api/internships", (200,)) for _ in range(iterations)]


def w_filters(iterations):
    return lambda i, c: [timed(c, "GET /api/internships?filter", "GET", "/api/internships", (200,), params=FILTERS[(i + n) % len(FILTERS)]) for n in range(iterations)]


def w_apply(iterations):
    def work(i, c):
        ids = [x["id"] for x in c.get("/api/internships", params={"q": "Perf Intern", "page_size": 50, "open_only": "true"}).json()["items"]]
        out = []
        for n in range(iterations):
            files = {"resume": ("resume.pdf", MINIMAL_PDF, "application/pdf")}
            out.append(timed(c, "POST /api/applications", "POST", "/api/applications", (201,), data={"internship_id": str(ids[n % len(ids)]), "cover_note": "Keen to apply"}, files=files))
        return out
    return work


def w_start(iterations):
    def work(i, c):
        test_id, out = first_mock_test_id(c), []
        for _ in range(iterations):
            state, sample = start_attempt(c, test_id)
            out.append(sample)
            if state:  # clean up so the next start creates a new attempt (not timed)
                timed(c, "clean-up", "POST", f"/api/mock-attempts/{state['attempt_id']}/submit", (200, 409))
        return out
    return work


def w_submit(iterations):
    def work(i, c):
        test_id, out = first_mock_test_id(c), []
        for _ in range(iterations):
            state, _ = start_attempt(c, test_id)  # set-up, not timed
            if not state:
                out.append(Sample("POST submit", 0, False, False, "could not start an attempt"))
                continue
            out.append(timed(c, "POST /api/mock-attempts/{id}/submit", "POST", f"/api/mock-attempts/{state['attempt_id']}/submit", (200,), json={"answers": final_answers(state)}))
        return out
    return work


def w_dashboard(iterations):
    return lambda i, c: [timed(c, f"GET {p}", "GET", p, (200,)) for _ in range(iterations) for p in DASHBOARD]


def w_mixed(iterations):
    def work(i, c):
        rng, test_id, out = random.Random(1000 + i), first_mock_test_id(c), []
        for n in range(iterations):
            out.append(timed(c, "GET /api/internships", "GET", "/api/internships", (200,)))
            out.append(timed(c, "GET /api/internships?filter", "GET", "/api/internships", (200,), params=rng.choice(FILTERS)))
            out.append(timed(c, "GET /api/mock-tests", "GET", "/api/mock-tests", (200,)))
            out.append(timed(c, "GET /api/practice/history", "GET", "/api/practice/history", (200,)))
            out.append(timed(c, "GET /api/mock-results", "GET", "/api/mock-results", (200,)))
            for p in DASHBOARD:
                out.append(timed(c, f"GET {p}", "GET", p, (200,)))
            if n % 3 == 0:
                state, sample = start_attempt(c, test_id)
                out.append(sample)
                if state:
                    out.append(timed(c, "POST submit", "POST", f"/api/mock-attempts/{state['attempt_id']}/submit", (200,), json={"answers": final_answers(state)}))
            if n % 5 == 0:
                with new_client(BASE) as fresh:
                    out.append(timed(fresh, "POST /api/auth/login", "POST", "/api/auth/login", (200,), json={"email": f"perf.student{i}@example.com", "password": PASSWORD}))
        return out
    return work


# ---------------------------------------------------------------- cases
def describe(stats: dict, users: int, extra: str = "") -> str:
    base = (f"{stats['requests']} requests from {users} concurrent users: median {stats['p50_ms']:.0f} ms, 95th percentile {stats['p95_ms']:.0f} ms, "
            f"slowest {stats['max_ms']:.0f} ms; {stats['within_budget_percent']:.1f}% within 2 s; {stats['errors']} errors, {stats['timeouts']} timeouts.")
    if stats["first_error"]:
        base += f" First error: {stats['first_error']}."
    return base + (" " + extra if extra else "")


def route_note(base_url: str, wanted: list[str]) -> str:
    try:
        rows = {(r["method"], r["route"]): r for r in server_stats(base_url)}
    except Exception as exc:  # statistics are supporting evidence only
        return f"(server-side statistics unavailable: {exc})"
    parts = []
    for method, route in wanted:
        r = rows.get((method, route))
        if r:
            parts.append(f"{method} {route} p95 {r['p95_ms']:.0f} ms over {r['count']} requests")
    return "Server-side statistics: " + "; ".join(parts) + "." if parts else ""


def main() -> int:
    global BASE
    ap = argparse.ArgumentParser(description="NFR-001 performance run (Test Plan cases PT-N01_01 .. 08)")
    ap.add_argument("--users", type=int, default=10, help="concurrent virtual users that define 'normal load' (default 10)")
    ap.add_argument("--iterations", type=int, default=30, help="requests (or rounds) per user per case (default 30)")
    args = ap.parse_args()
    users, iters = args.users, args.iterations
    if iters > 40:
        print("Note: --iterations above 40 would reuse internships in the application case; capped at 40 for PT-N01_04.")

    server = ManagedServer(users, min(iters, 40))
    mode = "managed"
    BASE = server.base_url
    cases: dict[str, dict] = {}
    started = datetime.now(timezone.utc)
    try:
        plan = [
            ("PT-N01_01", lambda: run_users(BASE, users, w_login(iters), login=False), [("POST", "/api/auth/login")]),
            ("PT-N01_02", lambda: run_users(BASE, users, w_listings(iters)), [("GET", "/api/internships")]),
            ("PT-N01_03", lambda: run_users(BASE, users, w_filters(iters)), [("GET", "/api/internships")]),
            ("PT-N01_04", lambda: run_users(BASE, users, w_apply(min(iters, 40))), [("POST", "/api/applications")]),
            ("PT-N01_05", lambda: run_users(BASE, users, w_start(iters)), [("POST", "/api/mock-tests/{test_id}/attempts")]),
            ("PT-N01_06", lambda: run_users(BASE, users, w_submit(iters)), [("POST", "/api/mock-attempts/{attempt_id}/submit")]),
            ("PT-N01_07", lambda: run_users(BASE, users, w_dashboard(iters)), [("GET", p) for p in DASHBOARD]),
        ]
        for case_id, run, routes in plan:
            server.restart()  # fresh process: the server-side statistics then belong to this case only
            samples = run()
            stats = summarise(samples)
            stats["server_note"] = route_note(BASE, routes)
            stats["result"] = "Pass" if verdict(stats) else "Fail"
            stats["actual"] = describe(stats, users, stats["server_note"])
            cases[case_id] = stats
            print(f"{case_id}  {CASE_NAMES[case_id]:34} p95 {stats['p95_ms']:>7.0f} ms  errors {stats['errors']:>3}  -> {stats['result']}")

        server.restart()
        samples = run_users(BASE, users, w_mixed(max(10, iters // 2)))
        stats = summarise(samples)
        per_label = {}
        for s in samples:
            per_label.setdefault(s.label, []).append(s)
        stats["per_request_p95_ms"] = {k: round(nearest_rank([x.ms for x in v], 95), 1) for k, v in sorted(per_label.items())}
        try:
            rows = core_routes(server_stats(BASE))
        except Exception as exc:
            rows = []
            stats["errors"] += 1
            stats["first_error"] = stats["first_error"] or f"admin statistics unavailable: {exc}"
        worst = max(rows, key=lambda r: r["p95_ms"]) if rows else None
        stats["server_routes"] = rows
        stats["server_worst_route"] = f"{worst['method']} {worst['route']} p95 {worst['p95_ms']:.0f} ms" if worst else "n/a"
        stats["server_slow_requests"] = sum(r["slow"] for r in rows)
        server_ok = bool(rows) and worst["p95_ms"] <= BUDGET_MS and stats["server_slow_requests"] == 0
        stats["result"] = "Pass" if verdict(stats) and server_ok else "Fail"
        stats["actual"] = describe(stats, users, f"Admin performance statistics: {len(rows)} core routes, slowest {stats['server_worst_route']}, {stats['server_slow_requests']} requests over 2 s.")
        cases["PT-N01_08"] = stats
        print(f"PT-N01_08  {CASE_NAMES['PT-N01_08']:34} p95 {stats['p95_ms']:>7.0f} ms  errors {stats['errors']:>3}  -> {stats['result']}")
    finally:
        server.close()

    for cid, c in cases.items():
        c["name"] = CASE_NAMES[cid]
    finished = datetime.now(timezone.utc)
    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=BACKEND, capture_output=True, text=True, timeout=10).stdout.strip() or "not a git checkout"
    except Exception:
        commit = "not a git checkout"
    report = {
        "requirement": "NFR-001",
        "run": {
            "started_utc": started.isoformat(timespec="seconds"), "finished_utc": finished.isoformat(timespec="seconds"),
            "date": started.astimezone().strftime("%d %B %Y").lstrip("0"), "build": commit, "mode": mode,
            "python": platform.python_version(), "os": f"{platform.system()} {platform.release()}",
            "normal_load": f"{users} concurrent users, requests sent back to back (no think time), {iters} requests per user per case",
            "users": users, "iterations": iters, "budget_ms": BUDGET_MS, "required_share_percent": REQUIRED_SHARE,
            "database": "temporary SQLite database seeded with dummy data",
            "rate_limiter": "off for the run (all virtual users share one IP)",
        },
        "cases": cases,
        "overall": "Pass" if all(c["result"] == "Pass" for c in cases.values()) else "Fail",
    }
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "nfr01_results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    write_markdown(report)
    print(f"\nNFR-001 overall: {report['overall']}   (results: {RESULTS / 'nfr01_results.json'})")
    return 0 if report["overall"] == "Pass" else 1


def write_markdown(report: dict) -> None:
    run = report["run"]
    lines = [
        "# NFR-001 performance run", "",
        f"- Date: {run['date']}   Build: {run['build']}   Mode: {run['mode']}",
        f"- Environment: Python {run['python']}, {run['os']}",
        f"- Normal load used: {run['normal_load']}", f"- Pass rule: at least {run['required_share_percent']:.0f}% of requests within {run['budget_ms']:.0f} ms, no errors, no timeouts", "",
        "| Case | Name | Requests | p50 ms | p95 ms | Max ms | Within 2 s | Errors | Result |", "|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for cid, c in report["cases"].items():
        lines.append(f"| {cid} | {c['name']} | {c['requests']} | {c['p50_ms']:.0f} | {c['p95_ms']:.0f} | {c['max_ms']:.0f} | {c['within_budget_percent']:.1f}% | {c['errors']} | {c['result']} |")
    lines += ["", f"Overall: **{report['overall']}**", ""]
    (RESULTS / "nfr01_report.md").write_text("\n".join(lines), encoding="utf-8")


BASE = ""

if __name__ == "__main__":
    sys.exit(main())
