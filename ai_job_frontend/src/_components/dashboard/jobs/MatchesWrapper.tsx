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

function discoverJobToListing(job: { title?: string; company?: string; url?: string; snippet?: string }, index: number, searchLocation: string): JobListing {
  return {
    id: job.url || `discover-${index}-${Date.now()}`,
    title: job.title || "Job",
    company: job.company || "",
    location: searchLocation || "",
    work_mode: "Remote",
    source_url: job.url || null,
    description: job.snippet || null,
  };
}

type Props = {
  initialMatches: JobListing[];
};

export default function MatchesWrapper({ initialMatches }: Props) {
  const [matches, setMatches] = useState<JobListing[]>(initialMatches);
  const [selectedId, setSelectedId] = useState<string>(initialMatches[0]?.id ?? "");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [agentStatus, setAgentStatus] = useState<string | null>(null);
  const [dismissedIds, setDismissedIds] = useState<Set<string>>(new Set());
  const [savedIds, setSavedIds] = useState<Set<string>>(new Set());
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
  const [reasoning, setReasoning] = useState<string | null>(null);
  const [backendStatus, setBackendStatus] = useState<{
    reachable: boolean;
    openai_configured?: boolean;
    model?: string;
  } | null>(null);
  const [fullDescriptions, setFullDescriptions] = useState<Record<string, string>>({});
  const [loadingFullId, setLoadingFullId] = useState<string | null>(null);

  useEffect(() => {
    const base = getBackendBase();
    if (!base) {
      setBackendStatus({ reachable: false });
      return;
    }
    fetch(`${base}/api/status`, { credentials: "include" })
      .then((res) => res.json().catch(() => ({})))
      .then((data) => {
        setBackendStatus({
          reachable: true,
          openai_configured: data.openai_configured,
          model: data.model,
        });
      })
      .catch(() => setBackendStatus({ reachable: false }));
  }, []);

  // Auto-fetch real-time profile-matched jobs on mount (scraper + DeepSeek R1)
  useEffect(() => {
    if (initialMatches.length > 0) return;
    const timer = setTimeout(() => findMatches(), 100);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const visibleMatches = useMemo(
    () => matches.filter((j) => !dismissedIds.has(j.id)),
    [matches, dismissedIds]
  );

  const selectedJob = useMemo(
    () => visibleMatches.find((j) => j.id === selectedId) ?? visibleMatches[0],
    [visibleMatches, selectedId]
  );

  const findMatches = useCallback(async () => {
    const base = getBackendBase();
    if (!base) {
      setError(
        "Backend URL not set. Add NEXT_PUBLIC_BACKEND_URL to ai_job_frontend/.env.local (e.g. http://localhost:8000) and restart the frontend."
      );
      return;
    }
    setLoading(true);
    setError(null);
    setReasoning(null);
    setAgentStatus("Using your profile from preferences…");
    try {
      const { data: userData } = await supabaseClient.auth.getUser();
      const userId = userData.user?.id;

      if (userId) {
        setAgentStatus("Fetching jobs and ranking with DeepSeek R1…");
        const rankRes = await fetch(`${base}/api/job/rank-for-user`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ user_id: userId, max_jobs: 20, max_ranked: 15 }),
        });
        const rankData = await rankRes.json().catch(() => ({}));
        if (rankRes.ok && !rankData.error) {
          setReasoning(rankData.reasoning || null);
          const ranked: Array<{ rank?: number; title?: string; company?: string; url?: string; snippet?: string; location?: string; explanation?: string; score?: number }> =
            rankData.ranked_jobs || [];
          const list: JobListing[] = ranked.map((r, i) => ({
            id: r.url || `rank-${r.rank ?? i}-${Date.now()}`,
            title: r.title || "Job",
            company: r.company || "",
            location: r.location || "",
            work_mode: "Remote",
            source_url: r.url || null,
            description: r.snippet || null,
            match_score: r.score ?? null,
            ai_analysis: r.explanation ? { explanation: r.explanation, reasons: [r.explanation] } : undefined,
          }));
          setMatches(list);
          setDismissedIds(new Set());
          setSavedIds(new Set());
          setSelectedId(list[0]?.id ?? "");
          setAgentStatus(null);
          if (list.length === 0) {
            setError(rankData.reasoning || "No ranked jobs. Update your preferences (roles, skills, location) and try again.");
          }
          return;
        }
        if (rankData.error) {
          setError(rankData.error);
          setAgentStatus(null);
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
      setAgentStatus("Finding matches…");
      const discoverUrl = `${base}/api/job/discover?q=${encodeURIComponent(query)}&location=${encodeURIComponent(location)}&max_results=20`;
      const res = await fetch(discoverUrl, { credentials: "include" });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        const msg =
          (typeof data.detail === "string" ? data.detail : null) ||
          data.error ||
          (res.status === 502
            ? "Backend unreachable. Is it running? Check NEXT_PUBLIC_BACKEND_URL in .env.local."
            : null) ||
          `Backend error: ${res.status}`;
        throw new Error(msg);
      }
      setAgentStatus("Ranking results…");
      const jobs: Record<string, unknown>[] = Array.isArray(data.jobs) ? data.jobs : [];
      const list: JobListing[] = jobs.map((j, i) =>
        discoverJobToListing(
          {
            title: String(j.title ?? "Job"),
            company: String(j.company ?? ""),
            url: j.url ? String(j.url) : undefined,
            snippet: j.snippet ? String(j.snippet) : undefined,
          },
          i,
          data.location ? String(data.location) : location
        )
      );
      setMatches(list);
      setDismissedIds(new Set());
      setSavedIds(new Set());
      setSelectedId(list[0]?.id ?? "");
      setAgentStatus(null);
      if (list.length === 0) {
        setError(
          "No jobs found for this search. Indeed may have returned no results—try a different role or location, or check backend logs."
        );
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to find matches");
      setAgentStatus(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleNotInterested = useCallback((id: string) => {
    setDismissedIds((prev) => new Set(prev).add(id));
    setSelectedId((current) => {
      if (current !== id) return current;
      const nextVisible = matches.filter((j) => j.id !== id && !dismissedIds.has(j.id));
      return nextVisible[0]?.id ?? "";
    });
  }, [matches, dismissedIds]);

  const handleSaveToTracker = useCallback(
    async (job: JobListing) => {
      const { data: user } = await supabaseClient.auth.getUser();
      if (!user.user?.id) {
        setError("Please sign in to save jobs to your tracker.");
        return;
      }
      const { error: insertError } = await supabaseClient.from("jobs").insert({
        user_id: user.user.id,
        title: job.title,
        company: job.company,
        source_url: job.source_url ?? null,
        location: job.location ?? "",
        description: job.description ?? null,
        work_mode: job.work_mode ?? "Remote",
        status: "not_submitted",
      });
      if (insertError) {
        setError(insertError.message);
      } else {
        setSavedIds((prev) => new Set(prev).add(job.id));
      }
    },
    []
  );

  const loadFullDescription = useCallback(async (job: JobListing) => {
    const url = job.source_url ?? (job as { url?: string }).url;
    if (!url) return;
    const base = getBackendBase();
    if (!base) return;
    setLoadingFullId(job.id);
    try {
      const res = await fetch(`${base}/api/job/scrape`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ job_url: url }),
      });
      const data = await res.json().catch(() => ({}));
      if (res.ok && data.text) {
        setFullDescriptions((prev) => ({ ...prev, [job.id]: String(data.text) }));
      }
    } finally {
      setLoadingFullId((id) => (id === job.id ? null : id));
    }
  }, []);

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      <div className="w-full px-6 md:px-10 lg:px-16 xl:px-20 py-8 space-y-6">
        <header className="flex flex-col gap-3">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h1 className="text-2xl font-semibold">Best Matches</h1>
              <p className="text-sm text-slate-400">AI-ranked roles based on your profile</p>
            </div>
            <button
              type="button"
              onClick={findMatches}
              disabled={loading}
              className="rounded-xl bg-sky-600 px-4 py-2 text-sm font-medium text-white hover:bg-sky-500 disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {loading ? "Finding…" : "Find matches"}
            </button>
          </div>
          {backendStatus != null && (
            <div className="text-xs text-slate-500">
              {backendStatus.reachable ? (
                <>
                  Backend: connected
                  {backendStatus.openai_configured !== undefined && (
                    <> · LLM: {backendStatus.openai_configured ? `configured (${backendStatus.model ?? "—"})` : "not configured"}</>
                  )}
                </>
              ) : (
                "Backend: unreachable — set NEXT_PUBLIC_BACKEND_URL in .env.local and ensure the backend is running."
              )}
            </div>
          )}
          {agentStatus && (
            <div className="flex items-center gap-2 rounded-lg border border-sky-800 bg-sky-950/50 px-4 py-2 text-sm text-sky-200" role="status">
              <span className="inline-block h-2 w-2 animate-pulse rounded-full bg-sky-400" aria-hidden />
              {agentStatus}
            </div>
          )}
          {reasoning && (
            <div className="rounded-lg border border-slate-700 bg-slate-800/50 px-4 py-3 text-sm text-slate-200">
              <p className="font-medium text-slate-100 mb-1">Why these matches</p>
              <p className="text-slate-300">{reasoning}</p>
            </div>
          )}
          {error && (
            <div className="rounded-lg border border-red-800 bg-red-950/30 px-4 py-2 text-sm text-red-200">
              {error}
            </div>
          )}
        </header>

        {visibleMatches.length === 0 && !loading && (
          <div className="rounded-2xl border border-slate-800 bg-slate-800/40 p-8 text-center">
            <p className="text-slate-300 mb-4">No matches yet. Get AI-ranked roles based on your profile.</p>
            <button
              type="button"
              onClick={findMatches}
              className="rounded-xl bg-sky-600 px-4 py-2 text-sm font-medium text-white hover:bg-sky-500"
            >
              Find matches
            </button>
          </div>
        )}

        {visibleMatches.length > 0 && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1 space-y-3">
              <div className="text-xs text-slate-400">Showing {visibleMatches.length} matches</div>
              <JobCardList
                jobs={visibleMatches}
                selectedId={selectedId}
                onSelect={setSelectedId}
              />
            </div>
            <div className="lg:col-span-2 space-y-4">
              {selectedJob && (
                <JobDisplay
                  job={selectedJob}
                  fullDescription={fullDescriptions[selectedJob.id]}
                  loadingFullDescription={loadingFullId === selectedJob.id}
                  onLoadFullDescription={() => loadFullDescription(selectedJob)}
                  onNotInterested={() => handleNotInterested(selectedJob.id)}
                  onSaveToTracker={() => handleSaveToTracker(selectedJob)}
                  saved={savedIds.has(selectedJob.id)}
                />
              )}
            </div>
          </div>
        )}

        {!feedbackSubmitted && (visibleMatches.length > 0 || loading) && (
          <div className="mt-8 rounded-xl border border-slate-700 bg-slate-800/50 p-4">
            <p className="text-sm text-slate-300 mb-2">Was this helpful?</p>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setFeedbackSubmitted(true)}
                className="rounded-lg border border-slate-600 bg-slate-800 px-3 py-1.5 text-sm text-slate-200 hover:bg-slate-700"
              >
                Yes
              </button>
              <button
                type="button"
                onClick={() => setFeedbackSubmitted(true)}
                className="rounded-lg border border-slate-600 bg-slate-800 px-3 py-1.5 text-sm text-slate-200 hover:bg-slate-700"
              >
                No
              </button>
            </div>
          </div>
        )}
        {feedbackSubmitted && (
          <p className="text-sm text-slate-500">Thanks for your feedback.</p>
        )}
      </div>
    </div>
  );
}
