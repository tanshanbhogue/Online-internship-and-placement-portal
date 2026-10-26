# ==============================================================================
# FILE   : backend/tests/test_question_bank.py
# STORY  : #21 Categorized Question Bank  [FR-003; SEC-07, SEC-12, SEC-20]
# OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 4
# ==============================================================================
#
# PURPOSE
#   Tests for the question bank.
#
# TEST CASES
#   - UT_08/UT_09/UT_10 each category returns only questions of that category (Aptitude, Technical MCQ, Coding)
#   - IT_07 empty category returns 200 with items == [] and no error
#   - SEC-12 student responses never contain is_correct, explanation or test_cases anywhere in the JSON
#   - categories list returns correct question counts; inactive (soft-deleted) questions are excluded
#   - admin CRUD: create valid MCQ -> 201; no correct option / two correct options / <2 options -> 422; update; delete -> 204 and disappears for students
#   - SEC-07 student and guest calling /api/admin/question-bank/* get 403 / 401
#   - audit log line is written for admin changes and contains no answer data (caplog)
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================
