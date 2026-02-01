# Supabase Setup Guide

## How to Add Supabase API Credentials

### Step 1: Get Your Supabase Credentials

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project (or create a new one)
3. Navigate to **Settings** → **API**
4. You'll find three important values:
   - **Project URL** → This is your `NEXT_PUBLIC_SUPABASE_URL`
   - **anon/public key** → This is your `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - **service_role key** → This is your `SUPABASE_SERVICE_ROLE_KEY` (⚠️ Keep this secret!)

### Step 2: Create `.env.local` File

Create a file named `.env.local` in the `ai_job_frontend` directory with the following content:

```env
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# Backend API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# NextAuth Configuration (if using NextAuth)
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your_nextauth_secret_here
```

### Step 3: Replace the Placeholder Values

Replace the placeholder values with your actual Supabase credentials:

- `your-project-id.supabase.co` → Your actual Supabase project URL
- `your_anon_key_here` → Your actual anon/public key
- `your_service_role_key_here` → Your actual service_role key
- `your_nextauth_secret_here` → Generate a random secret (you can use: `openssl rand -base64 32`)

### Step 4: Restart the Frontend Server

After creating/updating `.env.local`, restart your Next.js development server:

```bash
# Stop the current server (Ctrl+C)
# Then restart:
npm run dev
```

## Where These Variables Are Used

- **`NEXT_PUBLIC_SUPABASE_URL`** and **`NEXT_PUBLIC_SUPABASE_ANON_KEY`**:
  - Used in: `src/proxy.ts` (line 58-59)
  - Used in: `src/_lib/supabaseClient.ts` (line 4-5)
  - Used in: `src/_lib/supabaseServer.ts` (line 8-9)

- **`SUPABASE_SERVICE_ROLE_KEY`**:
  - Used in: `src/_lib/supabaseAdmin.ts` (line 12)
  - ⚠️ **Important**: This key bypasses Row Level Security. Never expose it to the client-side!

- **`NEXT_PUBLIC_API_URL`**:
  - Used to connect to your FastAPI backend
  - For local development: `http://localhost:8000`

## Quick Setup Command (PowerShell)

You can create the `.env.local` file using PowerShell:

```powershell
cd ai_job_frontend
@"
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url_here
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your_nextauth_secret_here
"@ | Out-File -FilePath .env.local -Encoding utf8
```

Then edit `.env.local` and replace the placeholder values with your actual credentials.

## Troubleshooting

- **Error: "Your project's URL and Key are required"**
  - Make sure `.env.local` exists in the `ai_job_frontend` directory
  - Verify the variable names are exactly as shown (case-sensitive)
  - Restart the Next.js server after creating/updating `.env.local`

- **Frontend not connecting to backend**
  - Check that `NEXT_PUBLIC_API_URL` is set to `http://localhost:8000`
  - Verify the backend is running on port 8000
