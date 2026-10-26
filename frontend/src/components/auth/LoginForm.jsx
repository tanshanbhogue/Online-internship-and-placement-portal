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

import { useState } from "react";

import { useAuth } from "../../context/AuthContext.jsx";
import { isValidEmail } from "../../utils/validators.js";
import StatusMessage from "../common/StatusMessage.jsx";

export default function LoginForm({ onSuccess }) {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    if (!email.trim() || !password) {
      setError("Please enter your email and password");
      return;
    }
    if (!isValidEmail(email)) {
      setError("Please enter a valid email address");
      return;
    }
    setSubmitting(true);
    try {
      const user = await login(email.trim(), password);
      setPassword("");
      onSuccess?.(user);
    } catch (err) {
      if (err.status === 429) {
        setError("Too many attempts, try again later");
      } else if (err.status === 401) {
        setError(err.message); // exactly as received: never says whether the email exists
      } else {
        setError(err.message || "Something went wrong");
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} noValidate>
      {error && <StatusMessage kind="error" message={error} />}
      <div className="field">
        <label htmlFor="login-email">Email</label>
        <input
          id="login-email"
          type="email"
          autoComplete="username"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
      </div>
      <div className="field">
        <label htmlFor="login-password">Password</label>
        <input
          id="login-password"
          type="password"
          autoComplete="current-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
      </div>
      <button className="btn" type="submit" disabled={submitting}>
        {submitting ? "Logging in..." : "Log in"}
      </button>
    </form>
  );
}
