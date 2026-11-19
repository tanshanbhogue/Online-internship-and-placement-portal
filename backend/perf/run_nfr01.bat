@echo off
REM NFR-001 performance run + Test Plan update (Windows).  Run from backend\ with the virtual environment active:
REM     perf\run_nfr01.bat "C:\path\to\Test_Plan_Internship_Placement_Prep_Portal.docx"
REM Optional load settings:  set NFR01_ARGS=--users 20 --iterations 50
if "%~1"=="" (
  echo Usage: perf\run_nfr01.bat "path\to\Test_Plan.docx"
  exit /b 2
)
python -m perf.run_nfr01 %NFR01_ARGS%
set RUN_CODE=%ERRORLEVEL%
if %RUN_CODE% GEQ 2 exit /b %RUN_CODE%
REM a failed case (exit code 1) is still written into the plan, so the failure is recorded
python -m perf.update_test_plan "%~1"
exit /b %RUN_CODE%
