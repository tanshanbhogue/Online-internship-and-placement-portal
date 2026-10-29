import PracticeHistoryPage from "../pages/PracticeHistoryPage.jsx";
import PracticeResultPage from "../pages/PracticeResultPage.jsx";
import PracticeSessionPage from "../pages/PracticeSessionPage.jsx";

export default [
  { path: "/practice/session/:sessionId", element: <PracticeSessionPage />, access: "student" },
  { path: "/practice/result/:sessionId", element: <PracticeResultPage />, access: "student" },
  { path: "/practice/history", element: <PracticeHistoryPage />, access: "student" },
];
