"use client";

import { useMemo, useState } from "react";
import { Job, Status } from "@/types/jobTracker";

const STATUS_ORDER: Status[] = [
    "not_submitted",
    "submitted",
    "initial_response",
    "interview_requested",
    "onsite_video_requested",
    "rejected_after_interview",
    "offer",
    "rejected",
];

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

const initialCounts = (): Record<Status, number> => ({
    not_submitted: 0,
    submitted: 0,
    initial_response: 0,
    interview_requested: 0,
    onsite_video_requested: 0,
    rejected_after_interview: 0,
    offer: 0,
    rejected: 0,
});

export default function JobTracker() {
    const [jobs] = useState<Job[]>([]);

    const totals = useMemo(() => {
        const counts = initialCounts();
        for (const job of jobs) {
            if (counts[job.status] !== undefined) counts[job.status] += 1;
        }
        return counts;
    }, [jobs]);

    const totalJobs = jobs.length;

    return (
        <div className="min-h-screen bg-slate-900 text-slate-100">
            <div className="w-full px-6 md:px-12 lg:px-20 xl:px-28 py-10 space-y-6">
                <header className="flex flex-col gap-2">
                    <div className="flex items-center gap-3">
                        <h1 className="text-2xl font-semibold">Your Job Tracker</h1>
                        <span className="rounded-full border border-slate-700 bg-slate-800 px-3 py-1 text-xs text-slate-200">
                            {totalJobs} total
                        </span>
                    </div>
                    <p className="text-sm text-slate-400">
                        See where each application is: not submitted → submitted → responses → interviews → offer or rejected.
                    </p>
                </header>

                <div className="rounded-2xl border border-slate-800 bg-slate-800/60 overflow-hidden">
                    <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 divide-y sm:divide-y-0 sm:divide-x divide-slate-800">
                        {STATUS_ORDER.map((status) => (
                            <div key={status} className="p-3 sm:p-4 space-y-2 min-w-0">
                                <div className="flex flex-col gap-1 text-xs uppercase tracking-wide text-slate-400">
                                    <span className="leading-tight">{STATUS_LABEL[status]}</span>
                                    <span className="rounded-md bg-slate-900 px-2 py-0.5 text-slate-200 w-fit">
                                        {totals[status]}
                                    </span>
                                </div>
                                <div className="min-h-20 rounded-lg border border-dashed border-slate-700 bg-slate-900/60 flex items-center justify-center text-xs text-slate-500 p-2">
                                    {totals[status] === 0 ? "—" : "Jobs here"}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
