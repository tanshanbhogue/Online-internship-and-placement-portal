// ==============================================================================
// FILE   : frontend/src/components/auth/RegisterForm.jsx
// STORY  : #14 Student Registration  [FR-001; SEC-02, SEC-08, SEC-09]
// OWNER  : Eshwar (@ESHWAR1024)   |   MERGE ORDER: Phase 2
// ==============================================================================
//
// PURPOSE
//   Registration form component (presentation + validation, no routing).
//
// PROPS
//   onSuccess(user) callback, optional initial values.
//
// BEHAVIOUR
//   Fields: Name, Email, Password (type=password, autoComplete="new-password"), College (optional), Batch (optional). Show strength hints live using passwordProblems.
//   On submit run client validation (blank fields -> inline field errors, test UT_04); then call registerStudent.
//   Map server 422 `fields` to inline errors and 409 duplicate_email to an email error "Email already exists" plus a link to /login (use case A2).
//   Disable the button while submitting. Never log or store the password; clear it from state after success.
//
// A11Y/NFR003
//   Labels bound to inputs, errors announced with role=alert, layout works at 360px width.
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================
