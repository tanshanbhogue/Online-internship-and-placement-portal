// Story #29 Cross-Browser and Responsive Testing - owner: Tanmayi (tanshanbhogue)
// File: frontend/e2e/playwright.config.js
//
// Run (portal already running, database seeded with backend/scripts/seed_ui_test_data.py):
//   cd frontend/e2e && npm install && npx playwright install chromium firefox webkit && npx playwright test
// Environment: E2E_BASE_URL (default http://localhost:5173), E2E_STUDENT_EMAIL / E2E_STUDENT_PASSWORD, E2E_ADMIN_EMAIL / E2E_ADMIN_PASSWORD.
// Browsers: Chrome/Edge (Chromium engine, "msedge" channel when Microsoft Edge is installed), Firefox, Safari (WebKit engine).
// Sizes: phone 360x740, tablet 768x1024, desktop 1280x800 (the three layouts of the stylesheet's breakpoints).
const { defineConfig, devices } = require("@playwright/test");

const sizes = {
  desktop: { width: 1280, height: 800 },
  tablet: { width: 768, height: 1024 },
  mobile: { width: 360, height: 740 },
};

const engines = {
  chromium: { use: devices["Desktop Chrome"] },
  firefox: { use: devices["Desktop Firefox"] },
  webkit: { use: devices["Desktop Safari"] },
  edge: { use: { ...devices["Desktop Edge"], channel: "msedge" } },
};

const projects = [];
for (const [engine, base] of Object.entries(engines)) {
  for (const [size, viewport] of Object.entries(sizes)) {
    projects.push({
      name: `${engine}-${size}`,
      use: { ...base.use, viewport, hasTouch: size !== "desktop", isMobile: false },
    });
  }
}

module.exports = defineConfig({
  testDir: "./tests",
  timeout: 45_000,
  retries: 0,
  reporter: [["list"], ["html", { open: "never" }]],
  use: {
    baseURL: process.env.E2E_BASE_URL || "http://localhost:5173",
    screenshot: "only-on-failure",
    trace: "retain-on-failure",
  },
  // Edge only exists on machines that have it; select it explicitly with --project=edge-desktop.
  projects: projects.filter((p) => !p.name.startsWith("edge") || process.env.E2E_EDGE === "1"),
});
