import { Component } from "react";
import { Link, Navigate, Route, Routes } from "react-router-dom";

import NavBar from "./components/NavBar.jsx";

// 1. Every src/routes/*.routes.jsx default-exports an array of { path, element, access }.
const routeModules = import.meta.glob("./routes/*.routes.jsx", { eager: true });
const routes = Object.values(routeModules).flatMap((m) => m.default);

// 2. Story #19 pieces are optional so a missing file never breaks the build.
const authModules = import.meta.glob("./context/AuthContext.jsx", { eager: true });
const guardModules = import.meta.glob("./components/auth/ProtectedRoute.jsx", { eager: true });
const AuthProvider = Object.values(authModules)[0]?.AuthProvider;
const ProtectedRoute = Object.values(guardModules)[0]?.default;

function withAuth(children) {
  return AuthProvider ? <AuthProvider>{children}</AuthProvider> : children;
}

function guard(route) {
  return ProtectedRoute ? <ProtectedRoute access={route.access}>{route.element}</ProtectedRoute> : route.element;
}

function NotFound() {
  return (
    <div className="page-medium card">
      <h1>Page not found</h1>
      <p>The page you are looking for does not exist.</p>
      <Link to="/internships">Go to internships</Link>
    </div>
  );
}

// 4. A crash shows a generic message only: never a stack trace in the UI (SEC-19).
class ErrorBoundary extends Component {
  state = { failed: false };

  static getDerivedStateFromError() {
    return { failed: true };
  }

  componentDidCatch() {
    // Intentionally empty: details stay out of the UI.
  }

  render() {
    if (this.state.failed) {
      return (
        <div className="page-medium card" role="alert">
          <h1>Something went wrong</h1>
          <p>Please refresh the page and try again.</p>
        </div>
      );
    }
    return this.props.children;
  }
}

export default function App() {
  return withAuth(
    <>
      <NavBar />
      <main className="container">
        <ErrorBoundary>
          <Routes>
            <Route path="/" element={<Navigate to="/internships" replace />} />
            {routes.map((route) => (
              <Route key={route.path} path={route.path} element={guard(route)} />
            ))}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </ErrorBoundary>
      </main>
    </>
  );
}
