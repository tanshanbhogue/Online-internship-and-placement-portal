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
