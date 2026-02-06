# Job Discovery: ScraperAPI 500 and Zero Results

## ScraperAPI 500 (ZipRecruiter / long URLs)

### Why it happens
- The **request URL** we send to ScraperAPI is:  
  `http://api.scraperapi.com/?api_key=...&url=<ENCODED_TARGET_URL>&render=true`.  
  The **target URL** is the ZipRecruiter search page with `search=<query>&location=<location>`.
- When the profile (or API) sends a **very long** query (e.g. "AI & Machine Learning, Software Engineering, Lab & Research, Data & Analytics, PyTorch, AWS, NumPy, Pandas") and a **very long** location (e.g. "Atlanta, Austin, Chicago, Denver, Los Angeles, Miami, New York City, Remote in USA, ..."), the ZipRecruiter URL becomes huge. After encoding, the **full request URI** can exceed the server’s limit (often 2KB–8KB). The server then returns **500 Internal Server Error** (or 414 URI Too Long).
- Job boards are designed for **short** search phrases (e.g. "software engineer", "data scientist Python"), not 200-character comma-separated lists.

### Fix (no patchwork)
1. **Discovery-friendly query/location** (`job_matches.py`): Before calling discovery, we build a **short** search string and **short** location from the profile (e.g. first role + first 1–2 skills, max 80 chars; one city or "Remote", max 60 chars). Discovery uses these; the full profile is still used for **ranking**.
2. **Defensive caps** (`job_discovery.py`): ZipRecruiter discovery **always** truncates query and location to 80 and 60 characters so the built URL never exceeds a safe length, even if another caller passes long strings.

---

## Why DailyAIJobs and AIWorkPortal Sometimes Return 0 Jobs

## Root causes (from diagnostics)

### 1. DailyAIJobs.com
- **Cause:** The page is a **client-side app**. ScraperAPI returns HTML (80k chars) but the **job list is loaded by JavaScript after load**. The HTML we get has only **3 `<a href>` links** in the whole document — no job links.
- So with `render=true` alone, the browser often returns the page **before** the JS has finished loading the job listings.
- **Fix:** Wait for content to appear. Use ScraperAPI’s **instruction set** to add a `wait` (e.g. 10s) or `wait_for_selector` so the job list is present before we capture HTML. The code now adds a 10-second wait for DailyAIJobs when `SCRAPER_API_KEY` is set.

### 2. AIWorkPortal.com
- **Cause (when it works):** With the same ScraperAPI + `render=true`, the diagnostic run found **11** job links on the homepage and **40** on `/jobs`. So the site **does** return job links when the full page is rendered.
- **Causes (when you get 0):**
  - **Timeout:** The `/jobs` page can be **~6.8 MB** and slow. A 60s timeout may not be enough under load.
  - **No key / key not loaded:** If `SCRAPER_API_KEY` is missing in the environment where the app runs, we fall back to a direct request and get a “Loading…” page with no job links.
- **Fix:** Use a **longer timeout** (e.g. 90s) for AIWorkPortal (and DailyAIJobs), and ensure `SCRAPER_API_KEY` is set in the environment that runs discovery.

## Summary
| Site           | Root cause                          | Fix in code                          |
|----------------|-------------------------------------|-------------------------------------|
| DailyAIJobs    | Job list loaded by JS after load   | ScraperAPI instruction: wait 10s    |
| AIWorkPortal   | Timeout or no JS render (no key)    | Timeout 90s; ensure SCRAPER_API_KEY |

## How to re-run diagnostics
```bash
cd ai_job_backend
python scripts/diagnose_dailyai_aiworkportal.py
```
