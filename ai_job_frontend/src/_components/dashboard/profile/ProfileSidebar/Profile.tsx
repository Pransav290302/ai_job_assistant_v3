"use client";

import Documents from "../Documents";
import { PersonalInfo } from "@/types/profile";

type Props = {
    userId: string | null;
    value: PersonalInfo;
    onChange: (info: PersonalInfo) => void;
};

export default function DefaultProfile({ userId, value, onChange }: Props) {
    return (
        <div className="space-y-4">
            <div className="rounded-2xl border border-slate-800 bg-slate-800/60 p-4">
                <Documents userId={userId} value={value} onChange={onChange} />
            </div>
        </div>
    );
}
