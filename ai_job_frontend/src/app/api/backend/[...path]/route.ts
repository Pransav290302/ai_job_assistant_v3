/**
 * Proxy to backend - avoids CORS by routing through Next.js (same-origin).
 * For local: set NEXT_PUBLIC_BACKEND_URL=http://localhost:8000 in .env.local
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
      { detail: "Backend URL not configured. Set NEXT_PUBLIC_BACKEND_URL in .env.local (e.g. http://localhost:8000)." },
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
    const contentType = res.headers.get("Content-Type") || "";
    // Backend may return HTML error page (502/503) - return JSON so frontend can parse
    if (
      !res.ok &&
      (!contentType.includes("json") || !data.trim() || !data.startsWith("{"))
    ) {
      return NextResponse.json(
        {
          detail:
            res.status === 502
              ? "Backend unreachable"
              : res.status === 504
                ? "Backend timed out (cold start?)"
                : `Backend error: ${res.status}`,
        },
        { status: res.status }
      );
    }
    return new NextResponse(data, {
      status: res.status,
      headers: { "Content-Type": contentType || "application/json" },
    });
  } catch (e) {
    console.error("Backend proxy error:", e);
    return NextResponse.json(
      { error: "Backend unreachable", detail: String(e) },
      { status: 502 }
    );
  }
}
