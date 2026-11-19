const { test, expect } = require("@playwright/test");
const { student, admin, login, hasHorizontalScroll } = require("./helpers");

const PUBLIC = ["/login", "/register"];
// Only include routes that are actually registered in the supplied frontend.
const STUDENT = ["/internships", "/applications", "/practice", "/practice/history", "/mock-tests/history"];
const ADMIN = ["/admin/question-bank"];

function watchConsole(page) {
  const errors = [];

  page.on("pageerror", (e) => errors.push(String(e)));

  page.on("console", (m) => {
    if (
      m.type() === "error" &&
      !/401|Unauthorized/.test(m.text()) &&
      !/datalist/i.test(m.text()) &&
      !/Failed to load resource: the server responded with a status of 404/i.test(m.text())
    ) {
      errors.push(m.text());
    }
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
  test("implemented pages fit the screen and student navigation works", async ({ page, viewport }) => {
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
    } else {
      await expect(toggle).toBeHidden();
      await expect(links).toBeVisible();
    }

    await links.getByRole("link", { name: "Practice History" }).click();
    await expect(page).toHaveURL(/\/practice\/history$/);
    if (phone) await expect(links).toBeHidden();
    expect(errors).toEqual([]);
  });

  test("touch targets are at least 44px tall on small screens", async ({ page, viewport }) => {
    test.skip(viewport.width >= 768, "only checked on phone and tablet sizes");
    await login(page, student);
    await page.goto("/practice");
    const heights = await page.$$eval(
      "button, a.btn",
      (els) => els.filter((e) => e.offsetParent).map((e) => Math.round(e.getBoundingClientRect().height))
    );
    expect(heights.length, "the practice page should contain visible interactive controls").toBeGreaterThan(0);
    expect(Math.min(...heights)).toBeGreaterThanOrEqual(44);
  });
});

test.describe("admin pages", () => {
  test("admin page fits the screen", async ({ page }) => {
    await login(page, admin);
    for (const path of ADMIN) await expectFits(page, path);
  });
});
