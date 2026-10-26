# ==============================================================================
# FILE   : backend/tests/test_practice_scoring.py
# STORY  : #22 Practice Test Scoring  [FR-003; SEC-06, SEC-12]
# OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 5
# ==============================================================================
#
# PURPOSE
#   Tests for scoring, sessions and history.
#
# TEST CASES
#   - unit: score_session with 5 answers (e.g. 3 correct) -> correct 3, percent 60.0; zero questions; all pending -> percent None; unanswered count as wrong (UT_11)
#   - UT_11 API: start session, answer 5 MCQs (mix), finish -> result correct_count equals the number of right answers
#   - ST_05 end-to-end: category -> all questions -> submit -> result screen data shows score and category
#   - ST_06: session for Aptitude, then a new session for Technical MCQ -> second question set has only Technical MCQ questions, none carried over
#   - IT_07: empty category -> start_session returns 404 code no_questions, no crash
#   - IT_08: completed session appears in /history with date and score; in-progress sessions do not
#   - SEC-06: student B cannot answer, finish or read student A's session (404); answering twice -> 409; answering after finish -> 409
#   - SEC-12: start response and answer endpoint never expose correct options before the question is answered; result is refused until finished
#   - coding answer is stored as pending, never executed, excluded from the percent denominator
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================

import pytest

from app.modules.practice.models import EvaluationStatus, PracticeAnswer, PracticeSession
from app.modules.practice.scoring import score_session
from app.modules.question_bank.models import Category, Difficulty, Question, QuestionOption, QuestionType

E, P = EvaluationStatus.EVALUATED, EvaluationStatus.PENDING


# ------------------------------------------------------------------ pure scoring unit tests
def test_score_session_three_of_five():
    results = [(True, E), (True, E), (False, E), (True, E), (False, E)]
    summary = score_session(5, results)
    assert (summary.correct, summary.answered, summary.pending, summary.percent) == (3, 5, 0, 60.0)


def test_score_session_rounds_to_two_decimals():
    assert score_session(3, [(True, E), (False, E), (False, E)]).percent == 33.33


def test_score_session_zero_questions_is_none():
    assert score_session(0, []).percent is None


def test_score_session_all_pending_is_none():
    summary = score_session(2, [(None, P), (None, P)])
    assert summary.pending == 2 and summary.percent is None


def test_unanswered_questions_count_as_wrong():
    assert score_session(4, [(True, E)]).percent == 25.0


def test_pending_is_excluded_from_denominator():
    assert score_session(4, [(True, E), (True, E), (None, P), (None, P)]).percent == 100.0


def test_accepts_plain_string_status():
    assert score_session(2, [(True, "evaluated"), (None, "pending")]).percent == 100.0


# ------------------------------------------------------------------ API helpers
@pytest.fixture()
def bank(db):
    cats = {k: Category(name=n, slug=k) for k, n in (("aptitude", "Aptitude"), ("technical", "Technical MCQ"), ("coding", "Coding"), ("empty", "Advanced DSA"))}
    db.add_all(cats.values())
    db.commit()
    for cat_key, label in (("aptitude", "Apt"), ("technical", "Tech")):
        for n in range(5):
            db.add(Question(
                category_id=cats[cat_key].id, type=QuestionType.MCQ, prompt=f"{label} Q{n}", difficulty=Difficulty.EASY,
                explanation=f"Explanation {label}{n}",
                options=[QuestionOption(text=f"o{i}", is_correct=(i == 1), position=i) for i in range(3)],
            ))
    db.add(Question(category_id=cats["coding"].id, type=QuestionType.CODING, prompt="Code Q", difficulty=Difficulty.EASY,
                    starter_code="def f():\n    pass", test_cases='[{"input": 1, "output": 1}]', explanation="Secret code explanation"))
    db.commit()
    return cats


def _start(client, category, count=None):
    body = {"category_id": category.id}
    if count:
        body["count"] = count
    return client.post("/api/practice/sessions", json=body)


