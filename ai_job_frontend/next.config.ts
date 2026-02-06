import type { NextConfig } from "next";
import path from "path";
import fs from "fs";

// #region agent log
try {
  const logPath = path.join(process.cwd(), "..", ".cursor", "debug.log");
  const line =
    JSON.stringify({
      timestamp: Date.now(),
      sessionId: "debug-session",
      runId: "run1",
      hypothesisId: "H1",
      location: "next.config.ts:load",
      message: "Next config loaded (webpack process)",
      data: {
        memoryUsage: process.memoryUsage(),
        cwd: process.cwd(),
        nodeArch: process.arch,
      },
    }) + "\n";
  const logDir = path.dirname(logPath);
  if (!fs.existsSync(logDir)) fs.mkdirSync(logDir, { recursive: true });
  fs.appendFileSync(logPath, line);
} catch (_) {}
// #endregion

const nextConfig: NextConfig = {
  // Disable webpack pack cache to avoid "Array buffer allocation failed" (PackFileCacheStrategy)
  webpack: (config) => {
    config.cache = false;
    return config;
  },
  images: {
    qualities: [75, 80],
    remotePatterns: [
      {
        protocol: "https",
        hostname: "lh3.googleusercontent.com",
      },
      {
        protocol: "https",
        hostname: "**.googleusercontent.com",
      },
      {
        protocol: "https",
        hostname: "media.licdn.com",
      },
    ],
  },
  // Reduce memory usage during build (helps with Vercel OOM)
  productionBrowserSourceMaps: false,
  experimental: {
    webpackMemoryOptimizations: true,
  },
  // Externalize heavy pdfjs-dist to reduce bundle/memory
  serverExternalPackages: ["pdfjs-dist"],
};

export default nextConfig;
