-- Create jobs table for saved/tracked job listings
-- Run this in Supabase SQL Editor or via: supabase db push

CREATE TABLE IF NOT EXISTS public.jobs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  title text NOT NULL,
  company text NOT NULL,
  location text DEFAULT '',
  work_mode text DEFAULT 'Remote',
  source_url text,
  description text,
  salary_range text,
  ai_analysis jsonb,
  status text DEFAULT 'not_submitted',
  applied_at timestamptz,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Index for listing jobs by user
CREATE INDEX IF NOT EXISTS idx_jobs_user_id ON public.jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_jobs_updated_at ON public.jobs(updated_at DESC);

-- Enable RLS
ALTER TABLE public.jobs ENABLE ROW LEVEL SECURITY;

-- Users can read their own jobs
CREATE POLICY "Users can read own jobs"
  ON public.jobs FOR SELECT
  USING (auth.uid() = user_id);

-- Users can insert their own jobs
CREATE POLICY "Users can insert own jobs"
  ON public.jobs FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Users can update their own jobs
CREATE POLICY "Users can update own jobs"
  ON public.jobs FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- Users can delete their own jobs
CREATE POLICY "Users can delete own jobs"
  ON public.jobs FOR DELETE
  USING (auth.uid() = user_id);

COMMENT ON TABLE public.jobs IS 'User-saved job listings and application status';