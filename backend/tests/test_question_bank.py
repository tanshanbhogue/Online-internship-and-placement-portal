import json
import logging

import pytest

from app.modules.question_bank.models import Category, Difficulty, Question, QuestionOption, QuestionType


@pytest.fixture()
def bank(db):
    """Categories + a few questions. Returns a dict of categories by key."""
    cats = {k: Category(name=n, slug=k) for k, n in (("aptitude", "Aptitude"), ("technical", "Technical MCQ"), ("coding", "Coding"), ("empty", "Advanced DSA"))}
    db.add_all(cats.values())
    db.commit()

    def mcq(cat, prompt, correct=0):
        q = Question(
            category_id=cat.id, type=QuestionType.MCQ, prompt=prompt, difficulty=Difficulty.EASY,
            explanation="Because reasons.",
            options=[QuestionOption(text=f"opt{i}", is_correct=(i == correct), position=i) for i in range(4)],
        )
        db.add(q)
        return q

    for n in range(3):
        mcq(cats["aptitude"], f"Aptitude Q{n}")
    for n in range(2):
        mcq(cats["technical"], f"Technical Q{n}")
    db.add(Question(category_id=cats["coding"].id, type=QuestionType.CODING, prompt="Reverse a string",
                    difficulty=Difficulty.EASY, starter_code="def f(s):\n    pass", test_cases=json.dumps([{"input": "ab", "output": "ba"}]),
                    explanation="Slice it."))
    db.commit()
    return cats


def _prompts(response):
    return sorted(q["prompt"] for q in response.json()["items"])


@pytest.mark.parametrize("key, expected", [
    ("aptitude", ["Aptitude Q0", "Aptitude Q1", "Aptitude Q2"]),        # UT_08
    ("technical", ["Technical Q0", "Technical Q1"]),                    # UT_09
    ("coding", ["Reverse a string"]),                                   # UT_10
])
def test_ut08_09_10_category_returns_only_its_questions(student_client, bank, key, expected):
    response = student_client.get(f"/api/question-bank/categories/{bank[key].id}/questions")
    assert response.status_code == 200
    assert _prompts(response) == expected


def test_it07_empty_category_is_200_with_no_items(student_client, bank):
    response = student_client.get(f"/api/question-bank/categories/{bank['empty'].id}/questions")
    assert response.status_code == 200 and response.json()["items"] == []


def test_unknown_category_is_404(student_client, bank):
    assert student_client.get("/api/question-bank/categories/9999/questions").status_code == 404


def test_count_and_difficulty_params(student_client, bank):
    url = f"/api/question-bank/categories/{bank['aptitude'].id}/questions"
    assert len(student_client.get(url, params={"count": 2}).json()["items"]) == 2
    assert student_client.get(url, params={"difficulty": "hard"}).json()["items"] == []
    assert student_client.get(url, params={"count": 51}).status_code == 422


def test_sec12_student_json_never_contains_answers(student_client, bank):
    for cat in bank.values():
        text = student_client.get(f"/api/question-bank/categories/{cat.id}/questions").text
        for forbidden in ("is_correct", "explanation", "test_cases", "Because reasons", "Slice it"):
            assert forbidden not in text
    mcq = student_client.get(f"/api/question-bank/categories/{bank['aptitude'].id}/questions").json()["items"][0]
    assert set(mcq) == {"id", "category_id", "type", "prompt", "difficulty", "options", "starter_code"}
    assert all(set(o) == {"id", "text"} for o in mcq["options"])


def test_categories_list_counts_and_excludes_soft_deleted(student_client, admin_client, bank, db):
    counts = {c["name"]: c["question_count"] for c in student_client.get("/api/question-bank/categories").json()}
    assert counts == {"Aptitude": 3, "Technical MCQ": 2, "Coding": 1, "Advanced DSA": 0}
    victim = db.query(Question).filter_by(prompt="Aptitude Q0").one()
    assert admin_client.delete(f"/api/admin/question-bank/questions/{victim.id}").status_code == 204
    counts = {c["name"]: c["question_count"] for c in student_client.get("/api/question-bank/categories").json()}
    assert counts["Aptitude"] == 2
    assert "Aptitude Q0" not in _prompts(student_client.get(f"/api/question-bank/categories/{bank['aptitude'].id}/questions"))


def _mcq_payload(category_id, **overrides):
    payload = {
        "category_id": category_id, "type": "mcq", "prompt": "What is 2 + 2?", "difficulty": "easy",
        "explanation": "Basic arithmetic.",
        "options": [{"text": "3", "is_correct": False}, {"text": "4", "is_correct": True}],
    }
    payload.update(overrides)
    return payload


def test_admin_create_valid_mcq(admin_client, bank):
    response = admin_client.post("/api/admin/question-bank/questions", json=_mcq_payload(bank["aptitude"].id))
    assert response.status_code == 201
    body = response.json()
    assert body["is_active"] is True and [o["is_correct"] for o in body["options"]] == [False, True]


