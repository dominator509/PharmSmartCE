import { expect, test } from "@playwright/test";

import { API_BASE } from "./env";

function uniqueEmail(prefix: string): string {
  return `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2, 8)}@example.com`;
}

test("upload source", async ({ page, request }) => {
  const email = uniqueEmail("course");
  const password = "secretsecret12";

  await request.post(`${API_BASE}/auth/register`, {
    data: {
      email,
      password,
    },
  });

  const loginResponse = await request.post(`${API_BASE}/auth/login`, {
    data: {
      email,
      password,
    },
  });
  expect(loginResponse.ok()).toBeTruthy();
  const { access_token: accessToken } = (await loginResponse.json()) as {
    access_token: string;
  };

  const createCourseResponse = await request.post(`${API_BASE}/api/courses`, {
    headers: {
      authorization: `Bearer ${accessToken}`,
    },
    data: {
      title: "Cardiology CE",
      n_questions: 6,
      pass_pct: 70,
    },
  });
  expect(createCourseResponse.ok()).toBeTruthy();
  const { id: courseId } = (await createCourseResponse.json()) as {
    id: string;
  };

  await page.goto("/login");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill(password);
  await page.getByRole("button", { name: "Log in" }).click();
  await expect(page).toHaveURL(/\/courses$/);

  await expect(page.getByRole("link", { name: "Cardiology CE" })).toBeVisible();
  await page.getByRole("link", { name: "Cardiology CE" }).click();
  await expect(page).toHaveURL(new RegExp(`/courses/${courseId}$`));

  await page.getByLabel("Source file").setInputFiles({
    name: "source.pdf",
    mimeType: "application/pdf",
    buffer: Buffer.from(
      "%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF",
    ),
  });
  await page.getByRole("button", { name: "Upload source" }).click();

  await expect(page).toHaveURL(
    new RegExp(`/courses/${courseId}\\?uploaded=1$`),
  );
  await expect(
    page.getByRole("heading", { name: "Cardiology CE", exact: true }),
  ).toBeVisible();
  await expect(page.getByText("source.pdf")).toBeVisible();
  await expect(page.getByText("Source uploaded.")).toBeVisible();
});
