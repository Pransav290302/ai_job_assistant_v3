"use client";

import { useTheme } from "@/_lib/ThemeContext";

export default function Settings() {
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === "dark";

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-1">Settings</h3>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Customize appearance and preferences.
        </p>
      </div>

      <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50 p-4">
        <h4 className="text-sm font-medium text-slate-700 dark:text-slate-200 mb-3">Appearance</h4>
        <div className="flex items-center justify-between gap-4">
          <div>
            <p className="text-sm font-medium text-slate-800 dark:text-slate-100">Dark mode</p>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              {isDark ? "Night theme (dark)" : "Day theme (light)"}
            </p>
          </div>
          <button
            type="button"
            role="switch"
            aria-checked={isDark}
            onClick={toggleTheme}
            className={`relative inline-flex h-7 w-12 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors focus:outline-none focus:ring-2 focus:ring-sky-500 focus:ring-offset-2 dark:focus:ring-offset-slate-900 ${
              isDark ? "bg-sky-600" : "bg-slate-300 dark:bg-slate-600"
            }`}
          >
            <span
              className={`pointer-events-none inline-block h-6 w-6 transform rounded-full bg-white shadow ring-0 transition ${
                isDark ? "translate-x-5" : "translate-x-1"
              }`}
            />
          </button>
        </div>
        <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">
          Switch between day (light) and night (dark) theme. Your choice is saved automatically.
        </p>
      </div>
    </div>
  );
}
