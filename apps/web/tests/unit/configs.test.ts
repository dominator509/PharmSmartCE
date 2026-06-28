import { describe, expect, it } from "vitest";

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
});
