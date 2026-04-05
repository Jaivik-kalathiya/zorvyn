import clsx from "clsx";

import type { UserRole } from "@/lib/types";

const roleStyles: Record<UserRole, string> = {
  viewer: "bg-cyan-500/20 text-cyan-200 border-cyan-400/40",
  analyst: "bg-amber-500/20 text-amber-100 border-amber-300/40",
  admin: "bg-emerald-500/20 text-emerald-100 border-emerald-300/40",
};

export function RolePill({ role }: { role: UserRole }) {
  return (
    <span
      className={clsx(
        "inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-[0.12em]",
        roleStyles[role],
      )}
    >
      {role}
    </span>
  );
}
