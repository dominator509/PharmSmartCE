import axe from "axe-core";
import { expect, test, type Locator, type Page } from "@playwright/test";

import { API_BASE, WEB_BASE_URL } from "./env";

function uniqueEmail(prefix: string): string {
  return `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2, 8)}@example.com`;
}

test("axe-core reports no serious violations on the core pages", async ({
  page,
  request,
}) => {
  const email = uniqueEmail("a11y");
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

  const courseResponse = await request.post(`${API_BASE}/api/courses`, {
    headers: {
      authorization: `Bearer ${accessToken}`,
    },
    data: {
      title: "A11y CE",
      n_questions: 6,
      pass_pct: 70,
    },
  });
  expect(courseResponse.ok()).toBeTruthy();
  const { id: courseId } = (await courseResponse.json()) as { id: string };

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

  const sessionResponse = await request.post(
    `${API_BASE}/api/sessions/${courseId}/start`,
    {
      headers: {
        authorization: `Bearer ${accessToken}`,
      },
    },
  );
  expect(sessionResponse.ok()).toBeTruthy();
  const { id: sessionId } = (await sessionResponse.json()) as { id: string };

  await page.goto("/login");
  await runAxe(page);
  await expectTabReachable(page, page.getByLabel("Email"));
  await expectTabReachable(page, page.getByLabel("Password"));
  await expectTabReachable(page, page.getByRole("button", { name: "Log in" }));

  await page.context().addCookies([
    {
      name: "access",
      value: accessToken,
      url: WEB_BASE_URL,
    },
  ]);

  await page.goto("/courses");
  await runAxe(page);
  await expectTabReachable(page, page.getByRole("link", { name: "A11y CE" }));

  await page.goto(`/sessions/${sessionId}`, {
    waitUntil: "domcontentloaded",
    timeout: 10_000,
  });
  await runAxe(page);
  await expectTabReachable(page, page.getByRole("radio").first());
  await expectTabReachable(
    page,
    page.getByRole("button", { name: "Submit answer" }).first(),
  );
});

async function runAxe(page: Page) {
  await page.addScriptTag({ content: axe.source });
  const results = await page.evaluate(async () => {
    const axeWindow = window as typeof window & {
      axe: {
        run: typeof axe.run;
      };
    };
    return axeWindow.axe.run(document);
  });

  const seriousViolations = results.violations.filter((violation) =>
    ["serious", "critical"].includes(violation.impact ?? ""),
  );
  const colorContrastViolations = results.violations.filter(
    (violation) => violation.id === "color-contrast",
  );

  expect(
    seriousViolations,
    JSON.stringify(seriousViolations, null, 2),
  ).toHaveLength(0);
  expect(
    colorContrastViolations,
    JSON.stringify(colorContrastViolations, null, 2),
  ).toHaveLength(0);
}

async function expectTabReachable(page: Page, target: Locator): Promise<void> {
  for (let i = 0; i < 12; i += 1) {
    if (
      await target.evaluate((element) => element === document.activeElement)
    ) {
      return;
    }
    await page.keyboard.press("Tab");
  }

  await expect(target).toBeFocused();
}
