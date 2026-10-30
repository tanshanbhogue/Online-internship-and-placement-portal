// Story #25 Score and Answer Analysis - owner: Sinchana (sinchanaurs1104)
// File: frontend/src/routes/mock_result.routes.jsx   (auto-discovered by App.jsx)
import MockTestHistoryPage from "../pages/MockTestHistoryPage.jsx";
import MockTestResultPage from "../pages/MockTestResultPage.jsx";

export default [
  { path: "/mock-tests/history", element: <MockTestHistoryPage />, access: "student" },
  { path: "/mock-tests/result/:attemptId", element: <MockTestResultPage />, access: "student" },
];
