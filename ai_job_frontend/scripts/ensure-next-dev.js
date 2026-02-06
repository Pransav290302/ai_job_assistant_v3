"use strict";
const fs = require("fs");
const path = require("path");
const net = require("net");
const { spawn } = require("child_process");

const LOG_PATH = path.join(__dirname, "..", "..", ".cursor", "debug.log");
const LOCK_PATH = path.join(__dirname, "..", ".next", "dev", "lock");
const DEV_PORT = 3000;

// #region agent log
function log(id, location, message, data) {
  const line = JSON.stringify({
    id: "log_" + Date.now() + "_" + Math.random().toString(36).slice(2, 8),
    timestamp: Date.now(),
    location,
    message,
    data: data || {},
    sessionId: "debug-session",
    runId: process.env.DEBUG_RUN_ID || "run1",
    hypothesisId: id,
  }) + "\n";
  try {
    const logDir = path.dirname(LOG_PATH);
    if (!fs.existsSync(logDir)) fs.mkdirSync(logDir, { recursive: true });
    fs.appendFileSync(LOG_PATH, line);
  } catch (e) {
    console.error("[ensure-next-dev] log write failed:", e.message);
  }
}
// #endregion

// #region agent log
function getDirSizeBytes(dirPath) {
  let total = 0;
  try {
    if (!fs.existsSync(dirPath)) return 0;
    const entries = fs.readdirSync(dirPath, { withFileTypes: true });
    for (const e of entries) {
      const full = path.join(dirPath, e.name);
      if (e.isDirectory()) total += getDirSizeBytes(full);
      else total += fs.statSync(full).size || 0;
    }
  } catch (_) {}
  return total;
}
log("H1", "ensure-next-dev.js:entry", "Pre-dev check started", {
  lockPath: LOCK_PATH,
  logPath: LOG_PATH,
  nodeArch: process.arch,
  nodeVersion: process.version,
  memoryUsage: process.memoryUsage(),
  NODE_OPTIONS_before: process.env.NODE_OPTIONS || "(none)",
});
// #endregion

const lockExists = (() => {
  try {
    return fs.existsSync(LOCK_PATH);
  } catch (_) {
    return false;
  }
})();

// #region agent log
log("H1", "ensure-next-dev.js:lockCheck", "Lock file existence", {
  lockExists,
  lockPath: LOCK_PATH,
});
// #endregion

function portInUse(port) {
  return new Promise((resolve) => {
    const server = net.createServer(() => {});
    server.once("error", () => resolve(true));
    server.once("listening", () => {
      server.close(() => resolve(false));
    });
    server.listen(port, "127.0.0.1");
  });
}

(async () => {
  const inUse = await portInUse(DEV_PORT);

  // #region agent log
  log("H2", "ensure-next-dev.js:portCheck", "Port 3000 in use?", {
    portInUse: inUse,
    port: DEV_PORT,
  });
  // #endregion

  if (lockExists && !inUse) {
    try {
      fs.unlinkSync(LOCK_PATH);
      // #region agent log
      log("H1", "ensure-next-dev.js:removedLock", "Removed stale lock (H1)", {
        lockPath: LOCK_PATH,
        action: "unlink",
      });
      // #endregion
    } catch (err) {
      // #region agent log
      log("H4", "ensure-next-dev.js:unlinkError", "Failed to remove lock", {
        error: String(err && err.message),
        lockPath: LOCK_PATH,
      });
      // #endregion
      console.error("Could not remove stale lock:", err.message);
    }
  } else if (lockExists && inUse) {
    // #region agent log
    log("H2", "ensure-next-dev.js:skipRemove", "Lock exists and port in use; not removing lock", {
      lockExists: true,
      portInUse: true,
    });
    // #endregion
    console.error("Port 3000 is in use. Stop the other 'npm run dev' (or the process on port 3000), then run again.");
    process.exit(1);
  }

  const cwd = path.join(__dirname, "..");
  const nextDir = path.join(cwd, ".next");
  const cacheDirs = [
    path.join(nextDir, "cache"),
    path.join(nextDir, "dev", "cache"),
  ];
  // #region agent log
  const cacheSizes = {};
  for (const dir of cacheDirs) {
    if (fs.existsSync(dir)) cacheSizes[path.basename(dir)] = getDirSizeBytes(dir);
  }
  log("H2", "ensure-next-dev.js:cacheSizeBeforeClear", "Cache dir sizes (bytes) before clear", {
    cacheSizes,
    cacheDirs: cacheDirs.map((d) => path.basename(d)),
  });
  log("H3", "ensure-next-dev.js:nodeEnv", "Node arch/version for allocation hypothesis", {
    arch: process.arch,
    nodeVersion: process.version,
    is32Bit: process.arch === "ia32" || process.arch === "x32",
  });
  // #endregion
  for (const dir of cacheDirs) {
    if (fs.existsSync(dir)) {
      try {
        fs.rmSync(dir, { recursive: true });
        log("H2", "ensure-next-dev.js:clearCache", "Cleared cache to avoid Gunzip allocation failure", { dir });
      } catch (_) {}
    }
  }

  const env = { ...process.env };
  const existing = env.NODE_OPTIONS || "";
  env.NODE_OPTIONS = (existing + " --max-old-space-size=4096").trim();
  // #region agent log
  log("H1", "ensure-next-dev.js:beforeSpawn", "NODE_OPTIONS and memory before spawning Next", {
    NODE_OPTIONS_after: env.NODE_OPTIONS,
    memoryUsage: process.memoryUsage(),
  });
  // #endregion
  const child = spawn("npx", ["next", "dev", "--webpack", "-p", String(DEV_PORT)], {
    stdio: "inherit",
    shell: true,
    cwd,
    env,
  });
  child.on("exit", (code) => process.exit(code != null ? code : 0));
})();
