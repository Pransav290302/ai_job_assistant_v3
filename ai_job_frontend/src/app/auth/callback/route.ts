import { NextResponse } from "next/server";
import { createClient } from "@/_lib/supabaseServer";
import { supabaseAdmin } from "@/_lib/supabaseAdmin";

const splitName = (fullName: string | null | undefined) => {
  if (!fullName) return { firstName: null, lastName: null };
  const parts = fullName.trim().split(/\s+/);
  return {
    firstName: parts[0] || null,
    lastName: parts.length > 1 ? parts.slice(1).join(" ") : null,
  };
};

/** Resolve redirect base URL - handles Vercel/proxy (x-forwarded-host). */
function getRedirectBase(request: Request, origin: string): string {
  const forwardedHost = request.headers.get("x-forwarded-host");
  const isLocal = process.env.NODE_ENV === "development";
  if (isLocal || !forwardedHost) return origin;
  const proto = request.headers.get("x-forwarded-proto") || "https";
  return `${proto}://${forwardedHost}`;
}

export async function GET(request: Request) {
  const { searchParams, origin } = new URL(request.url);
  const code = searchParams.get("code");
  const base = getRedirectBase(request, origin);

  if (code) {
    const supabase = await createClient();
    const { error } = await supabase.auth.exchangeCodeForSession(code);

    if (!error) {
      // Fetch the authenticated user from the session cookies
      const { data: userData, error: userError } = await supabase.auth.getUser();
      if (!userError && userData.user) {
        const u = userData.user;
        const meta = u.user_metadata || {};
        const fullName = meta.full_name || meta.name || null;
        const { firstName, lastName } = splitName(fullName);
        const provider = (u.app_metadata as any)?.provider || "google";

        // Upsert profile with service role to bypass RLS
        const { error: upsertError } = await supabaseAdmin.from("profiles").upsert(
          {
            id: u.id,
            email: u.email,
            first_name: meta.first_name ?? firstName,
            last_name: meta.last_name ?? lastName,
            provider,
            avatar_url: meta.avatar_url ?? meta.picture ?? null,
          },
          { onConflict: "id" }
        );

        if (upsertError) {
          console.error("Auth callback upsert error:", upsertError.message);
        }
      } else if (userError) {
        console.error("Auth callback user fetch error:", userError.message);
      }

      // Session is established; redirect to home (middleware routes to dashboard/preferences)
      return NextResponse.redirect(`${base}/`);
    }

    console.error("Auth error:", error.message);
  }

  return NextResponse.redirect(`${base}/auth/login?error=auth_callback_failed`);
}