import { afterEach, describe, expect, it, vi } from "vitest";

const spawnCalls: Array<{ command: string; args: string[] }> = [];
const fetchCalls: string[] = [];
const killedChildren: Array<{ killed: boolean }> = [];

vi.mock("node:child_process", () => ({
  spawn: vi.fn((command: string, args: string[]) => {
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
    spawnCalls.push({ command, args });
    killedChildren.push(child);
    return child;
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

    expect(spawnCalls).toHaveLength(3);
    expect(spawnCalls[0]?.args).toContain("uvicorn");
    expect(spawnCalls[1]?.args).toContain("dev");
    expect(spawnCalls[2]?.args).toContain("test");
    expect(fetchCalls[0]).toBe("http://127.0.0.1:8000/healthz");
    expect(fetchCalls[1]).toBe("http://127.0.0.1:3000");
    expect(killedChildren[0]?.killed).toBe(true);
  });
});
