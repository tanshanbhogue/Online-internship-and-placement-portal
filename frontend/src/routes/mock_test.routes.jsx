// Story #23 Timed Mock Tests - owner: Eshwar (ESHWAR1024)
// File: frontend/src/routes/mock_test.routes.jsx
// Auto-discovered by App.jsx. Result and history routes (/mock-tests/result/:id, /mock-tests/history) belong to story #25.
import MockTestAttemptPage from "../pages/MockTestAttemptPage.jsx";
import MockTestInstructionsPage from "../pages/MockTestInstructionsPage.jsx";
import MockTestListPage from "../pages/MockTestListPage.jsx";

export default [
  { path: "/mock-tests", element: <MockTestListPage />, access: "student" },
  { path: "/mock-tests/test/:testId", element: <MockTestInstructionsPage />, access: "student" },
  { path: "/mock-tests/attempt/:attemptId", element: <MockTestAttemptPage />, access: "student" },
];
