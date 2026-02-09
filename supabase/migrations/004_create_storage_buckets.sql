INSERT INTO storage.buckets (id, name, public)
VALUES
  ('resumes', 'resumes', false),
  ('cover_letter', 'cover_letter', false)
ON CONFLICT (id) DO NOTHING;


CREATE POLICY "Users can upload own resume or cover letter"
  ON storage.objects FOR INSERT
  TO authenticated
  WITH CHECK (
    bucket_id IN ('resumes', 'cover_letter')
    AND (name LIKE (auth.uid()::text || '-%'))
  );

CREATE POLICY "Users can read own documents"
  ON storage.objects FOR SELECT
  TO authenticated
  USING (
    bucket_id IN ('resumes', 'cover_letter')
    AND owner_id = auth.uid()::text
  );

CREATE POLICY "Users can update own documents"
  ON storage.objects FOR UPDATE
  TO authenticated
  USING (bucket_id IN ('resumes', 'cover_letter') AND owner_id = auth.uid()::text)
  WITH CHECK (bucket_id IN ('resumes', 'cover_letter') AND owner_id = auth.uid()::text);

CREATE POLICY "Users can delete own documents"
  ON storage.objects FOR DELETE
  TO authenticated
  USING (bucket_id IN ('resumes', 'cover_letter') AND owner_id = auth.uid()::text);
