import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError, apiFetch } from "../../lib/api";

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("apiFetch", () => {
  it("throws an ApiError for problem+json responses", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => {
        return new Response(
          JSON.stringify({
            type: "https://example.test/problem",
            status: 422,
            detail: "Validation failed.",
          }),
          {
            status: 422,
            headers: {
              "content-type": "application/problem+json",
            },
          },
        );
      }),
    );

    const request = apiFetch("/api/test", { baseUrl: "https://api.example" });

    await expect(request).rejects.toBeInstanceOf(ApiError);
    await expect(request).rejects.toMatchObject({
      status: 422,
      problem: {
        detail: "Validation failed.",
      },
    });
  });

  it("rejects non-path inputs before making a request", async () => {
    const fetchImpl = vi.fn();
    vi.stubGlobal("fetch", fetchImpl);

    await expect(
      apiFetch("https://example.test/api/test", {
        baseUrl: "https://api.example",
      }),
    ).rejects.toThrow("API paths must start with '/'.");
    expect(fetchImpl).not.toHaveBeenCalled();
  });
});
