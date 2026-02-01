/**
 * OAuth redirect URL helper.
 * Ensures Google/LinkedIn OAuth callbacks work on Vercel (production + preview).
 * Set NEXT_PUBLIC_SITE_URL in Vercel for production (e.g. https://ai-job-assistant-v3.vercel.app).
 */
export function getAuthRedirectUrl(): string {
  if (typeof window !== "undefined") {
    return `${window.location.origin}/auth/callback`;
  }
  // Server-side: use env vars (for SSR or callback logic)
  const siteUrl =
    process.env.NEXT_PUBLIC_SITE_URL ||
    (process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : null) ||
    "http://localhost:3000";
  const base = siteUrl.replace(/\/$/, "");
  return `${base}/auth/callback`;
}
