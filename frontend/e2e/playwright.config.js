
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
