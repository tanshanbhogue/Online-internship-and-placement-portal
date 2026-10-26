# ==============================================================================
# FILE   : backend/app/modules/auth/register_service.py
# STORY  : #14 Student Registration  [FR-001; SEC-02, SEC-08, SEC-09]
# OWNER  : Eshwar (@ESHWAR1024)   |   MERGE ORDER: Phase 2
# ==============================================================================
#
# PURPOSE
#   Business logic for creating a student account (use case 'Register & Login', basic flow steps 3-7).
#
# EXPOSES
#   register_student(db: Session, data: RegisterRequest) -> User
#
# FLOW TO IMPLEMENT
#   1. normalise: strip name, lowercase+strip email.
#   2. problems = core.security.validate_password_strength(data.password); if any -> raise ValidationFailed(fields={"password": problems}).
#   3. if a user with that email exists -> raise DuplicateEmail() ("Email already exists", test IT_02). Use ORM filter (parameterised, SEC-09).
#   4. create User(role=Role.STUDENT always, password_hash=hash_password(...)); db.add; commit.
#   5. if commit raises IntegrityError (two simultaneous registrations) -> rollback and raise DuplicateEmail().
#   6. return the user.
#
# RULES
#   Do not log the request. Role is hard-coded to STUDENT; admin creation is not possible through this path (SEC-07).
#
# ==============================================================================
# CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
# ==============================================================================
