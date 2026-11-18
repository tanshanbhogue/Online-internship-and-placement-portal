# Fills the NFR-001 results into the Software Test Plan (.docx)
# File: backend/perf/update_test_plan.py
#
# Reads perf/results/nfr01_results.json (written by run_nfr01.py) and writes a NEW copy of the Test Plan; the original is
# never changed. Everything is derived from the results and from the document itself, so running it again is safe.
#
# Run from backend/ (needs:  pip install python-docx):
#     python -m perf.update_test_plan "path/to/Test_Plan_Internship_Placement_Prep_Portal.docx"
#     python -m perf.update_test_plan plan.docx --results perf/results/nfr01_results.json --out plan_updated.docx
#
# What is updated (NFR-001 only; nothing of FR-001..FR-005, NFR-002 or NFR-003 is touched except the totals):
#   - Appendix A: Actual Result and Test Result of PT-N01_01..08, and the "normal load" wording in their test data;
#   - the failed-case line of NFR-001 and a new "Execution record" line (date, build, environment, load, pass rule);
#   - Appendix B evidence rows of PT-N01_01..08;
#   - section 13 outcome of NFR-001 (Pass only if all 8 cases pass);
#   - section 14 counts and shares, and the "Current record" paragraph in section 1, recounted from the case tables;
#   - the sentences that said NFR-001 was "planned, not yet executed", and the "normal load" risk row.
import argparse
import copy
import json
import re
import sys
from pathlib import Path

from docx import Document

HERE = Path(__file__).resolve().parent
NFR = "NFR-001"
PREFIX = "PT-N01_"
EXEC_PARAGRAPH = "Execution record — NFR-001:"


# ------------------------------------------------------------------ helpers
def set_par(paragraph, text: str) -> None:
    runs = paragraph.runs
    if runs:
        runs[0].text = text
        for extra in runs[1:]:
            extra._r.getparent().remove(extra._r)
    else:
        paragraph.add_run(text)


def set_cell(cell, text: str, style_from=None) -> None:
    """Replace the text of a table cell, keeping the 8 pt cell font (copied from a neighbouring cell)."""
    paragraph = cell.paragraphs[0]
    template = None
    source = style_from if style_from is not None else cell
    if source.paragraphs[0].runs:
        template = source.paragraphs[0].runs[0]._r.find("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rPr")
    for run in list(paragraph.runs):
        run._r.getparent().remove(run._r)
    run = paragraph.add_run(text)
    if template is not None:
        old = run._r.find("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rPr")
        if old is not None:
            run._r.remove(old)
        run._r.insert(0, copy.deepcopy(template))


def case_tables(doc):
    """The Appendix A tables: nine columns, first header cell 'Test Case ID'."""
    return [t for t in doc.tables if len(t.columns) == 9 and t.rows[0].cells[0].text.strip() == "Test Case ID"]


def all_case_rows(doc):
    for table in case_tables(doc):
        for row in table.rows[1:]:
            cells = row.cells
            if cells[0].text.strip():
                yield cells


def requirement_of(case_id: str) -> str:
    m = re.match(r"^[A-Z]{2}-(N?)(\d\d)_", case_id)
    if not m:
        return "?"
    return f"{'NFR' if m.group(1) else 'FR'}-0{m.group(2)}"


def outcome(results: list[str]) -> str:
    if any(r == "Fail" for r in results):
        return "Fail"
    if any(r == "Partial" for r in results):
        return "Partial"
    if results and all(r == "Pass" for r in results):
        return "Pass"
    if results and all(r in ("", "Not Run") for r in results):
        return "Not Run"
    return "Partial"


def fmt_load(run: dict) -> str:
    return f"{run['users']} concurrent users, {run['iterations']} requests each, sent back to back"


