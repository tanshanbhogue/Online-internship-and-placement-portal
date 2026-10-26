// ==============================================================================
// FILE   : frontend/src/context/AuthContext.jsx
// STORY  : #19 Student Login and Session Validation  [FR-001; SEC-01, SEC-03, SEC-04, SEC-05, SEC-07]
// OWNER  : Sanskar (@sanskarghenappagol)   |   MERGE ORDER: Phase 3
// ==============================================================================
//
// PURPOSE
//   Global session state for the SPA.
//
// EXPOSES
//   <AuthProvider> and hook useAuth() -> { user, loading, login(email, password), logout(), isAdmin, isStudent }
//   On mount call fetchMe(); 401 means 'not logged in' (user = null, loading false) and is not an error message.
//   Listens for the window "auth:expired" event (from api/client.js): clear user and navigate to /login with a 'session expired' notice.
//
// RULES
//   Hold the user object only in React state (never localStorage/sessionStorage); the cookie is the credential.
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import * as sessionApi from "../api/sessionApi";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  // The user lives only in React state. The HttpOnly cookie is the credential; nothing goes in web storage.
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // Restore the session on page load. A 401 simply means "not logged in" and is not an error message.
  useEffect(() => {
    let cancelled = false;
    sessionApi
      .fetchMe()
      .then((me) => {
        if (!cancelled) setUser(me);
      })
      .catch(() => {
        if (!cancelled) setUser(null);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  // api/client.js fires this when a protected call comes back 401 not_authenticated.
  useEffect(() => {
    const onExpired = () => {
      setUser(null);
      navigate("/login", { replace: true, state: { expired: true } });
    };
    window.addEventListener("auth:expired", onExpired);
    return () => window.removeEventListener("auth:expired", onExpired);
  }, [navigate]);

  const login = useCallback(async (email, password) => {
    const { user: loggedIn } = await sessionApi.login({ email, password });
    setUser(loggedIn);
    return loggedIn;
  }, []);

  const logout = useCallback(async () => {
    try {
      await sessionApi.logout();
    } finally {
      setUser(null);
      navigate("/login", { replace: true });
    }
  }, [navigate]);

  const value = useMemo(
    () => ({
      user,
      loading,
      login,
      logout,
      isAdmin: user?.role === "admin",
      isStudent: user?.role === "student",
    }),
    [user, loading, login, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside <AuthProvider>");
  return context;
}
