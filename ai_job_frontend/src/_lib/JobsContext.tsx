"use client";

import { createContext, useCallback, useContext, useState } from "react";
import { JobListing } from "@/types/jobs";

type JobsContextValue = {
  jobs: JobListing[];
  setJobs: (jobs: JobListing[]) => void;
  reasoning: string | null;
  setReasoning: (s: string | null) => void;
  hasFetched: boolean;
  setHasFetched: (v: boolean) => void;
};

const JobsContext = createContext<JobsContextValue | null>(null);

export function JobsProvider({ children }: { children: React.ReactNode }) {
  const [jobs, setJobsState] = useState<JobListing[]>([]);
  const [reasoning, setReasoningState] = useState<string | null>(null);
  const [hasFetched, setHasFetched] = useState(false);

  const setJobs = useCallback((list: JobListing[]) => {
    setJobsState(list);
    setHasFetched(true);
  }, []);

  const setReasoning = useCallback((s: string | null) => {
    setReasoningState(s);
  }, []);

  return (
    <JobsContext.Provider
      value={{
        jobs,
        setJobs,
        reasoning,
        setReasoning,
        hasFetched,
        setHasFetched,
      }}
    >
      {children}
    </JobsContext.Provider>
  );
}

export function useJobsContext() {
  const ctx = useContext(JobsContext);
  if (!ctx) throw new Error("useJobsContext must be used within JobsProvider");
  return ctx;
}

export function useJobsContextOptional() {
  return useContext(JobsContext);
}
