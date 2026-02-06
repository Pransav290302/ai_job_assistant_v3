/**
 * Application pipeline statuses (assignment: "where has my application been?").
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
  updated_at?: string | null;
};
