# System Validation and Verification Report

## Online Internship & Placement Preparation Portal

  Item                    Details
  ----------------------- ----------------------------------------------
  Validation evidence     24 automated pytest tests
  Test execution          10 November 2026, 23:02:43 IST
  Environment             Python 3.11.9 \| Windows 10 (10.0.26200-SP0)
  Requirements baseline   SRS Version 1.1, dated 19 November 2026
  Report date             19 November 2026

## Test-run summary

    Total tests   Passed   Failed   Skipped        Duration
  ------------- -------- -------- --------- ---------------
             24       24        0         0   10.55 seconds

**Overall test-run outcome: PASS.** All 24 tests in the supplied pytest
report passed. The SRS Version 1.1 Requirements Traceability Matrix
(RTM) also records SR-001 through SR-010 as verified (status A). This
report distinguishes the supplied 24-test execution from the broader
security verification status recorded in the SRS RTM.

------------------------------------------------------------------------

## 1. Executive Summary

This report records the available validation evidence for the Online
Internship & Placement Preparation Portal. The supplied automated run
covered end-to-end student journeys, mock-test lifecycle behaviour,
authorization and data isolation, answer-key protection, response-time
instrumentation, rate limiting, response compression and database-index
integrity.

The run completed with **24 passed, 0 failed and 0 skipped in 10.55
seconds**. The SRS Version 1.1 RTM marks FR-001 to FR-005, NFR-001 to
NFR-003 and SR-001 to SR-010 as verified. Individual security controls
not named in the 24-test summary are identified as verified according to
the SRS RTM rather than being attributed to this particular execution.

## 2. Validation Scope and Objectives

Scope follows the SRS: authentication; internship listings and
applications; practice questions; timed mock tests and result analysis;
personal analytics; performance; compatibility; and security.

**Objectives** - Verify the integrated student journey from
registration/login through internship browsing, practice, mock testing
and analytics. - Verify timeout handling, result consistency and the
ability to begin a subsequent mock-test attempt. - Verify authentication
boundaries, role separation, ownership checks and answer-key
protection. - Verify response-time metadata, rate limiting, compression
and database-index integrity.

## 3. Test Execution Summary

All tests below were reported as **PASSED**.

  -----------------------------------------------------------------------------------------------------------------------------------
  Test case                                                                                          Result              Duration (s)
  ------------------------------------------------------------------------------- ------------------------- -------------------------
  `test_register_login_browse_apply_practise_mock_and_see_analytics`                                 PASSED                     0.507

  `test_weak_category_improves_after_more_good_attempts`                                             PASSED                     0.432

  `test_time_runs_out_while_the_student_is_away_and_everything_still_adds_up`                        PASSED                     0.255

  `test_a_second_attempt_can_start_after_the_first_is_closed`                                        PASSED                     0.198

  `test_every_sprint2_route_is_covered_by_this_sweep`                                                PASSED                     0.000

  `test_guests_get_401_everywhere`                                                                   PASSED                     0.106

  `test_admins_cannot_use_student_endpoints_and_students_cannot_use_admin_ones`                      PASSED                     0.323

  `test_students_cannot_touch_someone_elses_attempt`                                                 PASSED                     0.218

  `test_no_answer_keys_before_submission_anywhere`                                                   PASSED                     0.219

  `test_a_closed_attempt_cannot_be_submitted_twice_or_edited`                                        PASSED                     0.286

  `test_dashboard_and_attempt_data_is_never_cached`                                                  PASSED                     0.215

  `test_every_response_carries_a_timing_header`                                                      PASSED                     0.014

  `test_percentile_is_nearest_rank`                                                                  PASSED                     0.000

  `test_stats_use_the_route_template_not_the_real_path`                                              PASSED                     0.021

  `test_slow_requests_are_counted_and_logged_without_ids`                                            PASSED                     0.000

  `test_performance_endpoint_is_admin_only`                                                          PASSED                     0.265

  `test_responses_are_gzipped_for_clients_that_accept_it_and_plain_otherwise`                        PASSED                     0.153

  `test_rate_limiter_is_off_under_pytest_unless_forced`                                              PASSED                     2.478

  `test_login_is_limited_then_recovers`                                                              PASSED                     1.307

  `test_limits_are_per_rule_and_other_routes_are_free`                                               PASSED                     1.252

  `test_limiter_can_be_switched_off`                                                                 PASSED                     1.547

  `test_rule_patterns_match_only_the_intended_routes`                                                PASSED                     0.000

  `test_every_index_is_attached_to_a_real_table_column`                                              PASSED                     0.012

  `test_ensure_indexes_upgrades_an_old_database_and_is_repeatable`                                   PASSED                     0.023
  -----------------------------------------------------------------------------------------------------------------------------------

*Source: supplied System Validation Report test-run summary. Test names,
outcomes and durations are transcribed from that report.*

## 4. End-to-End and Security Validation Scenarios

### SVR-01 --- Integrated student journey

