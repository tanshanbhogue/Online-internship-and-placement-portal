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

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function isValidEmail(value) {
  return typeof value === "string" && value.length <= 254 && EMAIL_RE.test(value.trim());
}

// Mirrors backend app/core/security.py (UX only; the server is authoritative).
export function passwordProblems(value) {
  const password = value || "";
  const problems = [];
  if (password.length < 8) problems.push("Password must be at least 8 characters");
  if (password.length > 128) problems.push("Password must be at most 128 characters");
  if (!/\p{L}/u.test(password)) problems.push("Password must contain a letter");
  if (!/\p{Nd}/u.test(password)) problems.push("Password must contain a digit");
  if (!/[^\p{L}\p{N}\s]/u.test(password)) problems.push("Password must contain a symbol");
  return problems;
}

export function requiredFields(values, names) {
  const errors = {};
  for (const name of names) {
    const value = values?.[name];
    if (value === undefined || value === null || String(value).trim() === "") {
      errors[name] = "This field is required";
    }
  }
  return errors;
}
