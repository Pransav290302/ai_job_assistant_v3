import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@/_lib/supabaseServer";

const PREFERENCES_UPDATE_COOLDOWN_MS = 24 * 60 * 60 * 1000; // 24 hours

type PreferencesPayload = {
  job_status?: string | null;
  expected_salary?: number | null;
  roles?: string[] | null;
  role_values?: string[] | null;
  locations?: string[] | null;
  work_modes?: string[] | null;
  company_sizes?: string[] | null;
  industries_prefer?: string[] | null;
  industries_avoid?: string[] | null;
  skills_prefer?: string[] | null;
  skills_avoid?: string[] | null;
};

export async function POST(req: NextRequest) {
  try {
    const supabase = await createClient();
    const { data: { user } } = await supabase.auth.getUser();
    if (!user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const body = (await req.json()) as PreferencesPayload;

    // Fetch current preferences to check updated_at
    const { data: existing } = await supabase
      .from("user_preferences")
      .select("updated_at")
      .eq("user_id", user.id)
      .maybeSingle();

    if (existing?.updated_at) {
      const updatedAt = new Date(existing.updated_at).getTime();
      const now = Date.now();
      const nextAvailableAt = updatedAt + PREFERENCES_UPDATE_COOLDOWN_MS;
      if (now < nextAvailableAt) {
        return NextResponse.json(
          {
            error: "You can update preferences once per day. Job suggestions and LLM use this data.",
            next_available_at: new Date(nextAvailableAt).toISOString(),
          },
          { status: 429 }
        );
      }
    }

    const { data: updated, error } = await supabase
      .from("user_preferences")
      .upsert(
        {
          user_id: user.id,
          job_status: body.job_status ?? null,
          expected_salary: body.expected_salary ?? null,
          roles: body.roles ?? [],
          role_values: body.role_values ?? [],
          locations: body.locations ?? [],
          work_modes: body.work_modes ?? [],
          company_sizes: body.company_sizes ?? [],
          industries_prefer: body.industries_prefer ?? [],
          industries_avoid: body.industries_avoid ?? [],
          skills_prefer: body.skills_prefer ?? [],
          skills_avoid: body.skills_avoid ?? [],
          updated_at: new Date().toISOString(),
        },
        { onConflict: "user_id" }
      )
      .select()
      .single();

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 });
    }
    return NextResponse.json(updated);
  } catch (err) {
    console.error("[PREFERENCES_POST]", err);
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Server error" },
      { status: 500 }
    );
  }
}
