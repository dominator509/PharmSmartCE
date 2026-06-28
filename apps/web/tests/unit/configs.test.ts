import { describe, expect, it, vi } from "vitest";

import nextConfig from "../../next.config.mjs";
import playwrightConfig from "../../playwright.config.ts";
import tailwindConfig from "../../tailwind.config.ts";

describe("frontend configs", () => {
  it("keeps the expected build and test settings", () => {
    expect(nextConfig).toMatchObject({
      reactStrictMode: true,
      output: "standalone",
    });
    expect(playwrightConfig).toMatchObject({
      testDir: "./tests/e2e",
      use: { baseURL: "http://127.0.0.1:3000" },
    });
    expect(tailwindConfig).toMatchObject({
      content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
      theme: { extend: {} },
      plugins: [],
    });
  });

  it("lets playwright read the runner base URL from the environment", async () => {
    vi.stubEnv("PLAYWRIGHT_BASE_URL", "http://127.0.0.1:41234");
    vi.resetModules();

    try {
      const { default: configuredPlaywright } = await import(
        "../../playwright.config.ts"
      );

      expect(configuredPlaywright).toMatchObject({
        use: { baseURL: "http://127.0.0.1:41234" },
      });
    } finally {
      vi.unstubAllEnvs();
      vi.resetModules();
    }
  });
});
