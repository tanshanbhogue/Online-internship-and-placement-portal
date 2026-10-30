import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";

import App from "./App.jsx";
import "./styles/global.css";

// Sprint 2: every other stylesheet dropped into src/styles/ is loaded automatically (after global.css).
import.meta.glob("./styles/*.css", { eager: true });

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);
