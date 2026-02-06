import Link from "next/link";
import { createClient } from "@/_lib/supabaseServer";

export default async function DashboardPage() {
  const supabase = await createClient();
  const { data: authData } = await supabase.auth.getUser();
  const uid = authData.user?.id ?? null;

  let firstName: string | null = null;
  let lastName: string | null = null;

  if (uid) {
    const { data: profile } = await supabase
      .from("profiles")
      .select("first_name, last_name")
      .eq("id", uid)
      .single();
    firstName = profile?.first_name ?? null;
    lastName = profile?.last_name ?? null;
  }

  const displayName = [firstName, lastName].filter(Boolean).join(" ") || "there";

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      <div className="max-w-6xl mx-auto px-4 py-10">
        <div className="rounded-3xl border border-slate-800 bg-slate-800/70 shadow-lg px-8 py-6">
          <div className="flex flex-col gap-4">
            <div className="flex items-center justify-between gap-4 flex-wrap">
              <div>
                <p className="text-sm font-semibold text-slate-300">Welcome</p>
                <h1 className="text-2xl md:text-3xl font-bold text-white">Welcome, {displayName} 👋</h1>
              </div>
              <div className="flex gap-3">
                <Link
                  href="/preferences"
                  className="rounded-full border border-slate-600 bg-slate-900 px-4 py-2 text-sm font-semibold text-slate-100 hover:border-slate-400"
                >
                  Match Preferences
                </Link>
                <Link
                  href="/matches"
                  className="rounded-full bg-sky-600 px-4 py-2 text-sm font-semibold text-white hover:bg-sky-500"
                >
                  View All Matches
                </Link>
              </div>
            </div>
            <div className="rounded-2xl bg-slate-900/60 border border-slate-700 px-4 py-3">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <div className="flex items-center gap-3 text-sm font-semibold text-slate-100">
                  <span className="text-lg">🔥</span>
                  <span>0 Day Streak</span>
                </div>
                <div className="flex items-center gap-2 text-xs text-slate-300">
                  <span>View 5 matches to start your streak!</span>
                  <span className="h-1.5 w-28 bg-slate-800 rounded-full overflow-hidden">
                    <span className="block h-full w-0 bg-sky-500" />
                  </span>
                  <span>day 0/7</span>
                </div>
              </div>
            </div>

            <section className="rounded-2xl border border-slate-700 bg-slate-900/50 p-6">
              <h2 className="text-lg font-semibold text-white mb-1">Overview</h2>
              <p className="text-sm text-slate-400 mb-4">Quick access to job search and tracking.</p>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                <Link
                  href="/matches"
                  className="group rounded-xl border border-slate-600 bg-slate-800/50 p-5 hover:border-sky-500/50 hover:bg-slate-800/70 transition-all"
                >
                  <div className="flex items-start gap-3">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-sky-500/20 text-sky-400 group-hover:bg-sky-500/30">
                      <span className="text-lg">🎯</span>
                    </div>
                    <div>
                      <span className="font-semibold text-slate-100">Job Matching</span>
                      <p className="text-xs text-slate-400 mt-1">AI-ranked roles based on your profile. Find best matches.</p>
                      <span className="inline-block mt-2 rounded-full bg-slate-700/80 px-2.5 py-0.5 text-xs text-slate-300">Matches</span>
                    </div>
                  </div>
                </Link>
                <Link
                  href="/jobs"
                  className="group rounded-xl border border-slate-600 bg-slate-800/50 p-5 hover:border-sky-500/50 hover:bg-slate-800/70 transition-all"
                >
                  <div className="flex items-start gap-3">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-emerald-500/20 text-emerald-400 group-hover:bg-emerald-500/30">
                      <span className="text-lg">📋</span>
                    </div>
                    <div>
                      <span className="font-semibold text-slate-100">Browse Jobs</span>
                      <p className="text-xs text-slate-400 mt-1">Discover jobs from ZipRecruiter, DailyAIJobs & more.</p>
                      <span className="inline-block mt-2 rounded-full bg-slate-700/80 px-2.5 py-0.5 text-xs text-slate-300">Discover</span>
                    </div>
                  </div>
                </Link>
                <Link
                  href="/job_tracker"
                  className="group rounded-xl border border-slate-600 bg-slate-800/50 p-5 hover:border-sky-500/50 hover:bg-slate-800/70 transition-all"
                >
                  <div className="flex items-start gap-3">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-amber-500/20 text-amber-400 group-hover:bg-amber-500/30">
                      <span className="text-lg">📌</span>
                    </div>
                    <div>
                      <span className="font-semibold text-slate-100">Job Tracker</span>
                      <p className="text-xs text-slate-400 mt-1">Track applications and status in one place.</p>
                      <span className="inline-block mt-2 rounded-full bg-slate-700/80 px-2.5 py-0.5 text-xs text-slate-300">Track</span>
                    </div>
                  </div>
                </Link>
              </div>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}