def _correct_option(db, question_id):
    return db.query(QuestionOption).filter_by(question_id=question_id, is_correct=True).one().id


def _wrong_option(db, question_id):
    return db.query(QuestionOption).filter_by(question_id=question_id, is_correct=False).first().id


def _answer(client, session_id, question_id, option_id):
    return client.post(f"/api/practice/sessions/{session_id}/answers", json={"question_id": question_id, "selected_option_id": option_id})


# ------------------------------------------------------------------ API tests
def test_ut11_start_answer_five_and_finish(student_client, bank, db):
    started = _start(student_client, bank["aptitude"], 5)
    assert started.status_code == 201
    data = started.json()
    assert data["total_questions"] == 5 and data["category"]["name"] == "Aptitude"
    right = 0
    for index, question in enumerate(data["questions"]):
        picks_right = index in (0, 2, 3)
        option = _correct_option(db, question["id"]) if picks_right else _wrong_option(db, question["id"])
        feedback = _answer(student_client, data["session_id"], question["id"], option)
        assert feedback.status_code == 200 and feedback.json()["is_correct"] is picks_right
        right += picks_right
    result = student_client.post(f"/api/practice/sessions/{data['session_id']}/finish")
    assert result.status_code == 200
    body = result.json()
    assert body["correct_count"] == right == 3 and body["score_percent"] == 60.0 and body["status"] == "completed"
    assert len(body["breakdown"]) == 5 and all(item["explanation"] for item in body["breakdown"])


def test_st05_end_to_end_result_has_score_and_category(student_client, bank, db):
    session = _start(student_client, bank["technical"]).json()
    for q in session["questions"]:
        _answer(student_client, session["session_id"], q["id"], _correct_option(db, q["id"]))
    student_client.post(f"/api/practice/sessions/{session['session_id']}/finish")
    result = student_client.get(f"/api/practice/sessions/{session['session_id']}").json()
    assert result["category"]["name"] == "Technical MCQ" and result["score_percent"] == 100.0
    assert result["answered_count"] == 5 == result["correct_count"]


def test_st06_new_category_means_new_session_with_only_that_category(student_client, bank):
    first = _start(student_client, bank["aptitude"]).json()
    second = _start(student_client, bank["technical"]).json()
    assert first["session_id"] != second["session_id"]
    assert all(q["category_id"] == bank["aptitude"].id for q in first["questions"])
    assert all(q["category_id"] == bank["technical"].id for q in second["questions"])
    assert not {q["id"] for q in first["questions"]} & {q["id"] for q in second["questions"]}


def test_it07_empty_category_returns_404_no_questions(student_client, bank):
    response = _start(student_client, bank["empty"])
    assert response.status_code == 404
    assert response.json()["code"] == "no_questions" and response.json()["detail"] == "No questions found"
    assert student_client.post("/api/practice/sessions", json={"category_id": 9999}).status_code == 404


def test_it08_history_lists_only_completed_sessions(student_client, bank, db):
    done = _start(student_client, bank["aptitude"], 2).json()
    open_session = _start(student_client, bank["technical"], 2).json()
    student_client.post(f"/api/practice/sessions/{done['session_id']}/finish")
    items = student_client.get("/api/practice/history").json()["items"]
    assert [i["session_id"] for i in items] == [done["session_id"]]
    assert items[0]["category_name"] == "Aptitude" and items[0]["completed_at"] and items[0]["score_percent"] == 0.0
    assert open_session["session_id"] not in [i["session_id"] for i in items]


def test_sec06_other_students_cannot_touch_a_session(student_client, client_factory, make_user, login, bank, db):
    session = _start(student_client, bank["aptitude"], 2).json()
    make_user("b@test.com")
    intruder = client_factory()
    login(intruder, "b@test.com")
    q = session["questions"][0]["id"]
    sid = session["session_id"]
    assert _answer(intruder, sid, q, _correct_option(db, q)).status_code == 404
    assert intruder.post(f"/api/practice/sessions/{sid}/finish").status_code == 404
    student_client.post(f"/api/practice/sessions/{sid}/finish")
    assert intruder.get(f"/api/practice/sessions/{sid}").status_code == 404
    assert intruder.get("/api/practice/history").json()["items"] == []


