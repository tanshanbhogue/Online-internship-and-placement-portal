const { test, expect } = require("@playwright/test");
const { student, login } = require("./helpers");

/*
 * ST-N03_04 — Resume upload on each browser.
 * API responses are mocked so the test is repeatable and does not create
 * real applications or modify the test database.
 */
test("ST-N03_04 resume upload validation and application submission", async ({ page }) => {
  const internship = {
    id: 42,
    title: "Playwright Test Internship",
    company: "Test Company",
    location: "Remote",
    domain: "Software",
    stipend_per_month: 10000,
    duration_months: 3,
    deadline: "2027-12-31",
    description: "Test internship description",
    eligibility: "Open to students",
    short_description: "Browser automation test listing",
    is_open: true,
  };

  let submittedRequest;
  await page.route("**/api/internships/42", (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(internship) })
  );
  await page.route("**/api/internships**", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ items: [internship], total: 1, page: 1, page_size: 12 }),
    })
  );
  await page.route("**/api/applications/check/42", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ internship_id: 42, applied: false, status: null, applied_at: null }),
    })
  );
  await page.route("**/api/applications/mine", (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [] }) })
  );
  await page.route("**/api/applications", async (route) => {
    if (route.request().method() !== "POST") return route.continue();
    submittedRequest = route.request();
    await route.fulfill({
      status: 201,
      contentType: "application/json",
      body: JSON.stringify({ id: 9876, internship_id: 42, status: "submitted" }),
    });
  });

  await login(page, student);
  await page.goto("/internships/42/apply");

  const resume = page.locator("#apply-resume");
  await expect(resume).toBeVisible();

  // Unsupported extension must be rejected in the browser.
  await resume.setInputFiles({
    name: "resume.txt",
    mimeType: "text/plain",
    buffer: Buffer.from("not a resume"),
  });
  await page.getByRole("button", { name: "Submit application" }).click();
  await expect(page.getByRole("alert")).toContainText("Resume must be a PDF or DOCX file");
  expect(submittedRequest).toBeUndefined();

  // Valid PDF must be sent as multipart form data.
  await resume.setInputFiles({
    name: "sample-resume.pdf",
    mimeType: "application/pdf",
    buffer: Buffer.from("%PDF-1.4\n% Playwright test fixture\n"),
  });
  await page.getByRole("button", { name: "Submit application" }).click();

  await expect(page).toHaveURL(/\/applications$/);
  await expect(page.getByText("Application submitted")).toBeVisible();
  expect(submittedRequest, "application POST should be sent").toBeTruthy();
  expect(submittedRequest.headers()["content-type"]).toContain("multipart/form-data");
  expect(submittedRequest.postData()).toContain("sample-resume.pdf");
});

/*
 * ST-N03_05 cannot be honestly exercised end-to-end with the supplied frontend:
 * it has no mock-test attempt/start route or page. The existing AttemptTimer is
 * a display-only component (secondsLeft prop); it does not start or submit tests.
 *
 * ST-N03_08 cannot be exercised because the supplied frontend has no Analytics
 * route/page or chart components.
 *
 * These are documented blockers in README-NFR003.txt, not fake passing tests.
 */
