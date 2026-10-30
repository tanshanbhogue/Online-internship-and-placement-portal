import { useState } from "react";
import { Link, NavLink } from "react-router-dom";

// Auth is optional (it arrives with story #19), so it is looked up without a hard import.
const authModules = import.meta.glob("../context/AuthContext.jsx", { eager: true });
const useAuth = Object.values(authModules)[0]?.useAuth;
const useNoAuth = () => null;
const useAuthSafe = useAuth || useNoAuth; // stable for the lifetime of the app, so hook order never changes

const navModules = import.meta.glob("../nav/*.nav.js", { eager: true });
const extraNavItems = Object.values(navModules)
  .flatMap((m) => (Array.isArray(m.default) ? m.default : [m.default]))
  .filter(Boolean)
  .sort((a, b) => (a.order ?? 100) - (b.order ?? 100));

const linkClass = ({ isActive }) => (isActive ? "active" : undefined);

export default function NavBar() {
  const auth = useAuthSafe();
  const [open, setOpen] = useState(false);
  const user = auth?.user;
  const close = () => setOpen(false);
  const visibleExtras = extraNavItems.filter(
    (item) =>
      item.access === "authenticated" ||
      (item.access === "student" && auth?.isStudent) ||
      (item.access === "admin" && auth?.isAdmin)
  );

  return (
    <header className="navbar">
      <nav className="navbar-inner" aria-label="Main">
        <Link to="/" className="brand" onClick={close}>
          Internship &amp; Placement Prep
        </Link>
        <button
          type="button"
          className="nav-toggle"
          aria-expanded={open}
          aria-controls="nav-links"
          onClick={() => setOpen((v) => !v)}
        >
          {open ? "Close" : "Menu"}
        </button>
        <ul id="nav-links" className={`nav-links${open ? " open" : ""}`}>
          {user ? (
            <>
              <li><NavLink to="/internships" className={linkClass} onClick={close}>Internships</NavLink></li>
              {auth.isStudent && (
                <>
                  <li><NavLink to="/applications" className={linkClass} onClick={close}>My Applications</NavLink></li>
                  <li><NavLink to="/practice" end className={linkClass} onClick={close}>Practice</NavLink></li>
                  <li><NavLink to="/practice/history" className={linkClass} onClick={close}>Practice History</NavLink></li>
                </>
              )}
              {auth.isAdmin && (
                <li><NavLink to="/admin/question-bank" className={linkClass} onClick={close}>Admin Question Bank</NavLink></li>
              )}
              {visibleExtras.map((item) => (
                <li key={item.to}>
                  <NavLink to={item.to} end={item.end} className={linkClass} onClick={close}>{item.label}</NavLink>
                </li>
              ))}
              <li className="nav-user">{user.name}</li>
              <li>
                <button type="button" onClick={() => { close(); auth.logout(); }}>
                  Log out
                </button>
              </li>
            </>
          ) : (
            <>
              <li><NavLink to="/login" className={linkClass} onClick={close}>Login</NavLink></li>
              <li><NavLink to="/register" className={linkClass} onClick={close}>Register</NavLink></li>
            </>
          )}
        </ul>
      </nav>
    </header>
  );
}
