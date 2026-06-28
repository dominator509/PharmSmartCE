import { expect, test } from "@playwright/test";

import { API_BASE } from "./env";

function uniqueEmail(prefix: string): string {
  return `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2, 8)}@example.com`;
}

test("citation drawer deep link opens from click and direct URL", async ({
  page,
  request,
}) => {
  const email = uniqueEmail("citation");
  const password = "secretsecret12";

  await request.post(`${API_BASE}/auth/register`, {
    data: { email, password },
  });

  const loginResponse = await request.post(`${API_BASE}/auth/login`, {
    data: { email, password },
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

  const uploadResponse = await request.post(
    `${API_BASE}/api/courses/${courseId}/sources`,
    {
      headers: {
        authorization: `Bearer ${accessToken}`,
      },
      multipart: {
        file: {
          name: "source.pdf",
          mimeType: "application/pdf",
          buffer: Buffer.from(
            "%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF",
          ),
        },
      },
    },
  );
  expect(uploadResponse.ok()).toBeTruthy();

  const startResponse = await request.post(
    `${API_BASE}/api/sessions/${courseId}/start`,
    {
      headers: {
        authorization: `Bearer ${accessToken}`,
      },
    },
  );
  expect(startResponse.ok()).toBeTruthy();
  const started = (await startResponse.json()) as {
    id: string;
    questions: Array<{
      id: string;
      citation: { doc_id: string; page: number; span: string; url: string };
    }>;
  };
  const sessionId = started.id;
  const question = started.questions[0];

  await page.goto("/login");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill(password);
  await page.getByRole("button", { name: "Log in" }).click();
  await expect(page).toHaveURL(/\/courses$/);

  await page.goto(`/sessions/${sessionId}`);
  await expect(page.getByRole("heading", { name: sessionId })).toBeVisible();

  const questionCard = page.locator(`[data-question-id="${question.id}"]`);
  await questionCard.getByRole("link", { name: "[1]" }).first().click();
  await expect(page).toHaveURL(new RegExp(`/sessions/${sessionId}\\?cite=`));
  await expect(
    page.getByRole("dialog", { name: "Citation details" }),
  ).toBeVisible();
  await expect(page.getByText("source.pdf")).toBeVisible();

  await page.goto(
    `/sessions/${sessionId}?cite=${question.citation.doc_id}:${question.citation.page}:${question.citation.span}`,
  );
  await expect(
    page.getByRole("dialog", { name: "Citation details" }),
  ).toBeVisible();
  await expect(page.getByText("source.pdf")).toBeVisible();
  await expect(page.getByText(question.citation.span)).toBeVisible();
});
