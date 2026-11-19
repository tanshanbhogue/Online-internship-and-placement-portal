# Unit Test Report

- Run date: 2026-11-10 23:02:43 India Standard Time
- Python: 3.11.9
- Platform: Windows-10-10.0.26200-SP0
- Total tests: 203
- Passed: 203
- Failed: 0
- Skipped: 0
- Other outcomes: 0
- Duration: 26.51 seconds

## Result

**All 203 tests passed.**

## Test results

| Test | Result | Duration (s) |
|---|---:|---:|
| `tests/test_analytics.py::test_st09_new_student_gets_an_empty_but_valid_summary` | PASSED | 0.424 |
| `tests/test_analytics.py::test_it12_average_of_60_75_90_is_75_and_other_totals_match` | PASSED | 0.139 |
| `tests/test_analytics.py::test_average_is_rounded_to_two_decimals` | PASSED | 0.137 |
| `tests/test_analytics.py::test_open_unscored_and_unfinished_attempts_are_not_counted` | PASSED | 0.136 |
| `tests/test_analytics.py::test_it11_a_new_attempt_changes_the_numbers_at_once_and_nothing_is_cached` | PASSED | 0.179 |
| `tests/test_analytics.py::test_ut18_each_student_sees_only_their_own_data` | PASSED | 0.256 |
| `tests/test_analytics.py::test_source_filter` | PASSED | 0.148 |
| `tests/test_analytics.py::test_date_range_filter_is_inclusive_of_both_days` | PASSED | 0.161 |
| `tests/test_analytics.py::test_attempts_list_is_newest_first_with_kind_and_id_for_drill_down` | PASSED | 0.137 |
| `tests/test_analytics.py::test_attempts_limit` | PASSED | 0.137 |
| `tests/test_analytics.py::test_guests_and_admins_are_refused` | PASSED | 0.150 |
| `tests/test_analytics_insights.py::test_it12_moving_average_matches_hand_calculation` | PASSED | 0.000 |
| `tests/test_analytics_insights.py::test_trend_direction[scores0-not_enough_data]` | PASSED | 0.000 |
| `tests/test_analytics_insights.py::test_trend_direction[scores1-improving]` | PASSED | 0.000 |
| `tests/test_analytics_insights.py::test_trend_direction[scores2-declining]` | PASSED | 0.000 |
| `tests/test_analytics_insights.py::test_trend_direction[scores3-steady]` | PASSED | 0.000 |
| `tests/test_analytics_insights.py::test_trend_direction[scores4-steady]` | PASSED | 0.000 |
| `tests/test_analytics_insights.py::test_trend_direction[scores5-improving]` | PASSED | 0.000 |
| `tests/test_analytics_insights.py::test_classify[scores0-not_enough_data]` | PASSED | 0.000 |
| `tests/test_analytics_insights.py::test_classify[scores1-strong]` | PASSED | 0.000 |
| `tests/test_analytics_insights.py::test_classify[scores2-weak]` | PASSED | 0.000 |
| `tests/test_analytics_insights.py::test_classify[scores3-average]` | PASSED | 0.000 |
| `tests/test_analytics_insights.py::test_classify[scores4-strong]` | PASSED | 0.000 |
| `tests/test_analytics_insights.py::test_classify[scores5-average]` | PASSED | 0.000 |
| `tests/test_analytics_insights.py::test_classify[scores6-improved]` | PASSED | 0.000 |
| `tests/test_analytics_insights.py::test_classify[scores7-average]` | PASSED | 0.000 |
| `tests/test_analytics_insights.py::test_classify[scores8-improved]` | PASSED | 0.000 |
| `tests/test_analytics_insights.py::test_classify[scores9-weak]` | PASSED | 0.000 |
| `tests/test_analytics_insights.py::test_classify[scores10-strong]` | PASSED | 0.000 |
| `tests/test_analytics_insights.py::test_classify_numbers` | PASSED | 0.000 |
| `tests/test_analytics_insights.py::test_focus_areas_put_the_weakest_first_and_respect_the_limit` | PASSED | 0.000 |
| `tests/test_analytics_insights.py::test_st09_new_student_gets_empty_valid_answers` | PASSED | 0.134 |
| `tests/test_analytics_insights.py::test_it12_trend_points_and_moving_average` | PASSED | 0.143 |
| `tests/test_analytics_insights.py::test_trend_mixes_practice_and_mock_in_time_order` | PASSED | 0.139 |
| `tests/test_analytics_insights.py::test_ut17_categories_are_classified_and_listed` | PASSED | 0.145 |
| `tests/test_analytics_insights.py::test_st11_a_weak_category_becomes_improved_after_good_attempts` | PASSED | 0.138 |
| `tests/test_analytics_insights.py::test_st10_combined_history_feeds_both_endpoints` | PASSED | 0.141 |
| `tests/test_analytics_insights.py::test_ut18_other_students_attempts_never_appear` | PASSED | 0.201 |
| `tests/test_analytics_insights.py::test_filters_apply_to_both_endpoints` | PASSED | 0.149 |
| `tests/test_analytics_insights.py::test_guests_and_admins_are_refused` | PASSED | 0.145 |
| `tests/test_application_apply.py::test_ut06_apply_with_valid_pdf_then_listed_in_mine` | PASSED | 0.153 |
| `tests/test_application_apply.py::test_docx_resume_is_accepted` | PASSED | 0.142 |
| `tests/test_application_apply.py::test_ut07_sec15_second_application_is_409_and_one_row` | PASSED | 0.137 |
| `tests/test_application_apply.py::test_st04_expired_listing_rejected_even_when_ui_is_bypassed` | PASSED | 0.137 |
| `tests/test_application_apply.py::test_it04_it06_two_listings_recorded_independently` | PASSED | 0.165 |
| `tests/test_application_apply.py::test_st03_listing_apply_check_mine` | PASSED | 0.148 |
| `tests/test_application_apply.py::test_sec16_bad_files_are_rejected[virus.exe-MZ\x90\x00\x03\x00\x00\x00-application/x-msdownload]` | PASSED | 0.145 |
| `tests/test_application_apply.py::test_sec16_bad_files_are_rejected[notes.pdf-just some plain text pretending to be a pdf-application/pdf]` | PASSED | 0.141 |
| `tests/test_application_apply.py::test_sec16_bad_files_are_rejected[fake.docx-PK\x03\x04 not really a zip archive-application/vnd.openxmlformats-officedocument.wordprocessingml.document]` | PASSED | 0.146 |
| `tests/test_application_apply.py::test_sec16_bad_files_are_rejected[plain.zip-None-application/zip]` | PASSED | 0.136 |
| `tests/test_application_apply.py::test_sec16_bad_files_are_rejected[cv.exe-%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF\n-application/pdf]` | PASSED | 0.137 |
| `tests/test_application_apply.py::test_sec16_bad_files_are_rejected[empty.pdf--application/pdf]` | PASSED | 0.137 |
| `tests/test_application_apply.py::test_sec16_oversized_file_is_rejected` | PASSED | 0.200 |
| `tests/test_application_apply.py::test_sec16_missing_resume_is_validation_error` | PASSED | 0.139 |
| `tests/test_application_apply.py::test_cover_note_too_long_is_rejected` | PASSED | 0.136 |
| `tests/test_application_apply.py::test_sec16_stored_name_is_random_and_inside_storage_dir` | PASSED | 0.136 |
| `tests/test_application_apply.py::test_sec06_student_b_cannot_see_student_a_applications` | PASSED | 0.263 |
| `tests/test_application_apply.py::test_sec07_guest_401_admin_403` | PASSED | 0.143 |
| `tests/test_application_apply.py::test_sec10_18_script_in_cover_note_is_plain_text_and_nothing_sensitive_leaks` | PASSED | 0.138 |
| `tests/test_application_duplicates.py::test_ensure_not_already_applied_passes_then_raises` | PASSED | 0.074 |
| `tests/test_application_duplicates.py::test_db_constraint_blocks_duplicates_and_is_translated` | PASSED | 0.067 |
| `tests/test_application_duplicates.py::test_other_integrity_errors_are_re_raised` | PASSED | 0.064 |
| `tests/test_application_duplicates.py::test_different_listing_and_different_student_are_allowed` | PASSED | 0.121 |
| `tests/test_application_duplicates.py::test_check_endpoint_before_and_after` | PASSED | 0.139 |
| `tests/test_application_duplicates.py::test_sec06_student_never_sees_another_students_record` | PASSED | 0.187 |
| `tests/test_application_duplicates.py::test_check_unknown_listing_guest_and_admin` | PASSED | 0.263 |
| `tests/test_auth_login.py::test_valid_login_sets_secure_session_cookie` | PASSED | 0.128 |
| `tests/test_auth_login.py::test_wrong_password_returns_401` | PASSED | 0.140 |
| `tests/test_auth_login.py::test_unknown_email_has_same_error_as_wrong_password` | PASSED | 0.183 |
| `tests/test_auth_login.py::test_login_then_me_returns_current_user` | PASSED | 0.131 |
| `tests/test_auth_login.py::test_logged_out_user_cannot_access_me` | PASSED | 0.013 |
| `tests/test_auth_login.py::test_logout_revokes_previous_session` | PASSED | 0.138 |
| `tests/test_auth_login.py::test_sixth_failed_login_is_throttled` | PASSED | 0.364 |
| `tests/test_auth_registration.py::test_ut04_blank_fields_rejected_with_field_errors` | PASSED | 0.017 |
| `tests/test_auth_registration.py::test_valid_registration_returns_profile_without_secrets_and_stores_argon2` | PASSED | 0.073 |
| `tests/test_auth_registration.py::test_it02_duplicate_email_rejected_including_other_case` | PASSED | 0.101 |
| `tests/test_auth_registration.py::test_weak_password_gives_message_under_fields_password` | PASSED | 0.021 |
| `tests/test_auth_registration.py::test_role_admin_in_body_never_creates_an_admin` | PASSED | 0.014 |
| `tests/test_auth_registration.py::test_sql_injection_strings_are_inert` | PASSED | 0.073 |
| `tests/test_auth_registration.py::test_validation_errors_never_echo_the_submitted_password` | PASSED | 0.014 |
| `tests/test_internship_listings.py::test_ut05_active_listings_for_student_and_guest_gets_401` | PASSED | 0.136 |
| `tests/test_internship_listings.py::test_it05_new_listing_visible_on_next_request` | PASSED | 0.145 |
| `tests/test_internship_listings.py::test_draft_and_inactive_hidden_and_detail_404` | PASSED | 0.151 |
| `tests/test_internship_listings.py::test_detail_includes_description_and_eligibility` | PASSED | 0.136 |
| `tests/test_internship_listings.py::test_expired_listing_is_closed_and_sorted_last` | PASSED | 0.138 |
| `tests/test_internship_listings.py::test_deadline_today_is_still_open` | PASSED | 0.134 |
| `tests/test_internship_listings.py::test_filters` | PASSED | 0.188 |
| `tests/test_internship_listings.py::test_sec09_injection_and_wildcards_are_plain_text` | PASSED | 0.160 |
| `tests/test_internship_listings.py::test_pagination_bounds` | PASSED | 0.145 |
| `tests/test_internship_listings.py::test_short_description_is_truncated` | PASSED | 0.131 |
| `tests/test_mock_auto_submit.py::test_timing_helpers_use_the_given_clock` | PASSED | 0.172 |
| `tests/test_mock_auto_submit.py::test_ut14_expired_attempt_is_auto_submitted_and_scored` | PASSED | 0.120 |
| `tests/test_mock_auto_submit.py::test_answers_are_marked_only_after_finalization` | PASSED | 0.091 |
| `tests/test_mock_auto_submit.py::test_manual_submit_before_expiry_is_a_normal_submission` | PASSED | 0.074 |
| `tests/test_mock_auto_submit.py::test_manual_submit_after_expiry_is_recorded_as_auto_submitted` | PASSED | 0.086 |
| `tests/test_mock_auto_submit.py::test_auto_finalize_refuses_while_time_remains` | PASSED | 0.072 |
| `tests/test_mock_auto_submit.py::test_sec14_finalizing_twice_changes_nothing_the_second_time` | PASSED | 0.081 |
| `tests/test_mock_auto_submit.py::test_sec14_lost_race_after_manual_submit_creates_no_second_record` | PASSED | 0.095 |
| `tests/test_mock_auto_submit.py::test_one_open_attempt_per_student_and_test_is_enforced_by_the_database` | PASSED | 0.069 |
| `tests/test_mock_auto_submit.py::test_sweeper_closes_only_expired_attempts` | PASSED | 0.134 |
| `tests/test_mock_auto_submit.py::test_endpoint_rejects_early_request_and_keeps_the_attempt_open` | PASSED | 0.147 |
| `tests/test_mock_auto_submit.py::test_st07_endpoint_after_expiry_auto_submits_and_reports_it` | PASSED | 0.169 |
| `tests/test_mock_auto_submit.py::test_endpoint_after_manual_submit_reports_already_final` | PASSED | 0.156 |
| `tests/test_mock_auto_submit.py::test_sec06_another_students_attempt_looks_missing` | PASSED | 0.197 |
| `tests/test_mock_auto_submit.py::test_endpoint_requires_a_session` | PASSED | 0.078 |
| `tests/test_mock_auto_submit.py::test_sec07_admin_sweep_is_admin_only` | PASSED | 0.342 |
| `tests/test_mock_auto_submit.py::test_sec20_auto_submit_is_logged_without_answers` | PASSED | 0.091 |
| `tests/test_mock_results.py::test_ut15_summary_and_breakdown_mark_each_question` | PASSED | 0.168 |
| `tests/test_mock_results.py::test_st07_auto_submitted_attempt_is_flagged_and_analysed` | PASSED | 0.253 |
| `tests/test_mock_results.py::test_all_unanswered_has_no_accuracy_but_a_zero_score` | PASSED | 0.160 |
| `tests/test_mock_results.py::test_by_difficulty_totals` | PASSED | 0.163 |
| `tests/test_mock_results.py::test_breakdown_filters_by_difficulty_and_outcome` | PASSED | 0.189 |
| `tests/test_mock_results.py::test_it09_result_is_retrievable_later_from_history` | PASSED | 0.179 |
| `tests/test_mock_results.py::test_st08_back_to_back_attempts_are_listed_separately_newest_first` | PASSED | 0.178 |
| `tests/test_mock_results.py::test_history_excludes_open_attempts_and_other_students` | PASSED | 0.221 |
| `tests/test_mock_results.py::test_sec12_open_attempt_has_no_result_and_leaks_nothing` | PASSED | 0.150 |
| `tests/test_mock_results.py::test_open_attempt_whose_time_is_up_is_closed_then_shown` | PASSED | 0.159 |
| `tests/test_mock_results.py::test_sec06_other_students_results_are_invisible` | PASSED | 0.223 |
| `tests/test_mock_results.py::test_guests_and_admins_are_refused` | PASSED | 0.148 |
| `tests/test_mock_results.py::test_percentile_needs_five_other_attempts_then_ranks_among_them` | PASSED | 0.513 |
| `tests/test_mock_tests.py::test_list_shows_active_tests_with_counts` | PASSED | 0.145 |
| `tests/test_mock_tests.py::test_list_hides_inactive_tests_and_tests_without_usable_questions` | PASSED | 0.245 |
| `tests/test_mock_tests.py::test_coding_and_inactive_questions_are_not_part_of_an_attempt` | PASSED | 0.161 |
| `tests/test_mock_tests.py::test_ut12_start_returns_server_time_countdown_and_questions` | PASSED | 0.143 |
| `tests/test_mock_tests.py::test_sec12_no_answer_keys_or_explanations_before_submission` | PASSED | 0.167 |
| `tests/test_mock_tests.py::test_it10_start_again_resumes_the_same_attempt_with_less_time` | PASSED | 0.163 |
| `tests/test_mock_tests.py::test_it10_get_attempt_reports_remaining_time_from_the_server_clock` | PASSED | 0.169 |
| `tests/test_mock_tests.py::test_list_marks_the_open_attempt_so_the_student_can_resume` | PASSED | 0.166 |
| `tests/test_mock_tests.py::test_starting_after_the_old_attempt_expired_closes_it_and_starts_fresh` | PASSED | 0.182 |
| `tests/test_mock_tests.py::test_answers_can_be_saved_changed_and_cleared` | PASSED | 0.199 |
| `tests/test_mock_tests.py::test_saved_answers_survive_a_refresh` | PASSED | 0.178 |
| `tests/test_mock_tests.py::test_invalid_choices_are_rejected` | PASSED | 0.170 |
| `tests/test_mock_tests.py::test_sec13_saving_after_the_time_limit_is_refused_and_the_attempt_is_closed` | PASSED | 0.173 |
| `tests/test_mock_tests.py::test_sec13_reading_an_expired_attempt_closes_it` | PASSED | 0.169 |
| `tests/test_mock_tests.py::test_ut13_manual_submit_before_the_limit_scores_the_attempt` | PASSED | 0.196 |
| `tests/test_mock_tests.py::test_submit_with_final_answers_keeps_them` | PASSED | 0.283 |
| `tests/test_mock_tests.py::test_submit_with_a_bad_answer_changes_nothing` | PASSED | 0.160 |
| `tests/test_mock_tests.py::test_submit_at_the_buzzer_inside_the_grace_window_keeps_late_answers_but_counts_as_auto` | PASSED | 0.173 |
| `tests/test_mock_tests.py::test_submit_long_after_the_limit_ignores_the_late_answers` | PASSED | 0.175 |
| `tests/test_mock_tests.py::test_sec14_submitting_twice_is_harmless_and_input_is_locked_afterwards` | PASSED | 0.178 |
| `tests/test_mock_tests.py::test_st08_two_tests_back_to_back_are_recorded_separately` | PASSED | 0.194 |
| `tests/test_mock_tests.py::test_the_same_test_can_be_retaken_after_submitting` | PASSED | 0.172 |
| `tests/test_mock_tests.py::test_sec01_guests_get_401_on_every_route` | PASSED | 0.033 |
| `tests/test_mock_tests.py::test_admins_cannot_take_tests` | PASSED | 0.149 |
| `tests/test_mock_tests.py::test_sec06_another_students_attempt_is_invisible_in_every_route` | PASSED | 0.299 |
| `tests/test_mock_tests.py::test_unknown_or_inactive_test_is_404` | PASSED | 0.152 |
| `tests/test_practice_scoring.py::test_score_session_three_of_five` | PASSED | 0.000 |
| `tests/test_practice_scoring.py::test_score_session_rounds_to_two_decimals` | PASSED | 0.000 |
| `tests/test_practice_scoring.py::test_score_session_zero_questions_is_none` | PASSED | 0.000 |
| `tests/test_practice_scoring.py::test_score_session_all_pending_is_none` | PASSED | 0.000 |
| `tests/test_practice_scoring.py::test_unanswered_questions_count_as_wrong` | PASSED | 0.000 |
| `tests/test_practice_scoring.py::test_pending_is_excluded_from_denominator` | PASSED | 0.000 |
| `tests/test_practice_scoring.py::test_accepts_plain_string_status` | PASSED | 0.000 |
| `tests/test_practice_scoring.py::test_ut11_start_answer_five_and_finish` | PASSED | 0.224 |
| `tests/test_practice_scoring.py::test_st05_end_to_end_result_has_score_and_category` | PASSED | 0.324 |
| `tests/test_practice_scoring.py::test_st06_new_category_means_new_session_with_only_that_category` | PASSED | 0.159 |
| `tests/test_practice_scoring.py::test_it07_empty_category_returns_404_no_questions` | PASSED | 0.149 |
| `tests/test_practice_scoring.py::test_it08_history_lists_only_completed_sessions` | PASSED | 0.181 |
| `tests/test_practice_scoring.py::test_sec06_other_students_cannot_touch_a_session` | PASSED | 0.306 |
| `tests/test_practice_scoring.py::test_answering_twice_or_after_finish_is_409` | PASSED | 0.188 |
| `tests/test_practice_scoring.py::test_sec12_no_answers_before_answering_and_result_refused_until_finished` | PASSED | 0.177 |
| `tests/test_practice_scoring.py::test_invalid_answer_payloads_are_422` | PASSED | 0.186 |
| `tests/test_practice_scoring.py::test_coding_answer_is_pending_never_executed_and_excluded_from_percent` | PASSED | 0.170 |
| `tests/test_practice_scoring.py::test_finish_is_idempotent_and_partial_sessions_score_unanswered_as_wrong` | PASSED | 0.176 |
| `tests/test_practice_scoring.py::test_practice_requires_a_student` | PASSED | 0.146 |
| `tests/test_question_bank.py::test_ut08_09_10_category_returns_only_its_questions[aptitude-expected0]` | PASSED | 0.146 |
| `tests/test_question_bank.py::test_ut08_09_10_category_returns_only_its_questions[technical-expected1]` | PASSED | 0.143 |
| `tests/test_question_bank.py::test_ut08_09_10_category_returns_only_its_questions[coding-expected2]` | PASSED | 0.147 |
| `tests/test_question_bank.py::test_it07_empty_category_is_200_with_no_items` | PASSED | 0.145 |
| `tests/test_question_bank.py::test_unknown_category_is_404` | PASSED | 0.147 |
| `tests/test_question_bank.py::test_count_and_difficulty_params` | PASSED | 0.266 |
| `tests/test_question_bank.py::test_sec12_student_json_never_contains_answers` | PASSED | 0.169 |
| `tests/test_question_bank.py::test_categories_list_counts_and_excludes_soft_deleted` | PASSED | 0.286 |
| `tests/test_question_bank.py::test_admin_create_valid_mcq` | PASSED | 0.149 |
| `tests/test_question_bank.py::test_admin_invalid_mcq_options_give_422_field_errors[options0]` | PASSED | 0.142 |
| `tests/test_question_bank.py::test_admin_invalid_mcq_options_give_422_field_errors[options1]` | PASSED | 0.143 |
| `tests/test_question_bank.py::test_admin_invalid_mcq_options_give_422_field_errors[options2]` | PASSED | 0.144 |
| `tests/test_question_bank.py::test_admin_invalid_mcq_options_give_422_field_errors[options3]` | PASSED | 0.147 |
| `tests/test_question_bank.py::test_admin_mcq_without_options_and_unknown_category_are_422` | PASSED | 0.157 |
| `tests/test_question_bank.py::test_admin_coding_question_rules` | PASSED | 0.171 |
| `tests/test_question_bank.py::test_admin_update_and_validation_after_merge` | PASSED | 0.172 |
| `tests/test_question_bank.py::test_admin_delete_is_soft_and_hidden_from_students` | PASSED | 0.291 |
| `tests/test_question_bank.py::test_admin_category_create_and_duplicate` | PASSED | 0.154 |
| `tests/test_question_bank.py::test_admin_list_questions_paginates_and_filters` | PASSED | 0.146 |
| `tests/test_question_bank.py::test_sec07_students_and_guests_cannot_use_admin_routes` | PASSED | 0.171 |
| `tests/test_question_bank.py::test_admin_audit_log_has_no_answer_data` | PASSED | 0.150 |
| `tests/test_security_credentials.py::test_weak_passwords_are_rejected[Ab1!]` | PASSED | 0.000 |
| `tests/test_security_credentials.py::test_weak_passwords_are_rejected[Password!]` | PASSED | 0.000 |
| `tests/test_security_credentials.py::test_weak_passwords_are_rejected[Password123]` | PASSED | 0.000 |
| `tests/test_security_credentials.py::test_weak_passwords_are_rejected[12345678!]` | PASSED | 0.000 |
| `tests/test_security_credentials.py::test_weak_passwords_are_rejected[]` | PASSED | 0.000 |
| `tests/test_security_credentials.py::test_weak_passwords_are_rejected[AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA1!]` | PASSED | 0.000 |
| `tests/test_security_credentials.py::test_strong_password_is_accepted` | PASSED | 0.000 |
| `tests/test_security_credentials.py::test_hash_password_uses_random_salt` | PASSED | 0.107 |
| `tests/test_security_credentials.py::test_hash_password_rejects_empty_password` | PASSED | 0.000 |
| `tests/test_security_credentials.py::test_hash_password_rejects_password_over_maximum_length` | PASSED | 0.000 |
| `tests/test_security_credentials.py::test_verify_password_accepts_correct_password` | PASSED | 0.111 |
| `tests/test_security_credentials.py::test_verify_password_rejects_wrong_password` | PASSED | 0.115 |
| `tests/test_security_credentials.py::test_verify_password_handles_malformed_hash` | PASSED | 0.000 |
| `tests/test_security_credentials.py::test_verify_password_handles_non_string_inputs` | PASSED | 0.000 |
| `tests/test_security_credentials.py::test_verify_dummy_returns_none` | PASSED | 0.057 |
| `tests/test_security_credentials.py::test_needs_rehash_handles_malformed_hash` | PASSED | 0.000 |
| `tests/test_security_credentials.py::test_log_redaction_hides_sensitive_values` | PASSED | 0.001 |

## Run information

This report was generated from pytest's JSON report. It reflects the test run performed by `generate_reports.py`.
