/**
 * Application pipeline statuses (assignment: "where has my application been?").
 * Order reflects typical flow; terminal states: rejected, rejected_after_interview, offer.
 */
export type Status =
  | "not_submitted"
  | "submitted"
  | "initial_response"
  | "interview_requested"
  | "onsite_video_requested"
  | "rejected_after_interview"
  | "offer"
  | "rejected";

export type Job = {
  id: string;
  title: string;
  company: string;
  status: Status;
  source_url?: string | null;
  location?: string | null;
  updated_at?: string | null;
};

/** Valid status values for DB - must match Status type */
export const VALID_STATUSES: Status[] = [
  "not_submitted",
  "submitted",
  "initial_response",
  "interview_requested",
  "onsite_video_requested",
  "rejected_after_interview",
  "offer",
  "rejected",
];

export function normalizeStatus(s: string | null | undefined): Status {
  if (s && VALID_STATUSES.includes(s as Status)) return s as Status;
  return "not_submitted";
}
