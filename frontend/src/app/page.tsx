import Link from "next/link";

export default function Home() {
  return (
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden px-6 py-16 text-slate-100">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_18%_12%,rgba(255,166,76,0.2),transparent_43%),radial-gradient(circle_at_80%_10%,rgba(34,211,238,0.2),transparent_43%),radial-gradient(circle_at_70%_80%,rgba(16,185,129,0.2),transparent_40%)]" />

      <section className="animate-rise relative w-full max-w-5xl rounded-4xl border border-slate-500/30 bg-slate-900/60 p-8 shadow-[0_24px_90px_rgba(0,0,0,0.35)] backdrop-blur-xl md:p-12">
        <p className="inline-block rounded-full border border-cyan-300/40 bg-cyan-300/10 px-4 py-1 text-xs uppercase tracking-[0.18em] text-cyan-200">
          Zorvyn Finance Cloud
        </p>
        <h1 className="mt-5 max-w-3xl text-4xl font-semibold leading-tight md:text-6xl">
          Cash flow clarity for teams that move fast.
        </h1>
        <p className="mt-5 max-w-2xl text-base text-slate-300 md:text-lg">
          Track income and expenses, control access by role, and turn raw
          financial activity into decisions through clean dashboards, secure
          workflows, and export-ready reporting.
        </p>

        <div className="mt-8 grid gap-3 text-sm text-slate-200 sm:grid-cols-3">
          <div className="rounded-2xl border border-slate-500/35 bg-slate-800/60 px-4 py-3">
            Live financial visibility
          </div>
          <div className="rounded-2xl border border-slate-500/35 bg-slate-800/60 px-4 py-3">
            Role-aware secure operations
          </div>
          <div className="rounded-2xl border border-slate-500/35 bg-slate-800/60 px-4 py-3">
            CSV and report automation
          </div>
        </div>

        <div className="mt-9 flex flex-wrap gap-3">
          <Link
            href="/login"
            className="rounded-xl bg-cyan-400 px-5 py-3 text-sm font-semibold text-slate-900 transition hover:bg-cyan-300"
          >
            Sign in
          </Link>
          <Link
            href="/dashboard"
            className="rounded-xl border border-slate-400/40 px-5 py-3 text-sm font-semibold text-slate-100 transition hover:border-emerald-300/40 hover:text-emerald-200"
          >
            Open dashboard
          </Link>
          <Link
            href="/platform-info"
            className="rounded-xl border border-amber-300/45 px-5 py-3 text-sm font-semibold text-amber-100 transition hover:bg-amber-300/12"
          >
            Platform information
          </Link>
        </div>
      </section>
    </main>
  );
}
