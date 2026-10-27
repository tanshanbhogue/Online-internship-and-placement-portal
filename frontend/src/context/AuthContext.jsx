
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { useNavigate } from "react-router-dom";
import { ApiError } from "../api/client";
import { fetchMe, login as loginRequest, logout as logoutRequest } from "../api/sessionApi";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const login = useCallback(async (email, password) => {
    const result = await loginRequest({ email, password });
    setUser(result.user);
    return result.user;
  }, []);

  const logout = useCallback(async () => {
    try {
      await logoutRequest();
    } finally {
      setUser(null);
      navigate("/login", { replace: true });
    }
  }, [navigate]);

  useEffect(() => {
    let active = true;

    fetchMe()
      .then((currentUser) => {
        if (active) setUser(currentUser);
      })
      .catch((error) => {
        if (active) {
          setUser(null);

          if (!(error instanceof ApiError) || error.status !== 401) {
            // Keep sensitive server details out of the UI.
          }
        }
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    const handleExpired = () => {
      setUser(null);
      navigate("/login", {
        replace: true,
        state: { sessionExpired: true },
      });
    };

    window.addEventListener("auth:expired", handleExpired);
    return () => window.removeEventListener("auth:expired", handleExpired);
  }, [navigate]);

  const value = useMemo(() => ({
    user,
    loading,
    login,
    logout,
    isAdmin: user?.role === "admin",
    isStudent: user?.role === "student",
  }), [user, loading, login, logout]);

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }

  return context;
}
