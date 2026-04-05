"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import clsx from "clsx";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { RolePill } from "@/components/role-pill";
import { StatCard } from "@/components/stat-card";
import {
  ApiError,
  createRecord,
  createUser,
  deleteRecord,
  exportRecordsCsv,
  exportReportCsv,
  getDashboardSummary,
  getMe,
  listRecords,
  listReports,
  listUsers,
  logout,
  runReportNow,
} from "@/lib/api";
import { clearStoredTokens, getStoredTokens } from "@/lib/auth";
import type { FinanceEntryType, UserRole } from "@/lib/types";

const money = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 2,
});

function formatMoney(value: string | number): string {
  return money.format(Number(value));
}

function extractValidationIssueMessage(error: ApiError): string | null {
  const details = error.details as
    | {
        issues?: Array<{
          loc?: Array<string | number>;
          msg?: string;
        }>;
      }
    | undefined;

  const firstIssue = details?.issues?.[0];
  if (!firstIssue?.msg) {
    return null;
  }

  const path = (firstIssue.loc ?? [])
    .filter((segment) => segment !== "body")
    .map(String)
    .join(".");

  if (!path) {
    return firstIssue.msg;
  }

  return `${path}: ${firstIssue.msg}`;
}

function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

export default function DashboardPage() {
  const router = useRouter();
  const queryClient = useQueryClient();

  const [accessToken] = useState<string | null>(() =>
    typeof window === "undefined" ? null : getStoredTokens().accessToken,
  );

  const [page, setPage] = useState(1);
  const [entryType, setEntryType] = useState<FinanceEntryType | "">("");
  const [category, setCategory] = useState("");
  const [search, setSearch] = useState("");
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");

  const [recordError, setRecordError] = useState<string | null>(null);
  const [userError, setUserError] = useState<string | null>(null);
  const [reportError, setReportError] = useState<string | null>(null);
  const [exportingRecords, setExportingRecords] = useState(false);

  useEffect(() => {
    if (!accessToken) {
      router.replace("/login");
    }
  }, [accessToken, router]);

  const meQuery = useQuery({
    queryKey: ["me", accessToken],
    queryFn: () => getMe(accessToken as string),
    enabled: Boolean(accessToken),
  });

  useEffect(() => {
    if (meQuery.error) {
      clearStoredTokens();
      router.replace("/login");
    }
  }, [meQuery.error, router]);

  const role = meQuery.data?.role;
  const canReadRecords = role === "admin" || role === "analyst";
  const canManageRecords = role === "admin";
  const canManageUsers = role === "admin";
  const canViewReports = role === "admin" || role === "analyst";

  const summaryQuery = useQuery({
    queryKey: ["dashboard-summary", accessToken, fromDate, toDate],
    queryFn: () =>
      getDashboardSummary(accessToken as string, {
        fromDate: fromDate || undefined,
        toDate: toDate || undefined,
      }),
    enabled: Boolean(accessToken),
  });

  const recordsQuery = useQuery({
    queryKey: [
      "records",
      accessToken,
      page,
      entryType,
      category,
      search,
      fromDate,
      toDate,
      role,
    ],
    queryFn: () =>
      listRecords(accessToken as string, {
        page,
        pageSize: 8,
        entryType: entryType || undefined,
        category: category || undefined,
        search: search || undefined,
        fromDate: fromDate || undefined,
        toDate: toDate || undefined,
      }),
    enabled: Boolean(accessToken && canReadRecords),
  });

  const usersQuery = useQuery({
    queryKey: ["users", accessToken, role],
    queryFn: () => listUsers(accessToken as string, { page: 1, pageSize: 8 }),
    enabled: Boolean(accessToken && canManageUsers),
  });

  const reportsQuery = useQuery({
    queryKey: ["reports", accessToken, role],
    queryFn: () => listReports(accessToken as string, { page: 1, pageSize: 8 }),
    enabled: Boolean(accessToken && canViewReports),
  });

  const createRecordMutation = useMutation({
    mutationFn: (payload: {
      amount: number;
      entry_type: FinanceEntryType;
      category: string;
      entry_date: string;
      notes?: string;
    }) => createRecord(accessToken as string, payload),
    onSuccess: () => {
      setRecordError(null);
      queryClient.invalidateQueries({ queryKey: ["records"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
    },
    onError: (error) => {
      setRecordError(
        error instanceof ApiError
          ? error.message
          : "Could not create record. Please try again.",
      );
    },
  });

  const deleteRecordMutation = useMutation({
    mutationFn: (recordId: number) =>
      deleteRecord(accessToken as string, recordId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["records"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
    },
  });

  const createUserMutation = useMutation({
    mutationFn: (payload: {
      email: string;
      full_name: string;
      password: string;
      role: UserRole;
    }) => createUser(accessToken as string, payload),
    onSuccess: () => {
      setUserError(null);
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
    onError: (error) => {
      if (error instanceof ApiError) {
        const validationMessage =
          error.code === "validation_error"
            ? extractValidationIssueMessage(error)
            : null;
        setUserError(validationMessage ?? error.message);
        return;
      }

      setUserError("Could not create user. Please try again.");
    },
  });

  const runReportMutation = useMutation({
    mutationFn: (payload: { report_name: string; lookback_days: number }) =>
      runReportNow(accessToken as string, payload),
    onSuccess: () => {
      setReportError(null);
      queryClient.invalidateQueries({ queryKey: ["reports"] });
    },
    onError: (error) => {
      setReportError(
        error instanceof ApiError
          ? error.message
          : "Could not run report. Please try again.",
      );
    },
  });

  const trendData = useMemo(
    () =>
      (summaryQuery.data?.trends ?? []).map((point) => ({
        period: new Date(point.period).toLocaleDateString("en-US", {
          month: "short",
          year: "2-digit",
        }),
        income: Number(point.income),
        expense: Number(point.expense),
      })),
    [summaryQuery.data?.trends],
  );

  function handleCreateRecord(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);

    const amount = Number(form.get("amount"));
    const entryTypeValue = form.get("entry_type") as FinanceEntryType;
    const categoryValue = String(form.get("category") ?? "");
    const entryDateValue = String(form.get("entry_date") ?? "");
    const notesValue = String(form.get("notes") ?? "").trim();

    if (!amount || !entryTypeValue || !categoryValue || !entryDateValue) {
      setRecordError("Amount, type, category, and date are required.");
      return;
    }

    createRecordMutation.mutate({
      amount,
      entry_type: entryTypeValue,
      category: categoryValue,
      entry_date: entryDateValue,
      notes: notesValue || undefined,
    });

    event.currentTarget.reset();
  }

  function handleCreateUser(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);

    const payload = {
      email: String(form.get("email") ?? "").trim(),
      full_name: String(form.get("full_name") ?? "").trim(),
      password: String(form.get("password") ?? "").trim(),
      role: String(form.get("role") ?? "viewer") as UserRole,
    };

    if (!payload.email || !payload.full_name || !payload.password) {
      setUserError("Email, full name, and password are required.");
      return;
    }

    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(payload.email)) {
      setUserError("Please enter a valid email address.");
      return;
    }

    if (payload.full_name.length < 2) {
      setUserError("Full name must be at least 2 characters.");
      return;
    }

    if (payload.password.length < 8) {
      setUserError("Password must be at least 8 characters.");
      return;
    }

    if (!["viewer", "analyst", "admin"].includes(payload.role)) {
      setUserError("Please select a valid role.");
      return;
    }

    createUserMutation.mutate(payload);
    event.currentTarget.reset();
  }

  async function handleLogout(): Promise<void> {
    const tokens = getStoredTokens();
    try {
      if (accessToken) {
        await logout(accessToken, {
          refresh_token: tokens.refreshToken ?? undefined,
        });
      }
    } catch {
      // If logout API fails, clear local tokens anyway to avoid a stuck session.
    } finally {
      clearStoredTokens();
      router.push("/login");
    }
  }

  async function handleExportRecordsCsv(): Promise<void> {
    if (!accessToken) {
      return;
    }

    setExportingRecords(true);
    setRecordError(null);
    try {
      const file = await exportRecordsCsv(accessToken, {
        entryType: entryType || undefined,
        category: category || undefined,
        search: search || undefined,
        fromDate: fromDate || undefined,
        toDate: toDate || undefined,
      });
      downloadBlob(file.blob, file.filename);
    } catch (error) {
      setRecordError(
        error instanceof ApiError
          ? error.message
          : "Could not export records CSV.",
      );
    } finally {
      setExportingRecords(false);
    }
  }

  async function handleExportReportCsv(reportId: number): Promise<void> {
    if (!accessToken) {
      return;
    }

    try {
      const file = await exportReportCsv(accessToken, reportId);
      downloadBlob(file.blob, file.filename);
    } catch (error) {
      setReportError(
        error instanceof ApiError ? error.message : "Could not export report.",
      );
    }
  }

  if (!accessToken || meQuery.isLoading) {
    return (
      <main className="grid min-h-screen place-items-center bg-[#071426] text-slate-200">
        <p className="text-sm uppercase tracking-[0.2em]">
          Loading dashboard...
        </p>
      </main>
    );
  }

  return (
    <main className="relative min-h-screen overflow-hidden bg-[#071426] px-4 py-8 text-slate-100 md:px-8">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_20%_15%,rgba(255,166,76,0.2),transparent_45%),radial-gradient(circle_at_75%_10%,rgba(34,211,238,0.18),transparent_45%),radial-gradient(circle_at_75%_85%,rgba(16,185,129,0.2),transparent_40%)]" />

      <section className="relative mx-auto w-full max-w-7xl space-y-8">
        <header className="flex flex-wrap items-center justify-between gap-4 rounded-3xl border border-slate-500/35 bg-slate-900/60 px-6 py-5 backdrop-blur-xl">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-cyan-200/90">
              Financial Operations Hub
            </p>
            <h1 className="mt-1 text-2xl font-semibold text-white">
              Welcome back, {meQuery.data?.full_name}
            </h1>
          </div>

          <div className="flex items-center gap-3">
            {role ? <RolePill role={role} /> : null}
            <button
              type="button"
              className="rounded-xl border border-slate-400/40 px-4 py-2 text-sm font-medium text-slate-100 transition hover:border-rose-300/50 hover:text-rose-200"
              onClick={() => {
                void handleLogout();
              }}
            >
              Log out
            </button>
          </div>
        </header>

        <section className="grid gap-4 md:grid-cols-3">
          <StatCard
            label="Total income"
            value={formatMoney(summaryQuery.data?.total_income ?? 0)}
            tone="success"
          />
          <StatCard
            label="Total expenses"
            value={formatMoney(summaryQuery.data?.total_expenses ?? 0)}
            tone="danger"
          />
          <StatCard
            label="Net balance"
            value={formatMoney(summaryQuery.data?.net_balance ?? 0)}
            tone="neutral"
          />
        </section>

        <section className="grid gap-5 lg:grid-cols-[1.8fr_1fr]">
          <article className="rounded-3xl border border-slate-500/35 bg-slate-900/65 p-5 backdrop-blur-xl">
            <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
              <h2 className="text-lg font-semibold text-slate-100">
                Monthly trend
              </h2>
              <div className="flex flex-wrap gap-2">
                <input
                  type="date"
                  className="rounded-lg border border-slate-500/40 bg-slate-800/70 px-3 py-2 text-sm"
                  value={fromDate}
                  onChange={(event) => {
                    setFromDate(event.target.value);
                    setPage(1);
                  }}
                />
                <input
                  type="date"
                  className="rounded-lg border border-slate-500/40 bg-slate-800/70 px-3 py-2 text-sm"
                  value={toDate}
                  onChange={(event) => {
                    setToDate(event.target.value);
                    setPage(1);
                  }}
                />
              </div>
            </div>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={trendData}>
                  <defs>
                    <linearGradient
                      id="incomeGradient"
                      x1="0"
                      y1="0"
                      x2="0"
                      y2="1"
                    >
                      <stop offset="5%" stopColor="#22d3ee" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#22d3ee" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient
                      id="expenseGradient"
                      x1="0"
                      y1="0"
                      x2="0"
                      y2="1"
                    >
                      <stop offset="5%" stopColor="#fb7185" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#fb7185" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="4 4" stroke="#334155" />
                  <XAxis dataKey="period" stroke="#cbd5e1" />
                  <YAxis stroke="#cbd5e1" />
                  <Tooltip
                    formatter={(value) => formatMoney(Number(value ?? 0))}
                    contentStyle={{
                      background: "#0f172a",
                      border: "1px solid #334155",
                      borderRadius: 12,
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="income"
                    stroke="#22d3ee"
                    fillOpacity={1}
                    fill="url(#incomeGradient)"
                    strokeWidth={2}
                  />
                  <Area
                    type="monotone"
                    dataKey="expense"
                    stroke="#fb7185"
                    fillOpacity={1}
                    fill="url(#expenseGradient)"
                    strokeWidth={2}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </article>

          <article className="rounded-3xl border border-slate-500/35 bg-slate-900/65 p-5 backdrop-blur-xl">
            <h2 className="mb-4 text-lg font-semibold text-slate-100">
              Category split
            </h2>
            <div className="space-y-3">
              {(summaryQuery.data?.category_totals ?? []).map((item) => (
                <div
                  key={item.category}
                  className="flex items-center justify-between rounded-xl border border-slate-600/40 bg-slate-800/60 px-3 py-2"
                >
                  <p className="text-sm capitalize text-slate-100">
                    {item.category}
                  </p>
                  <p className="text-sm font-semibold text-cyan-200">
                    {formatMoney(item.total)}
                  </p>
                </div>
              ))}
              {summaryQuery.data?.category_totals.length === 0 ? (
                <p className="text-sm text-slate-400">No category data yet.</p>
              ) : null}
            </div>
          </article>
        </section>

        <section className="rounded-3xl border border-slate-500/35 bg-slate-900/65 p-5 backdrop-blur-xl">
          <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
            <div>
              <h2 className="text-lg font-semibold text-slate-100">
                Financial records
              </h2>
              <p className="text-sm text-slate-400">
                Analysts and admins can inspect records with filters and search.
              </p>
            </div>
            {canReadRecords ? null : (
              <p className="rounded-xl border border-cyan-300/40 bg-cyan-500/20 px-3 py-2 text-sm text-cyan-100">
                Viewer role can only access dashboard summaries.
              </p>
            )}
          </div>

          {canReadRecords ? (
            <>
              <div className="mb-4 grid gap-3 md:grid-cols-5">
                <input
                  type="search"
                  placeholder="Search notes/category"
                  value={search}
                  onChange={(event) => {
                    setSearch(event.target.value);
                    setPage(1);
                  }}
                  className="rounded-lg border border-slate-500/40 bg-slate-800/70 px-3 py-2 text-sm"
                />
                <input
                  type="text"
                  placeholder="Category"
                  value={category}
                  onChange={(event) => {
                    setCategory(event.target.value);
                    setPage(1);
                  }}
                  className="rounded-lg border border-slate-500/40 bg-slate-800/70 px-3 py-2 text-sm"
                />
                <select
                  value={entryType}
                  onChange={(event) => {
                    setEntryType(event.target.value as FinanceEntryType | "");
                    setPage(1);
                  }}
                  className="rounded-lg border border-slate-500/40 bg-slate-800/70 px-3 py-2 text-sm"
                >
                  <option value="">All types</option>
                  <option value="income">Income</option>
                  <option value="expense">Expense</option>
                </select>
                <button
                  type="button"
                  onClick={() => {
                    setSearch("");
                    setCategory("");
                    setEntryType("");
                    setFromDate("");
                    setToDate("");
                    setPage(1);
                  }}
                  className="rounded-lg border border-slate-500/40 px-3 py-2 text-sm font-semibold text-slate-100 hover:border-cyan-300/50"
                >
                  Clear filters
                </button>
                <button
                  type="button"
                  onClick={() => {
                    void handleExportRecordsCsv();
                  }}
                  className="rounded-lg border border-emerald-400/45 px-3 py-2 text-sm font-semibold text-emerald-100 hover:bg-emerald-500/15 disabled:opacity-60"
                  disabled={exportingRecords}
                >
                  {exportingRecords ? "Exporting..." : "Export CSV"}
                </button>
              </div>

              <div className="overflow-x-auto rounded-2xl border border-slate-600/35">
                <table className="min-w-full text-sm">
                  <thead className="bg-slate-800/80 text-xs uppercase tracking-[0.12em] text-slate-300">
                    <tr>
                      <th className="px-4 py-3 text-left">Date</th>
                      <th className="px-4 py-3 text-left">Type</th>
                      <th className="px-4 py-3 text-left">Category</th>
                      <th className="px-4 py-3 text-left">Amount</th>
                      <th className="px-4 py-3 text-left">Notes</th>
                      <th className="px-4 py-3 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(recordsQuery.data?.items ?? []).map((record) => (
                      <tr
                        key={record.id}
                        className="border-t border-slate-700/40 text-slate-100"
                      >
                        <td className="px-4 py-3">{record.entry_date}</td>
                        <td className="px-4 py-3">
                          <span
                            className={clsx(
                              "rounded-full px-2 py-1 text-xs font-semibold uppercase tracking-[0.12em]",
                              record.entry_type === "income"
                                ? "bg-emerald-500/20 text-emerald-100"
                                : "bg-rose-500/20 text-rose-100",
                            )}
                          >
                            {record.entry_type}
                          </span>
                        </td>
                        <td className="px-4 py-3 capitalize">
                          {record.category}
                        </td>
                        <td className="px-4 py-3 font-semibold">
                          {formatMoney(record.amount)}
                        </td>
                        <td className="max-w-64 truncate px-4 py-3 text-slate-300">
                          {record.notes || "-"}
                        </td>
                        <td className="px-4 py-3 text-right">
                          {canManageRecords ? (
                            <button
                              type="button"
                              className="rounded-lg border border-rose-300/40 px-3 py-1.5 text-xs font-semibold text-rose-100 hover:bg-rose-500/20"
                              onClick={() =>
                                deleteRecordMutation.mutate(record.id)
                              }
                              disabled={deleteRecordMutation.isPending}
                            >
                              Delete
                            </button>
                          ) : (
                            <span className="text-xs text-slate-500">
                              Read only
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="mt-4 flex items-center justify-between text-sm text-slate-300">
                <p>
                  Page {recordsQuery.data?.meta.page ?? 1} of{" "}
                  {recordsQuery.data?.meta.total_pages ?? 1}
                </p>
                <div className="flex gap-2">
                  <button
                    type="button"
                    className="rounded-lg border border-slate-500/40 px-3 py-1.5 disabled:opacity-40"
                    onClick={() => setPage((prev) => Math.max(prev - 1, 1))}
                    disabled={page === 1}
                  >
                    Previous
                  </button>
                  <button
                    type="button"
                    className="rounded-lg border border-slate-500/40 px-3 py-1.5 disabled:opacity-40"
                    onClick={() => setPage((prev) => prev + 1)}
                    disabled={
                      (recordsQuery.data?.meta.total_pages ?? 1) <=
                      (recordsQuery.data?.meta.page ?? 1)
                    }
                  >
                    Next
                  </button>
                </div>
              </div>
            </>
          ) : null}
        </section>

        {canViewReports ? (
          <section className="rounded-3xl border border-slate-500/35 bg-slate-900/65 p-5 backdrop-blur-xl">
            <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
              <div>
                <h2 className="text-lg font-semibold text-slate-100">
                  Scheduled reports
                </h2>
                <p className="text-sm text-slate-400">
                  Snapshot reports can be downloaded as CSV for audit and
                  review.
                </p>
              </div>
              {canManageUsers ? (
                <button
                  type="button"
                  className="rounded-lg border border-cyan-300/45 px-3 py-2 text-sm font-semibold text-cyan-100 hover:bg-cyan-500/15 disabled:opacity-60"
                  onClick={() => {
                    runReportMutation.mutate({
                      report_name: "manual_snapshot",
                      lookback_days: 30,
                    });
                  }}
                  disabled={runReportMutation.isPending}
                >
                  {runReportMutation.isPending
                    ? "Running..."
                    : "Run report now"}
                </button>
              ) : null}
            </div>

            {reportError ? (
              <p className="mb-3 rounded-lg border border-rose-300/40 bg-rose-500/20 px-3 py-2 text-sm text-rose-100">
                {reportError}
              </p>
            ) : null}

            <div className="overflow-x-auto rounded-2xl border border-slate-600/35">
              <table className="min-w-full text-sm">
                <thead className="bg-slate-800/80 text-xs uppercase tracking-[0.12em] text-slate-300">
                  <tr>
                    <th className="px-4 py-3 text-left">Generated</th>
                    <th className="px-4 py-3 text-left">Name</th>
                    <th className="px-4 py-3 text-left">Period</th>
                    <th className="px-4 py-3 text-left">Net</th>
                    <th className="px-4 py-3 text-left">Records</th>
                    <th className="px-4 py-3 text-right">Download</th>
                  </tr>
                </thead>
                <tbody>
                  {(reportsQuery.data?.items ?? []).map((report) => (
                    <tr
                      key={report.id}
                      className="border-t border-slate-700/40 text-slate-100"
                    >
                      <td className="px-4 py-3">
                        {new Date(report.generated_at).toLocaleString()}
                      </td>
                      <td className="px-4 py-3">{report.report_name}</td>
                      <td className="px-4 py-3">
                        {report.period_start} to {report.period_end}
                      </td>
                      <td className="px-4 py-3 font-semibold text-cyan-200">
                        {formatMoney(report.net_balance)}
                      </td>
                      <td className="px-4 py-3">{report.record_count}</td>
                      <td className="px-4 py-3 text-right">
                        <button
                          type="button"
                          className="rounded-lg border border-slate-400/45 px-3 py-1.5 text-xs font-semibold text-slate-100 hover:border-emerald-300/50 hover:text-emerald-200"
                          onClick={() => {
                            void handleExportReportCsv(report.id);
                          }}
                        >
                          CSV
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        ) : null}

        {canManageRecords || canManageUsers ? (
          <section className="grid gap-5 lg:grid-cols-2">
            {canManageRecords ? (
              <article className="rounded-3xl border border-slate-500/35 bg-slate-900/65 p-5 backdrop-blur-xl">
                <h2 className="text-lg font-semibold">Create finance record</h2>
                <form className="mt-4 grid gap-3" onSubmit={handleCreateRecord}>
                  <input
                    name="amount"
                    type="number"
                    step="0.01"
                    min="0.01"
                    placeholder="Amount"
                    className="rounded-lg border border-slate-500/40 bg-slate-800/70 px-3 py-2 text-sm"
                    required
                  />
                  <select
                    name="entry_type"
                    className="rounded-lg border border-slate-500/40 bg-slate-800/70 px-3 py-2 text-sm"
                    defaultValue="income"
                  >
                    <option value="income">Income</option>
                    <option value="expense">Expense</option>
                  </select>
                  <input
                    name="category"
                    type="text"
                    placeholder="Category"
                    className="rounded-lg border border-slate-500/40 bg-slate-800/70 px-3 py-2 text-sm"
                    required
                  />
                  <input
                    name="entry_date"
                    type="date"
                    className="rounded-lg border border-slate-500/40 bg-slate-800/70 px-3 py-2 text-sm"
                    required
                  />
                  <textarea
                    name="notes"
                    placeholder="Notes (optional)"
                    rows={3}
                    className="rounded-lg border border-slate-500/40 bg-slate-800/70 px-3 py-2 text-sm"
                  />
                  <button
                    type="submit"
                    className="rounded-lg bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-900 hover:bg-cyan-300"
                    disabled={createRecordMutation.isPending}
                  >
                    {createRecordMutation.isPending
                      ? "Creating..."
                      : "Create record"}
                  </button>
                  {recordError ? (
                    <p className="rounded-lg border border-rose-300/40 bg-rose-500/20 px-3 py-2 text-sm text-rose-100">
                      {recordError}
                    </p>
                  ) : null}
                </form>
              </article>
            ) : null}

            {canManageUsers ? (
              <article className="rounded-3xl border border-slate-500/35 bg-slate-900/65 p-5 backdrop-blur-xl">
                <h2 className="text-lg font-semibold">User management</h2>
                <form className="mt-4 grid gap-3" onSubmit={handleCreateUser}>
                  <input
                    name="email"
                    type="email"
                    placeholder="Email"
                    className="rounded-lg border border-slate-500/40 bg-slate-800/70 px-3 py-2 text-sm"
                    required
                  />
                  <input
                    name="full_name"
                    type="text"
                    placeholder="Full name"
                    className="rounded-lg border border-slate-500/40 bg-slate-800/70 px-3 py-2 text-sm"
                    minLength={2}
                    required
                  />
                  <input
                    name="password"
                    type="password"
                    placeholder="Temporary password"
                    className="rounded-lg border border-slate-500/40 bg-slate-800/70 px-3 py-2 text-sm"
                    minLength={8}
                    required
                  />
                  <select
                    name="role"
                    className="rounded-lg border border-slate-500/40 bg-slate-800/70 px-3 py-2 text-sm"
                    defaultValue="viewer"
                  >
                    <option value="viewer">Viewer</option>
                    <option value="analyst">Analyst</option>
                    <option value="admin">Admin</option>
                  </select>
                  <button
                    type="submit"
                    className="rounded-lg bg-emerald-400 px-4 py-2 text-sm font-semibold text-slate-900 hover:bg-emerald-300"
                    disabled={createUserMutation.isPending}
                  >
                    {createUserMutation.isPending
                      ? "Creating..."
                      : "Create user"}
                  </button>
                  {userError ? (
                    <p className="rounded-lg border border-rose-300/40 bg-rose-500/20 px-3 py-2 text-sm text-rose-100">
                      {userError}
                    </p>
                  ) : null}
                </form>

                <div className="mt-4 space-y-2">
                  {(usersQuery.data?.items ?? []).map((user) => (
                    <div
                      key={user.id}
                      className="flex items-center justify-between rounded-xl border border-slate-600/40 bg-slate-800/60 px-3 py-2"
                    >
                      <div>
                        <p className="text-sm font-semibold text-slate-100">
                          {user.full_name}
                        </p>
                        <p className="text-xs text-slate-400">{user.email}</p>
                      </div>
                      <RolePill role={user.role} />
                    </div>
                  ))}
                </div>
              </article>
            ) : null}
          </section>
        ) : null}
      </section>
    </main>
  );
}
