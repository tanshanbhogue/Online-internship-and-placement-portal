# System Validation Report

- Run date: 2026-11-10 23:02:43 India Standard Time
- Python: 3.11.9
- Platform: Windows-10-10.0.26200-SP0
- Total tests: 24
- Passed: 24
- Failed: 0
- Skipped: 0
- Other outcomes: 0
- Duration: 10.55 seconds

## Result

**All 24 tests passed.**

## Test results

| Test | Result | Duration (s) |
|---|---:|---:|
| `tests/test_e2e_journeys.py::test_register_login_browse_apply_practise_mock_and_see_analytics` | PASSED | 0.507 |
| `tests/test_e2e_journeys.py::test_weak_category_improves_after_more_good_attempts` | PASSED | 0.432 |
| `tests/test_e2e_journeys.py::test_time_runs_out_while_the_student_is_away_and_everything_still_adds_up` | PASSED | 0.255 |
| `tests/test_e2e_journeys.py::test_a_second_attempt_can_start_after_the_first_is_closed` | PASSED | 0.198 |
| `tests/test_e2e_security_sweep.py::test_every_sprint2_route_is_covered_by_this_sweep` | PASSED | 0.000 |
| `tests/test_e2e_security_sweep.py::test_guests_get_401_everywhere` | PASSED | 0.106 |
| `tests/test_e2e_security_sweep.py::test_admins_cannot_use_student_endpoints_and_students_cannot_use_admin_ones` | PASSED | 0.323 |
| `tests/test_e2e_security_sweep.py::test_students_cannot_touch_someone_elses_attempt` | PASSED | 0.218 |
| `tests/test_e2e_security_sweep.py::test_no_answer_keys_before_submission_anywhere` | PASSED | 0.219 |
| `tests/test_e2e_security_sweep.py::test_a_closed_attempt_cannot_be_submitted_twice_or_edited` | PASSED | 0.286 |
| `tests/test_e2e_security_sweep.py::test_dashboard_and_attempt_data_is_never_cached` | PASSED | 0.215 |
| `tests/test_response_time.py::test_every_response_carries_a_timing_header` | PASSED | 0.014 |
| `tests/test_response_time.py::test_percentile_is_nearest_rank` | PASSED | 0.000 |
| `tests/test_response_time.py::test_stats_use_the_route_template_not_the_real_path` | PASSED | 0.021 |
| `tests/test_response_time.py::test_slow_requests_are_counted_and_logged_without_ids` | PASSED | 0.000 |
| `tests/test_response_time.py::test_performance_endpoint_is_admin_only` | PASSED | 0.265 |
| `tests/test_response_time.py::test_responses_are_gzipped_for_clients_that_accept_it_and_plain_otherwise` | PASSED | 0.153 |
| `tests/test_response_time.py::test_rate_limiter_is_off_under_pytest_unless_forced` | PASSED | 2.478 |
| `tests/test_response_time.py::test_login_is_limited_then_recovers` | PASSED | 1.307 |
| `tests/test_response_time.py::test_limits_are_per_rule_and_other_routes_are_free` | PASSED | 1.252 |
| `tests/test_response_time.py::test_limiter_can_be_switched_off` | PASSED | 1.547 |
| `tests/test_response_time.py::test_rule_patterns_match_only_the_intended_routes` | PASSED | 0.000 |
| `tests/test_response_time.py::test_every_index_is_attached_to_a_real_table_column` | PASSED | 0.012 |
| `tests/test_response_time.py::test_ensure_indexes_upgrades_an_old_database_and_is_repeatable` | PASSED | 0.023 |

## Run information

This report was generated from pytest's JSON report. It reflects the test run performed by `generate_reports.py`.
