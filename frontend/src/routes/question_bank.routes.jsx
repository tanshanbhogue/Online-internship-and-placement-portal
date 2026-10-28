import AdminQuestionBankPage from "../pages/admin/AdminQuestionBankPage.jsx";
import PracticeHomePage from "../pages/PracticeHomePage.jsx";

export default [
  { path: "/practice", element: <PracticeHomePage />, access: "student" },
  { path: "/admin/question-bank", element: <AdminQuestionBankPage />, access: "admin" },
];