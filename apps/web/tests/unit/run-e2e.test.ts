import { afterEach, describe, expect, it, vi } from "vitest";

const spawnCalls: Array<{
  command: string;
  args: string[];
  env: Record<string, string | undefined>;
}> = [];
const fetchCalls: string[] = [];
const killedChildren: Array<{ killed: boolean }> = [];
const reservedPorts = [43210, 43211];

vi.mock("node:child_process", () => ({
  spawn: vi.fn((command: string, args: string[], options?: { env?: Record<string, string | undefined> }) => {
    const child = {
      killed: false,
      on(event: string, handler: (code: number | null) => void) {
        if (event === "exit") {
          queueMicrotask(() => handler(0));
        }
      },
      kill() {
        this.killed = true;
      },
    };
    spawnCalls.push({ command, args, env: options?.env ?? {} });
    killedChildren.push(child);
    return child;
  }),
}));

vi.mock("node:net", () => ({
  createServer: vi.fn(() => {
    let port = reservedPorts.shift();
    return {
      unref() {},
      once(_event: string, handler: (error: Error) => void) {
        void handler;
      },
      listen(_port: number, _host: string, handler: () => void) {
        port = port ?? 43210;
        queueMicrotask(handler);
      },
      address() {
        return port === undefined ? null : { port };
      },
      close(handler: (error?: Error) => void) {
        queueMicrotask(() => handler());
      },
    };
  }),
}));

vi.mock("node:timers/promises", () => ({
  setTimeout: vi.fn(() => Promise.resolve()),
}));

afterEach(() => {
  spawnCalls.length = 0;
  fetchCalls.length = 0;
  killedChildren.length = 0;
});

describe("run-e2e.mjs", () => {
  it("spawns the dev server and playwright runner", async () => {
    const originalFetch = global.fetch;
    global.fetch = (async (input: RequestInfo | URL) => {
      fetchCalls.push(String(input));
      return { ok: true } as Response;
    }) as typeof fetch;

    try {
      await import("../../scripts/run-e2e.mjs");
    } finally {
      global.fetch = originalFetch;
    }

    expect(spawnCalls.some(({ args }) => args.includes("uvicorn"))).toBe(true);
    expect(spawnCalls.some(({ args }) => args.includes("alembic"))).toBe(true);
    expect(
      spawnCalls.some(({ args }) => args.includes("dev") && args.includes("43211")),
    ).toBe(true);
    expect(spawnCalls.some(({ args }) => args.includes("test"))).toBe(true);
    expect(spawnCalls[0]?.args).toContain("43210");
    expect(spawnCalls[0]?.env.WEB_PUBLIC_API_URL).toBe(
      "http://127.0.0.1:43210",
    );
    expect(spawnCalls[0]?.env.E2E_API_BASE_URL).toBe(
      "http://127.0.0.1:43210",
    );
    expect(spawnCalls[2]?.env.E2E_WEB_BASE_URL).toBe(
      "http://127.0.0.1:43211",
    );
    expect(spawnCalls[2]?.env.PLAYWRIGHT_BASE_URL).toBe(
      "http://127.0.0.1:43211",
    );
    expect(fetchCalls[0]).toBe("http://127.0.0.1:43210/healthz");
    expect(fetchCalls[1]).toBe("http://127.0.0.1:43211");
  });

  it("honors explicit api and web port env vars", async () => {
    vi.stubEnv("E2E_API_PORT", "5001");
    vi.stubEnv("E2E_WEB_PORT", "5002");
    vi.resetModules();

    const originalFetch = global.fetch;
    global.fetch = (async (input: RequestInfo | URL) => {
      fetchCalls.push(String(input));
      return { ok: true } as Response;
    }) as typeof fetch;

    try {
      await import("../../scripts/run-e2e.mjs");
    } finally {
      global.fetch = originalFetch;
      vi.unstubAllEnvs();
      vi.resetModules();
    }

    expect(spawnCalls.some(({ args }) => args.includes("5001"))).toBe(true);
    expect(spawnCalls.some(({ args }) => args.includes("5002"))).toBe(true);
    expect(fetchCalls[0]).toBe("http://127.0.0.1:5001/healthz");
    expect(fetchCalls[1]).toBe("http://127.0.0.1:5002");
  });
});
