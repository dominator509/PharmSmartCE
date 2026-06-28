import { spawn } from "node:child_process";
import { createServer } from "node:net";
import { resolve } from "node:path";
import { setTimeout as delay } from "node:timers/promises";

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

async function reservePort() {
  const server = createServer();
  server.unref();

  return await new Promise((resolve, reject) => {
    server.once("error", reject);
    server.listen(0, "127.0.0.1", () => {
      const address = server.address();
      if (address === null || typeof address === "string") {
        reject(new Error("Unable to reserve a local port."));
        return;
      }
      const port = address.port;
      server.close((closeError) => {
        if (closeError) {
          reject(closeError);
          return;
        }
        resolve(port);
      });
    });
  });
}

async function waitForUrl(url, timeoutMs = 30_000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    try {
      const response = await fetch(url);
      if (response.ok) {
        return;
      }
    } catch {
      // Server is not ready yet.
    }
    await delay(500);
  }
  throw new Error(`Timed out waiting for ${url}`);
}

function waitForExit(child) {
  return new Promise((resolve) => {
    child.on("exit", (code) => resolve(code));
  });
}

async function terminate(child) {
  if (!child) {
    return;
  }
  if (child.exitCode === null && child.signalCode === null) {
    if (process.platform === "win32" && child.pid !== undefined) {
      const killer = spawn(
        "taskkill",
        ["/PID", String(child.pid), "/T", "/F"],
        {
          stdio: "inherit",
          windowsHide: true,
        },
      );
      await waitForExit(killer);
    } else {
      child.kill();
    }
    await waitForExit(child);
  }
}

const backendEnv = {
  ...process.env,
  UV_CACHE_DIR: process.env.UV_CACHE_DIR ?? resolve(tempRoot, "uv-cache"),
  TMP: process.env.TMP ?? tempRoot,
  TEMP: process.env.TEMP ?? tempRoot,
  TMPDIR: process.env.TMPDIR ?? tempRoot,
};

let apiServer;
let migrate;
let nextServer;

try {
  const apiPort = process.env.E2E_API_PORT
    ? Number(process.env.E2E_API_PORT)
    : await reservePort();
  const webPort = process.env.E2E_WEB_PORT
    ? Number(process.env.E2E_WEB_PORT)
    : await reservePort();
  const apiUrl = process.env.E2E_API_BASE_URL ?? `http://127.0.0.1:${apiPort}`;
  const webUrl =
    process.env.PLAYWRIGHT_BASE_URL ?? `http://127.0.0.1:${webPort}`;

  backendEnv.WEB_PUBLIC_API_URL = process.env.WEB_PUBLIC_API_URL ?? apiUrl;
  backendEnv.E2E_API_BASE_URL = apiUrl;
  backendEnv.E2E_WEB_BASE_URL = webUrl;
  backendEnv.PLAYWRIGHT_BASE_URL = webUrl;

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
      String(apiPort),
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

  nextServer = spawnCommand(
    process.execPath,
    [
      "node_modules/next/dist/bin/next",
      "dev",
      "-H",
      "127.0.0.1",
      "-p",
      String(webPort),
    ],
    backendEnv,
  );

  const migrateCode = await waitForExit(migrate);
  if (migrateCode !== 0) {
    process.exitCode = migrateCode ?? 1;
    throw new Error("Failed to migrate the API database before e2e tests.");
  }

  await waitForUrl(`${apiUrl}/healthz`);
  await waitForUrl(webUrl);

  const playwrightArgs = process.argv.slice(2).filter((arg) => arg !== "--");
  const playwright = spawnCommand(
    process.execPath,
    ["node_modules/@playwright/test/cli.js", "test", ...playwrightArgs],
    backendEnv,
  );
  const code = await waitForExit(playwright);
  if (code !== 0) {
    process.exitCode = code ?? 1;
  }
} finally {
  await terminate(apiServer);
  await terminate(migrate);
  await terminate(nextServer);
}
