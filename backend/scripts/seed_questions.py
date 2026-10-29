import json
import re
import sys

from sqlalchemy import select

from app.core.database import SessionLocal, init_db
from app.modules.question_bank.models import Category, Difficulty, Question, QuestionOption, QuestionType

E, M, H = Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD

# (prompt, difficulty, [options], index of the correct option, explanation)
APTITUDE = [
    ("A train travels 120 km in 2 hours. What is its average speed?", E, ["40 km/h", "60 km/h", "80 km/h", "120 km/h"], 1, "Speed = distance / time = 120 / 2 = 60 km/h."),
    ("What is 15% of 200?", E, ["20", "25", "30", "35"], 2, "15% of 200 = 0.15 x 200 = 30."),
    ("What comes next in the series 2, 6, 12, 20, 30, ?", M, ["38", "40", "42", "44"], 2, "The differences are 4, 6, 8, 10 and so the next difference is 12: 30 + 12 = 42."),
    ("A can finish a job in 10 days and B in 15 days. Working together, how long will they take?", M, ["5 days", "6 days", "7.5 days", "12.5 days"], 1, "Combined rate = 1/10 + 1/15 = 1/6 of the job per day, so 6 days."),
    ("Two numbers are in the ratio 3:5 and their sum is 40. What is the larger number?", E, ["15", "20", "25", "30"], 2, "Total parts = 8, one part = 5, so the larger number = 5 x 5 = 25."),
    ("What is the simple interest on Rs 1000 at 5% per annum for 2 years?", E, ["Rs 50", "Rs 100", "Rs 105", "Rs 150"], 1, "SI = P x R x T / 100 = 1000 x 5 x 2 / 100 = Rs 100."),
    ("What is the average of 10, 20, 30, 40 and 50?", E, ["25", "30", "35", "150"], 1, "The sum is 150 and dividing by 5 numbers gives 30."),
    ("Which number is the odd one out: 2, 3, 5, 9, 11?", M, ["2", "5", "9", "11"], 2, "All the others are prime; 9 = 3 x 3 is not."),
    ("A price rises by 20% and then falls by 20%. What is the net change?", H, ["No change", "4% decrease", "4% increase", "2% decrease"], 1, "1.2 x 0.8 = 0.96, which is a 4% decrease from the original price."),
    ("In how many different ways can the letters of the word CAT be arranged?", M, ["3", "6", "9", "12"], 1, "3 distinct letters can be arranged in 3! = 6 ways."),
]

TECHNICAL = [
    ("What is the time complexity of binary search on a sorted array of n elements?", E, ["O(n)", "O(log n)", "O(n log n)", "O(1)"], 1, "Each step halves the search space, giving O(log n)."),
    ("Which data structure follows the LIFO principle?", E, ["Queue", "Stack", "Array", "Linked list"], 1, "A stack removes the most recently added element first (Last In, First Out)."),
    ("Which SQL keyword removes duplicate rows from a query result?", E, ["UNIQUE", "DISTINCT", "GROUP", "REMOVE"], 1, "SELECT DISTINCT returns only unique rows."),
    ("Which HTTP status code means the requested resource was not found?", E, ["200", "301", "404", "500"], 2, "404 Not Found is returned when the server cannot find the resource."),
    ("Which of these Python types is immutable?", M, ["list", "dict", "set", "tuple"], 3, "Tuples cannot be changed after creation; lists, dicts and sets can."),
    ("What is it called when different classes respond to the same method call in different ways?", M, ["Encapsulation", "Inheritance", "Polymorphism", "Abstraction"], 2, "Polymorphism lets one interface have many implementations."),
    ("Which Git command creates a new branch and switches to it?", M, ["git branch -d feature", "git checkout -b feature", "git merge feature", "git stash feature"], 1, "git checkout -b <name> (or git switch -c <name>) creates and switches in one step."),
    ("In the ACID properties of database transactions, what does the letter I stand for?", M, ["Integrity", "Isolation", "Indexing", "Inheritance"], 1, "Isolation means concurrent transactions do not interfere with each other."),
    ("What is the worst-case time complexity of quicksort?", H, ["O(n)", "O(n log n)", "O(n^2)", "O(log n)"], 2, "With consistently bad pivots the partitions are unbalanced, giving O(n^2)."),
    ("Which HTTP method is idempotent and normally used to replace a resource entirely?", H, ["POST", "PUT", "PATCH", "CONNECT"], 1, "PUT replaces the target resource, and repeating the same request has the same effect."),
]

CODING = [
    ("Write a function reverse_string(s) that returns the string s reversed.", E,
     "def reverse_string(s):\n    # your code here\n    pass\n",
     [{"input": "hello", "output": "olleh"}, {"input": "", "output": ""}],
     "Slicing with s[::-1] reverses a string in one step."),
    ("Write a function is_palindrome(s) that returns True if s reads the same forwards and backwards, ignoring case.", M,
     "def is_palindrome(s):\n    # your code here\n    pass\n",
     [{"input": "Level", "output": True}, {"input": "portal", "output": False}],
     "Normalise the case, then compare the string with its reverse."),
    ("Write a function two_sum(nums, target) that returns the indices of the two numbers that add up to target.", M,
     "def two_sum(nums, target):\n    # your code here\n    pass\n",
     [{"input": [[2, 7, 11, 15], 9], "output": [0, 1]}],
     "Store each number's index in a dict and look up target - n as you iterate: O(n) time."),
]


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def _category(db, name: str) -> Category:
    existing = db.scalar(select(Category).where(Category.name == name))
    if existing:
        return existing
    category = Category(name=name, slug=_slug(name))
    db.add(category)
    db.flush()
    return category


def _exists(db, category_id: int, prompt: str) -> bool:
    return db.scalar(select(Question.id).where(Question.category_id == category_id, Question.prompt == prompt)) is not None


def main() -> int:
    init_db()
    created = 0
    with SessionLocal() as db:
        aptitude, technical, coding = _category(db, "Aptitude"), _category(db, "Technical MCQ"), _category(db, "Coding")
        _category(db, "Advanced DSA")  # intentionally EMPTY: test IT_07 (category with no questions)

        for category, rows in ((aptitude, APTITUDE), (technical, TECHNICAL)):
            for prompt, difficulty, options, correct, explanation in rows:
                if _exists(db, category.id, prompt):
                    continue
                db.add(Question(
                    category_id=category.id, type=QuestionType.MCQ, prompt=prompt, difficulty=difficulty,
                    explanation=explanation,
                    options=[QuestionOption(text=t, is_correct=(i == correct), position=i) for i, t in enumerate(options)],
                ))
                created += 1

        for prompt, difficulty, starter, tests, explanation in CODING:
            if _exists(db, coding.id, prompt):
                continue
            db.add(Question(
                category_id=coding.id, type=QuestionType.CODING, prompt=prompt, difficulty=difficulty,
                explanation=explanation, starter_code=starter, test_cases=json.dumps(tests),
            ))
            created += 1
        db.commit()
    print(f"Question bank: {created} questions created.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
