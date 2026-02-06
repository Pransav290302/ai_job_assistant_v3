import Link from "next/link";

export default function NotFound() {
  return (
    <div className="min-h-[60vh] flex flex-col items-center justify-center text-primary-100 px-4">
      <h1 className="text-4xl md:text-5xl font-medium text-primary-50 mb-2">
        404
      </h1>
      <p className="text-primary-300 mb-8 text-center">
        The page you&apos;re looking for doesn&apos;t exist or has been moved.
      </p>
      <Link
        href="/"
        className="bg-accent-600 hover:bg-accent-500 text-accent-50 px-6 py-3 rounded-lg transition-colors"
      >
        Go home
      </Link>
    </div>
  );
}
