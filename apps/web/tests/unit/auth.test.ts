import { afterEach, describe, expect, it, vi } from "vitest";

import { createAuthActions } from "../../lib/auth";

afterEach(() => {
  vi.restoreAllMocks();
});

describe("createAuthActions", () => {
  it("registers, logs in, and stores the refresh cookie", async () => {
    const fetchImpl = vi
      .fn()
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ id: "user-1" }), {
          status: 201,
          headers: {
            "content-type": "application/json",
          },
        }),
      )
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            access_token: "access-token",
            token_type: "Bearer",
            expires_in: 900,
          }),
          {
            status: 200,
            headers: {
              "content-type": "application/json",
              "set-cookie":
                "refresh=refresh-token; Path=/auth; HttpOnly; Secure; SameSite=Lax",
            },
          },
        ),
      );
    const store = createCookieStore();
    const actions = createAuthActions({
      baseUrl: "https://api.example",
      fetchImpl,
      cookieStore: store,
    });

    const result = await actions.register({
      email: "pharmacist@example.com",
      password: "secretsecret12",
    });

    expect(result).toEqual({
      accessToken: "access-token",
      tokenType: "Bearer",
      expiresIn: 900,
    });
    expect(fetchImpl).toHaveBeenCalledTimes(2);
    expect(store.get("refresh")?.value).toBe("refresh-token");
  });

  it("refreshes with the stored cookie and clears it on logout", async () => {
    const fetchImpl = vi
      .fn()
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            access_token: "refreshed-token",
            token_type: "Bearer",
            expires_in: 900,
          }),
          {
            status: 200,
            headers: {
              "content-type": "application/json",
              "set-cookie":
                "refresh=refreshed-cookie; Path=/auth; HttpOnly; Secure; SameSite=Lax",
            },
          },
        ),
      )
      .mockResolvedValueOnce(new Response(null, { status: 204 }));
    const store = createCookieStore({ refresh: "current-cookie" });
    const actions = createAuthActions({
      baseUrl: "https://api.example",
      fetchImpl,
      cookieStore: store,
    });

    const refreshed = await actions.refresh();
    expect(refreshed.accessToken).toBe("refreshed-token");
    expect(fetchImpl).toHaveBeenNthCalledWith(
      1,
      expect.any(URL),
      expect.objectContaining({
        method: "POST",
      }),
    );
    expect(store.get("refresh")?.value).toBe("refreshed-cookie");

    await actions.logout();
    expect(store.get("refresh")).toBeUndefined();
  });
});

function createCookieStore(initial: Record<string, string> = {}) {
  const values = new Map(Object.entries(initial));
  return {
    get(name: string) {
      const value = values.get(name);
      return value ? { value } : undefined;
    },
    set(name: string, value: string) {
      values.set(name, value);
    },
    delete(name: string) {
      values.delete(name);
    },
  };
}
