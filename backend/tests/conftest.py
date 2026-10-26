# ==============================================================================
# FILE   : backend/tests/conftest.py
# STORY  : Foundation - shared scaffold (chore, no backlog issue)
# OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 0
# ==============================================================================
#
# PURPOSE
#   Shared pytest fixtures used by every story's tests.
#
# FIXTURES TO WRITE
#   - engine / db: fresh in-memory SQLite (StaticPool, foreign keys ON) per test; create_all after load_all_models(); drop afterwards.
#   - client: fastapi TestClient(app) with get_db overridden to the test session; settings.COOKIE_SECURE forced False so cookies work over http.
#   - make_user(email, password, role="student", name="Test User"): factory that hashes with app.core.security.hash_password and inserts a User.
#   - login(client, email, password): POSTs /api/auth/login and returns the response (the TestClient keeps the cookie jar).
#   - student_client / admin_client: a TestClient already logged in as a student / admin (separate cookie jars, so two clients can coexist for isolation tests).
#   - sample data helpers are created in each story's own test file, not here.
#   IMPORTANT: fixtures that need modules from later phases (User model, hashing, login, Internship, Question...) must import them INSIDE the fixture
#   function so this file works at Phase 0 before those modules exist; they should pytest.skip with a clear message if the import fails.
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================