def test_answering_twice_or_after_finish_is_409(student_client, bank, db):
    session = _start(student_client, bank["aptitude"], 2).json()
    sid, q = session["session_id"], session["questions"][0]["id"]
    assert _answer(student_client, sid, q, _correct_option(db, q)).status_code == 200
    again = _answer(student_client, sid, q, _correct_option(db, q))
    assert again.status_code == 409 and again.json()["code"] == "conflict"
    student_client.post(f"/api/practice/sessions/{sid}/finish")
    other = session["questions"][1]["id"]
    assert _answer(student_client, sid, other, _correct_option(db, other)).status_code == 409


def test_sec12_no_answers_before_answering_and_result_refused_until_finished(student_client, bank, db):
    started = _start(student_client, bank["aptitude"], 3)
    for forbidden in ("is_correct", "explanation", "correct_option", "Explanation Apt"):
        assert forbidden not in started.text
    sid = started.json()["session_id"]
    early = student_client.get(f"/api/practice/sessions/{sid}")
    assert early.status_code == 409 and early.json()["detail"] == "Session not finished"
    q = started.json()["questions"][0]["id"]
    feedback = _answer(student_client, sid, q, _wrong_option(db, q)).json()
    assert feedback["correct_option_id"] == _correct_option(db, q) and feedback["explanation"]


def test_invalid_answer_payloads_are_422(student_client, bank, db):
    session = _start(student_client, bank["aptitude"], 2).json()
    sid, q = session["session_id"], session["questions"][0]["id"]
    url = f"/api/practice/sessions/{sid}/answers"
    assert student_client.post(url, json={"question_id": q}).status_code == 422
    assert student_client.post(url, json={"question_id": q, "selected_option_id": 1, "code": "x"}).status_code == 422
    assert student_client.post(url, json={"question_id": q, "selected_option_id": 99999}).status_code == 422
    assert student_client.post(url, json={"question_id": q, "code": "print(1)"}).status_code == 422
    assert student_client.post(url, json={"question_id": 99999, "selected_option_id": 1}).status_code == 404


def test_coding_answer_is_pending_never_executed_and_excluded_from_percent(student_client, bank, db):
    session = _start(student_client, bank["coding"]).json()
    sid, q = session["session_id"], session["questions"][0]["id"]
    assert session["questions"][0]["starter_code"]
    marker = "raise SystemExit('should never run')"
    feedback = student_client.post(f"/api/practice/sessions/{sid}/answers", json={"question_id": q, "code": marker})
    assert feedback.status_code == 200
    assert feedback.json()["is_correct"] is None and feedback.json()["evaluation_status"] == "pending"
    stored = db.query(PracticeAnswer).one()
    assert stored.submitted_code == marker and stored.is_correct is None
    result = student_client.post(f"/api/practice/sessions/{sid}/finish").json()
    assert result["score_percent"] is None and result["answered_count"] == 1


def test_finish_is_idempotent_and_partial_sessions_score_unanswered_as_wrong(student_client, bank, db):
    session = _start(student_client, bank["aptitude"], 4).json()
    sid, q = session["session_id"], session["questions"][0]["id"]
    _answer(student_client, sid, q, _correct_option(db, q))
    first = student_client.post(f"/api/practice/sessions/{sid}/finish").json()
    second = student_client.post(f"/api/practice/sessions/{sid}/finish").json()
    assert first == second
    assert first["score_percent"] == 25.0 and first["answered_count"] == 1
    assert sum(1 for b in first["breakdown"] if b["is_correct"] is False) == 3


def test_practice_requires_a_student(admin_client, client_factory, bank):
    assert client_factory().post("/api/practice/sessions", json={"category_id": bank["aptitude"].id}).status_code == 401
    assert admin_client.post("/api/practice/sessions", json={"category_id": bank["aptitude"].id}).status_code == 403
