"use client";

import { useRef, useState } from "react";
import { extractTextFromPdf } from "./extractPdf";

// Use proxy to avoid CORS - same-origin /api/backend/* forwards to Render
const BACKEND =
  typeof window !== "undefined"
    ? "/api/backend"
    : process.env.NEXT_PUBLIC_BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || "";

// Render free tier cold-starts in ~50–90s; use long timeout
const FETCH_TIMEOUT_MS = 90000;

async function fetchWithTimeout(
  url: string,
  options: RequestInit & { timeout?: number } = {}
): Promise<Response> {
  const { timeout = FETCH_TIMEOUT_MS, ...fetchOptions } = options;
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);
  try {
    const res = await fetch(url, { ...fetchOptions, signal: controller.signal });
    clearTimeout(id);
    return res;
  } catch (e) {
    clearTimeout(id);
    if (e instanceof Error) {
      if (e.name === "AbortError")
        throw new Error("Request timed out. The backend may be waking up (Render cold start takes ~1 min). Try again.");
      if (e.message === "Failed to fetch")
        throw new Error(
          "Cannot reach backend. Check CORS (FRONTEND_URL/ALLOWED_ORIGINS on Render) and NEXT_PUBLIC_BACKEND_URL on Vercel."
        );
    }
    throw e;
  }
}

async function parseJsonOrThrow(
  res: Response,
  fallbackMsg: string
): Promise<Record<string, unknown>> {
  const text = await res.text();
  if (!text.trim()) {
    if (!res.ok)
      throw new Error(
        res.status === 502
          ? "Backend unreachable. Check NEXT_PUBLIC_BACKEND_URL and that Render is running."
          : res.status === 504
            ? "Backend timed out. Render may be cold-starting (try again in 1 min)."
            : fallbackMsg
      );
    return {};
  }
  try {
    return JSON.parse(text) as Record<string, unknown>;
  } catch {
    throw new Error(
      res.ok ? fallbackMsg : `Backend error (${res.status}). Try again or check Render logs.`
    );
  }
}

type Tab = "scrape" | "analyze" | "answer";

