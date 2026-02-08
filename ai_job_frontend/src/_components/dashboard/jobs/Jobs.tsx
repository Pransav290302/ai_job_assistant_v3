"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { JobListing } from "@/types/jobs";
import { supabaseClient } from "@/_lib/supabaseClient";
import { useJobsContextOptional } from "@/_lib/JobsContext";
import JobCardList from "./JobCardList";
import JobDisplay from "./JobDisplay";

const getBackendBase = () =>
  typeof window !== "undefined"
    ? "/api/backend"
    : process.env.NEXT_PUBLIC_BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || "";

const EXPERIENCE_OPTIONS = ["All", "Entry", "Junior", "Mid", "Senior", "Lead", "Manager", "Director"];
const CATEGORY_OPTIONS = ["All", "Engineering", "Software", "Data", "Product", "Sales", "Marketing", "Design", "Research", "Analyst"];

function matchesSearch(job: JobListing, q: string): boolean {
  if (!q.trim()) return true;
  const lower = q.toLowerCase();
  const title = (job.title || "").toLowerCase();
  const company = (job.company || "").toLowerCase();
  const location = (job.location || "").toLowerCase();
  const desc = (job.description || "").toLowerCase();
  return title.includes(lower) || company.includes(lower) || location.includes(lower) || desc.includes(lower);
}

function matchesExperience(job: JobListing, exp: string): boolean {
  if (!exp || exp === "All") return true;
  const title = (job.title || "").toLowerCase();
  const desc = (job.description || "").toLowerCase();
  const combined = `${title} ${desc}`;
  if (exp === "Entry") return /entry|intern|graduate|0-1|0–1/i.test(combined);
  if (exp === "Junior") return /junior|jr\.?|entry|associate/i.test(combined);
  if (exp === "Mid") return /mid|middle|mid-level|intermediate|2-4|3\+/i.test(combined);
  if (exp === "Senior") return /senior|sr\.?|lead|principal|staff|5\+|experience/i.test(combined);
  if (exp === "Lead") return /lead|principal|staff/i.test(combined);
  if (exp === "Manager") return /manager|management|head of/i.test(combined);
  if (exp === "Director") return /director|head of/i.test(combined);
  return combined.includes(exp.toLowerCase());
}

function matchesCategory(job: JobListing, cat: string): boolean {
  if (!cat || cat === "All") return true;
  const title = (job.title || "").toLowerCase();
  const desc = (job.description || "").toLowerCase();
  const combined = `${title} ${desc}`;
  return combined.includes(cat.toLowerCase());
}

type Props = {
  initialJobs: JobListing[];
};

export default function Jobs({ initialJobs }: Props) {
  const ctx = useJobsContextOptional();
  const [jobs, setJobs] = useState<JobListing[]>([]);
  const [selectedId, setSelectedId] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);

  const [searchQuery, setSearchQuery] = useState("");
  const [filterLocation, setFilterLocation] = useState<string>("All");
  const [filterJobType, setFilterJobType] = useState<string>("All");
  const [filterExperience, setFilterExperience] = useState<string>("All");
  const [filterCategory, setFilterCategory] = useState<string>("All");

  const filteredJobs = useMemo(() => {
    return jobs.filter((job) => {
      if (!matchesSearch(job, searchQuery)) return false;
      if (filterLocation && filterLocation !== "All" && (job.location || "").toLowerCase() !== filterLocation.toLowerCase()) return false;
      if (filterJobType && filterJobType !== "All" && (job.work_mode || "").toLowerCase() !== filterJobType.toLowerCase()) return false;
      if (!matchesExperience(job, filterExperience)) return false;
      if (!matchesCategory(job, filterCategory)) return false;
      return true;
    });
  }, [jobs, searchQuery, filterLocation, filterJobType, filterExperience, filterCategory]);

  const uniqueLocations = useMemo(() => {
    const set = new Set<string>();
    jobs.forEach((j) => {
      const loc = (j.location || "").trim();
      if (loc) set.add(loc);
    });
    return ["All", ...Array.from(set).sort()];
  }, [jobs]);

  const uniqueJobTypes = useMemo(() => {
    const set = new Set<string>();
    jobs.forEach((j) => {
      const w = (j.work_mode || "").trim();
      if (w) set.add(w);
    });
    return ["All", ...Array.from(set).sort()];
  }, [jobs]);

  const selectedJob = useMemo(
    () => filteredJobs.find((j) => j.id === selectedId) ?? filteredJobs[0],
    [filteredJobs, selectedId]
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
          body: JSON.stringify({ user_id: userId, max_jobs: 60, max_ranked: 50 }),
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
          ctx?.setJobs(list);
          ctx?.setReasoning(rankData.reasoning || null);
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
        `${base}/api/job/discover?q=${encodeURIComponent(query)}&location=${encodeURIComponent(location)}&max_results=60`,
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
        location: (j.location as string) || (data.location as string) || "",
        work_mode: (j.type as string) || "Remote",
        source_url: (j.url as string) || null,
        description: j.snippet ? String(j.snippet) : null,
      }));
      setJobs(list);
      ctx?.setJobs(list);
      ctx?.setReasoning(null);
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
  }, [ctx]);

  useEffect(() => {
    if (ctx?.jobs?.length) {
      setJobs(ctx.jobs);
      setSelectedId(ctx.jobs[0]?.id ?? "");
      setLoading(false);
      return;
    }
    fetchRealJobs();
  }, [ctx?.jobs?.length, fetchRealJobs]);

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
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full md:w-96 rounded-xl border border-slate-700 bg-slate-900 px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500"
              aria-label="Search jobs"
            />
            <div className="flex flex-wrap gap-2 items-center">
              <select
                value={filterLocation}
                onChange={(e) => setFilterLocation(e.target.value)}
                className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-sky-500"
                aria-label="Filter by location"
              >
                {uniqueLocations.map((loc) => (
                  <option key={loc} value={loc}>{loc}</option>
                ))}
              </select>
              <select
                value={filterJobType}
                onChange={(e) => setFilterJobType(e.target.value)}
                className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-sky-500"
                aria-label="Filter by job type"
              >
                {uniqueJobTypes.map((t) => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
              <select
                value={filterExperience}
                onChange={(e) => setFilterExperience(e.target.value)}
                className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-sky-500"
                aria-label="Filter by experience"
              >
                {EXPERIENCE_OPTIONS.map((e) => (
                  <option key={e} value={e}>{e}</option>
                ))}
              </select>
              <select
                value={filterCategory}
                onChange={(e) => setFilterCategory(e.target.value)}
                className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-sky-500"
                aria-label="Filter by category"
              >
                {CATEGORY_OPTIONS.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
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
              <div className="text-xs text-slate-400">
                Showing {filteredJobs.length} of {jobs.length} jobs
              </div>
              <JobCardList jobs={filteredJobs} selectedId={selectedId} onSelect={setSelectedId} />
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
