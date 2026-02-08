"use client";

type Props = {
  activeTab: "profile" | "personal" | "preferences";
  onTabChange: (tab: "profile" | "personal" | "preferences") => void;
};

export default function ProfileSidebar({ activeTab, onTabChange }: Props) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-800/60 p-6 space-y-6">
      <div className="flex flex-col gap-3">
        <button
          onClick={() => onTabChange("profile")}
          className={`w-full flex items-center justify-between rounded-xl px-4 py-3 text-sm font-medium transition-colors ${
            activeTab === "profile"
              ? "bg-sky-600 text-white shadow-sm shadow-sky-900/40"
              : "bg-slate-900 border border-slate-700 hover:border-slate-500"
          }`}
        >
          <span className="flex items-center gap-3">
            <span className="text-base">📝</span>
            Profile
          </span>
        </button>

        <button
          onClick={() => onTabChange("personal")}
          className={`w-full flex items-center justify-between rounded-xl px-4 py-3 text-sm font-medium transition-colors ${
            activeTab === "personal"
              ? "bg-sky-600 text-white shadow-sm shadow-sky-900/40"
              : "bg-slate-900 border border-slate-700 hover:border-slate-500"
          }`}
        >
          <span className="flex items-center gap-3">
            <span className="text-base">📊</span>
            Personal Info
          </span>
        </button>

        <button
          onClick={() => onTabChange("preferences")}
          className={`w-full flex items-center justify-between rounded-xl px-4 py-3 text-sm font-medium transition-colors ${
            activeTab === "preferences"
              ? "bg-sky-600 text-white shadow-sm shadow-sky-900/40"
              : "bg-slate-900 border border-slate-700 hover:border-slate-500"
          }`}
        >
          <span className="flex items-center gap-3">
            <span className="text-base">💼</span>
            Job Preferences
          </span>
        </button>
      </div>

    </div>
  );
}