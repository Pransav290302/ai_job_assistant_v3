import { createBrowserClient } from '@supabase/ssr'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

// Warn if on Vercel but using local Supabase (use cloud: https://xxx.supabase.co)
if (typeof window === 'undefined' && process.env.VERCEL && supabaseUrl?.includes('localhost')) {
  console.error(
    '[Supabase] On Vercel, use cloud Supabase (https://your-project.supabase.co). ' +
    'Set NEXT_PUBLIC_SUPABASE_URL in Vercel Environment Variables.'
  )
}

export const supabaseClient = createBrowserClient(supabaseUrl, supabaseAnonKey)