import { spawn } from "node:child_process";
import { setTimeout as delay } from "node:timers/promises";

const baseUrl = "http://127.0.0.1:3000";

function spawnCommand(command, args) {
  return spawn(command, args, {
    cwd: process.cwd(),
    env: process.env,
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

function waitForExit(child) {
  return new Promise((resolve) => {
    child.on("exit", (code) => resolve(code));
  });
}

const nextServer = spawnCommand(process.execPath, [
  "node_modules/next/dist/bin/next",
  "dev",
  "-H",
  "127.0.0.1",
]);

try {
  await waitForServer();
  const playwright = spawnCommand(process.execPath, [
    "node_modules/@playwright/test/cli.js",
    "test",
  ]);
  const code = await waitForExit(playwright);
  if (code !== 0) {
    process.exitCode = code ?? 1;
  }
} finally {
  nextServer.kill();
}
