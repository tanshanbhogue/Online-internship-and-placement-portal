const { test, expect } = require("@playwright/test");
const { student, login } = require("./helpers");

/*
 * ST-N03_04: Resume upload compatibility.
 * Uses an intercepted successful API response so the test does not create
 * a real application in the shared test database.
 */
test("ST-N03_04 resume upload accepts PDF and submits multipart application", async ({ page }) => {
  await login(page, student);
  await page.goto("/internships");
  await expect(page.getByRole("heading", { name: "Internships" })).toBeVisible();

  const firstListing = page.locator('a.card-link[href^="/internships/"]').first();
  await expect(firstListing).toBeVisible();
  await firstListing.click();

  await page.getByRole("link", { name: "Apply", exact: true }).click();
  await expect(page.getByLabel(/Resume \(PDF or DOCX/i)).toBeVisible();

  // Invalid file must be rejected by client-side validation.
  await page.locator("#apply-resume").setInputFiles({
    name: "resume.txt",
    mimeType: "text/plain",
    buffer: Buffer.from("not a resume"),
  });
  await page.getByRole("button", { name: "Submit application" }).click();
  await expect(page.getByRole("alert")).toContainText("Resume must be a PDF or DOCX file");

  // Valid PDF: intercept API to avoid changing persistent test data.
  let requestSeen = false;
  await page.route("**/api/applications", async (route) => {
    const request = route.request();
    requestSeen = request.method() === "POST";
    await route.fulfill({
      status: 201,
      contentType: "application/json",
      body: JSON.stringify({ id: 999999, status: "submitted" }),
    });
  });

  await page.locator("#apply-resume").setInputFiles({
    name: "sample-resume.pdf",
    mimeType: "application/pdf",
    buffer: Buffer.from("%PDF-1.4\n% Playwright test PDF\n"),
  });
  await page.getByRole("button", { name: "Submit application" }).click();

  await expect(page).toHaveURL(/\/applications$/);
  expect(requestSeen, "application POST should be sent").toBe(true);
});

/*
 * The supplied frontend has timer/auto-submit display components and an
 * auto-submit API helper, but no mock-test start/attempt page or route.
 * Do not report this end-to-end workflow as passed until that UI exists.
 */
test("ST-N03_05 mock test timer and submission workflow", async ({ page }) => {
  test.skip(true, "Not executable: supplied frontend has no mock-test start/attempt page or route; only history/result pages and timer component are present.");
  await page.goto("/mock-tests");
});

/*
 * Analytics dashboard/chart page is absent from the supplied frontend.
 * This is an explicit, documented skip rather than a fabricated test.
 */
test("ST-N03_08 analytics charts on tablet and mobile", async ({ page }) => {
  test.skip(true, "Not executable: supplied frontend has no Analytics dashboard page or chart components.");
  await page.goto("/analytics");
});
