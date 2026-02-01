"use client";

import { useState } from "react";

const BACKEND =
  process.env.NEXT_PUBLIC_BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || "";

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
  const [scrapeResult, setScrapeResult] = useState<Record<string, unknown> | null>(null);
  const [analyzeResult, setAnalyzeResult] = useState<Record<string, unknown> | null>(null);
  const [answerResult, setAnswerResult] = useState<Record<string, unknown> | null>(null);

  const tabs: { id: Tab; label: string }[] = [
    { id: "scrape", label: "Scrape Job" },
    { id: "analyze", label: "Analyze Resume" },
    { id: "answer", label: "Generate Answer" },
  ];

  async function handleScrape() {
    if (!jobUrl.trim()) {
      setError("Please enter a job URL.");
      return;
    }
    setError(null);
    setLoading(true);
    setScrapeResult(null);
    try {
      const res = await fetch(`${BACKEND}/api/job/scrape`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ job_url: jobUrl.trim() }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Scraping failed");
      setScrapeResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Scraping failed");
    } finally {
      setLoading(false);
    }
  }

  async function handleAnalyze() {
    if (!jobUrl.trim() || !resumeText.trim()) {
      setError("Please enter both job URL and resume text.");
      return;
    }
    setError(null);
    setLoading(true);
    setAnalyzeResult(null);
    try {
      const res = await fetch(`${BACKEND}/api/resume/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          job_url: jobUrl.trim(),
          resume_text: resumeText.trim(),
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Analysis failed");
      setAnalyzeResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Analysis failed");
    } finally {
      setLoading(false);
    }
  }

  async function handleGenerateAnswer() {
    if (!jobUrl.trim() || !question.trim()) {
      setError("Please enter job URL and question.");
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
      const res = await fetch(`${BACKEND}/api/generate/answer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          job_url: jobUrl.trim(),
          question: question.trim(),
          user_profile: profile,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Answer generation failed");
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

        {tab === "scrape" && (
          <>
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
            <label className="block">
              <span className="text-primary-200 font-medium">Resume text</span>
              <textarea
                value={resumeText}
                onChange={(e) => setResumeText(e.target.value)}
                placeholder="Paste your resume text here..."
                rows={6}
                className="mt-1 w-full rounded-lg bg-primary-800 border border-primary-600 px-4 py-2 text-primary-100 placeholder-primary-500 focus:border-accent-500 focus:outline-none resize-y"
              />
            </label>
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
            <div className="grid gap-4 sm:grid-cols-2">
              <label className="block">
                <span className="text-primary-200 font-medium">Work history</span>
                <textarea
                  value={userProfile.work_history}
                  onChange={(e) => setUserProfile((p) => ({ ...p, work_history: e.target.value }))}
                  rows={2}
                  className="mt-1 w-full rounded-lg bg-primary-800 border border-primary-600 px-4 py-2 text-primary-100 focus:border-accent-500 focus:outline-none resize-y"
                />
              </label>
              <label className="block">
                <span className="text-primary-200 font-medium">Skills (comma-separated)</span>
                <input
                  type="text"
                  value={userProfile.skills}
                  onChange={(e) => setUserProfile((p) => ({ ...p, skills: e.target.value }))}
                  className="mt-1 w-full rounded-lg bg-primary-800 border border-primary-600 px-4 py-2 text-primary-100 focus:border-accent-500 focus:outline-none"
                />
              </label>
              <label className="block">
                <span className="text-primary-200 font-medium">Education</span>
                <input
                  type="text"
                  value={userProfile.education}
                  onChange={(e) => setUserProfile((p) => ({ ...p, education: e.target.value }))}
                  className="mt-1 w-full rounded-lg bg-primary-800 border border-primary-600 px-4 py-2 text-primary-100 focus:border-accent-500 focus:outline-none"
                />
              </label>
              <label className="block">
                <span className="text-primary-200 font-medium">Additional info</span>
                <textarea
                  value={userProfile.additional_info}
                  onChange={(e) => setUserProfile((p) => ({ ...p, additional_info: e.target.value }))}
                  rows={2}
                  className="mt-1 w-full rounded-lg bg-primary-800 border border-primary-600 px-4 py-2 text-primary-100 focus:border-accent-500 focus:outline-none resize-y"
                />
              </label>
            </div>
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
        <div className="rounded-lg bg-red-900/30 border border-red-700 text-red-200 px-4 py-2">
          {error}
        </div>
      )}
    </div>
  );
}
