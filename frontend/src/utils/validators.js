// ==============================================================================
// FILE   : frontend/src/utils/validators.js
// STORY  : #14 Student Registration  [FR-001; SEC-02, SEC-08, SEC-09]
// OWNER  : Eshwar (@ESHWAR1024)   |   MERGE ORDER: Phase 2
// ==============================================================================
//
// PURPOSE
//   Client-side form validators that mirror the server rules (UX only; the server is authoritative).
//
// EXPOSES
//   isValidEmail(value) -> boolean
//   passwordProblems(value) -> string[]   (same 4 rules as backend: length>=8, letter, digit, symbol)
//   requiredFields(values, names) -> { field: "This field is required" }
//
// USED BY
//   RegisterForm.jsx (#14). Story #19's LoginForm may import isValidEmail.
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================
