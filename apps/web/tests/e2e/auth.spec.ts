import { expect, test } from "@playwright/test";

function uniqueEmail(prefix: string): string {
  return `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2, 8)}@example.com`;
}

test("register redirects to courses", async ({ page }) => {
  const email = uniqueEmail("register");

  await page.goto("/register", {
    waitUntil: "domcontentloaded",
    timeout: 10_000,
  });
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill("secretsecret12");
  await Promise.all([
    page.waitForURL(/\/courses$/, { timeout: 10_000 }),
    page.getByRole("button", { name: "Create account" }).click(),
  ]);
  await expect(
    page.getByRole("heading", { name: "Courses", exact: true }),
  ).toBeVisible();
});

test("login redirects to courses after registration", async ({ page }) => {
  const email = uniqueEmail("login");

  await page.goto("/register", {
    waitUntil: "domcontentloaded",
    timeout: 10_000,
  });
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill("secretsecret12");
  await Promise.all([
    page.waitForURL(/\/courses$/, { timeout: 10_000 }),
    page.getByRole("button", { name: "Create account" }).click(),
  ]);

  await page.goto("/login", {
    waitUntil: "domcontentloaded",
    timeout: 10_000,
  });
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill("secretsecret12");
  await Promise.all([
    page.waitForURL(/\/courses$/, { timeout: 10_000 }),
    page.getByRole("button", { name: "Log in" }).click(),
  ]);
  await expect(
    page.getByRole("heading", { name: "Courses", exact: true }),
  ).toBeVisible();
});
