import { spawn } from "node:child_process";
import { execFile } from "node:child_process";
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

function execCommand(command, args) {
  return new Promise((resolve) => {
    const child = execFile(command, args, { windowsHide: true }, (_error, stdout) => {
      resolve(stdout ?? "");
    });
    child.stdin?.end();
  });
}

async function terminate(child) {
  if (!child) {
    return;
  }
  if (child.exitCode === null && child.signalCode === null) {
    if (process.platform === "win32" && child.pid !== undefined) {
      const killer = spawn("taskkill", ["/PID", String(child.pid), "/T", "/F"], {
        stdio: "inherit",
        windowsHide: true,
      });
      await waitForExit(killer);
    } else {
      child.kill();
    }
    await waitForExit(child);
  }
}

async function freePort(port) {
  if (process.platform !== "win32") {
    return;
  }

  const output = await execCommand("cmd", [
    "/c",
    `netstat -ano | findstr :${port}`,
  ]);
  const pids = new Set();

  for (const line of output.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || !trimmed.includes("LISTENING")) {
      continue;
    }
    const pid = trimmed.split(/\s+/).at(-1);
    if (pid && pid !== "0") {
      pids.add(pid);
    }
  }

  for (const pid of pids) {
    const killer = spawn("taskkill", ["/PID", pid, "/T", "/F"], {
      stdio: "inherit",
      windowsHide: true,
    });
    await waitForExit(killer);
  }
}

const backendEnv = {
  ...process.env,
  UV_CACHE_DIR: process.env.UV_CACHE_DIR ?? resolve(tempRoot, "uv-cache"),
  TMP: process.env.TMP ?? tempRoot,
  TEMP: process.env.TEMP ?? tempRoot,
  TMPDIR: process.env.TMPDIR ?? tempRoot,
  WEB_PUBLIC_API_URL: process.env.WEB_PUBLIC_API_URL ?? apiUrl,
};

let apiServer;
let migrate;
let nextServer;

try {
  await freePort(8000);
  await freePort(3000);
  apiServer = spawnCommand(
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

  migrate = spawnCommand(
    "python",
    [
      "-m",
      "uv",
      "run",
      "--directory",
      resolve(process.cwd(), "..", "api"),
      "alembic",
      "upgrade",
      "head",
    ],
    backendEnv,
  );

  nextServer = spawnCommand(process.execPath, [
    "node_modules/next/dist/bin/next",
    "dev",
    "-H",
    "127.0.0.1",
  ]);

  const migrateCode = await waitForExit(migrate);
  if (migrateCode !== 0) {
    process.exitCode = migrateCode ?? 1;
    throw new Error("Failed to migrate the API database before e2e tests.");
  }
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
  await terminate(apiServer);
  await terminate(migrate);
  await terminate(nextServer);
}
