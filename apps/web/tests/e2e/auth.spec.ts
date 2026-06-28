import { expect, test } from "@playwright/test";

function uniqueEmail(prefix: string): string {
  return `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2, 8)}@example.com`;
}

test("register redirects to courses", async ({ page }) => {
  const email = uniqueEmail("register");

  await page.goto("/register");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill("secretsecret12");
  await page.getByRole("button", { name: "Create account" }).click();

  await expect(page).toHaveURL(/\/courses$/);
  await expect(
    page.getByRole("heading", { name: "Courses", exact: true }),
  ).toBeVisible();
});

test("login redirects to courses after registration", async ({ page }) => {
  const email = uniqueEmail("login");

  await page.goto("/register");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill("secretsecret12");
  await page.getByRole("button", { name: "Create account" }).click();
  await expect(page).toHaveURL(/\/courses$/);

  await page.goto("/login");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill("secretsecret12");
  await page.getByRole("button", { name: "Log in" }).click();

  await expect(page).toHaveURL(/\/courses$/);
  await expect(
    page.getByRole("heading", { name: "Courses", exact: true }),
  ).toBeVisible();
});