@pytest.mark.parametrize("options", [
    [{"text": "a", "is_correct": False}, {"text": "b", "is_correct": False}],          # no correct option
    [{"text": "a", "is_correct": True}, {"text": "b", "is_correct": True}],            # two correct
    [{"text": "a", "is_correct": True}],                                               # fewer than 2
    [{"text": str(i), "is_correct": i == 0} for i in range(7)],                        # more than 6
])
def test_admin_invalid_mcq_options_give_422_field_errors(admin_client, bank, options):
    response = admin_client.post("/api/admin/question-bank/questions", json=_mcq_payload(bank["aptitude"].id, options=options))
    assert response.status_code == 422
    assert "options" in response.json()["fields"]


def test_admin_mcq_without_options_and_unknown_category_are_422(admin_client, bank):
    missing = _mcq_payload(bank["aptitude"].id)
    del missing["options"]
    assert admin_client.post("/api/admin/question-bank/questions", json=missing).status_code == 422
    response = admin_client.post("/api/admin/question-bank/questions", json=_mcq_payload(9999))
    assert response.status_code == 422 and "category_id" in response.json()["fields"]


def test_admin_coding_question_rules(admin_client, bank):
    ok = {"category_id": bank["coding"].id, "type": "coding", "prompt": "Add", "difficulty": "easy",
          "starter_code": "def add(a, b):\n    pass", "test_cases": json.dumps([{"input": [1, 2], "output": 3}])}
    assert admin_client.post("/api/admin/question-bank/questions", json=ok).status_code == 201
    with_options = {**ok, "options": [{"text": "x", "is_correct": True}]}
    assert admin_client.post("/api/admin/question-bank/questions", json=with_options).status_code == 422
    bad_json = {**ok, "test_cases": "{not json"}
    assert "test_cases" in admin_client.post("/api/admin/question-bank/questions", json=bad_json).json()["fields"]


def test_admin_update_and_validation_after_merge(admin_client, bank):
    created = admin_client.post("/api/admin/question-bank/questions", json=_mcq_payload(bank["aptitude"].id)).json()
    url = f"/api/admin/question-bank/questions/{created['id']}"
    updated = admin_client.put(url, json={"prompt": "What is 3 + 3?", "difficulty": "hard"})
    assert updated.status_code == 200
    assert updated.json()["prompt"] == "What is 3 + 3?" and updated.json()["difficulty"] == "hard"
    assert len(updated.json()["options"]) == 2  # untouched fields survive the merge
    bad = admin_client.put(url, json={"options": [{"text": "a", "is_correct": False}, {"text": "b", "is_correct": False}]})
    assert bad.status_code == 422
    assert admin_client.get(url).json()["prompt"] == "What is 3 + 3?"
    assert admin_client.put("/api/admin/question-bank/questions/9999", json={"prompt": "x"}).status_code == 404


def test_admin_delete_is_soft_and_hidden_from_students(admin_client, student_client, bank, db):
    created = admin_client.post("/api/admin/question-bank/questions", json=_mcq_payload(bank["empty"].id)).json()
    url = f"/api/question-bank/categories/{bank['empty'].id}/questions"
    assert len(student_client.get(url).json()["items"]) == 1
    assert admin_client.delete(f"/api/admin/question-bank/questions/{created['id']}").status_code == 204
    assert student_client.get(url).json()["items"] == []
    assert db.get(Question, created["id"]).is_active is False  # row kept for practice history


def test_admin_category_create_and_duplicate(admin_client, bank):
    ok = admin_client.post("/api/admin/question-bank/categories", json={"name": "System Design"})
    assert ok.status_code == 201 and ok.json()["slug"] == "system-design" and ok.json()["question_count"] == 0
    dup = admin_client.post("/api/admin/question-bank/categories", json={"name": "system design"})
    assert dup.status_code == 409 and dup.json()["code"] == "conflict"


def test_admin_list_questions_paginates_and_filters(admin_client, bank):
    page = admin_client.get("/api/admin/question-bank/questions", params={"category_id": bank["aptitude"].id, "page_size": 2}).json()
    assert page["total"] == 3 and len(page["items"]) == 2
    assert "is_correct" in json.dumps(page)  # admins DO see answers


def test_sec07_students_and_guests_cannot_use_admin_routes(student_client, client_factory, bank):
    routes = [("get", "/categories"), ("get", "/questions"), ("post", "/questions"), ("delete", "/questions/1")]
    guest = client_factory()
    for method, path in routes:
        url = f"/api/admin/question-bank{path}"
        kwargs = {"json": {}} if method == "post" else {}
        assert getattr(student_client, method)(url, **kwargs).status_code == 403
        assert getattr(guest, method)(url, **kwargs).status_code == 401


def test_admin_audit_log_has_no_answer_data(admin_client, bank, caplog):
    with caplog.at_level(logging.INFO, logger="security.audit"):
        created = admin_client.post(
            "/api/admin/question-bank/questions",
            json=_mcq_payload(bank["aptitude"].id, prompt="Secret prompt text", explanation="Secret explanation"),
        ).json()
        admin_client.delete(f"/api/admin/question-bank/questions/{created['id']}")
    audit_lines = [r.getMessage() for r in caplog.records if r.name == "security.audit"]
    assert any("question_created" in line for line in audit_lines)
    assert any("question_deleted" in line for line in audit_lines)
    joined = " ".join(audit_lines)
    assert "Secret" not in joined and "is_correct" not in joined
