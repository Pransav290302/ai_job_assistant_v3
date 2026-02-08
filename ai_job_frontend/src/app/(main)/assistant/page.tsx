"use client";

import { useEffect, useRef, useState } from "react";
import { extractTextFromPdf } from "./extractPdf";
import { supabaseClient } from "@/_lib/supabaseClient";

// Use proxy to avoid CORS - same-origin /api/backend/* forwards to your backend (local or hosted)
const BACKEND =
  typeof window !== "undefined"
    ? "/api/backend"
    : process.env.NEXT_PUBLIC_BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || "";

// Long timeout for backend (local or cold-start)
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
        throw new Error("Request timed out. Ensure the backend is running (e.g. python main.py in ai_job_backend). Try again.");
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

type Tab = "analyze" | "answer";

function ResumeAnalysisResult({ data }: { data: Record<string, unknown> }) {
  const analysis = (data.analysis as Record<string, unknown>) || data;
  const score = Number(analysis.score ?? analysis.match_percentage ?? 0);
  const strengths = (analysis.strengths as string[]) ?? [];
  const suggestions = (analysis.suggestions as string[]) ?? [];
  const missing = (analysis.missing_skills as string[]) ?? [];
  return (
    <div className="mt-4 space-y-4">
      <div className="rounded-lg bg-primary-800 p-4 flex flex-wrap items-center gap-4">
        <div className="flex items-center gap-2">
          <span className="text-primary-400 text-sm font-medium">Match score</span>
          <span className={`text-2xl font-bold ${score >= 70 ? "text-emerald-400" : score >= 50 ? "text-amber-400" : "text-rose-400"}`}>
            {score}%
          </span>
        </div>
      </div>
      {strengths.length > 0 && (
        <div className="rounded-lg bg-emerald-900/20 border border-emerald-700/50 p-4">
          <p className="text-xs text-emerald-400/90 font-medium mb-2">Strengths</p>
          <ul className="list-disc list-inside text-sm text-primary-200 space-y-1">
            {strengths.map((s, i) => (
              <li key={i}>{String(s)}</li>
            ))}
          </ul>
        </div>
      )}
      {suggestions.length > 0 && (
        <div className="rounded-lg bg-sky-900/20 border border-sky-700/50 p-4">
          <p className="text-xs text-sky-400/90 font-medium mb-2">Suggestions</p>
          <ul className="list-disc list-inside text-sm text-primary-200 space-y-1">
            {suggestions.map((s, i) => (
              <li key={i}>{String(s)}</li>
            ))}
          </ul>
        </div>
      )}
      {missing.length > 0 && (
        <div className="rounded-lg bg-amber-900/20 border border-amber-700/50 p-4">
          <p className="text-xs text-amber-400/90 font-medium mb-2">Missing skills / areas</p>
          <ul className="list-disc list-inside text-sm text-primary-200 space-y-1">
            {missing.map((s, i) => (
              <li key={i}>{String(s)}</li>
            ))}
          </ul>
        </div>
      )}
      <details className="rounded-lg bg-primary-800/60 p-2">
        <summary className="text-xs text-primary-400 cursor-pointer">Raw JSON</summary>
        <pre className="mt-2 p-2 text-xs text-primary-300 overflow-auto max-h-48">
          {JSON.stringify(data, null, 2)}
        </pre>
      </details>
    </div>
  );
}

function TailoredAnswerResult({ data }: { data: Record<string, unknown> }) {
  const answer = typeof data.answer === "string" ? data.answer : "";
  return (
    <div className="mt-4 space-y-4">
      <div className="rounded-lg bg-primary-800 p-4">
        <p className="text-xs text-primary-400 mb-2 font-medium">Tailored answer</p>
        <div className="text-sm text-primary-200 whitespace-pre-wrap leading-relaxed">
          {answer || "No answer returned."}
        </div>
      </div>
      <details className="rounded-lg bg-primary-800/60 p-2">
        <summary className="text-xs text-primary-400 cursor-pointer">Raw response</summary>
        <pre className="mt-2 p-2 text-xs text-primary-300 overflow-auto max-h-48">
          {JSON.stringify(data, null, 2)}
        </pre>
      </details>
    </div>
  );
}

