"use client";

import { useState } from "react";
import { JobListing } from "@/types/jobs";

type Props = {
  job?: JobListing;
  fullDescription?: string;
  loadingFullDescription?: boolean;
  onLoadFullDescription?: () => void;
  onNotInterested?: () => void;
  onSaveToTracker?: () => void;
  saved?: boolean;
};

function IconLocation() {
  return (
    <svg className="w-4 h-4 text-slate-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
    </svg>
  );
}
function IconBriefcase() {
  return (
    <svg className="w-4 h-4 text-slate-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
    </svg>
  );
}
function IconCurrency() {
  return (
    <svg className="w-4 h-4 text-slate-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  );
}
function IconCheck() {
  return (
    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
    </svg>
  );
}

export default function JobDisplay({
  job,
  fullDescription,
  loadingFullDescription,
  onLoadFullDescription,
  onNotInterested,
  onSaveToTracker,
  saved,
}: Props) {
  const [activeTab, setActiveTab] = useState<"summary" | "full">("summary");
  if (!job) return null;

  const hasSourceUrl = !!(job.source_url ?? (job as { url?: string }).url);
  const descriptionToShow = fullDescription ?? job.description ?? "";
  const showLoadFullButton = hasSourceUrl && !fullDescription && onLoadFullDescription;
  const matchReasons = job.ai_analysis?.reasons;
  const hasMatchReasons = Array.isArray(matchReasons) && matchReasons.length > 0;

  return (
    <div className="rounded-2xl border border-slate-700 bg-slate-900/40 overflow-hidden">
      {/* Top bar: actions */}
      <div className="flex flex-wrap items-center justify-between gap-3 px-5 py-4 border-b border-slate-700 bg-slate-800/50">
        <div className="flex gap-2">
          <span className="text-sm font-medium text-slate-300">Overview</span>
          <span className="text-sm text-slate-500">|</span>
          <span className="text-sm text-slate-500">Company</span>
        </div>
        <div className="flex items-center gap-2">
          {onNotInterested != null && (
            <button
              type="button"
              onClick={onNotInterested}
              className="rounded-lg border border-slate-600 bg-transparent px-3 py-2 text-sm text-slate-300 hover:bg-slate-700/50"
            >
              Not interested
            </button>
          )}
          {onSaveToTracker != null && (
            <button
              type="button"
              onClick={onSaveToTracker}
              disabled={saved}
              className="rounded-lg border border-slate-600 bg-slate-800 px-3 py-2 text-sm text-slate-200 hover:bg-slate-700 disabled:opacity-60"
            >
              {saved ? "Saved" : "Save"}
            </button>
          )}
          {hasSourceUrl && (
            <a
              href={job.source_url ?? (job as { url?: string }).url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 rounded-lg bg-sky-600 px-4 py-2 text-sm font-semibold text-white hover:bg-sky-500"
            >
              <span>Apply</span>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
            </a>
          )}
        </div>
      </div>

      <div className="grid lg:grid-cols-[340px_1fr] min-h-[420px]">
        {/* Left pane: job summary & company */}
        <div className="border-b lg:border-b-0 lg:border-r border-slate-700 bg-slate-800/30 p-5 space-y-4">
          <div>
            <span className="inline-block rounded-md bg-emerald-500/20 px-2.5 py-1 text-xs font-medium text-emerald-300">
              {job.work_mode || "Full-Time"}
            </span>
            <h1 className="mt-2 text-xl font-bold text-white">{job.title}</h1>
            <p className="mt-0.5 text-xs text-slate-400">Recent listing</p>
          </div>

          <div className="flex items-start gap-3">
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-slate-700 text-lg font-bold text-slate-300">
              {job.company.charAt(0).toUpperCase()}
            </div>
            <div>
              <p className="font-semibold text-slate-100">{job.company}</p>
              <p className="text-xs text-slate-400">Company</p>
            </div>
          </div>

          <div className="space-y-2 text-sm">
            <div className="flex items-center gap-2 text-slate-300">
              <IconCurrency />
              <span>{job.salary_range || "No salary listed"}</span>
            </div>
            <div className="flex items-start gap-2 text-slate-300">
              <IconBriefcase />
              <span>{job.work_mode || "—"}</span>
            </div>
            {job.location && (
              <div className="flex items-start gap-2 text-slate-300">
                <IconLocation />
                <span>{job.location}</span>
              </div>
            )}
          </div>

          <div className="flex flex-wrap gap-1.5">
            {job.location && (
              <span className="rounded-full bg-slate-700/80 px-3 py-1 text-xs text-slate-200">{job.location}</span>
            )}
            <span className="rounded-full bg-slate-700/80 px-3 py-1 text-xs text-slate-200">{job.work_mode ?? "—"}</span>
            {job.match_score != null && (
              <span className="rounded-full bg-emerald-500/20 px-3 py-1 text-xs font-medium text-emerald-300">
                Match {job.match_score}/10
              </span>
            )}
          </div>
        </div>

        {/* Right pane: tabs + matching + description */}
        <div className="p-5 flex flex-col">
          <div className="flex gap-1 border-b border-slate-700 mb-4">
            <button
              type="button"
              onClick={() => setActiveTab("summary")}
              className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${
                activeTab === "summary"
                  ? "bg-slate-800 text-white border border-slate-700 border-b-0 -mb-px"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Summary
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("full")}
              className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${
                activeTab === "full"
                  ? "bg-slate-800 text-white border border-slate-700 border-b-0 -mb-px"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Full Job Posting
            </button>
          </div>

          {(job.match_score != null || hasMatchReasons || job.ai_analysis?.explanation) && (
            <div className="rounded-xl border border-slate-700 bg-slate-800/40 p-4 mb-4">
              <h3 className="text-sm font-semibold text-white flex items-center gap-2 mb-1">
                <span className="text-amber-400">★</span>
                You match the following candidate preferences
              </h3>
              <p className="text-xs text-slate-400 mb-3">Employers are more likely to interview you if you match these preferences.</p>
              <div className="flex flex-wrap gap-2">
                {job.match_score != null && (
                  <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500/20 px-3 py-1 text-xs font-medium text-emerald-300">
                    <IconCheck /> Match score {job.match_score}/10
                  </span>
                )}
                {hasMatchReasons &&
                  matchReasons.slice(0, 4).map((r: string, idx: number) => (
                    <span
                      key={idx}
                      className="inline-flex items-center gap-1 rounded-full bg-emerald-500/20 px-3 py-1 text-xs font-medium text-emerald-300"
                    >
                      <IconCheck /> {r.length > 30 ? r.slice(0, 30) + "…" : r}
                    </span>
                  ))}
                {!hasMatchReasons && job.ai_analysis?.explanation && (
                  <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500/20 px-3 py-1 text-xs text-emerald-300">
                    <IconCheck /> Profile match
                  </span>
                )}
              </div>
            </div>
          )}

          <div className="flex-1 overflow-y-auto">
            {activeTab === "summary" && (
              <div className="text-sm leading-relaxed text-slate-200 whitespace-pre-wrap max-h-[20rem]">
                {descriptionToShow
                  ? descriptionToShow.slice(0, 1200) + (descriptionToShow.length > 1200 ? "…" : "")
                  : "No description available."}
              </div>
            )}
            {activeTab === "full" && (
              <div className="text-sm leading-relaxed text-slate-200 whitespace-pre-wrap">
                {descriptionToShow || "No description available."}
              </div>
            )}
          </div>

          {showLoadFullButton && (
            <button
              type="button"
              onClick={onLoadFullDescription}
              disabled={loadingFullDescription}
              className="mt-3 rounded-lg border border-sky-600 bg-sky-950/40 px-3 py-2 text-sm text-sky-300 hover:bg-sky-900/40 disabled:opacity-60"
            >
              {loadingFullDescription ? "Loading…" : "Load full description"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
