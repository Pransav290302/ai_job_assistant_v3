# Google & LinkedIn OAuth Setup (Supabase + Vercel)

This app uses **Supabase Auth** for Google and LinkedIn login. Auth runs entirely on the **Vercel frontend**; the Render backend does not handle auth.

## 1. Supabase URL Configuration

In [Supabase Dashboard](https://supabase.com/dashboard) → **Authentication** → **URL Configuration**:

| Setting | Value |
|---------|-------|
| **Site URL** | `https://your-app.vercel.app` (your production URL) |
| **Redirect URLs** | Add these (one per line): |
| | `https://your-app.vercel.app/auth/callback` |
| | `http://localhost:3000/auth/callback` |
| | `https://*-your-org.vercel.app/auth/callback` (for preview deploys) |

Replace `your-app` and `your-org` with your actual Vercel project and team/account slug.

## 2. Vercel Environment Variable

Add to Vercel → **Settings** → **Environment Variables**:

| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_SITE_URL` | `https://your-app.vercel.app` |

This ensures OAuth redirects use the correct production URL. If unset, the app falls back to `VERCEL_URL`.

## 3. Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project (or select one)
3. **APIs & Services** → **Credentials** → **Create Credentials** → **OAuth client ID**
4. Application type: **Web application**
5. **Authorized redirect URIs**: add your Supabase callback (from Supabase → Auth → Providers → Google):
   ```
   https://<your-project-ref>.supabase.co/auth/v1/callback
   ```
   Find your project ref in Supabase Dashboard → Settings → API.
6. Copy **Client ID** and **Client Secret**
7. In Supabase → **Authentication** → **Providers** → **Google**:
   - Enable Google
   - Paste Client ID and Client Secret
   - Save

## 4. LinkedIn OAuth Setup (OIDC)

1. Go to [LinkedIn Developer Dashboard](https://www.linkedin.com/developers/apps)
2. Create an app (or use existing)
3. **Products** → Request access to **Sign In with LinkedIn using OpenID Connect**
4. **Auth** tab → **Authorized redirect URLs for your app**:
   - Add: `https://<your-project-ref>.supabase.co/auth/v1/callback`
   - (Get this from Supabase → Auth → Providers → LinkedIn (OIDC))
5. Copy **Client ID** and **Client Secret**
6. In Supabase → **Authentication** → **Providers** → **LinkedIn (OIDC)**:
   - Enable LinkedIn (OIDC)
   - Paste Client ID and Client Secret
   - Save

> **Note:** Use **LinkedIn (OIDC)**, not the deprecated "LinkedIn" provider.

## 5. Quick Checklist

- [ ] Supabase: Site URL = production Vercel URL
- [ ] Supabase: Redirect URLs include `/auth/callback` for prod + local
- [ ] Vercel: `NEXT_PUBLIC_SITE_URL` = production URL
- [ ] Google Console: Redirect URI = `https://<project-ref>.supabase.co/auth/v1/callback`
- [ ] Supabase: Google provider enabled with Client ID + Secret
- [ ] LinkedIn: OIDC product enabled, redirect URI added
- [ ] Supabase: LinkedIn (OIDC) provider enabled with Client ID + Secret
- [ ] Redeploy Vercel after changing env vars

## Troubleshooting

**"Redirect URL not allowed"**
- Ensure the exact callback URL is in Supabase Redirect URLs
- For preview deploys, add the wildcard: `https://*-your-org.vercel.app/auth/callback`

**"Invalid OAuth client"**
- Verify Client ID and Secret in Supabase match Google/LinkedIn
- Ensure the redirect URI in Google/LinkedIn exactly matches Supabase callback

**Auth works locally but not on Vercel**
- Set `NEXT_PUBLIC_SITE_URL` in Vercel to your production URL
- Redeploy after adding the variable
