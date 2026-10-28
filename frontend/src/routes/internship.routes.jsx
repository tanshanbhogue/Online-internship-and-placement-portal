

import InternshipDetailPage from "../pages/InternshipDetailPage.jsx";
import InternshipListPage from "../pages/InternshipListPage.jsx";

export default [
  { path: "/internships", element: <InternshipListPage />, access: "authenticated" },
  { path: "/internships/:id", element: <InternshipDetailPage />, access: "authenticated" },
];
