import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "node",
    coverage: {
      all: false,
      provider: "v8",
      include: ["app/**/*.{ts,tsx}"],
      exclude: ["tests/**"],
    },
  },
});
