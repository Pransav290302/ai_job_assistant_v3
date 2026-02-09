ALTER TABLE public.user_personal_info
  ADD COLUMN IF NOT EXISTS resume_url text,
  ADD COLUMN IF NOT EXISTS cover_letter_url text;

COMMENT ON COLUMN public.user_personal_info.resume_url IS 'Storage path for uploaded resume file';
COMMENT ON COLUMN public.user_personal_info.cover_letter_url IS 'Storage path for uploaded cover letter file';
