import MockTestHistoryPage from "../pages/MockTestHistoryPage.jsx";
import MockTestResultPage from "../pages/MockTestResultPage.jsx";

export default [
  { path: "/mock-tests/history", element: <MockTestHistoryPage />, access: "student" },
  { path: "/mock-tests/result/:attemptId", element: <MockTestResultPage />, access: "student" },
];
