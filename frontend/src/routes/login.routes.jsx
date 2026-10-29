import LoginPage from "../pages/LoginPage.jsx";

const loginRoutes = [
  {
    path: "/login",
    element: <LoginPage />,
    access: "public",
  },
];

export default loginRoutes;