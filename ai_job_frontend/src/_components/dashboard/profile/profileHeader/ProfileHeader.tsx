"use client";

import UserInfo from "./UserInfo";

const TITLE = "My Career Hub";
const BADGE = "Profile Overview";

type Props = {
  name: string;
  initials: string;
  status?: string | null;
};

export default function ProfileHeader({ name, initials, status }: Props) {
  return (
    <div className="rounded-3xl border border-slate-200 dark:border-slate-800 bg-white/90 dark:bg-slate-900/70 px-6 py-6 lg:px-8 lg:py-7 shadow-sm dark:shadow-none">
      <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
        <div className="space-y-3">
          <div className="inline-flex items-center gap-2 rounded-full bg-cyan-100 dark:bg-cyan-950/70 px-3 py-1 text-xs font-semibold text-cyan-800 dark:text-cyan-100">
            <span className="h-2 w-2 rounded-full bg-emerald-500" />
            <span>{BADGE}</span>
          </div>
          <div>
            <h1 className="text-3xl font-bold text-slate-900 dark:text-white">{TITLE}</h1>
          </div>
        </div>

        <UserInfo name={name} initials={initials || "?"} status={status ?? ""} />
      </div>
    </div>
  );
}
