"use client";

import { Job, Status } from "@/types/jobTracker";

const STATUS_LABEL: Record<Status, string> = {
  not_submitted: "Not submitted",
  submitted: "Submitted",
  initial_response: "Initial response",
  interview_requested: "Interview requested",
  onsite_video_requested: "Onsite / video",
  rejected_after_interview: "Rejected (after interview)",
  offer: "Offer",
  rejected: "Rejected",
};

type Props = {
  job: Job;
  onStatusChange: (jobId: string, newStatus: Status) => void;
  allStatuses: Status[];
};

export default function JobTrackerCard({
  job,
  onStatusChange,
  allStatuses,
}: Props) {
  return (
    <div className="rounded-lg border border-slate-700 bg-slate-900/80 p-3 shadow-sm hover:border-slate-600 transition-colors">
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0 flex-1">
          <h3 className="text-sm font-semibold text-white truncate" title={job.title}>
            {job.title}
          </h3>
          <p className="text-xs text-slate-400 truncate">{job.company}</p>
        </div>
        <select
          value={job.status}
          onChange={(e) => onStatusChange(job.id, e.target.value as Status)}
          className="text-[10px] rounded border border-slate-600 bg-slate-800 text-slate-200 px-2 py-1 cursor-pointer hover:border-slate-500 focus:outline-none focus:ring-1 focus:ring-sky-500"
          onClick={(e) => e.stopPropagation()}
        >
          {allStatuses.map((s) => (
            <option key={s} value={s}>
              {STATUS_LABEL[s]}
            </option>
          ))}
        </select>
      </div>
      {job.source_url && (
        <a
          href={job.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-2 block text-[10px] text-sky-400 hover:text-sky-300 truncate"
          onClick={(e) => e.stopPropagation()}
        >
          View posting →
        </a>
      )}
    </div>
  );
}
