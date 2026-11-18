#!/usr/bin/env sh
# NFR-001 performance run + Test Plan update (Linux/macOS). Run from backend/ with the virtual environment active:
#     sh perf/run_nfr01.sh path/to/Test_Plan_Internship_Placement_Prep_Portal.docx
# Optional load settings:  NFR01_ARGS="--users 20 --iterations 50" sh perf/run_nfr01.sh plan.docx
[ -z "$1" ] && { echo "Usage: sh perf/run_nfr01.sh path/to/Test_Plan.docx"; exit 2; }
python -m perf.run_nfr01 $NFR01_ARGS
code=$?
[ "$code" -ge 2 ] && exit "$code"
python -m perf.update_test_plan "$1"
exit "$code"
