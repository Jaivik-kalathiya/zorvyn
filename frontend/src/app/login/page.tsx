"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { ApiError, bootstrapAdmin, login } from "@/lib/api";
import { getStoredTokens, setStoredTokens } from "@/lib/auth";

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

const bootstrapSchema = z.object({
  email: z.string().email(),
  full_name: z.string().min(2),
  password: z.string().min(8),
});

type LoginInput = z.infer<typeof loginSchema>;
type BootstrapInput = z.infer<typeof bootstrapSchema>;

export default function LoginPage() {
  const router = useRouter();
  const [showBootstrap, setShowBootstrap] = useState(false);
  const [bootstrapMessage, setBootstrapMessage] = useState<string | null>(null);

  const loginForm = useForm<LoginInput>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "" },
  });

  const bootstrapForm = useForm<BootstrapInput>({
    resolver: zodResolver(bootstrapSchema),
    defaultValues: { email: "", full_name: "", password: "" },
  });

  useEffect(() => {
    if (getStoredTokens().accessToken) {
      router.replace("/dashboard");
    }
  }, [router]);

  const loginMutation = useMutation({
    mutationFn: login,
    onSuccess: (tokenResponse) => {
      setStoredTokens(tokenResponse.access_token, tokenResponse.refresh_token);
      router.push("/dashboard");
    },
  });

  const bootstrapMutation = useMutation({
    mutationFn: bootstrapAdmin,
    onSuccess: async (_, variables) => {
      setBootstrapMessage("Admin user created. Logging in...");
      const tokenResponse = await login({
        email: variables.email,
        password: variables.password,
      });
      setStoredTokens(tokenResponse.access_token, tokenResponse.refresh_token);
      router.push("/dashboard");
    },
    onError: (error) => {
      const message =
        error instanceof ApiError
          ? error.message
          : "Bootstrap failed. Please try again.";
      setBootstrapMessage(message);
    },
  });

  return (
    <main className="relative min-h-screen overflow-hidden bg-[#071426] px-6 py-14 text-slate-100">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_15%_20%,rgba(255,166,76,0.2),transparent_45%),radial-gradient(circle_at_80%_10%,rgba(34,211,238,0.2),transparent_45%),radial-gradient(circle_at_70%_80%,rgba(16,185,129,0.2),transparent_40%)]" />

      <section className="relative mx-auto grid w-full max-w-6xl gap-8 lg:grid-cols-[1.2fr_1fr]">
        <div className="space-y-6 rounded-3xl border border-slate-500/30 bg-slate-900/55 p-8 backdrop-blur-xl">
          <p className="inline-block rounded-full border border-cyan-300/40 bg-cyan-300/10 px-4 py-1 text-xs uppercase tracking-[0.18em] text-cyan-200">
            Finance Command Center
          </p>
          <h1 className="text-4xl font-semibold leading-tight md:text-5xl">
            Secure finance intelligence with role-first access control.
          </h1>
          <p className="max-w-xl text-base text-slate-300">
            Built for real operations with resilient APIs, protected workflows,
            and dashboard views that surface the numbers that matter most.
          </p>
          <div className="grid gap-4 text-sm text-slate-300 sm:grid-cols-3">
            <div className="rounded-2xl border border-slate-500/30 bg-slate-800/50 p-4">
              RBAC enforced
            </div>
            <div className="rounded-2xl border border-slate-500/30 bg-slate-800/50 p-4">
              Aggregated insights
            </div>
            <div className="rounded-2xl border border-slate-500/30 bg-slate-800/50 p-4">
              Soft-delete safe
            </div>
          </div>
        </div>

        <div className="space-y-4 rounded-3xl border border-slate-500/30 bg-slate-900/70 p-8 backdrop-blur-xl">
          <h2 className="text-2xl font-semibold">Sign in</h2>
          <form
            className="space-y-4"
            onSubmit={loginForm.handleSubmit((values) =>
              loginMutation.mutate(values),
            )}
          >
            <label className="block">
              <span className="mb-1 block text-sm text-slate-300">Email</span>
              <input
                className="w-full rounded-xl border border-slate-500/40 bg-slate-800/70 px-4 py-3 outline-none ring-cyan-300 transition focus:ring"
                placeholder="admin@example.com"
                type="email"
                {...loginForm.register("email")}
              />
            </label>
            <label className="block">
              <span className="mb-1 block text-sm text-slate-300">
                Password
              </span>
              <input
                className="w-full rounded-xl border border-slate-500/40 bg-slate-800/70 px-4 py-3 outline-none ring-cyan-300 transition focus:ring"
                placeholder="Your password"
                type="password"
                {...loginForm.register("password")}
              />
            </label>

            <button
              type="submit"
              className="w-full rounded-xl bg-cyan-400 px-4 py-3 text-sm font-semibold text-slate-900 transition hover:bg-cyan-300"
              disabled={loginMutation.isPending}
            >
              {loginMutation.isPending ? "Signing in..." : "Sign in"}
            </button>
          </form>

          {loginMutation.error ? (
            <p className="rounded-xl border border-rose-300/40 bg-rose-500/20 px-4 py-3 text-sm text-rose-100">
              {loginMutation.error instanceof ApiError
                ? loginMutation.error.message
                : "Could not sign in."}
            </p>
          ) : null}

          <button
            type="button"
            className="text-sm font-medium text-cyan-200 underline-offset-4 hover:underline"
            onClick={() => setShowBootstrap((prev) => !prev)}
          >
            {showBootstrap
              ? "Hide admin bootstrap"
              : "First run? Bootstrap admin"}
          </button>

          {showBootstrap ? (
            <form
              className="space-y-3 rounded-2xl border border-amber-300/40 bg-amber-300/10 p-4"
              onSubmit={bootstrapForm.handleSubmit((values) => {
                setBootstrapMessage(null);
                bootstrapMutation.mutate(values);
              })}
            >
              <h3 className="text-sm font-semibold uppercase tracking-[0.14em] text-amber-100">
                Bootstrap admin
              </h3>
              <input
                className="w-full rounded-lg border border-amber-100/30 bg-slate-900/60 px-3 py-2 text-sm outline-none ring-amber-200 focus:ring"
                placeholder="Admin email"
                type="email"
                {...bootstrapForm.register("email")}
              />
              <input
                className="w-full rounded-lg border border-amber-100/30 bg-slate-900/60 px-3 py-2 text-sm outline-none ring-amber-200 focus:ring"
                placeholder="Full name"
                type="text"
                {...bootstrapForm.register("full_name")}
              />
              <input
                className="w-full rounded-lg border border-amber-100/30 bg-slate-900/60 px-3 py-2 text-sm outline-none ring-amber-200 focus:ring"
                placeholder="Strong password"
                type="password"
                {...bootstrapForm.register("password")}
              />
              <button
                type="submit"
                className="w-full rounded-lg bg-amber-300 px-4 py-2 text-sm font-semibold text-slate-900 transition hover:bg-amber-200"
                disabled={bootstrapMutation.isPending}
              >
                {bootstrapMutation.isPending ? "Creating..." : "Create admin"}
              </button>
              {bootstrapMessage ? (
                <p className="text-sm text-amber-50">{bootstrapMessage}</p>
              ) : null}
            </form>
          ) : null}
        </div>
      </section>
    </main>
  );
}
