/**
 * Proxy to backend - avoids CORS by routing through Vercel (same-origin).
 * Frontend calls /api/backend/api/job/scrape instead of BACKEND/api/job/scrape
 */
import { NextRequest, NextResponse } from "next/server";

const BACKEND =
  process.env.NEXT_PUBLIC_BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || "";

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  return proxy(request, params, "POST");
}

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  return proxy(request, params, "GET");
}

async function proxy(
  request: NextRequest,
  params: Promise<{ path: string[] }>,
  method: string
) {
  if (!BACKEND) {
    return NextResponse.json(
      { detail: "Backend URL not configured. Set NEXT_PUBLIC_BACKEND_URL in Vercel." },
      { status: 500 }
    );
  }
  const { path } = await params;
  const pathStr = path.join("/");
  const url = `${BACKEND.replace(/\/$/, "")}/${pathStr}`;
  const body = method === "POST" ? await request.text() : undefined;
  const headers = new Headers(request.headers);
  headers.delete("host");
  headers.delete("connection");
  try {
    const res = await fetch(url, {
      method,
      headers,
      body: body || undefined,
      signal: AbortSignal.timeout(90000),
    });
    const data = await res.text();
    return new NextResponse(data, {
      status: res.status,
      headers: {
        "Content-Type": res.headers.get("Content-Type") || "application/json",
      },
    });
  } catch (e) {
    console.error("Backend proxy error:", e);
    return NextResponse.json(
      { error: "Backend unreachable", detail: String(e) },
      { status: 502 }
    );
  }
}
