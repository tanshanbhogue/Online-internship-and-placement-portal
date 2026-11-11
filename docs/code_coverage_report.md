# Code Coverage Report

- Run date: 2026-11-10 23:02:43 India Standard Time
- Measurement: coverage.py through pytest-cov
- Statements: 2537
- Covered statements: 2398
- Missing statements: 139
- Statement coverage: **92.95%**

## Coverage by file

| File | Statements | Covered | Missing | Coverage |
|---|---:|---:|---:|---:|
| `app\__init__.py` | 0 | 0 | 0 | 100.00% |
| `app\core\__init__.py` | 0 | 0 | 0 | 100.00% |
| `app\core\config.py` | 45 | 40 | 5 | 82.35% |
| `app\core\database.py` | 21 | 12 | 9 | 56.52% |
| `app\core\dependencies.py` | 47 | 41 | 6 | 86.44% |
| `app\core\errors.py` | 124 | 112 | 12 | 88.31% |
| `app\core\log_redaction.py` | 52 | 39 | 13 | 68.57% |
| `app\core\security.py` | 45 | 42 | 3 | 90.77% |
| `app\core\tokens.py` | 38 | 33 | 5 | 83.33% |
| `app\db\__init__.py` | 0 | 0 | 0 | 100.00% |
| `app\db\base.py` | 26 | 24 | 2 | 88.24% |
| `app\db\models_registry.py` | 9 | 9 | 0 | 100.00% |
| `app\main.py` | 69 | 54 | 15 | 72.94% |
| `app\middleware\__init__.py` | 0 | 0 | 0 | 100.00% |
| `app\middleware\compression.py` | 5 | 5 | 0 | 100.00% |
| `app\middleware\rate_limit.py` | 72 | 69 | 3 | 93.33% |
| `app\middleware\request_timing.py` | 62 | 59 | 3 | 92.11% |
| `app\modules\__init__.py` | 0 | 0 | 0 | 100.00% |
| `app\modules\analytics\__init__.py` | 0 | 0 | 0 | 100.00% |
| `app\modules\analytics\insights.py` | 48 | 48 | 0 | 100.00% |
| `app\modules\analytics\insights_router.py` | 26 | 26 | 0 | 100.00% |
| `app\modules\analytics\insights_schemas.py` | 37 | 37 | 0 | 100.00% |
| `app\modules\analytics\router.py` | 17 | 17 | 0 | 100.00% |
| `app\modules\analytics\schemas.py` | 34 | 34 | 0 | 100.00% |
| `app\modules\analytics\service.py` | 49 | 49 | 0 | 100.00% |
| `app\modules\analytics\trends.py` | 25 | 25 | 0 | 100.00% |
| `app\modules\application\__init__.py` | 0 | 0 | 0 | 100.00% |
| `app\modules\application\duplicate_check.py` | 18 | 18 | 0 | 100.00% |
| `app\modules\application\duplicate_router.py` | 16 | 16 | 0 | 100.00% |
| `app\modules\application\duplicate_schemas.py` | 7 | 7 | 0 | 100.00% |
| `app\modules\application\models.py` | 27 | 27 | 0 | 100.00% |
| `app\modules\application\resume_storage.py` | 83 | 69 | 14 | 80.37% |
| `app\modules\application\router.py` | 14 | 14 | 0 | 100.00% |
| `app\modules\application\schemas.py` | 22 | 22 | 0 | 100.00% |
| `app\modules\application\service.py` | 34 | 30 | 4 | 89.47% |
| `app\modules\auth\__init__.py` | 0 | 0 | 0 | 100.00% |
| `app\modules\auth\login_router.py` | 30 | 28 | 2 | 90.62% |
| `app\modules\auth\login_schemas.py` | 13 | 13 | 0 | 100.00% |
| `app\modules\auth\login_service.py` | 39 | 36 | 3 | 91.11% |
| `app\modules\auth\login_throttle.py` | 20 | 20 | 0 | 100.00% |
| `app\modules\auth\models.py` | 19 | 19 | 0 | 100.00% |
| `app\modules\auth\register_router.py` | 9 | 9 | 0 | 100.00% |
| `app\modules\auth\register_schemas.py` | 30 | 30 | 0 | 100.00% |
| `app\modules\auth\register_service.py` | 23 | 20 | 3 | 88.89% |
| `app\modules\auth\session_models.py` | 23 | 23 | 0 | 100.00% |
| `app\modules\internship\__init__.py` | 0 | 0 | 0 | 100.00% |
| `app\modules\internship\models.py` | 24 | 24 | 0 | 100.00% |
| `app\modules\internship\router.py` | 22 | 22 | 0 | 100.00% |
| `app\modules\internship\schemas.py` | 31 | 31 | 0 | 100.00% |
| `app\modules\internship\service.py` | 42 | 42 | 0 | 100.00% |
| `app\modules\mock_result\__init__.py` | 0 | 0 | 0 | 100.00% |
| `app\modules\mock_result\router.py` | 17 | 17 | 0 | 100.00% |
| `app\modules\mock_result\schemas.py` | 58 | 58 | 0 | 100.00% |
| `app\modules\mock_result\service.py` | 51 | 49 | 2 | 93.85% |
| `app\modules\mock_test\__init__.py` | 0 | 0 | 0 | 100.00% |
| `app\modules\mock_test\auto_submit_router.py` | 25 | 25 | 0 | 100.00% |
| `app\modules\mock_test\auto_submit_schemas.py` | 11 | 11 | 0 | 100.00% |
| `app\modules\mock_test\finalize.py` | 73 | 62 | 11 | 84.62% |
| `app\modules\mock_test\models.py` | 78 | 78 | 0 | 100.00% |
| `app\modules\mock_test\router.py` | 31 | 31 | 0 | 100.00% |
| `app\modules\mock_test\schemas.py` | 51 | 51 | 0 | 100.00% |
| `app\modules\mock_test\service.py` | 121 | 110 | 11 | 90.91% |
| `app\modules\mock_test\timing.py` | 13 | 13 | 0 | 100.00% |
| `app\modules\performance\__init__.py` | 0 | 0 | 0 | 100.00% |
| `app\modules\performance\indexes.py` | 13 | 13 | 0 | 100.00% |
| `app\modules\performance\models.py` | 14 | 11 | 3 | 72.73% |
| `app\modules\performance\router.py` | 9 | 9 | 0 | 100.00% |
| `app\modules\practice\__init__.py` | 0 | 0 | 0 | 100.00% |
| `app\modules\practice\code_evaluator.py` | 13 | 13 | 0 | 100.00% |
| `app\modules\practice\models.py` | 51 | 51 | 0 | 100.00% |
| `app\modules\practice\router.py` | 25 | 25 | 0 | 100.00% |
| `app\modules\practice\schemas.py` | 58 | 58 | 0 | 100.00% |
| `app\modules\practice\scoring.py` | 21 | 21 | 0 | 100.00% |
| `app\modules\practice\service.py` | 90 | 86 | 4 | 95.69% |
| `app\modules\question_bank\__init__.py` | 0 | 0 | 0 | 100.00% |
| `app\modules\question_bank\admin_router.py` | 32 | 31 | 1 | 96.88% |
| `app\modules\question_bank\models.py` | 42 | 42 | 0 | 100.00% |
| `app\modules\question_bank\router.py` | 16 | 16 | 0 | 100.00% |
| `app\modules\question_bank\schemas.py` | 106 | 106 | 0 | 99.15% |
| `app\modules\question_bank\service.py` | 121 | 116 | 5 | 94.33% |

## Notes

Coverage is calculated from the Python files measured by the project's coverage configuration and imported during the full backend test run. Review `.coveragerc` or `pyproject.toml` if you need to change the measured source scope.
