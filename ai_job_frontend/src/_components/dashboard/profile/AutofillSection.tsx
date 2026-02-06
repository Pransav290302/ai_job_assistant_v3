"use client";

import { useCallback, useEffect, useState } from "react";
import type { AutofillProfile } from "@/types/profile";

const AUTOFILL_FIELDS: { key: keyof AutofillProfile; label: string }[] = [
  { key: "first_name", label: "First Name" },
  { key: "last_name", label: "Last Name" },
  { key: "full_name", label: "Full Name" },
  { key: "email", label: "Email" },
  { key: "phone", label: "Phone" },
  { key: "linkedin_url", label: "LinkedIn URL" },
  { key: "location", label: "Location" },
  { key: "current_title", label: "Current Title" },
  { key: "skills", label: "Skills" },
  { key: "education_summary", label: "Education Summary" },
  { key: "work_history_summary", label: "Work History Summary" },
  { key: "expected_salary", label: "Expected Salary" },
  { key: "availability", label: "Availability" },
];

function CopyButton({
  value,
  onCopied,
  size = "sm",
}: {
  value: string;
  onCopied?: () => void;
  size?: "sm" | "md";
}) {
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(async () => {
    if (!value) return;
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      onCopied?.();
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // fallback for older browsers
      const ta = document.createElement("textarea");
      ta.value = value;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    }
  }, [value, onCopied]);

  const sizeClass = size === "sm" ? "px-2 py-1 text-[10px]" : "px-3 py-1.5 text-xs";

  return (
    <button
      type="button"
      onClick={handleCopy}
      disabled={!value}
      className={`rounded border border-slate-600 bg-slate-800 text-slate-300 hover:border-sky-600 hover:text-sky-300 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:border-slate-600 disabled:hover:text-slate-300 transition-colors ${sizeClass}`}
      title={value ? "Copy to clipboard" : "No value"}
    >
      {copied ? "Copied!" : "Copy"}
    </button>
  );
}

export default function AutofillSection() {
  const [profile, setProfile] = useState<AutofillProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProfile = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/profile/autofill", { credentials: "include" });
      if (!res.ok) {
        if (res.status === 401) {
          setError("Please sign in to view your autofill profile.");
        } else {
          setError("Failed to load profile.");
        }
        setProfile(null);
        return;
      }
      const data = await res.json();
      setProfile(data);
    } catch {
      setError("Failed to load profile.");
      setProfile(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  const [jsonCopied, setJsonCopied] = useState(false);
  const copyAllJson = useCallback(async () => {
    if (!profile) return;
    const json = JSON.stringify(profile, null, 2);
    try {
      await navigator.clipboard.writeText(json);
      setJsonCopied(true);
      setTimeout(() => setJsonCopied(false), 1500);
    } catch {
      const ta = document.createElement("textarea");
      ta.value = json;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
      setJsonCopied(true);
      setTimeout(() => setJsonCopied(false), 1500);
    }
  }, [profile]);

  if (loading) {
    return (
      <div className="rounded-2xl border border-slate-800 bg-slate-800/60 p-8 text-center text-slate-400">
        Loading autofill profile...
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-2xl border border-slate-800 bg-slate-800/60 p-6 space-y-4">
        <div className="rounded-lg border border-amber-800 bg-amber-900/30 px-4 py-3 text-sm text-amber-200">
          {error}
        </div>
        <button
          type="button"
          onClick={fetchProfile}
          className="rounded-lg border border-slate-600 px-4 py-2 text-sm font-medium text-slate-300 hover:border-slate-500"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!profile) {
    return null;
  }

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-800/60 p-6 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-white">For autofill</h2>
          <p className="text-sm text-slate-400 mt-1">
            Copy individual fields or export as JSON for job application forms.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={fetchProfile}
            className="rounded-lg border border-slate-600 px-4 py-2 text-sm font-medium text-slate-300 hover:border-slate-500 hover:text-slate-200"
          >
            Refresh
          </button>
          <button
            type="button"
            onClick={copyAllJson}
            className="rounded-lg border border-sky-600 bg-sky-900/40 px-4 py-2 text-sm font-medium text-sky-200 hover:bg-sky-800/60 disabled:opacity-70"
          >
            {jsonCopied ? "Copied!" : "Copy all as JSON"}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {AUTOFILL_FIELDS.map(({ key, label }) => {
          const value = profile[key] ?? "";
          return (
            <div
              key={key}
              className="flex flex-col gap-1.5 rounded-lg border border-slate-700 bg-slate-900/60 p-4"
            >
              <label className="text-xs font-medium text-slate-400 uppercase tracking-wide">
                {label}
              </label>
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  readOnly
                  value={value}
                  className="flex-1 min-w-0 rounded border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-200 placeholder-slate-500"
                  placeholder="—"
                />
                <CopyButton value={value} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
