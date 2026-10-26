// ==============================================================================
// FILE   : frontend/src/pages/LoginPage.jsx
// STORY  : #19 Student Login and Session Validation  [FR-001; SEC-01, SEC-03, SEC-04, SEC-05, SEC-07]
// OWNER  : Sanskar (@sanskarghenappagol)   |   MERGE ORDER: Phase 3
// ==============================================================================
//
// PURPOSE
//   Page at /login.
//
// BEHAVIOUR
//   Renders LoginForm and a link to /register. Shows 'Registration successful, please log in' when router state.registered is true and 'Your session expired' when redirected by auth:expired.
//   After success go to router state.from or /internships (students) / /admin/question-bank (admins).
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================

import { Link, Navigate, useLocation } from "react-router-dom";

import LoginForm from "../components/auth/LoginForm.jsx";
import StatusMessage from "../components/common/StatusMessage.jsx";
import { useAuth } from "../context/AuthContext.jsx";

export default function LoginPage() {
  const { user, loading } = useAuth();
  const location = useLocation();
  const state = location.state || {};

  // Already logged in (or just logged in): go where they were headed, else their role's home.
  if (!loading && user) {
    const fallback = user.role === "admin" ? "/admin/question-bank" : "/internships";
    const from = state.from;
    const target = from?.pathname ? `${from.pathname}${from.search || ""}` : fallback;
    return <Navigate to={target} replace />;
  }

  return (
    <div className="page-narrow card">
      <h1>Log in</h1>
      {state.registered && <StatusMessage kind="success" message="Registration successful, please log in" />}
      {state.expired && <StatusMessage kind="error" message="Your session expired, please log in again" />}
      <LoginForm />
      <p className="small" style={{ marginTop: "1rem" }}>
        New here? <Link to="/register">Create an account</Link>
      </p>
    </div>
  );
}
