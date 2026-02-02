/**
 * Handles POST to /auth/login (e.g. from password managers, extensions).
 * Login is client-side via Supabase - redirect back to form to prevent 405.
 */
import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  const url = new URL(request.url);
  const base = url.origin;
  return NextResponse.redirect(new URL("/auth/login", base), 303);
}
