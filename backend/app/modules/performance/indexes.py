from sqlalchemy import text

INDEXES: list[tuple[str, str, list[str]]] = [
    ("ix_perf_practice_sessions_student_status_completed", "practice_sessions", ["student_id", "status", "completed_at"]),
    ("ix_perf_mock_attempts_student_status_submitted", "mock_attempts", ["student_id", "status", "submitted_at"]),
    ("ix_perf_mock_attempts_status_ends_at", "mock_attempts", ["status", "ends_at"]),
    ("ix_perf_mock_attempts_test_status_score", "mock_attempts", ["test_id", "status", "score_percent"]),
    ("ix_perf_applications_student_applied", "applications", ["student_id", "applied_at"]),
    ("ix_perf_internships_status_deadline", "internships", ["status", "deadline"]),
    ("ix_perf_questions_category_active", "questions", ["category_id", "is_active"]),
]


def ensure_indexes(engine) -> list[str]:
    """Create any missing index; returns the names that were requested for existing tables."""
    from sqlalchemy import inspect

    existing_tables = set(inspect(engine).get_table_names())
    done = []
    with engine.begin() as connection:
        for name, table, columns in INDEXES:
            if table not in existing_tables:
                continue
            # names and columns come from the constant list above, never from user input
            connection.execute(text(f'CREATE INDEX IF NOT EXISTS "{name}" ON "{table}" ({", ".join(columns)})'))
            done.append(name)
    return done
