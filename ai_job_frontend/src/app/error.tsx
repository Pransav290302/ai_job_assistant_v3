"use client";

import Link from "next/link";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="min-h-[60vh] flex flex-col items-center justify-center text-primary-100 px-4">
      <h1 className="text-2xl md:text-3xl font-medium text-primary-50 mb-2">
        Something went wrong
      </h1>
      <p className="text-primary-300 mb-8 max-w-md text-center">
        An unexpected error occurred. You can try again or return home.
      </p>
      <div className="flex gap-4">
        <button
          type="button"
          onClick={reset}
          className="bg-primary-600 hover:bg-primary-500 text-primary-100 px-6 py-3 rounded-lg transition-colors"
        >
          Try again
        </button>
        <Link
          href="/"
          className="bg-accent-600 hover:bg-accent-500 text-accent-50 px-6 py-3 rounded-lg transition-colors"
        >
          Go home
        </Link>
      </div>
    </div>
  );
}
