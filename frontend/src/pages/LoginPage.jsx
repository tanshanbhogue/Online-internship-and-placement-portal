
import { Link, useLocation, useNavigate } from "react-router-dom";
import LoginForm from "../components/auth/LoginForm.jsx";

export default function LoginPage() {
  const location = useLocation();
  const navigate = useNavigate();

  const registered = location.state?.registered;
  const sessionExpired = location.state?.sessionExpired;

  function handleLoginSuccess(user) {
    const destination = location.state?.from;
    const defaultPath =
      user?.role === "admin" ? "/admin/question-bank" : "/internships";

    const redirectTo = destination
      ? `${destination.pathname || ""}${destination.search || ""}${destination.hash || ""}`
      : defaultPath;

    navigate(redirectTo, { replace: true });
  }

  return (
    <main>
      <h1>Student Login</h1>

      {registered && (
        <p role="status">Registration successful, please log in.</p>
      )}

      {sessionExpired && (
        <p role="alert">Your session expired. Please log in again.</p>
      )}

      <LoginForm onSuccess={handleLoginSuccess} />

      <p>
        Don't have an account? <Link to="/register">Register here</Link>
      </p>
    </main>
  );
}
