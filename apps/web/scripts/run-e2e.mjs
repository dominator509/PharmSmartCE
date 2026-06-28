import { spawn } from "node:child_process";
import { resolve } from "node:path";
import { setTimeout as delay } from "node:timers/promises";

const baseUrl = "http://127.0.0.1:3000";
const apiUrl = "http://127.0.0.1:8000";
const repoRoot = resolve(process.cwd(), "..", "..");
const tempRoot = resolve(repoRoot, ".tmp");

function spawnCommand(command, args, env = process.env) {
  return spawn(command, args, {
    cwd: process.cwd(),
    env,
    stdio: "inherit",
    windowsHide: true,
  });
}

async function waitForServer(timeoutMs = 30_000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    try {
      const response = await fetch(baseUrl);
      if (response.ok) {
        return;
      }
    } catch {
      // Server is not ready yet.
    }
    await delay(500);
  }
  throw new Error(`Timed out waiting for ${baseUrl}`);
}

async function waitForApi(timeoutMs = 30_000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    try {
      const response = await fetch(`${apiUrl}/healthz`);
      if (response.ok) {
        return;
      }
    } catch {
      // API is not ready yet.
    }
    await delay(500);
  }
  throw new Error(`Timed out waiting for ${apiUrl}`);
}

function waitForExit(child) {
  return new Promise((resolve) => {
    child.on("exit", (code) => resolve(code));
  });
}

const backendEnv = {
  ...process.env,
  UV_CACHE_DIR: process.env.UV_CACHE_DIR ?? resolve(tempRoot, "uv-cache"),
  TMP: process.env.TMP ?? tempRoot,
  TEMP: process.env.TEMP ?? tempRoot,
  TMPDIR: process.env.TMPDIR ?? tempRoot,
  WEB_PUBLIC_API_URL: process.env.WEB_PUBLIC_API_URL ?? apiUrl,
};

const apiServer = spawnCommand(
  "python",
  [
    "-m",
    "uv",
    "run",
    "--directory",
    resolve(process.cwd(), "..", "api"),
    "uvicorn",
    "app.main:app",
    "--host",
    "127.0.0.1",
    "--port",
    "8000",
  ],
  backendEnv,
);

const nextServer = spawnCommand(process.execPath, [
  "node_modules/next/dist/bin/next",
  "dev",
  "-H",
  "127.0.0.1",
]);

try {
  await waitForApi();
  await waitForServer();
  const playwrightArgs = process.argv.slice(2).filter((arg) => arg !== "--");
  const playwright = spawnCommand(process.execPath, [
    "node_modules/@playwright/test/cli.js",
    "test",
    ...playwrightArgs,
  ]);
  const code = await waitForExit(playwright);
  if (code !== 0) {
    process.exitCode = code ?? 1;
  }
} finally {
  apiServer.kill();
  nextServer.kill();
}
