/**
 * GET /api/profile/autofill
 *
 * Returns the current user's profile in an autofill-friendly format for job
 * application forms. Requires Supabase auth session.
 *
 * Data sources: profiles, user_preferences, user_personal_info (if exists)
 * See: AGENTIC_WORKFLOWS_DESIGN.md - AutofillProfile contract
 */
import { NextResponse } from "next/server";
import { createClient } from "@/_lib/supabaseServer";
import type { AutofillProfile } from "@/types/profile";

function orEmpty(value: unknown): string {
  if (value == null || value === "") return "";
  if (Array.isArray(value)) return value.map(String).filter(Boolean).join(", ");
  return String(value);
}

export async function GET() {
  const supabase = await createClient();
  const { data, error } = await supabase.auth.getUser();

  if (error || !data.user) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const uid = data.user.id;

  // Fetch profiles (always exists for Supabase auth users)
  const { data: profile } = await supabase
    .from("profiles")
    .select("first_name, last_name, email")
    .eq("id", uid)
    .maybeSingle();

  // Fetch user_preferences
  const { data: prefs } = await supabase
    .from("user_preferences")
    .select("*")
    .eq("user_id", uid)
    .maybeSingle();

  // Fetch user_personal_info (optional; table may not exist in all projects)
  let personal: Record<string, unknown> | null = null;
  try {
    const { data: p } = await supabase
      .from("user_personal_info")
      .select("*")
      .eq("user_id", uid)
      .maybeSingle();
    personal = p as Record<string, unknown> | null;
  } catch {
    // user_personal_info table may not exist
  }

  const firstName =
    orEmpty(personal?.first_name) ||
    orEmpty(profile?.first_name) ||
    "";
  const lastName =
    orEmpty(personal?.last_name) ||
    orEmpty(profile?.last_name) ||
    "";
  const fullName = [firstName, lastName].filter(Boolean).join(" ").trim() ||
    orEmpty(profile?.email?.split("@")[0]) ||
    "";
  const email = orEmpty(personal?.email) || orEmpty(profile?.email) || "";

  const locations = prefs?.locations;
  const locationStr = Array.isArray(locations)
    ? locations.map(String).filter(Boolean).join(", ")
    : orEmpty(personal?.location);

  const roles = prefs?.roles;
  const currentTitle = Array.isArray(roles) && roles.length > 0
    ? String(roles[0])
    : "";

  const skillsPrefer = prefs?.skills_prefer;
  const skills = Array.isArray(skillsPrefer)
    ? skillsPrefer.map(String).filter(Boolean).join(", ")
    : "";

  const expectedSalary =
    prefs?.expected_salary != null
      ? String(prefs.expected_salary)
      : orEmpty(personal?.expected_salary);

  const autofill: AutofillProfile = {
    first_name: firstName,
    last_name: lastName,
    full_name: fullName,
    email,
    phone: orEmpty(personal?.phone),
    linkedin_url: orEmpty(personal?.linkedin_url),
    location: locationStr,
    current_title: currentTitle,
    skills,
    education_summary: orEmpty(personal?.education_summary),
    work_history_summary: orEmpty(personal?.work_history_summary),
    expected_salary: expectedSalary,
    availability: orEmpty(personal?.availability),
  };

  return NextResponse.json(autofill);
}
