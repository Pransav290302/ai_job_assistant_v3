import { NextResponse } from "next/server";
import { createClient } from "@supabase/supabase-js";

/**
 * Test endpoint to verify Supabase tables exist and store data.
 * Open: http://localhost:3000/api/test-supabase (when dev server is running)
 */
export async function GET() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY;

  if (!url || !key) {
    return NextResponse.json({
      ok: false,
      error: "Supabase not configured. Check .env.local has NEXT_PUBLIC_SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.",
    }, { status: 500 });
  }

  const supabase = createClient(url, key, {
    auth: { autoRefreshToken: false, persistSession: false },
  });

  const results: Record<string, unknown> = {
    supabase_configured: true,
    tables: {} as Record<string, unknown>,
  };

  // Test profiles table
  const { data: profilesData, error: profilesError } = await supabase
    .from("profiles")
    .select("id, email, first_name, last_name, onboarded, created_at")
    .limit(5);

  results.tables = {
    ...(results.tables as object),
    profiles: profilesError
      ? { ok: false, error: profilesError.message }
      : {
          ok: true,
          rowCount: profilesData?.length ?? 0,
          sample: profilesData?.map((p) => ({
            id: p.id?.slice(0, 8) + "...",
            email: p.email,
            first_name: p.first_name,
            last_name: p.last_name,
            onboarded: p.onboarded,
          })),
        },
  };

  // Test user_preferences table
  const { data: prefsData, error: prefsError } = await supabase
    .from("user_preferences")
    .select("user_id, roles, locations, job_status, updated_at")
    .limit(5);

  results.tables = {
    ...(results.tables as object),
    user_preferences: prefsError
      ? { ok: false, error: prefsError.message }
      : {
          ok: true,
          rowCount: prefsData?.length ?? 0,
          sample: prefsData?.map((p) => ({
            user_id: (p.user_id as string)?.slice(0, 8) + "...",
            job_status: p.job_status,
            roles_count: Array.isArray(p.roles) ? p.roles.length : 0,
            updated_at: p.updated_at,
          })),
        },
  };

  const allOk =
    !profilesError &&
    !prefsError;

  return NextResponse.json({
    ok: allOk,
    message: allOk
      ? "All tables accessible. Data is being stored."
      : "One or more tables failed. Check the errors below.",
    ...results,
  });
}
