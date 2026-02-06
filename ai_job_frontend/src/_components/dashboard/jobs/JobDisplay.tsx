"use client";

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

export default function JobDisplay({
  job,
  fullDescription,
  loadingFullDescription,
  onLoadFullDescription,
  onNotInterested,
  onSaveToTracker,
  saved,
}: Props) {
  if (!job) return null;

  const hasSourceUrl = !!(job.source_url ?? (job as { url?: string }).url);
  const descriptionToShow = fullDescription ?? job.description ?? "";
  const showLoadFullButton = hasSourceUrl && !fullDescription && onLoadFullDescription;

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-800/60 p-6 space-y-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="space-y-1">
          <div className="text-xs text-slate-400">{job.status ?? job.work_mode ?? ""}</div>
          <h2 className="text-xl font-semibold text-white">{job.title}</h2>
          <p className="text-sm text-slate-300">{job.company}</p>
          {job.match_score != null && (
            <div className="text-xs font-semibold text-emerald-300">Match score: {job.match_score}/10</div>
          )}
        </div>
        <div className="flex gap-2">
          {onNotInterested != null && (
            <button
              type="button"
              onClick={onNotInterested}
              className="rounded-lg border border-slate-600 bg-slate-800 px-3 py-1.5 text-sm text-slate-300 hover:border-slate-500 hover:text-slate-100"
            >
              Not interested
            </button>
          )}
          {onSaveToTracker != null && (
            <button
              type="button"
              onClick={onSaveToTracker}
              disabled={saved}
              className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-sm text-slate-200 hover:border-slate-500 disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {saved ? "Saved to tracker" : "Save to tracker"}
            </button>
          )}
          {(job.source_url ?? (job as { url?: string }).url) && (
            <a
              href={job.source_url ?? (job as { url?: string }).url}
              target="_blank"
              rel="noopener noreferrer"
              className="rounded-lg bg-sky-600 px-4 py-2 text-sm font-semibold text-white hover:bg-sky-500"
            >
              Apply
            </a>
          )}
        </div>
      </div>
      <div className="flex flex-wrap gap-2 text-xs">
        {job.location && (
          <span className="rounded-full border border-slate-700 bg-slate-900 px-3 py-1 text-slate-200">{job.location}</span>
        )}
        <span className="rounded-full border border-slate-700 bg-slate-900 px-3 py-1 text-slate-200">{job.work_mode ?? "—"}</span>
        {job.salary_range && (
          <span className="rounded-full border border-slate-700 bg-slate-900 px-3 py-1 text-slate-200">{job.salary_range}</span>
        )}
      </div>

      <div className="space-y-2">
        <h3 className="text-sm font-semibold text-slate-100">Description</h3>
        <div className="text-sm leading-relaxed text-slate-200 whitespace-pre-wrap max-h-[24rem] overflow-y-auto">
          {descriptionToShow || "No description available."}
        </div>
        {showLoadFullButton && (
          <button
            type="button"
            onClick={onLoadFullDescription}
            disabled={loadingFullDescription}
            className="rounded-lg border border-sky-600 bg-sky-950/50 px-3 py-1.5 text-sm text-sky-300 hover:bg-sky-900/50 disabled:opacity-60"
          >
            {loadingFullDescription ? "Loading…" : "Load full description"}
          </button>
        )}
      </div>
      {(job.ai_analysis?.reasons?.length || job.ai_analysis?.explanation) && (
        <div className="rounded-lg border border-slate-700 bg-slate-900/50 p-3 text-xs text-slate-300 space-y-1">
          <p className="font-semibold text-slate-100">Why this matches you</p>
          {Array.isArray(job.ai_analysis.reasons) && job.ai_analysis.reasons.length > 0 ? (
            <ul className="list-disc list-inside space-y-1">
              {job.ai_analysis.reasons.map((r: string, idx: number) => (
                <li key={idx}>{r}</li>
              ))}
            </ul>
          ) : (
            <p>{job.ai_analysis?.explanation}</p>
          )}
        </div>
      )}
    </div>
  );
}
