import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
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
