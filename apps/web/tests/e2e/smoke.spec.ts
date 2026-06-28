import { expect, test } from "@playwright/test";

test("home page renders the product name", async ({ page }) => {
  await page.goto("/", {
    waitUntil: "domcontentloaded",
    timeout: 10_000,
  });

  await expect(
    page.getByRole("heading", { name: "PharmSmartCE" }),
  ).toBeVisible();
});
