
const { test, expect } = require("@playwright/test");
const { student, admin, login, hasHorizontalScroll } = require("./helpers");

const PUBLIC = ["/login", "/register"];
const STUDENT = ["/internships", "/applications", "/practice", "/practice/history", "/mock-tests", "/mock-tests/history", "/analytics"];
const ADMIN = ["/admin/question-bank"];

function watchConsole(page) {
  const errors = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  page.on("console", (m) => {
    // the 401 of the "who am I" probe on public pages is expected
    if (m.type() === "error" && !/401|Unauthorized/.test(m.text())) errors.push(m.text());
  });
  return errors;
}

async function expectFits(page, path) {
  await page.goto(path);
  await page.waitForLoadState("networkidle");
  expect(await hasHorizontalScroll(page), `${path} scrolls sideways`).toBe(false);
}

test.describe("public pages", () => {
  for (const path of PUBLIC) {
    test(`${path} fits the screen`, async ({ page }) => {
      const errors = watchConsole(page);
      await expectFits(page, path);
      expect(errors).toEqual([]);
    });
  }
});

test.describe("student pages", () => {
  test("every page fits the screen and the navigation works", async ({ page, viewport }) => {
    const errors = watchConsole(page);
    await login(page, student);
    for (const path of STUDENT) await expectFits(page, path);

    const phone = viewport.width < 768;
    const toggle = page.locator(".nav-toggle");
    const links = page.locator("#nav-links");
    if (phone) {
      await expect(toggle).toBeVisible();
      await expect(links).toBeHidden();
      await toggle.click();
      await expect(links).toBeVisible();
      await links.getByRole("link", { name: "Analytics" }).click();
      await expect(page).toHaveURL(/\/analytics$/);
      await expect(links).toBeHidden(); // the menu closes after a choice
    } else {
      await expect(toggle).toBeHidden();
      await expect(links).toBeVisible();
      await links.getByRole("link", { name: "Analytics" }).click();
      await expect(page).toHaveURL(/\/analytics$/);
    }
    expect(errors).toEqual([]);
  });

  test("touch targets are at least 44px tall on small screens", async ({ page, viewport }) => {
    test.skip(viewport.width >= 768, "only checked on phone and tablet sizes");
    await login(page, student);
    await page.goto("/mock-tests");
    const heights = await page.$$eval("button, a.btn", (els) => els.filter((e) => e.offsetParent).map((e) => Math.round(e.getBoundingClientRect().height)));
    expect(Math.min(...heights)).toBeGreaterThanOrEqual(44);
  });
});

test.describe("admin pages", () => {
  test("admin page fits the screen", async ({ page }) => {
    await login(page, admin);
    for (const path of ADMIN) await expectFits(page, path);
  });
});
