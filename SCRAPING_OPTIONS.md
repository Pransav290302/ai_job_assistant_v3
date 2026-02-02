# LinkedIn & Glassdoor Scraping

Scraping uses **BROWSERLESS_URL** only (remote Chrome via [browserless.io](https://www.browserless.io)).

## Setup

**Free:** 6 hours/month at [browserless.io](https://www.browserless.io)

| Where   | Variable         | Value                                           |
|---------|------------------|--------------------------------------------------|
| Render  | `BROWSERLESS_URL` | `wss://chrome.browserless.io?token=YOUR_TOKEN` |
| Local   | `BROWSERLESS_URL` | Same, in `ai_job_backend/.env`                |

1. Create account at browserless.io
2. Get your token from the dashboard
3. Set `BROWSERLESS_URL=wss://chrome.browserless.io?token=YOUR_TOKEN`

## Alternative: Paste Job Description

Paste the job text (80+ chars) in the text area—no scraping needed, always works.
