import { createServerClient } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";

export default async function middleware(req: NextRequest) {
  const nextUrl = req.nextUrl;
  const pathname = nextUrl.pathname;

  /**
   * Normalize pathname: strip trailing slashes so "/about" and "/about/" match the same.
   * This must run first so public path detection is reliable.
   */
  const normalizedPath = pathname.replace(/\/+$/, "") || "/";

  /**
   * Path Logic Definitions (checked BEFORE any auth call).
   * Public paths: Accessible without login (Landing, About, Login, Signup).
   * Onboarding paths: Specific setup pages for new users.
   */
  const isPublicPath =
    normalizedPath === "/" ||
    normalizedPath === "/about" ||
    normalizedPath.startsWith("/about/") ||
    normalizedPath === "/assistant" ||
    normalizedPath.startsWith("/assistant/") ||
    normalizedPath.startsWith("/auth");
  const isOnboardingPath =
    normalizedPath.startsWith("/preferences") || normalizedPath.startsWith("/setup");
  const isApiPath = normalizedPath.startsWith("/api");

  /**
   * RULE 0: Always-public paths — allow immediately without touching Supabase.
   * /about and /auth/* are 100% accessible when not logged in (no trailing-slash or auth issues).
   * "/" is not included here so we can still redirect logged-in users from landing to dashboard.
   */
  const isAlwaysPublicPath =
    normalizedPath === "/about" ||
    normalizedPath.startsWith("/about/") ||
    normalizedPath === "/assistant" ||
    normalizedPath.startsWith("/assistant/") ||
    normalizedPath.startsWith("/auth");
  if (isAlwaysPublicPath) {
    return NextResponse.next({
      request: { headers: req.headers },
    });
  }

  /**
   * Initialize the response object for non-public routes.
   */
  let res = NextResponse.next({
    request: {
      headers: req.headers,
    },
  });

  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

  if (!supabaseUrl || !supabaseAnonKey) {
    console.error(
      "[Middleware] Supabase not configured. Set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY in Vercel → Project Settings → Environment Variables."
    );
    // Treat as not logged in: protect non-public routes by redirecting to login
    if (!isPublicPath) {
      return NextResponse.redirect(new URL("/auth/login", nextUrl));
    }
    return res;
  }

  /**
   * Create a Supabase client configured for Server-Side Rendering (SSR).
   * The 'cookies' object manages the syncing of authentication tokens 
   * between the incoming request and the outgoing response.
   */
  const supabase = createServerClient(
    supabaseUrl,
    supabaseAnonKey,
    {
      cookies: {
        getAll() { return req.cookies.getAll(); },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value, options }) => {
            req.cookies.set(name, value);
            res = NextResponse.next({
              request: { headers: req.headers },
            });
            res.cookies.set(name, value, options);
          });
        },
      },
    }
  );

  /**
   * Re-validate the user's session.
   * Using 'getUser()' instead of 'getSession()' is a security best practice 
   * as it verifies the user's ID with the Supabase Auth server.
   */
  const { data: { user } } = await supabase.auth.getUser();
  const isLoggedIn = !!user;

  /**
   * Onboarding: ask preferences only once (new signups). Use profiles.onboarded as source of truth
   * so returning users go straight to dashboard; user_metadata is fallback for backwards compatibility.
   */
  let hasCompletedOnboarding = user?.user_metadata?.onboarded === true;
  if (isLoggedIn && user?.id && !hasCompletedOnboarding) {
    const { data: profile } = await supabase.from("profiles").select("onboarded").eq("id", user.id).single();
    hasCompletedOnboarding = profile?.onboarded === true;
  }

  // --- ACCESS CONTROL & REDIRECT LOGIC (non-public only) ---

  /**
   * RULE 1: Authentication Guard.
   * If the user is NOT logged in and attempts to access any non-public page,
   * redirect them to login. Public paths (e.g. "/" home) are allowed without login.
   */
  if (!isLoggedIn && !isPublicPath) {
    return NextResponse.redirect(new URL("/auth/login", nextUrl));
  }

  /**
   * RULE 2: Onboarding Gate.
   * Logged-in users who haven't completed onboarding are forced to finish it
   * before accessing any authenticated pages (excluding APIs).
   */
  if (isLoggedIn && !hasCompletedOnboarding && !isPublicPath && !isOnboardingPath && !isApiPath) {
    return NextResponse.redirect(new URL("/preferences", nextUrl));
  }

  /**
   * RULE 2b: Already onboarded — send straight to dashboard (preferences only once).
   * If a returning user hits /preferences, redirect to dashboard.
   */
  if (isLoggedIn && hasCompletedOnboarding && isOnboardingPath) {
    return NextResponse.redirect(new URL("/dashboard", nextUrl));
  }

  /**
   * RULE 3: Intelligent Landing Page Redirect.
   * If a logged-in user hits the home page, send them to their dashboard 
   * or the setup page based on their onboarding status.
   */
  if (isLoggedIn && normalizedPath === "/") {
    const target = hasCompletedOnboarding ? "/dashboard" : "/preferences";
    return NextResponse.redirect(new URL(target, nextUrl));
  }

  return res;
}

/**
 * Middleware Matcher Configuration.
 * This "Negative Matcher" runs the middleware on all routes EXCEPT:
 * 1. Internal Next.js static files and images.
 * 2. Static assets in the public folder (favicons, svgs, common image formats).
 */
export const config = {
  matcher: [
    // Skip static assets AND the auth callback path so Supabase can finish OAuth without middleware interference
    '/((?!_next/static|_next/image|favicon.ico|auth/callback|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
};