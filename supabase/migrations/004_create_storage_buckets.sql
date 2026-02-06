-- Storage buckets for resumes and cover letters
-- Buckets must exist in Supabase before uploads work. Create them in Dashboard if this insert fails:
-- Storage → New bucket → "resumes" (Private) and "cover_letter" (Private).

-- Create buckets (works on many hosted Supabase projects; if it errors, create via Dashboard)
INSERT INTO storage.buckets (id, name, public)
VALUES
  ('resumes', 'resumes', false),
  ('cover_letter', 'cover_letter', false)
ON CONFLICT (id) DO NOTHING;

-- RLS on storage.objects: authenticated users can only access their own files in these buckets.
-- App stores paths like: {user_id}-{timestamp}-{filename}.pdf

-- INSERT: only into resumes/cover_letter and path must start with own user id
CREATE POLICY "Users can upload own resume or cover letter"
  ON storage.objects FOR INSERT
  TO authenticated
  WITH CHECK (
    bucket_id IN ('resumes', 'cover_letter')
    AND (name LIKE (auth.uid()::text || '-%'))
  );

-- SELECT: only own objects (owner_id is text; auth.uid() is uuid)
CREATE POLICY "Users can read own documents"
  ON storage.objects FOR SELECT
  TO authenticated
  USING (
    bucket_id IN ('resumes', 'cover_letter')
    AND owner_id = auth.uid()::text
  );

-- UPDATE: only own objects (needed for upsert overwrite)
CREATE POLICY "Users can update own documents"
  ON storage.objects FOR UPDATE
  TO authenticated
  USING (bucket_id IN ('resumes', 'cover_letter') AND owner_id = auth.uid()::text)
  WITH CHECK (bucket_id IN ('resumes', 'cover_letter') AND owner_id = auth.uid()::text);

-- DELETE: only own objects
CREATE POLICY "Users can delete own documents"
  ON storage.objects FOR DELETE
  TO authenticated
  USING (bucket_id IN ('resumes', 'cover_letter') AND owner_id = auth.uid()::text);