Registration/login, internship browsing and application, practice, mock
test and analytics were exercised in one end-to-end journey.

**Verdict:** PASSED ---
`test_register_login_browse_apply_practise_mock_and_see_analytics`

### SVR-02 --- Practice progression and analytics

The weak-category progression test checked the effect of additional good
attempts on category performance.

**Verdict:** PASSED ---
`test_weak_category_improves_after_more_good_attempts`

### SVR-03 --- Timeout while student is away

Timeout behaviour was exercised while the student was away, with
consistency of resulting data checked.

**Verdict:** PASSED ---
`test_time_runs_out_while_the_student_is_away_and_everything_still_adds_up`

### SVR-04 --- Subsequent attempt

A second attempt was started after the first attempt had been closed.

**Verdict:** PASSED ---
`test_a_second_attempt_can_start_after_the_first_is_closed`

### SVR-05 --- Guest access restriction

Guest requests to protected Sprint 2 routes were rejected with HTTP 401.

**Verdict:** PASSED --- `test_guests_get_401_everywhere`

### SVR-06 --- Role-based access control

Student-only and admin-only endpoint boundaries were checked; cross-role
access was denied.

**Verdict:** PASSED ---
`test_admins_cannot_use_student_endpoints_and_students_cannot_use_admin_ones`

### SVR-07 --- Ownership and answer-key protection

A student was prevented from touching another student's attempt; answer
keys were withheld before submission.

**Verdict:** PASSED ---
`test_students_cannot_touch_someone_elses_attempt`;
`test_no_answer_keys_before_submission_anywhere`

### SVR-08 --- Closed-attempt integrity and cache control

A closed attempt could not be submitted again or edited; dashboard and
attempt data were checked for cache prevention.

**Verdict:** PASSED ---
`test_a_closed_attempt_cannot_be_submitted_twice_or_edited`;
`test_dashboard_and_attempt_data_is_never_cached`

### SVR-09 --- Rate limiting and performance access

Login throttling, per-rule limits, recovery after lockout and admin-only
access to performance statistics were tested.

**Verdict:** PASSED --- relevant tests in `tests/test_response_time.py`

### SVR-10 --- Database index integrity

Indexes were checked against real table columns, and index setup was
checked for upgrade and repeatability.

**Verdict:** PASSED --- relevant database-index tests in
`tests/test_response_time.py`

## 5. Security Requirements Validation Matrix

Security requirement statements follow Section 5.1.2 of SRS Version 1.1.
Status **A (verified)** is taken from the SRS RTM. The evidence column
distinguishes tests explicitly named in the supplied 24-test run from
mapped test references recorded by the SRS.

  ---------------------------------------------------------------------------------------------------------------
  ID                Security requirement RTM status        Validation evidence / traceability
  ----------------- -------------------- ----------------- ------------------------------------------------------
  SR-001            TLS 1.2+ for all     A --- Verified    SRS RTM: ST-N02_08 (manual deployed-site check). Not
                    connections; HTTP                      named in supplied 24-test run.
                    redirected to HTTPS.                   

  SR-002            Salted Argon2        A --- Verified    SRS RTM: ST-N02_01, UT-01_03.
                    password hashes,                       
                    password-strength                      
                    rule and no password                   
                    disclosure in                          
                    responses.                             

  SR-003            HttpOnly session     A --- Verified    SRS RTM: ST-N02_02, IT-01_07.
                    cookie; token                          
                    invalidated on                         
                    logout.                                

  SR-004            Throttle repeated    A --- Verified    SRS RTM: ST-N02_03; supplied run includes
                    failed logins after                    `test_login_is_limited_then_recovers`.
                    five failures until                    
                    lockout expires.                       

  SR-005            Authentication       A --- Verified    SRS RTM: ST-N02_04, UT-01_05; supplied run:
                    required for                           `test_guests_get_401_everywhere`.
                    protected functions;                   
                    guests denied.                         

  SR-006            Admin functions      A --- Verified    SRS RTM: ST-N02_05; supplied run includes cross-role
                    restricted to Admin                    endpoint test.
                    role; no Admin                         
                    self-registration.                     

  SR-007            Students access only A --- Verified    SRS RTM: ST-N02_06; supplied run includes attempt
                    their own                              ownership test.
                    applications,                          
                    attempts, practice                     
                    history and                            
                    analytics.                             

  SR-008            No answer keys       A --- Verified    SRS RTM: ST-N02_07, UT-04_04, ST-04_08; supplied run
                    before submission;                     includes answer-key and closed-attempt tests.
                    server-side                            
                    timing/scoring; no                     
                    edit or duplicate                      
                    submission.                            

  SR-009            Resume uploads       A --- Verified    SRS RTM: UT-02_06. Not named in supplied 24-test run.
                    restricted by                          
                    type/size, renamed                     
                    and stored outside                     
                    web root.                              

  SR-010            Server-side input    A --- Verified    SRS RTM: `test_sql_injection_strings_are_inert` and
                    validation and                         `test_sec09_injection_and_wildcards_are_plain_text`;
                    parameterized                          not named in supplied 24-test run.
                    queries prevent                        
                    injection.                             
  ---------------------------------------------------------------------------------------------------------------

