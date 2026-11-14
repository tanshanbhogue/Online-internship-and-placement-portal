import AdminApplicationsPage from "../pages/admin/AdminApplicationsPage.jsx";
import AdminInternshipsPage from "../pages/admin/AdminInternshipsPage.jsx";

export default [
    { path: "/admin/internships", element: <AdminInternshipsPage />, access: "admin" },
    { path: "/admin/applications", element: <AdminApplicationsPage />, access: "admin" },
];
