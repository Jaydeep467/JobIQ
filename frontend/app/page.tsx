export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center px-6">
      <div className="max-w-3xl text-center">
        <p className="mb-4 text-sm font-semibold uppercase tracking-widest text-blue-600">
          JobIQ
        </p>

        <h1 className="text-4xl font-bold tracking-tight sm:text-6xl">
          Your AI-powered job search assistant.
        </h1>

        <p className="mx-auto mt-6 max-w-2xl text-lg text-gray-600">
          Analyze your resume, discover relevant opportunities, identify skill
          gaps, and tailor your applications with AI.
        </p>

        <div className="mt-8 flex justify-center gap-4">
          <a
            href="/login"
            className="rounded-lg bg-blue-600 px-6 py-3 font-semibold text-white transition hover:bg-blue-700"
          >
            Log in
          </a>

          <a
            href="/register"
            className="rounded-lg border border-gray-300 px-6 py-3 font-semibold transition hover:bg-gray-100"
          >
            Create account
          </a>
        </div>
      </div>
    </main>
  );
}