export default function AssistantPage() {
  const [tab, setTab] = useState<Tab>("analyze");
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
  const [analyzeResult, setAnalyzeResult] = useState<Record<string, unknown> | null>(null);
  const [answerResult, setAnswerResult] = useState<Record<string, unknown> | null>(null);
  const [userId, setUserId] = useState<string | null>(null);
  const [uploadingResume, setUploadingResume] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    supabaseClient.auth.getUser().then(({ data }) => {
      setUserId(data.user?.id ?? null);
    });
  }, []);

  const tabs: { id: Tab; label: string }[] = [
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

  async function handleAnalyze() {
    const hasJob = jobUrl.trim() || jobDescription.trim().length >= 80;
    if (!hasJob || !resumeText.trim()) {
      setError("Paste a job description (or job URL) above and provide your resume.");
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
          job_description: jobDescription.trim() || undefined,
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
    const hasJd = jobDescription.trim().length >= 80;
    const hasUrl = jobUrl.trim().length > 0;
    if ((!hasUrl && !hasJd) || !question.trim()) {
      setError("Enter a job URL (set SCRAPER_API_KEY or BROWSERLESS_URL in backend .env for LinkedIn/Glassdoor) or paste the job description above, then enter the question.");
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
          job_url: hasUrl ? jobUrl.trim() : undefined,
          job_description: hasJd ? jobDescription.trim() : undefined,
          question: question.trim(),
          user_profile: profile,
        }),
      });
      const data = await parseJsonOrThrow(res, "Answer generation failed");
      if (!res.ok) throw new Error(String(data.detail ?? data.error ?? "Answer generation failed"));
      setAnswerResult(data);
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Answer generation failed";
      setError(msg);
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
        Analyze your resume against a job description, or generate tailored answers for application questions.
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
              placeholder="https://indeed.com/viewjob?jk=... or https://glassdoor.com/..."
              className="mt-1 w-full rounded-lg bg-primary-800 border border-primary-600 px-4 py-2 text-primary-100 placeholder-primary-500 focus:border-accent-500 focus:outline-none"
            />
          </label>
          <p className="mt-1.5 text-xs text-primary-400">
            Indeed (easy) and Glassdoor (needs SCRAPER_API_KEY or BROWSERLESS_URL). Paste job description below if needed.
          </p>
        </div>
        <div>
          <label className="block">
            <span className="text-primary-200 font-medium">Or paste job description</span>
            <textarea
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste the full job description here (e.g. copy from Indeed or Glassdoor job page)"
              rows={5}
              className="mt-1 w-full rounded-lg bg-primary-800 border border-primary-600 px-4 py-2 text-primary-100 placeholder-primary-500 focus:border-accent-500 focus:outline-none resize-y"
            />
          </label>
        </div>

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
              <ResumeAnalysisResult data={analyzeResult} />
            )}
          </>
        )}

        {tab === "answer" && (
          <>
            <p className="text-sm text-primary-300">
              {userProfile.work_history || userProfile.skills || userProfile.education
                ? "Using profile from your resume (Analyze Resume tab) or from your account."
                : "Upload/paste your resume on the Analyze Resume tab, or load your saved profile below."}
            </p>
            {userId && (
              <button
                type="button"
                onClick={async () => {
                  try {
                    const res = await fetch("/api/profile/autofill", { credentials: "include" });
                    if (!res.ok) return;
                    const autofill = await res.json();
                    setUserProfile({
                      work_history: autofill.work_history_summary || autofill.current_title || "",
                      skills: autofill.skills || "",
                      education: autofill.education_summary || "",
                      additional_info: [autofill.location, autofill.expected_salary].filter(Boolean).join(" · ") || "",
                    });
                  } catch {
                    // ignore
                  }
                }}
                className="px-4 py-2 rounded-lg border border-accent-500 text-accent-400 hover:bg-accent-500/10 text-sm font-medium"
              >
                Load my profile from account
              </button>
            )}
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
              <TailoredAnswerResult data={answerResult} />
            )}
          </>
        )}
      </div>

      {error && (
        <div className="rounded-lg bg-red-900/30 border border-red-700 text-red-200 px-4 py-2">
          <p>{error}</p>
        </div>
      )}
    </div>
  );
}
