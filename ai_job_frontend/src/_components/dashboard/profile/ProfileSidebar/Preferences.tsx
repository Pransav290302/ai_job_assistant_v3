"use client";

import { useMemo, useState } from "react";
import { JobPreferences } from "@/types/profile";

const PREFERENCES_UPDATE_COOLDOWN_MS = 24 * 60 * 60 * 1000; // 24 hours

type Props = {
  userId: string | null;
  value: JobPreferences;
  onChange: (prefs: JobPreferences) => void;
};

const stringToArray = (value: string) =>
  value
    .split(",")
    .map((v) => v.trim())
    .filter(Boolean);

function canUpdatePreferences(updatedAt: string | null | undefined): boolean {
  if (!updatedAt) return true;
  const updated = new Date(updatedAt).getTime();
  return Date.now() - updated >= PREFERENCES_UPDATE_COOLDOWN_MS;
}

function nextAvailableAt(updatedAt: string | null | undefined): Date | null {
  if (!updatedAt) return null;
  const updated = new Date(updatedAt).getTime();
  return new Date(updated + PREFERENCES_UPDATE_COOLDOWN_MS);
}

export default function Preferences({ userId, value, onChange }: Props) {
  const [saving, setSaving] = useState(false);
  const [rateLimitMessage, setRateLimitMessage] = useState<string | null>(null);

  const canUpdate = useMemo(
    () => canUpdatePreferences(value.updated_at ?? null),
    [value.updated_at]
  );
  const nextAt = useMemo(
    () => nextAvailableAt(value.updated_at ?? null),
    [value.updated_at]
  );

  const updateField = (field: keyof JobPreferences, newValue: any) => {
    onChange({ ...value, [field]: newValue });
  };

  const handleSave = async () => {
    if (!userId) {
      alert("Please sign in to save your preferences.");
      return;
    }
    if (!canUpdate) {
      setRateLimitMessage(
        nextAt
          ? `You can update preferences once per day. Next update available at ${nextAt.toLocaleString()}.`
          : "You can update preferences once per day."
      );
      return;
    }
    setSaving(true);
    setRateLimitMessage(null);
    const res = await fetch("/api/profile/preferences", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        job_status: value.job_status ?? null,
        expected_salary: value.expected_salary ?? null,
        roles: value.roles ?? [],
        role_values: value.role_values ?? [],
        locations: value.locations ?? [],
        work_modes: value.work_modes ?? [],
        company_sizes: value.company_sizes ?? [],
        industries_prefer: value.industries_prefer ?? [],
        industries_avoid: value.industries_avoid ?? [],
        skills_prefer: value.skills_prefer ?? [],
        skills_avoid: value.skills_avoid ?? [],
      }),
    });
    const data = await res.json().catch(() => ({}));
    setSaving(false);
    if (res.status === 429) {
      const nextAtStr = data.next_available_at
        ? ` Next update at ${new Date(data.next_available_at).toLocaleString()}.`
        : "";
      setRateLimitMessage(
        (data.error || "You can update preferences once per day. Job suggestions and LLM use this data.") + nextAtStr
      );
      return;
    }
    if (!res.ok) {
      alert(data.error || "Failed to save preferences");
      return;
    }
    onChange({ ...value, ...data });
    alert("Preferences saved. You can change them again in 24 hours.");
  };

  return (
    <>
      <h3 className="text-lg font-semibold mb-3">Job Preferences</h3>
      <div className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-xs text-slate-400">Job Status</label>
            <input
              className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm"
              value={value.job_status ?? ""}
              onChange={(e) => updateField("job_status", e.target.value)}
              placeholder="Actively looking, Open to offers, etc."
            />
          </div>
          <div>
            <label className="text-xs text-slate-400">Expected Salary</label>
            <input
              type="number"
              className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm"
              value={value.expected_salary ?? ""}
              onChange={(e) => updateField("expected_salary", e.target.value ? Number(e.target.value) : null)}
              placeholder="125000"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-xs text-slate-400">Role Values</label>
            <input
              className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm"
              value={(value.role_values ?? []).join(", ")}
              onChange={(e) => updateField("role_values", stringToArray(e.target.value))}
              placeholder="Impact, Growth, Learning"
            />
          </div>
          <div>
            <label className="text-xs text-slate-400">Roles</label>
            <input
              className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm"
              value={(value.roles ?? []).join(", ")}
              onChange={(e) => updateField("roles", stringToArray(e.target.value))}
              placeholder="Frontend Engineer, Fullstack Engineer"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-xs text-slate-400">Locations</label>
            <input
              className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm"
              value={(value.locations ?? []).join(", ")}
              onChange={(e) => updateField("locations", stringToArray(e.target.value))}
              placeholder="Remote, New York, London"
            />
          </div>
          <div>
            <label className="text-xs text-slate-400">Work Modes</label>
            <input
              className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm"
              value={(value.work_modes ?? []).join(", ")}
              onChange={(e) => updateField("work_modes", stringToArray(e.target.value))}
              placeholder="Remote, Hybrid, Onsite"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-xs text-slate-400">Preferred Company Sizes</label>
            <input
              className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm"
              value={(value.company_sizes ?? []).join(", ")}
              onChange={(e) => updateField("company_sizes", stringToArray(e.target.value))}
              placeholder="1-10, 50-200, 500+"
            />
          </div>
          <div>
            <label className="text-xs text-slate-400">Preferred Industries</label>
            <input
              className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm"
              value={(value.industries_prefer ?? []).join(", ")}
              onChange={(e) => updateField("industries_prefer", stringToArray(e.target.value))}
              placeholder="Fintech, AI, Developer Tools"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-xs text-slate-400">Industries to Avoid</label>
            <input
              className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm"
              value={(value.industries_avoid ?? []).join(", ")}
              onChange={(e) => updateField("industries_avoid", stringToArray(e.target.value))}
              placeholder="Gambling, Tobacco"
            />
          </div>
          <div>
            <label className="text-xs text-slate-400">Skills to Highlight</label>
            <input
              className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm"
              value={(value.skills_prefer ?? []).join(", ")}
              onChange={(e) => updateField("skills_prefer", stringToArray(e.target.value))}
              placeholder="React, TypeScript, Node.js"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-xs text-slate-400">Skills to Avoid</label>
            <input
              className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm"
              value={(value.skills_avoid ?? []).join(", ")}
              onChange={(e) => updateField("skills_avoid", stringToArray(e.target.value))}
              placeholder="PHP, COBOL"
            />
          </div>
          <div />
        </div>

        {rateLimitMessage && (
          <p className="text-amber-400 text-sm mt-2">{rateLimitMessage}</p>
        )}
        {!canUpdate && nextAt && (
          <p className="text-slate-400 text-sm mt-2">
            Next update available at {nextAt.toLocaleString()}. Job suggestions and LLM depend on this data.
          </p>
        )}
        <div className="flex justify-end mt-4">
          <button
            onClick={handleSave}
            disabled={saving || !canUpdate}
            className="px-5 py-2 rounded-lg bg-sky-600 hover:bg-sky-500 disabled:opacity-60 disabled:cursor-not-allowed transition-colors text-sm font-semibold"
          >
            {saving ? "Saving..." : !canUpdate ? "Update once per day" : "Save Preferences"}
          </button>
        </div>
      </div>
    </>
  );
}
