"use client";

import { useCallback, useEffect, useState } from "react";
import { Job, Status, normalizeStatus } from "@/types/jobTracker";
import { supabaseClient } from "@/_lib/supabaseClient";
import JobTrackerCard from "./JobTrackerCard";
import AddJobModal from "./AddJobModal";

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
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [signedIn, setSignedIn] = useState<boolean | null>(null);
  const [updatingId, setUpdatingId] = useState<string | null>(null);
  const [addModalOpen, setAddModalOpen] = useState(false);

  const fetchJobs = useCallback(async () => {
    setLoading(true);
    setError(null);
    const { data, error: fetchError } = await supabaseClient
      .from("jobs")
      .select("id, title, company, status, source_url, location, updated_at")
      .order("updated_at", { ascending: false });

    if (fetchError) {
      setError(fetchError.message);
      setJobs([]);
    } else {
      const mapped: Job[] = (data ?? []).map((row) => ({
        id: row.id,
        title: row.title,
        company: row.company,
        status: normalizeStatus(row.status),
        source_url: row.source_url,
        location: row.location,
        updated_at: row.updated_at,
      }));
      setJobs(mapped);
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    supabaseClient.auth.getUser().then(({ data }) => {
      setSignedIn(!!data.user);
    });
  }, []);

  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  const updateStatus = useCallback(
    async (jobId: string, newStatus: Status) => {
      setUpdatingId(jobId);
      const { error: updateError } = await supabaseClient
        .from("jobs")
        .update({
          status: newStatus,
          updated_at: new Date().toISOString(),
          ...(newStatus === "submitted"
            ? { applied_at: new Date().toISOString() }
            : {}),
        })
        .eq("id", jobId);

      if (updateError) {
        setError(updateError.message);
      } else {
        setJobs((prev) =>
          prev.map((j) => (j.id === jobId ? { ...j, status: newStatus } : j))
        );
      }
      setUpdatingId(null);
    },
    []
  );

  const addJob = useCallback(
    async (data: {
      title: string;
      company: string;
      source_url?: string;
      location?: string;
    }) => {
      const { data: user } = await supabaseClient.auth.getUser();
      if (!user.user?.id) {
        setError("Please sign in to add jobs");
        return;
      }
      const { error: insertError } = await supabaseClient.from("jobs").insert({
        user_id: user.user.id,
        title: data.title,
        company: data.company,
        source_url: data.source_url ?? null,
        location: data.location ?? "",
        work_mode: "Remote",
        status: "not_submitted",
      });

      if (insertError) {
        setError(insertError.message);
      } else {
        fetchJobs();
      }
    },
    [fetchJobs]
  );

  const jobsByStatus = jobs.reduce<Record<Status, Job[]>>(
    (acc, job) => {
      acc[job.status].push(job);
      return acc;
    },
    {
      not_submitted: [],
      submitted: [],
      initial_response: [],
      interview_requested: [],
      onsite_video_requested: [],
      rejected_after_interview: [],
      offer: [],
      rejected: [],
    }
  );

  const totals = initialCounts();
  for (const job of jobs) {
    if (totals[job.status] !== undefined) totals[job.status] += 1;
  }
  const totalJobs = jobs.length;

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      <div className="w-full px-6 md:px-12 lg:px-20 xl:px-28 py-10 space-y-6">
        <header className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-semibold">Your Job Tracker</h1>
              <span className="rounded-full border border-slate-700 bg-slate-800 px-3 py-1 text-xs text-slate-200">
                {totalJobs} total
              </span>
            </div>
            <p className="text-sm text-slate-400">
              See where each application is: not submitted → submitted → responses → interviews → offer or rejected.
            </p>
          </div>
          {signedIn && (
            <button
              onClick={() => setAddModalOpen(true)}
              className="self-start rounded-lg bg-sky-600 px-4 py-2 text-sm font-medium text-white hover:bg-sky-500"
            >
              + Add Job
            </button>
          )}
        </header>

        {signedIn === false && (
          <div className="rounded-lg border border-amber-800 bg-amber-900/30 px-4 py-3 text-sm text-amber-200">
            Sign in to track your job applications.
          </div>
        )}

        {error && (
          <div className="rounded-lg border border-rose-800 bg-rose-900/30 px-4 py-3 text-sm text-rose-200">
            {error}
          </div>
        )}

        {loading ? (
          <div className="rounded-2xl border border-slate-800 bg-slate-800/60 p-12 text-center text-slate-400">
            Loading jobs...
          </div>
        ) : (
          <div className="rounded-2xl border border-slate-800 bg-slate-800/60 overflow-x-auto">
            <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 divide-y sm:divide-y-0 sm:divide-x divide-slate-800 min-w-[640px]">
              {STATUS_ORDER.map((status) => (
                <div
                  key={status}
                  className="p-3 sm:p-4 space-y-2 min-w-0 flex flex-col"
                >
                  <div className="flex flex-col gap-1 text-xs uppercase tracking-wide text-slate-400 shrink-0">
                    <span className="leading-tight">{STATUS_LABEL[status]}</span>
                    <span className="rounded-md bg-slate-900 px-2 py-0.5 text-slate-200 w-fit">
                      {totals[status]}
                    </span>
                  </div>
                  <div className="flex-1 min-h-[80px] space-y-2 overflow-y-auto">
                    {jobsByStatus[status].length === 0 ? (
                      <div className="min-h-20 rounded-lg border border-dashed border-slate-700 bg-slate-900/60 flex items-center justify-center text-xs text-slate-500 p-2">
                        —
                      </div>
                    ) : (
                      jobsByStatus[status].map((job) => (
                        <JobTrackerCard
                          key={job.id}
                          job={job}
                          onStatusChange={updateStatus}
                          allStatuses={STATUS_ORDER}
                        />
                      ))
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <AddJobModal
        isOpen={addModalOpen}
        onClose={() => setAddModalOpen(false)}
        onAdd={addJob}
      />
    </div>
  );
}
