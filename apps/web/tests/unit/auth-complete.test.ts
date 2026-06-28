import { describe, expect, it } from "vitest";

import { resolveNextPath } from "../../app/auth/complete/AuthCompleteClient";

describe("resolveNextPath", () => {
  it("keeps same-site paths", () => {
    expect(resolveNextPath("/courses")).toBe("/courses");
    expect(resolveNextPath("/sessions/abc?cite=source-1:1:p1:s1")).toBe(
      "/sessions/abc?cite=source-1:1:p1:s1",
    );
  });

  it("rejects off-origin or malformed paths", () => {
    expect(resolveNextPath("https://example.com")).toBe("/courses");
    expect(resolveNextPath("//example.com")).toBe("/courses");
    expect(resolveNextPath("courses")).toBe("/courses");
    expect(resolveNextPath("   ")).toBe("/courses");
  });
});