**Evidence interpretation:** All ten security requirements are marked A
in the SRS RTM. The supplied 24-test execution directly demonstrates
several access-control, ownership, answer-key, attempt-integrity,
cache-control and login-throttling behaviours. For SR-001, SR-002,
SR-003, SR-009 and SR-010, this report relies on the SRS RTM's mapped
verification record rather than claiming those cases appear in the
24-test summary.

## 6. Functional and Non-Functional Requirements Traceability

The SRS Version 1.1 RTM records FR-001 to FR-005 and NFR-001 to NFR-003
as verified. The evidence notes below identify the relationship to the
supplied run and preserve qualifications present in the SRS.

  ---------------------------------------------------------------------------
  ID                Requirement       RTM status        Evidence / note
  ----------------- ----------------- ----------------- ---------------------
  FR-001            Registration,     A --- Verified    Integrated journey,
                    login and session                   guest access and
                    authentication.                     login-throttling
                                                        tests.

  FR-002            Internship        A --- Verified    Integrated journey;
                    listing display                     SRS RTM records
                    and student                         mapped
                    applications.                       listing/application
                                                        cases as A.

  FR-003            Practice          A --- Verified    Integrated journey
                    aptitude,                           and weak-category
                    technical MCQ and                   progression tests;
                    coding question                     SRS RTM records
                    bank.                               mapped cases as A.

  FR-004            Timed mock tests, A --- Verified    Timeout-while-away,
                    auto-submit,                        second-attempt,
                    results and                         answer-key and
                    detailed                            closed-attempt tests.
                    analysis.                           

  FR-005            Personal          A --- Verified    Integrated journey
                    analytics from                      and weak-category
                    test and practice                   progression tests.
                    history.                            

  NFR-001           p95 response time A --- Verified    SRS RTM: PT-N01_01 to
                    ≤ 2 seconds under                   PT-N01_08 and
                    normal load (10                     PT-N01_06R. Supplied
                    concurrent                          run covers timing
                    users).                             headers, percentile
                                                        calculation and
                                                        performance endpoint
                                                        access; it is not the
                                                        separate 10-user load
                                                        report.

  NFR-002           Protect           A --- Verified    SRS RTM: ST-N02_01 to
                    credentials and                     ST-N02_08; see
                    user data using                     Security Matrix.
                    secure                              
                    authentication                      
                    and encrypted                       
                    transport.                          

  NFR-003           Chrome, Firefox   A --- Verified    SRS RTM status A, but
                    and Edge across                     its comment says
                    desktop, tablet                     ST-N03_05 and
                    and mobile.                         ST-N03_08 were not
                                                        executed at the time.
                                                        Attach later browser
                                                        test results to close
                                                        these evidence gaps.
  ---------------------------------------------------------------------------

## 7. Limitations and Evidence Notes

-   The supplied pytest report gives 24 test names, outcomes and
    durations. It does not include full logs, a coverage report,
    browser-compatibility results or the separate 10-concurrent-user
    performance measurements.
-   SR-001 to SR-010 are marked verified in the SRS RTM. Where a mapped
    test is not named in the supplied 24-test summary, the report cites
    the SRS RTM rather than implying that it ran in this particular
    execution.
-   The SRS RTM marks NFR-003 as A but states that ST-N03_05 and
    ST-N03_08 had not been executed at the time. This inconsistency is
    retained transparently; attach subsequent browser results for
    mock-test and analytics pages before treating those two cases as
    individually executed.
-   The supplied test run is dated 10 November 2026, while SRS Version
    1.1 is dated 19 November 2026. The run is treated as execution
    evidence and the later SRS RTM as the requirements-status baseline.

## 8. Acceptance Conclusion

The supplied system-validation run achieved a **100% pass rate: all 24
tests passed, with no failures or skips**. It provides positive evidence
for the integrated student journey, mock-test timeout and attempt
lifecycle, role and ownership enforcement, answer-key confidentiality,
cache controls, rate limiting, response-time instrumentation and
database-index integrity.

The SRS Version 1.1 RTM records FR-001 to FR-005, NFR-001 to NFR-003 and
SR-001 to SR-010 as verified. Security requirements are reported as
validated in accordance with that RTM, subject to the evidence
qualifications in this report. The two compatibility cases noted as not
executed remain an explicit evidence gap unless later results are
attached.

> **VALIDATION TEST RUN: PASSED --- 24/24 TESTS**

## Source Documents

1.  `System_Validation_Report.md` --- supplied pytest summary (24 tests,
    all passed).
2.  *Software Requirements Specification -- Online Internship &
    Placement Preparation Portal*, Version 1.1, 19 November 2026 ---
    Sections 4, 5.1 and 8 (Requirements Traceability Matrix).
