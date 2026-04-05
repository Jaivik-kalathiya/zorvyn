import Link from "next/link";

export default function PlatformInfoPage() {
  return (
    <main className="relative min-h-screen overflow-hidden px-6 py-14 text-slate-100">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_12%_18%,rgba(255,166,76,0.2),transparent_42%),radial-gradient(circle_at_78%_10%,rgba(34,211,238,0.2),transparent_43%),radial-gradient(circle_at_72%_82%,rgba(16,185,129,0.2),transparent_40%)]" />

      <section className="relative mx-auto w-full max-w-5xl rounded-4xl border border-slate-500/35 bg-slate-900/65 p-8 backdrop-blur-xl md:p-12">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <p className="inline-block rounded-full border border-amber-300/45 bg-amber-300/10 px-4 py-1 text-xs uppercase tracking-[0.16em] text-amber-100">
            Platform information
          </p>
          <Link
            href="/"
            className="rounded-lg border border-slate-400/45 px-3 py-2 text-sm font-semibold text-slate-100 hover:border-cyan-300/50 hover:text-cyan-200"
          >
            Back to home
          </Link>
        </div>

        <h1 className="mt-6 text-4xl font-semibold leading-tight md:text-5xl">
          How the platform works behind the scenes
        </h1>
        <p className="mt-4 max-w-3xl text-base text-slate-300 md:text-lg">
          This page summarizes product architecture and operational behavior for
          technical stakeholders, without affecting the main product journey.
        </p>

        <div className="mt-8 grid gap-4 md:grid-cols-2">
          <article className="rounded-2xl border border-slate-500/35 bg-slate-800/60 p-5">
            <h2 className="text-lg font-semibold text-slate-100">
              Security and access
            </h2>
            <ul className="mt-3 space-y-2 text-sm text-slate-300">
              <li>
                JWT-based sessions with refresh rotation and logout revocation.
              </li>
              <li>
                Role-based controls for viewers, analysts, and administrators.
              </li>
              <li>
                Server-side validation and structured error handling on every
                endpoint.
              </li>
            </ul>
          </article>

          <article className="rounded-2xl border border-slate-500/35 bg-slate-800/60 p-5">
            <h2 className="text-lg font-semibold text-slate-100">
              Data and analytics
            </h2>
            <ul className="mt-3 space-y-2 text-sm text-slate-300">
              <li>
                Financial records with filtering, pagination, and soft-delete
                safety.
              </li>
              <li>
                Dashboard summaries for income, expenses, category totals, and
                trends.
              </li>
              <li>CSV export for filtered records and generated reports.</li>
            </ul>
          </article>

          <article className="rounded-2xl border border-slate-500/35 bg-slate-800/60 p-5">
            <h2 className="text-lg font-semibold text-slate-100">
              Reporting automation
            </h2>
            <ul className="mt-3 space-y-2 text-sm text-slate-300">
              <li>On-demand report snapshots from the dashboard.</li>
              <li>Background scheduler for periodic report generation.</li>
              <li>Downloadable CSV outputs for audit and sharing workflows.</li>
            </ul>
          </article>

          <article className="rounded-2xl border border-slate-500/35 bg-slate-800/60 p-5">
            <h2 className="text-lg font-semibold text-slate-100">
              Experience design
            </h2>
            <ul className="mt-3 space-y-2 text-sm text-slate-300">
              <li>Role-aware views to reduce noise for each user type.</li>
              <li>
                High-contrast visual hierarchy with data-first dashboard
                components.
              </li>
              <li>
                Responsive layouts optimized for desktop and mobile screens.
              </li>
            </ul>
          </article>
        </div>
      </section>
    </main>
  );
}
