
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../../context/AuthContext.jsx";

export default function ProtectedRoute({ access = "authenticated", children }) {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (access === "public") {
    return children;
  }

  if (loading) {
    return <p role="status">Loading...</p>;
  }

  if (!user) {
    return (
      <Navigate
        to="/login"
        replace
        state={{ from: location }}
      />
    );
  }

  if (access === "student" && user.role !== "student") {
    return <ForbiddenPage />;
  }

  if (access === "admin" && user.role !== "admin") {
    return <ForbiddenPage />;
  }

  return children;
}

function ForbiddenPage() {
  return (
    <main>
      <h1>403 - Access denied</h1>
      <p>You do not have permission to view this page.</p>
    </main>
  );
}
