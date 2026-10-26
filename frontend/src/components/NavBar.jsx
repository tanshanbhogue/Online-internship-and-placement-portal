// ==============================================================================
// FILE   : frontend/src/components/NavBar.jsx
// STORY  : Foundation - shared scaffold (chore, no backlog issue)
// OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 0
// ==============================================================================
//
// PURPOSE
//   Top navigation bar shown on every authenticated page.
//
// CODE TO WRITE
//   Static links (plain strings, no imports from feature modules): Internships (/internships), My Applications (/applications),
//   Practice (/practice), Practice History (/practice/history), Admin Question Bank (/admin/question-bank, shown only to admins).
//   Reads the current user through an optional `useAuth` found via import.meta.glob("../context/AuthContext.jsx"); if auth is not available yet show only the brand and Login/Register links.
//   Logout button calls logout() from the auth context when available. Responsive: collapses to a menu button under 640px (NFR003).
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================

import { useState } from "react";
import { Link, NavLink } from "react-router-dom";

// Auth is optional (it arrives with story #19), so it is looked up without a hard import.
const authModules = import.meta.glob("../context/AuthContext.jsx", { eager: true });
const useAuth = Object.values(authModules)[0]?.useAuth;
const useNoAuth = () => null;
const useAuthSafe = useAuth || useNoAuth; // stable for the lifetime of the app, so hook order never changes

const linkClass = ({ isActive }) => (isActive ? "active" : undefined);

export default function NavBar() {
  const auth = useAuthSafe();
  const [open, setOpen] = useState(false);
  const user = auth?.user;
  const close = () => setOpen(false);

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
