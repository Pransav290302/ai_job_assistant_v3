# Connect Render Backend to Supabase PostgreSQL

The backend runs on **Render** and needs a database. You can use your **Supabase** Postgres (same project as auth). Configure in **Render Dashboard → Your Backend Service → Environment**.

> **Important:** Set these on **Render**, not Vercel. The backend runs on Render.

---

## Option A: PG_* Variables (Recommended – No Password Encoding)

Use separate variables so passwords with `@`, `:`, etc. work without encoding.

**Supabase Dashboard** → **Project Settings** → **Database** → copy values.

### Direct Connection (port 5432)

| Variable      | Value                                      |
|---------------|--------------------------------------------|
| `PG_HOST`     | `db.toyjqdqblstypruacwtm.supabase.co`      |
| `PG_PORT`     | `5432`                                     |
| `PG_USER`     | `postgres`                                 |
| `PG_PASSWORD` | Your database password (e.g. `Pransav@2903`) |
| `PG_DATABASE` | `postgres`                                 |

Leave `DATABASE_URL` empty. Do **not** set `DATABASE_URL` when using PG_*.

### Session Pooler (port 6543)

If Supabase recommends the pooler:

| Variable      | Value                                       |
|---------------|---------------------------------------------|
| `PG_HOST`     | `aws-1-us-east-1.pooler.supabase.com`       |
| `PG_PORT`     | `6543`                                      |
| `PG_USER`     | `postgres.toyjqdqblstypruacwtm`             |
| `PG_PASSWORD` | Your database password                      |
| `PG_DATABASE` | `postgres`                                  |

Replace `toyjqdqblstypruacwtm` with your Supabase project reference.

---

## Option B: DATABASE_URL (Single String)

**Supabase Dashboard** → **Project Settings** → **Database** → **Connection string** → **URI**.

1. Copy the string.
2. Replace `[YOUR-PASSWORD]` with your password.
3. If the password contains `@`, encode it as `%40` (e.g. `Pransav@2903` → `Pransav%402903`).

**Direct connection:**
```
postgresql://postgres:Pransav%402903@db.toyjqdqblstypruacwtm.supabase.co:5432/postgres
```

**Session pooler:**
```
postgresql://postgres.toyjqdqblstypruacwtm:Pransav%402903@aws-1-us-east-1.pooler.supabase.com:6543/postgres
```

Set `DATABASE_URL` in Render and leave PG_* empty.

---

## Checklist

- [ ] Render Dashboard → Your backend service → **Environment**
- [ ] Add either **Option A** (PG_*) or **Option B** (DATABASE_URL)
- [ ] Do **not** set both DATABASE_URL and PG_* (Option A takes precedence when DATABASE_URL is empty)
- [ ] Save → Render redeploys automatically
- [ ] If you forgot your DB password: Supabase → Settings → Database → **Reset database password**
