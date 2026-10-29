

import ApplyPage from "../pages/ApplyPage.jsx";
import MyApplicationsPage from "../pages/MyApplicationsPage.jsx";

export default [
  { path: "/internships/:id/apply", element: <ApplyPage />, access: "student" },
  { path: "/applications", element: <MyApplicationsPage />, access: "student" },
];
