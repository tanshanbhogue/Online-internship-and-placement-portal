// ==============================================================================
// FILE   : frontend/vite.config.js
// STORY  : Foundation - shared scaffold (chore, no backlog issue)
// OWNER  : Sinchana (@sinchanaurs1104)   |   MERGE ORDER: Phase 0
// ==============================================================================
//
// PURPOSE
//   Vite configuration.
//
// CODE TO WRITE
//   plugins: [react()]. server: { port: 5173, proxy: { "/api": { target: "http://localhost:8000", changeOrigin: false } } }.
//   The proxy keeps the browser same-origin so the HttpOnly session cookie works without CORS tricks.
//
// ==============================================================================
// CLAUDE: implement this file in place. KEEP this header comment at the top of the file, write the code below it, and do not edit files owned by other stories.
// ==============================================================================

import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // Same-origin proxy: the HttpOnly session cookie works without any CORS tricks.
    proxy: { "/api": { target: "http://localhost:8000", changeOrigin: false } },
  },
});
