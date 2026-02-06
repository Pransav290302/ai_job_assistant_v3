export type PersonalInfo = {
  first_name?: string | null;
  last_name?: string | null;
  preferred_name?: string | null;
  email?: string | null;
  phone?: string | null;
  location?: string | null;
  linkedin_url?: string | null;
  education_summary?: string | null;
  work_history_summary?: string | null;
  expected_salary?: string | null;
  availability?: string | null;
  address1?: string | null;
  address2?: string | null;
  address3?: string | null;
  postal_code?: string | null;
  ethnicity?: string | null;
  authorized_us?: boolean | null;
  authorized_canada?: boolean | null;
  authorized_uk?: boolean | null;
  visa_sponsorship?: boolean | null;
  disability?: boolean | null;
  lgbtq?: boolean | null;
  gender?: string | null;
  veteran?: boolean | null;
  resume_url?: string | null;
  cover_letter_url?: string | null;
};

export type JobPreferences = {
  idx?: number | null;
  user_id?: string | null;
  job_status?: string | null;
  expected_salary?: number | null;
  roles?: string[] | null;
  role_values?: string[] | null;
  locations?: string[] | null;
  work_modes?: string[] | null;
  company_sizes?: string[] | null;
  industries_prefer?: string[] | null;
  industries_avoid?: string[] | null;
  skills_prefer?: string[] | null;
  skills_avoid?: string[] | null;
  /** Set by server; used for "update once per day" limit. */
  updated_at?: string | null;
};

/** Autofill-friendly profile for job application forms. From GET /api/profile/autofill */
export type AutofillProfile = {
  first_name: string;
  last_name: string;
  full_name: string;
  email: string;
  phone: string;
  linkedin_url: string;
  location: string;
  current_title: string;
  skills: string;
  education_summary: string;
  work_history_summary: string;
  expected_salary: string;
  availability: string;
};
