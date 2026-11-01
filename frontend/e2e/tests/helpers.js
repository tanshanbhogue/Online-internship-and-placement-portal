
const student = { email: process.env.E2E_STUDENT_EMAIL || "ui.student@example.com", password: process.env.E2E_STUDENT_PASSWORD || "Student@123" };
const admin = { email: process.env.E2E_ADMIN_EMAIL || "ui.admin@example.com", password: process.env.E2E_ADMIN_PASSWORD || "Admin@12345" };

async function login(page, who) {
  await page.goto("/login");
  await page.getByLabel(/email/i).fill(who.email);
  await page.getByLabel(/password/i).fill(who.password);
  await page.getByRole("button", { name: /log in|login|sign in/i }).click();
  await page.waitForURL((url) => !url.pathname.startsWith("/login"));
}

/** true when the page can be scrolled sideways (a layout bug) */
async function hasHorizontalScroll(page) {
  return page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1);
}

module.exports = { student, admin, login, hasHorizontalScroll };