# ------------------------------------------------------------------ main update
def update(doc, report: dict) -> dict:
    run, cases = report["run"], report["cases"]
    when, load = run["date"], fmt_load(run)
    overall = outcome([c["result"] for c in cases.values()])
    failed_ids = [cid for cid, c in cases.items() if c["result"] != "Pass"]

    # 1. Appendix A rows
    touched = 0
    for cells in all_case_rows(doc):
        cid = cells[0].text.strip()
        if cid not in cases:
            continue
        c = cases[cid]
        set_cell(cells[7], c["actual"], style_from=cells[6])
        set_cell(cells[8], c["result"], style_from=cells[6])
        pre = cells[3].text.replace("normal-load level agreed by the team", f"normal load defined as {run['users']} concurrent users")
        set_cell(cells[3], pre, style_from=cells[6])
        data = cells[5].text
        if "to be fixed" in data:
            data = re.sub(r"normal-load level to be fixed( by the team)?", f"normal load = {load}", data, flags=re.I)
            set_cell(cells[5], data, style_from=cells[6])
        touched += 1
    if touched != 8:
        raise SystemExit(f"Expected to find 8 PT-N01 rows in Appendix A, found {touched}. Is this the right Test Plan?")

    # 2. failed-case line + execution record (a new paragraph right after it)
    paragraphs = doc.paragraphs
    for p in paragraphs:
        if p.text.startswith(EXEC_PARAGRAPH):
            p._p.getparent().remove(p._p)
    failed_par = next(p for p in doc.paragraphs if p.text.startswith("Failed test cases — NFR-001"))
    if failed_ids:
        set_par(failed_par, "Failed test cases — NFR-001: " + "; ".join(failed_ids) + " (Fail in the table above; the Actual Result column gives the measured figures).")
    else:
        set_par(failed_par, "Failed test cases — NFR-001: none.")
    record = copy.deepcopy(failed_par._p)
    failed_par._p.addnext(record)
    from docx.text.paragraph import Paragraph
    set_par(Paragraph(record, failed_par._parent),
            f"{EXEC_PARAGRAPH} automated run of {when} (build {run['build']}; Python {run['python']}, {run['os']}). Normal load: {load}. "
            f"{run['database'][0].upper() + run['database'][1:]}; rate limiter {run['rate_limiter']}. Pass rule: at least {run['required_share_percent']:.0f}% of requests "
            f"within {run['budget_ms'] / 1000:g} s with no errors or timeouts. Source: backend/perf/run_nfr01.py, results in perf/results/nfr01_results.json.")

    # 3. Appendix B evidence
    evidence_table = next(t for t in doc.tables if [c.text for c in t.rows[0].cells] == ["Test Case ID", "Automated evidence", "Manual"])
    for row in evidence_table.rows[1:]:
        cid = row.cells[0].text.strip()
        if cid in cases:
            extra = "; related instrumentation tests: test_response_time (timing header, admin performance endpoint)" if cid.endswith("08") else ""
            set_cell(row.cells[1], f"perf/run_nfr01.py, case {cid}: {cases[cid]['result']} in the run of {when} (perf/results/nfr01_results.json){extra}", style_from=row.cells[1])
            set_cell(row.cells[2], f"Automated run {when}", style_from=row.cells[2])

    # 4. section 13 traceability
    for table in doc.tables:
        if [c.text for c in table.rows[0].cells] == ["Req ID", "Mapped case IDs", "Outcome"]:
            for row in table.rows[1:]:
                if row.cells[0].text.strip() == NFR:
                    set_cell(row.cells[2], overall, style_from=row.cells[2])

    # 5. recount everything from the case tables
    results = [(cells[0].text.strip(), cells[8].text.strip() or "Not Run") for cells in all_case_rows(doc)]
    counts = {k: sum(1 for _, r in results if r == k) for k in ("Pass", "Partial", "Fail", "Not Run")}
    total = len(results)
    not_run_reqs = sorted({requirement_of(cid) for cid, r in results if r == "Not Run"})
    nfr_done = sorted({requirement_of(cid) for cid, r in results if requirement_of(cid).startswith("NFR") and r != "Not Run"})

    for table in doc.tables:
        if [c.text for c in table.rows[0].cells] == ["Outcome", "Count", "Share", "Interpretation"]:
            for row in table.rows[1:]:
                name = row.cells[0].text.strip()
                if name not in counts:
                    continue
                set_cell(row.cells[1], str(counts[name]), style_from=row.cells[1])
                set_cell(row.cells[2], f"{100 * counts[name] / total:.1f}%", style_from=row.cells[2])
                text = row.cells[3].text
                if name == "Pass":
                    text = "Functional cases passed (automated and manual)" + (f"; non-functional cases passed: {', '.join(nfr_done)} (automated)" if nfr_done else "") + "."
                elif name == "Fail":
                    base = re.split(r"\s*NFR-\d{3}[:\s]", text)[0].rstrip()
                    nfr_fail = [c for c in failed_ids if cases[c]["result"] == "Fail"]
                    text = base + (f" NFR-001: {', '.join(nfr_fail)} outside the 2 s limit." if nfr_fail else "")
                elif name == "Not Run":
                    text = (f"Non-functional cases of {' and '.join(not_run_reqs)}; testing not yet done." if not_run_reqs else "None.")
                set_cell(row.cells[3], text, style_from=row.cells[3])

    # 6. narrative sentences
    status = f"executed {when}: {overall}"
    for p in doc.paragraphs:
        t = p.text
        if t.startswith("Current record:"):
            tail = t[t.index("The automated pytest run"):] if "The automated pytest run" in t else ""
            tail = re.sub(r"The NFR-001 automated performance run of .*?\(Appendix A\)\. ", "", tail)
            nr = (f"The {counts['Not Run']} Not Run cases are the cases of {' and '.join(not_run_reqs)}; that testing has not been done, so their result fields are left empty. " if counts["Not Run"] else "Every planned case has a recorded result. ")
            nfr_sentence = f"The NFR-001 automated performance run of {when} ({load}) gave an overall result of {overall} (Appendix A). "
            tail = tail.replace("Manual browser testing", nfr_sentence + "Manual browser testing") if "Manual browser testing" in tail else tail + " " + nfr_sentence
            set_par(p, f"Current record: The plan contains {total} cases: {counts['Pass']} Pass, {counts['Partial']} Partial, {counts['Fail']} Fail and {counts['Not Run']} Not Run. " + nr + tail)
        elif t.startswith("- Non-functional behaviour:"):
            others = [r for r in ("NFR-002", "NFR-003") if r in not_run_reqs]
            set_par(p, f"- Non-functional behaviour: response time, security and browser/device compatibility (NFR-001 {status}" + (f"; {' and '.join(others)} planned, not yet executed)" if others else ")"))
        elif t.startswith("- NFR-001 — Performance:"):
            set_par(p, re.sub(r"(Planned; not yet executed\.|Executed .*)$", f"Executed {when}: {overall}.", t))
        elif t.startswith("Non-functional testing (NFR-001 to NFR-003)") or t.startswith("NFR-001 (performance) was executed"):
            others = [r for r in ("NFR-002", "NFR-003") if r in not_run_reqs]
            set_par(p, f"NFR-001 (performance) was executed on {when} by the automated run in backend/perf; its results are recorded in Appendix A." + (f" {' and '.join(others)} are planned in Appendix A but not yet executed, so their result fields are empty." if others else ""))
        elif t.startswith("- NFR cases need an agreed normal-load level") or t.startswith("- NFR-001 normal load is defined"):
            set_par(p, f"- NFR-001 normal load is defined as {load}; the team should confirm this level. Other NFR cases need real or emulated browsers and viewports (NFR-003) and a deployed HTTPS environment (NFR-002).")
        elif t.startswith("The following tables give the test steps"):
            set_par(p, "The following tables give the test steps, test data, expected and actual results and recorded outcomes. Failed cases are shown in a separate table below the main table of their requirement. For NFR-001 the Actual Result and Test Result fields come from the automated performance run; for the other non-functional requirements they stay empty until that testing is done.")
        elif t.startswith("Automated evidence refers to tests in backend/tests/"):
            set_par(p, "Automated evidence refers to tests in backend/tests/ from the run of 10 November 2026. Manual results for functional cases come from the team's browser execution. The evidence for NFR-001 is the automated performance run (backend/perf/run_nfr01.py). For the other planned non-functional cases, the related automated tests shown are not recorded as NFR results.")

    # 7. risk row about "normal load"
    for table in doc.tables:
        if [c.text for c in table.rows[0].cells] == ["Risk", "Mitigation"]:
            for row in table.rows[1:]:
                if "normal load" in row.cells[0].text and "NFR-001" in row.cells[0].text:
                    set_cell(row.cells[1], f"Normal load was set to {load} for the NFR-001 run; the team confirms or changes this figure (run_nfr01.py --users/--iterations) and re-runs.", style_from=row.cells[1])
    return {"counts": counts, "total": total, "overall": overall}


def main() -> int:
    ap = argparse.ArgumentParser(description="Write NFR-001 results into the Test Plan (.docx)")
    ap.add_argument("docx", help="the Test Plan to read (it is not modified)")
    ap.add_argument("--results", default=str(HERE / "results" / "nfr01_results.json"))
    ap.add_argument("--out", help="output file (default: <name>_NFR01_updated.docx next to the input)")
    args = ap.parse_args()

    src = Path(args.docx)
    out = Path(args.out) if args.out else src.with_name(src.stem + "_NFR01_updated.docx")
    report = json.loads(Path(args.results).read_text(encoding="utf-8"))
    if report.get("requirement") != NFR or len(report.get("cases", {})) != 8:
        print("The results file is not a complete NFR-001 run (8 cases expected). Run perf.run_nfr01 first.")
        return 2
    doc = Document(str(src))
    summary = update(doc, report)
    doc.save(str(out))
    c = summary["counts"]
    print(f"Written: {out}\nNFR-001 overall: {summary['overall']}.  Plan now: {c['Pass']} Pass, {c['Partial']} Partial, {c['Fail']} Fail, {c['Not Run']} Not Run (of {summary['total']}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
