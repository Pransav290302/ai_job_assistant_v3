import { createBrowserClient } from '@supabase/ssr'
import type { SupabaseClient } from '@supabase/supabase-js'

let _client: SupabaseClient | null = null

function getSupabaseClient() {
  if (_client) return _client
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL
  const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
  if (!url || !key) {
    throw new Error(
      "@supabase/ssr: Your project's URL and API key are required to create a Supabase client! " +
      "Set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY in .env.local"
    )
  }
  if (typeof window === 'undefined' && process.env.VERCEL && url.includes('localhost')) {
    console.error(
      '[Supabase] On Vercel, use cloud Supabase. Set NEXT_PUBLIC_SUPABASE_URL in Vercel Environment Variables.'
    )
  }
  _client = createBrowserClient(url, key)
  return _client
}

// Lazy-initialized client - avoids throwing at import time during prerender/build
export const supabaseClient = new Proxy({} as SupabaseClient, {
  get(_, prop) {
    return getSupabaseClient()[prop as keyof SupabaseClient]
  },
})