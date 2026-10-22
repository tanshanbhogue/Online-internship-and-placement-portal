CREATE TABLE IF NOT EXISTS categories (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS questions (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id    INTEGER NOT NULL,
    question_type  TEXT NOT NULL CHECK (question_type IN ('MCQ', 'CODING')),
    question_text  TEXT NOT NULL,
    options        TEXT,            -- JSON list of choices, MCQ only
    correct_answer TEXT,            -- server-side only, never sent to client
    test_cases     TEXT,            -- JSON, coding questions only
    explanation    TEXT,
    difficulty     TEXT NOT NULL DEFAULT 'Medium'
                   CHECK (difficulty IN ('Easy', 'Medium', 'Hard')),
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

CREATE INDEX IF NOT EXISTS idx_questions_category ON questions(category_id);

INSERT OR IGNORE INTO categories (name) VALUES
    ('Aptitude'),
    ('Technical MCQ'),
    ('Coding');