export default function AssistantPage() {
  const [tab, setTab] = useState<Tab>("scrape");
  const [jobUrl, setJobUrl] = useState("");
  const [resumeText, setResumeText] = useState("");
  const [question, setQuestion] = useState("");
  const [userProfile, setUserProfile] = useState({
    work_history: "",
    skills: "",
    education: "",
    additional_info: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [jobDescription, setJobDescription] = useState("");
  const [scrapeResult, setScrapeResult] = useState<Record<string, unknown> | null>(null);
  const [analyzeResult, setAnalyzeResult] = useState<Record<string, unknown> | null>(null);
  const [answerResult, setAnswerResult] = useState<Record<string, unknown> | null>(null);
  const [uploadingResume, setUploadingResume] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const tabs: { id: Tab; label: string }[] = [
    { id: "scrape", label: "Scrape Job" },
    { id: "analyze", label: "Analyze Resume" },
    { id: "answer", label: "Generate Answer" },
  ];

  async function handlePdfUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file || file.type !== "application/pdf") {
      setError("Please select a PDF file.");
      return;
    }
    setError(null);
    setUploadingResume(true);
    try {
      const text = await extractTextFromPdf(file);
      if (!text.trim()) {
        setError("Could not extract text from PDF. The file may be scanned or protected.");
        return;
      }
      setResumeText(text);

      // Extract structured profile for Generate Answer tab
      const res = await fetchWithTimeout(`${BACKEND}/api/resume/extract`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ resume_text: text }),
      });
      const data = await parseJsonOrThrow(res, "Resume extraction failed");
      if (res.ok && data.success) {
        setUserProfile({
          work_history: String(data.work_history ?? ""),
          skills: String(data.skills ?? ""),
          education: String(data.education ?? ""),
          additional_info: String(data.additional_info ?? ""),
        });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to process PDF");
    } finally {
      setUploadingResume(false);
      e.target.value = "";
    }
  }

  async function handleScrape() {
    const hasPaste = jobDescription.trim().length > 200;
    if (!jobUrl.trim() && !hasPaste) {
      setError("Enter a job URL or paste the job description below.");
      return;
    }
    setError(null);
    setLoading(true);
    setScrapeResult(null);
    try {
      const res = await fetchWithTimeout(`${BACKEND}/api/job/scrape`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          job_url: jobUrl.trim() || "https://pasted-job-description",
          job_description: hasPaste ? jobDescription.trim() : undefined,
        }),
      });
      const data = await parseJsonOrThrow(res, "Scraping failed");
      if (!res.ok) throw new Error(String(data.detail ?? data.error ?? "Scraping failed"));
      setScrapeResult(data);
      if (data.text && typeof data.text === "string") setJobDescription(data.text);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Scraping failed");
    } finally {
      setLoading(false);
    }
  }

  async function handleAnalyze() {
    const hasJob = jobUrl.trim() || jobDescription.trim().length > 200;
    if (!hasJob || !resumeText.trim()) {
      setError("Provide a job (URL or paste) and your resume.");
      return;
    }
    setError(null);
    setLoading(true);
    setAnalyzeResult(null);
    try {
      const res = await fetchWithTimeout(`${BACKEND}/api/resume/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          job_url: jobUrl.trim() || undefined,
          job_description: jobDescription.trim().length > 200 ? jobDescription.trim() : undefined,
          resume_text: resumeText.trim(),
        }),
      });
      const data = await parseJsonOrThrow(res, "Analysis failed");
      if (!res.ok) throw new Error(String(data.detail ?? data.error ?? "Analysis failed"));
      setAnalyzeResult(data);
      // Auto-extract profile for Generate Answer tab (works for pasted text too, not just PDF)
      try {
        const extractRes = await fetchWithTimeout(`${BACKEND}/api/resume/extract`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ resume_text: resumeText.trim() }),
        });
        const extractData = await parseJsonOrThrow(extractRes, "Extract failed");
        if (extractRes.ok && extractData.success) {
          setUserProfile({
            work_history: String(extractData.work_history ?? ""),
            skills: String(extractData.skills ?? ""),
            education: String(extractData.education ?? ""),
            additional_info: String(extractData.additional_info ?? ""),
          });
        }
      } catch {
        // Ignore extract errors; user can still use Generate Answer with existing profile
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Analysis failed");
    } finally {
      setLoading(false);
    }
  }

  async function handleGenerateAnswer() {
    const hasJob = jobUrl.trim() || jobDescription.trim().length > 200;
    if (!hasJob || !question.trim()) {
      setError("Provide a job (URL or paste) and the application question.");
      return;
    }
    setError(null);
    setLoading(true);
    setAnswerResult(null);
    const profile = {
      work_history: userProfile.work_history || "",
      skills: userProfile.skills.split(",").map((s) => s.trim()).filter(Boolean),
      education: userProfile.education || "",
      additional_info: userProfile.additional_info || "",
    };
    try {
      const res = await fetchWithTimeout(`${BACKEND}/api/generate/answer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          job_url: jobUrl.trim() || undefined,
          job_description: jobDescription.trim().length > 200 ? jobDescription.trim() : undefined,
          question: question.trim(),
          user_profile: profile,
        }),
      });
      const data = await parseJsonOrThrow(res, "Answer generation failed");
      if (!res.ok) throw new Error(String(data.detail ?? data.error ?? "Answer generation failed"));
      setAnswerResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Answer generation failed");
    } finally {
      setLoading(false);
    }
  }

  if (!BACKEND) {
    return (
      <div className="rounded-xl border border-primary-700 bg-primary-900/50 p-8 text-center">
        <p className="text-accent-300">
          Backend URL not configured. Set <code className="bg-primary-800 px-1 rounded">NEXT_PUBLIC_BACKEND_URL</code> or <code className="bg-primary-800 px-1 rounded">NEXT_PUBLIC_API_URL</code> in Vercel → Project Settings → Environment Variables (e.g. your Render backend URL like <code className="bg-primary-800 px-1 rounded">https://ai-job-backend.onrender.com</code>). Redeploy after adding.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <h1 className="text-4xl text-accent-400 font-medium">
        AI Job Assistant
      </h1>
      <p className="text-primary-200 text-lg">
        Scrape job descriptions, analyze your resume against a job, and generate tailored answers using AI.
      </p>

      <div className="flex gap-2 border-b border-primary-700 pb-2">
        {tabs.map(({ id, label }) => (
          <button
            key={id}
            onClick={() => setTab(id)}
            className={`px-4 py-2 rounded-t font-medium transition-colors ${
              tab === id
                ? "bg-accent-600 text-primary-900"
                : "bg-primary-800 text-primary-200 hover:bg-primary-700"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      <div className="rounded-xl border border-primary-700 bg-primary-900/50 p-6 space-y-4">
        <div>
          <label className="block">
            <span className="text-primary-200 font-medium">Job URL</span>
            <input
              type="url"
              value={jobUrl}
              onChange={(e) => setJobUrl(e.target.value)}
              placeholder="https://linkedin.com/jobs/..."
              className="mt-1 w-full rounded-lg bg-primary-800 border border-primary-600 px-4 py-2 text-primary-100 placeholder-primary-500 focus:border-accent-500 focus:outline-none"
            />
          </label>
        </div>

        {tab === "scrape" && (
          <>
            <div>
              <span className="text-primary-200 font-medium">Or paste job description</span>
              <p className="text-sm text-primary-400 mb-1">Use when scraping fails (e.g. LinkedIn blocks). Paste the full job posting text.</p>
              <textarea
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="Paste job description here (200+ chars)..."
                rows={5}
                className="mt-1 w-full rounded-lg bg-primary-800 border border-primary-600 px-4 py-2 text-primary-100 placeholder-primary-500 focus:border-accent-500 focus:outline-none resize-y"
              />
            </div>
            <button
              onClick={handleScrape}
              disabled={loading}
              className="bg-accent-500 hover:bg-accent-600 text-primary-900 font-semibold px-6 py-2 rounded-lg disabled:opacity-50"
            >
              {loading ? "Scraping…" : "Scrape job description"}
            </button>
            {scrapeResult && (
              <pre className="mt-4 p-4 rounded-lg bg-primary-800 text-sm text-primary-200 overflow-auto max-h-96">
                {JSON.stringify(scrapeResult, null, 2)}
              </pre>
            )}
          </>
        )}

        {tab === "analyze" && (
          <>
            <div className="block">
              <div className="flex flex-wrap items-center justify-between gap-3 mb-1">
                <span className="text-primary-200 font-medium">Resume text</span>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,application/pdf"
                  onChange={handlePdfUpload}
                  className="hidden"
                />
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={uploadingResume}
                  className="px-4 py-2 rounded-lg border border-accent-500 text-accent-400 hover:bg-accent-500/10 disabled:opacity-50 text-sm font-medium"
                >
                  {uploadingResume ? "Processing…" : "Upload Resume (PDF)"}
                </button>
              </div>
              <textarea
                value={resumeText}
                onChange={(e) => setResumeText(e.target.value)}
                placeholder="Paste your resume text here or upload a PDF..."
                rows={6}
                className="w-full rounded-lg bg-primary-800 border border-primary-600 px-4 py-2 text-primary-100 placeholder-primary-500 focus:border-accent-500 focus:outline-none resize-y"
              />
            </div>
            <button
              onClick={handleAnalyze}
              disabled={loading}
              className="bg-accent-500 hover:bg-accent-600 text-primary-900 font-semibold px-6 py-2 rounded-lg disabled:opacity-50"
            >
              {loading ? "Analyzing…" : "Analyze resume vs job"}
            </button>
            {analyzeResult && (
              <pre className="mt-4 p-4 rounded-lg bg-primary-800 text-sm text-primary-200 overflow-auto max-h-96">
                {JSON.stringify(analyzeResult, null, 2)}
              </pre>
            )}
          </>
        )}

        {tab === "answer" && (
          <>
            <p className="text-sm text-primary-300">
              {userProfile.work_history || userProfile.skills || userProfile.education
                ? "Using profile from your resume (Analyze Resume tab)."
                : "Upload or paste your resume on the Analyze Resume tab first—your profile will be auto-filled for tailored answers."}
            </p>
            <label className="block">
              <span className="text-primary-200 font-medium">Application question</span>
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="e.g. Why are you a good fit for this role?"
                className="mt-1 w-full rounded-lg bg-primary-800 border border-primary-600 px-4 py-2 text-primary-100 placeholder-primary-500 focus:border-accent-500 focus:outline-none"
              />
            </label>
            <button
              onClick={handleGenerateAnswer}
              disabled={loading}
              className="bg-accent-500 hover:bg-accent-600 text-primary-900 font-semibold px-6 py-2 rounded-lg disabled:opacity-50"
            >
              {loading ? "Generating…" : "Generate tailored answer"}
            </button>
            {answerResult && (
              <pre className="mt-4 p-4 rounded-lg bg-primary-800 text-sm text-primary-200 overflow-auto max-h-96">
                {JSON.stringify(answerResult, null, 2)}
              </pre>
            )}
          </>
        )}
      </div>

      {error && (
        <div className="rounded-lg bg-red-900/30 border border-red-700 text-red-200 px-4 py-2 space-y-1">
          <p>{error}</p>
          {(error.includes("Scraping failed") || error.includes("Analysis failed") || error.includes("unreachable") || error.includes("timed out")) && (
            <p className="text-sm text-red-300/90">
              Tip: If scraping fails (e.g. LinkedIn blocks), paste the job description manually in the Scrape tab. Add <code className="bg-red-900/50 px-1 rounded">SCRAPER_API_KEY</code> on Render for reliable scraping (1000 free req/mo at scraperapi.com).
            </p>
          )}
        </div>
      )}
    </div>
  );
}
