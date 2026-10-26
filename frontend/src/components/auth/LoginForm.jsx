// ==============================================================================
// FILE   : frontend/src/components/auth/LoginForm.jsx
// STORY  : #19 Student Login and Session Validation  [FR-001; SEC-01, SEC-03, SEC-04, SEC-05, SEC-07]
// OWNER  : Sanskar (@sanskarghenappagol)   |   MERGE ORDER: Phase 3
// ==============================================================================
//
// PURPOSE
//   Login form component.
//
// BEHAVIOUR
//   Email + Password (type=password, autoComplete="current-password"). Calls useAuth().login. Shows the server's generic message "Invalid username or password" exactly as received,
//   a 'Too many attempts, try again later' message for 429, and disables the button while submitting. Never reveals whether the email exists.
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================
