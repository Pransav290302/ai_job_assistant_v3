"use client";

export type ProfileTab = "profile" | "autofill" | "personal" | "preferences" | "settings";

type Props = {
  activeTab: ProfileTab;
  onTabChange: (tab: ProfileTab) => void;
};

export default function ProfileSidebar({ activeTab, onTabChange }: Props) {
  return (
    <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-800/60 p-6 space-y-6 shadow-sm dark:shadow-none">
      <div className="flex flex-col gap-3">
        <button
          onClick={() => onTabChange("profile")}
          className={`w-full flex items-center justify-between rounded-xl px-4 py-3 text-sm font-medium transition-colors ${
            activeTab === "profile"
              ? "bg-sky-600 text-white shadow-sm shadow-sky-900/40"
              : "bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 hover:border-slate-400 dark:hover:border-slate-500 text-slate-800 dark:text-slate-200"
          }`}
        >
          <span className="flex items-center gap-3">
            <span className="text-base">📝</span>
            Profile
          </span>
          <span className="text-xs text-sky-100">Documents + overview</span>
        </button>

        <button
          onClick={() => onTabChange("autofill")}
          className={`w-full flex items-center justify-between rounded-xl px-4 py-3 text-sm font-medium transition-colors ${
            activeTab === "autofill"
              ? "bg-sky-600 text-white shadow-sm shadow-sky-900/40"
              : "bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 hover:border-slate-400 dark:hover:border-slate-500 text-slate-800 dark:text-slate-200"
          }`}
        >
          <span className="flex items-center gap-3">
            <span className="text-base">📋</span>
            For autofill
          </span>
          <span className="text-xs text-slate-500 dark:text-slate-400">Copy fields for forms</span>
        </button>

        <button
          onClick={() => onTabChange("personal")}
          className={`w-full flex items-center justify-between rounded-xl px-4 py-3 text-sm font-medium transition-colors ${
            activeTab === "personal"
              ? "bg-sky-600 text-white shadow-sm shadow-sky-900/40"
              : "bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 hover:border-slate-400 dark:hover:border-slate-500 text-slate-800 dark:text-slate-200"
          }`}
        >
          <span className="flex items-center gap-3">
            <span className="text-base">📊</span>
            Personal Info
          </span>
          <span className="text-xs text-slate-500 dark:text-slate-400">Edit demographic data</span>
        </button>

        <button
          onClick={() => onTabChange("preferences")}
          className={`w-full flex items-center justify-between rounded-xl px-4 py-3 text-sm font-medium transition-colors ${
            activeTab === "preferences"
              ? "bg-sky-600 text-white shadow-sm shadow-sky-900/40"
              : "bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 hover:border-slate-400 dark:hover:border-slate-500 text-slate-800 dark:text-slate-200"
          }`}
        >
          <span className="flex items-center gap-3">
            <span className="text-base">💼</span>
            Job Preferences
          </span>
          <span className="text-xs text-slate-500 dark:text-slate-400">Refine your job search</span>
        </button>

        <button
          onClick={() => onTabChange("settings")}
          className={`w-full flex items-center justify-between rounded-xl px-4 py-3 text-sm font-medium transition-colors ${
            activeTab === "settings"
              ? "bg-sky-600 text-white shadow-sm shadow-sky-900/40"
              : "bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 hover:border-slate-400 dark:hover:border-slate-500 text-slate-800 dark:text-slate-200"
          }`}
        >
          <span className="flex items-center gap-3">
            <span className="text-base">⚙️</span>
            Settings
          </span>
          <span className="text-xs text-slate-500 dark:text-slate-400">Theme & preferences</span>
        </button>
      </div>
    </div>
  );
}