"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { JobListing } from "@/types/jobs";
import { supabaseClient } from "@/_lib/supabaseClient";
import JobCardList from "./JobCardList";
import JobDisplay from "./JobDisplay";

const getBackendBase = () =>
  typeof window !== "undefined"
    ? "/api/backend"
    : process.env.NEXT_PUBLIC_BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || "";

type Props = {
  initialJobs: JobListing[];
};

export default function Jobs({ initialJobs }: Props) {
  const [jobs, setJobs] = useState<JobListing[]>([]);
  const [selectedId, setSelectedId] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);

  const selectedJob = useMemo(
    () => jobs.find((j) => j.id === selectedId) ?? jobs[0],
    [jobs, selectedId]
  );

  const fetchRealJobs = useCallback(async () => {
    const base = getBackendBase();
    if (!base) {
      setError("Backend URL not set. Set NEXT_PUBLIC_BACKEND_URL in .env.local.");
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    setStatus("Fetching real jobs for you…");
    try {
      const { data: userData } = await supabaseClient.auth.getUser();
      const userId = userData.user?.id;

      if (userId) {
        setStatus("Using your profile and ranking with AI…");
        const rankRes = await fetch(`${base}/api/job/rank-for-user`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ user_id: userId, max_jobs: 25, max_ranked: 20 }),
        });
        const rankData = await rankRes.json().catch(() => ({}));
        if (rankRes.ok && !rankData.error) {
          const ranked: Array<{ title?: string; company?: string; url?: string; snippet?: string; location?: string; score?: number; explanation?: string }> =
            rankData.ranked_jobs || [];
          const list: JobListing[] = ranked.map((r, i) => ({
            id: r.url || `rank-${i}-${Date.now()}`,
            title: r.title || "Job",
            company: r.company || "",
            location: r.location || "",
            work_mode: "Remote",
            source_url: r.url || null,
            description: r.snippet || null,
            match_score: r.score ?? null,
            ai_analysis: r.explanation ? { explanation: r.explanation, reasons: [r.explanation] } : undefined,
          }));
          setJobs(list);
          setSelectedId(list[0]?.id ?? "");
          setStatus(null);
          if (list.length === 0) {
            setError(rankData.reasoning || "No jobs found. Update preferences or try again.");
          }
          return;
        }
        if (rankData.error) {
          setError(rankData.error);
          setStatus(null);
          return;
        }
      }

      let query = "software engineer";
      let location = "";
      try {
        const profileRes = await fetch("/api/profile/autofill", { credentials: "include" });
        if (profileRes.ok) {
          const profile = await profileRes.json();
          if (profile.current_title?.trim()) query = profile.current_title.trim();
          if (profile.skills?.trim()) query = [query, profile.skills].filter(Boolean).join(" ");
          if (profile.location?.trim()) location = profile.location.trim();
        }
      } catch {
        // keep defaults
      }
      setStatus("Searching job boards…");
      const res = await fetch(
        `${base}/api/job/discover?q=${encodeURIComponent(query)}&location=${encodeURIComponent(location)}&max_results=25`,
        { credentials: "include" }
      );
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setError(typeof data.detail === "string" ? data.detail : data.error || `Error ${res.status}`);
        setStatus(null);
        return;
      }
      const rawJobs: Record<string, unknown>[] = Array.isArray(data.jobs) ? data.jobs : [];
      const list: JobListing[] = rawJobs.map((j, i) => ({
        id: (j.url as string) || `discover-${i}-${Date.now()}`,
        title: String(j.title ?? "Job"),
        company: String(j.company ?? ""),
        location: (data.location as string) || location || "",
        work_mode: "Remote",
        source_url: (j.url as string) || null,
        description: j.snippet ? String(j.snippet) : null,
      }));
      setJobs(list);
      setSelectedId(list[0]?.id ?? "");
      setStatus(null);
      if (list.length === 0) {
        setError("No jobs found for this search. Try different keywords or location.");
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load jobs");
      setStatus(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRealJobs();
  }, [fetchRealJobs]);

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      <div className="w-full px-6 md:px-10 lg:px-16 xl:px-20 py-8 space-y-6">
        <header className="flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-semibold">Search All Jobs</h1>
            <button
              type="button"
              onClick={fetchRealJobs}
              disabled={loading}
              className="rounded-xl bg-sky-600 px-4 py-2 text-sm font-medium text-white hover:bg-sky-500 disabled:opacity-60"
            >
              {loading ? "Loading…" : "Refresh jobs"}
            </button>
          </div>
          <div className="flex flex-wrap gap-3">
            <input
              type="text"
              placeholder="Search for roles, companies, or locations"
              className="w-full md:w-96 rounded-xl border border-slate-700 bg-slate-900 px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500"
              readOnly
              aria-label="Search (filters coming soon)"
            />
            <div className="flex flex-wrap gap-2 text-xs">
              <span className="px-3 py-1 rounded-full border border-slate-700 bg-slate-800 text-slate-200">Location</span>
              <span className="px-3 py-1 rounded-full border border-slate-700 bg-slate-800 text-slate-200">Job Type</span>
              <span className="px-3 py-1 rounded-full border border-slate-700 bg-slate-800 text-slate-200">Experience</span>
              <span className="px-3 py-1 rounded-full border border-slate-700 bg-slate-800 text-slate-200">Category</span>
            </div>
          </div>
          {status && (
            <div className="flex items-center gap-2 rounded-lg border border-sky-800 bg-sky-950/50 px-4 py-2 text-sm text-sky-200">
              <span className="inline-block h-2 w-2 animate-pulse rounded-full bg-sky-400" aria-hidden />
              {status}
            </div>
          )}
          {error && (
            <div className="rounded-lg border border-red-800 bg-red-950/30 px-4 py-2 text-sm text-red-200">
              {error}
            </div>
          )}
        </header>

        {loading && jobs.length === 0 ? (
          <div className="rounded-2xl border border-slate-800 bg-slate-800/40 p-8 text-center text-slate-300">
            Loading real jobs for you…
          </div>
        ) : jobs.length === 0 ? (
          <div className="rounded-2xl border border-slate-800 bg-slate-800/40 p-8 text-center">
            <p className="text-slate-300 mb-4">No jobs found. Try refreshing or update your profile preferences.</p>
            <button
              type="button"
              onClick={fetchRealJobs}
              className="rounded-xl bg-sky-600 px-4 py-2 text-sm font-medium text-white hover:bg-sky-500"
            >
              Refresh jobs
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1 space-y-3">
              <div className="text-xs text-slate-400">Showing {jobs.length} real jobs</div>
              <JobCardList jobs={jobs} selectedId={selectedId} onSelect={setSelectedId} />
            </div>
            <div className="lg:col-span-2 space-y-4">
              {selectedJob && (
                <JobDisplay
                  job={selectedJob}
                  fullDescription={undefined}
                  loadingFullDescription={false}
                  onLoadFullDescription={undefined}
                  onSaveToTracker={undefined}
                  saved={false}
                />
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
