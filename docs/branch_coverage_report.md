# Branch Coverage Report

- Run date: 2026-11-10 23:02:43 India Standard Time
- Measurement: coverage.py branch measurement through pytest-cov
- Total branches: 414
- Covered branches: 345
- Missing branches: 69
- Branch coverage: **83.33%**

## Branch coverage by file

| File | Branches | Covered | Missing | Branch coverage |
|---|---:|---:|---:|---:|
| `app\__init__.py` | 0 | 0 | 0 | 0.00% |
| `app\core\__init__.py` | 0 | 0 | 0 | 0.00% |
| `app\core\config.py` | 6 | 2 | 4 | 33.33% |
| `app\core\database.py` | 2 | 1 | 1 | 50.00% |
| `app\core\dependencies.py` | 12 | 10 | 2 | 83.33% |
| `app\core\errors.py` | 30 | 24 | 6 | 80.00% |
| `app\core\log_redaction.py` | 18 | 9 | 9 | 50.00% |
| `app\core\security.py` | 20 | 17 | 3 | 85.00% |
| `app\core\tokens.py` | 4 | 2 | 2 | 50.00% |
| `app\db\__init__.py` | 0 | 0 | 0 | 0.00% |
| `app\db\base.py` | 8 | 6 | 2 | 75.00% |
| `app\db\models_registry.py` | 4 | 4 | 0 | 100.00% |
| `app\main.py` | 16 | 8 | 8 | 50.00% |
| `app\middleware\__init__.py` | 0 | 0 | 0 | 0.00% |
| `app\middleware\compression.py` | 0 | 0 | 0 | 0.00% |
| `app\middleware\rate_limit.py` | 18 | 15 | 3 | 83.33% |
| `app\middleware\request_timing.py` | 14 | 11 | 3 | 78.57% |
| `app\modules\__init__.py` | 0 | 0 | 0 | 0.00% |
| `app\modules\analytics\__init__.py` | 0 | 0 | 0 | 0.00% |
| `app\modules\analytics\insights.py` | 14 | 14 | 0 | 100.00% |
| `app\modules\analytics\insights_router.py` | 2 | 2 | 0 | 100.00% |
| `app\modules\analytics\insights_schemas.py` | 0 | 0 | 0 | 0.00% |
| `app\modules\analytics\router.py` | 0 | 0 | 0 | 0.00% |
| `app\modules\analytics\schemas.py` | 2 | 2 | 0 | 100.00% |
| `app\modules\analytics\service.py` | 18 | 18 | 0 | 100.00% |
| `app\modules\analytics\trends.py` | 8 | 8 | 0 | 100.00% |
| `app\modules\application\__init__.py` | 0 | 0 | 0 | 0.00% |
| `app\modules\application\duplicate_check.py` | 4 | 4 | 0 | 100.00% |
| `app\modules\application\duplicate_router.py` | 2 | 2 | 0 | 100.00% |
| `app\modules\application\duplicate_schemas.py` | 0 | 0 | 0 | 0.00% |
| `app\modules\application\models.py` | 0 | 0 | 0 | 0.00% |
| `app\modules\application\resume_storage.py` | 24 | 17 | 7 | 70.83% |
| `app\modules\application\router.py` | 0 | 0 | 0 | 0.00% |
| `app\modules\application\schemas.py` | 0 | 0 | 0 | 0.00% |
| `app\modules\application\service.py` | 4 | 4 | 0 | 100.00% |
| `app\modules\auth\__init__.py` | 0 | 0 | 0 | 0.00% |
| `app\modules\auth\login_router.py` | 2 | 1 | 1 | 50.00% |
| `app\modules\auth\login_schemas.py` | 0 | 0 | 0 | 0.00% |
| `app\modules\auth\login_service.py` | 6 | 5 | 1 | 83.33% |
| `app\modules\auth\login_throttle.py` | 2 | 2 | 0 | 100.00% |
| `app\modules\auth\models.py` | 0 | 0 | 0 | 0.00% |
| `app\modules\auth\register_router.py` | 0 | 0 | 0 | 0.00% |
| `app\modules\auth\register_schemas.py` | 0 | 0 | 0 | 0.00% |
| `app\modules\auth\register_service.py` | 4 | 4 | 0 | 100.00% |
| `app\modules\auth\session_models.py` | 0 | 0 | 0 | 0.00% |
| `app\modules\internship\__init__.py` | 0 | 0 | 0 | 0.00% |
| `app\modules\internship\models.py` | 0 | 0 | 0 | 0.00% |
| `app\modules\internship\router.py` | 0 | 0 | 0 | 0.00% |
| `app\modules\internship\schemas.py` | 0 | 0 | 0 | 0.00% |
| `app\modules\internship\service.py` | 16 | 16 | 0 | 100.00% |
| `app\modules\mock_result\__init__.py` | 0 | 0 | 0 | 0.00% |
| `app\modules\mock_result\router.py` | 0 | 0 | 0 | 0.00% |
| `app\modules\mock_result\schemas.py` | 0 | 0 | 0 | 0.00% |
| `app\modules\mock_result\service.py` | 14 | 12 | 2 | 85.71% |
| `app\modules\mock_test\__init__.py` | 0 | 0 | 0 | 0.00% |
| `app\modules\mock_test\auto_submit_router.py` | 4 | 4 | 0 | 100.00% |
| `app\modules\mock_test\auto_submit_schemas.py` | 0 | 0 | 0 | 0.00% |
| `app\modules\mock_test\finalize.py` | 18 | 15 | 3 | 83.33% |
| `app\modules\mock_test\models.py` | 0 | 0 | 0 | 0.00% |
| `app\modules\mock_test\router.py` | 2 | 2 | 0 | 100.00% |
| `app\modules\mock_test\schemas.py` | 0 | 0 | 0 | 0.00% |
| `app\modules\mock_test\service.py` | 44 | 40 | 4 | 90.91% |
| `app\modules\mock_test\timing.py` | 0 | 0 | 0 | 0.00% |
| `app\modules\performance\__init__.py` | 0 | 0 | 0 | 0.00% |
| `app\modules\performance\indexes.py` | 4 | 4 | 0 | 100.00% |
| `app\modules\performance\models.py` | 8 | 5 | 3 | 62.50% |
| `app\modules\performance\router.py` | 0 | 0 | 0 | 0.00% |
| `app\modules\practice\__init__.py` | 0 | 0 | 0 | 0.00% |
| `app\modules\practice\code_evaluator.py` | 0 | 0 | 0 | 0.00% |
| `app\modules\practice\models.py` | 0 | 0 | 0 | 0.00% |
| `app\modules\practice\router.py` | 0 | 0 | 0 | 0.00% |
| `app\modules\practice\schemas.py` | 2 | 2 | 0 | 100.00% |
| `app\modules\practice\scoring.py` | 0 | 0 | 0 | 0.00% |
| `app\modules\practice\service.py` | 26 | 25 | 1 | 96.15% |
| `app\modules\question_bank\__init__.py` | 0 | 0 | 0 | 0.00% |
| `app\modules\question_bank\admin_router.py` | 0 | 0 | 0 | 0.00% |
| `app\modules\question_bank\models.py` | 0 | 0 | 0 | 0.00% |
| `app\modules\question_bank\router.py` | 0 | 0 | 0 | 0.00% |
| `app\modules\question_bank\schemas.py` | 12 | 11 | 1 | 91.67% |
| `app\modules\question_bank\service.py` | 20 | 17 | 3 | 85.00% |

## Notes

A branch is a possible control-flow path (for example, the true and false outcomes of a conditional). Files with no measured branches show 0 branches; they are not included in the branch total.
