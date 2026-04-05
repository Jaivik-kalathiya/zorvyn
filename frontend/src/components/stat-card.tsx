interface StatCardProps {
  label: string;
  value: string;
  tone?: "neutral" | "success" | "danger";
}

const tones = {
  neutral: "from-slate-700/70 to-slate-800/40 border-slate-500/30",
  success: "from-emerald-700/60 to-emerald-900/30 border-emerald-400/40",
  danger: "from-rose-700/60 to-rose-900/30 border-rose-400/40",
};

export function StatCard({ label, value, tone = "neutral" }: StatCardProps) {
  return (
    <article
      className={`rounded-2xl border bg-linear-to-br ${tones[tone]} p-5 shadow-[0_12px_42px_rgba(0,0,0,0.28)]`}
    >
      <p className="text-xs uppercase tracking-[0.16em] text-slate-300/90">
        {label}
      </p>
      <p className="mt-2 text-2xl font-semibold text-slate-100">{value}</p>
    </article>
  );
}
