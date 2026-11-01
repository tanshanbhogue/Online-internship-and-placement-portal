// Story #29 Cross-Browser and Responsive Testing - owner: Tanmayi (tanshanbhogue)
// File: frontend/e2e/tests/smoke.spec.js
//
// The student journey works the same in every browser: log in, see the listings, take a one-question practice-sized look at
// the mock-test list, open the analytics and log out. Whole-product API journeys are in backend/tests/test_e2e_journeys.py (story #30).
const { test, expect } = require("@playwright/test");
const { student, login } = require("./helpers");

test("login, browse, analytics and logout", async ({ page }) => {
  await login(page, student);
  await page.goto("/internships");
  await expect(page.getByRole("heading").first()).toBeVisible();
  await page.goto("/mock-tests");
  await expect(page.getByText(/Quick Check/i).first()).toBeVisible();
  await page.goto("/analytics");
  await expect(page.getByText(/average|attempts/i).first()).toBeVisible();
  if (await page.locator(".nav-toggle").isVisible()) await page.locator(".nav-toggle").click();
  await page.getByRole("button", { name: /log out/i }).click();
  await expect(page).toHaveURL(/\/login|\/$/);
});

test("a guest is sent to the login page", async ({ page }) => {
  await page.goto("/mock-tests");
  await expect(page).toHaveURL(/\/login/);
});
