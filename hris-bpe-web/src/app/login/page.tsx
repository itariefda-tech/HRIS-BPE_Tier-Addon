"use client";

import { useEffect } from "react";
import { useMutation } from "@tanstack/react-query";
import Image from "next/image";
import { useForm } from "react-hook-form";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { t } from "@/lib/i18n";
import {
  helperTextClass,
  inputClass,
  labelClass,
  primaryButtonClass,
} from "@/lib/ui";
import { useAuthStore } from "@/store/auth-store";

type LoginFormValues = {
  identifier: string;
  password: string;
};

export default function LoginPage() {
  const router = useRouter();
  const hydrated = useAuthStore((state) => state.hydrated);
  const session = useAuthStore((state) => state.session);
  const setSession = useAuthStore((state) => state.setSession);
  const language = session?.user.preferred_language ?? "id";
  const form = useForm<LoginFormValues>({
    defaultValues: {
      identifier: "owner@bpe.co.id",
      password: "Admin123!",
    },
  });

  const loginMutation = useMutation({
    mutationFn: (values: LoginFormValues) => api.auth.login(values),
    onSuccess: (data) => {
      setSession(data);
      router.replace("/dashboard");
    },
  });

  useEffect(() => {
    if (hydrated && session) {
      router.replace("/dashboard");
    }
  }, [hydrated, router, session]);

  return (
    <main className="relative min-h-screen overflow-hidden">
      <Image
        src="https://images.unsplash.com/photo-1516321497487-e288fb19713f?auto=format&fit=crop&w=1600&q=80"
        alt="Tim operasional bekerja di command center."
        fill
        priority
        className="absolute inset-0 h-full w-full object-cover"
      />
      <div className="absolute inset-0 bg-[linear-gradient(90deg,rgba(20,32,25,0.86),rgba(20,32,25,0.58),rgba(20,32,25,0.4))]" />

      <div className="relative flex min-h-screen items-center px-6 py-8">
        <div className="w-full max-w-md rounded-md border border-white/10 bg-[rgba(255,255,255,0.92)] p-6 shadow-[0_16px_48px_rgba(0,0,0,0.18)] backdrop-blur-sm">
          <p className="text-xs font-semibold uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
            {t(language, "app.name")}
          </p>
          <h1 className="mt-3 text-3xl font-semibold text-[color:var(--foreground)]">
            {t(language, "auth.title")}
          </h1>
          <p className="mt-2 text-sm text-[color:var(--muted-foreground)]">
            {t(language, "auth.subtitle")}
          </p>

          <form
            className="mt-6 space-y-4"
            onSubmit={form.handleSubmit((values) => loginMutation.mutate(values))}
          >
            <div>
              <label className={labelClass} htmlFor="identifier">
                {t(language, "auth.identifier")}
              </label>
              <input
                id="identifier"
                className={inputClass}
                {...form.register("identifier", { required: true })}
              />
            </div>

            <div>
              <label className={labelClass} htmlFor="password">
                {t(language, "auth.password")}
              </label>
              <input
                id="password"
                type="password"
                className={inputClass}
                {...form.register("password", { required: true })}
              />
            </div>

            {loginMutation.error ? (
              <div className="rounded-md bg-[color:var(--danger)]/10 px-3 py-2 text-sm text-[color:var(--danger)]">
                {loginMutation.error.message}
              </div>
            ) : null}

            <button
              type="submit"
              className={`${primaryButtonClass} w-full`}
              disabled={loginMutation.isPending}
            >
              {loginMutation.isPending
                ? "Memproses..."
                : t(language, "auth.submit")}
            </button>
          </form>

          <div className="mt-6 rounded-md border border-[color:var(--border)] bg-white/85 p-4">
            <p className="text-sm font-semibold text-[color:var(--foreground)]">
              {t(language, "auth.demo")}
            </p>
            <div className={`mt-3 space-y-1 ${helperTextClass}`}>
              <p>`owner@bpe.co.id / Admin123!`</p>
              <p>`supervisor@bpe.co.id / Supervisor123!`</p>
              <p>`guard@bpe.co.id / Guard123!`</p>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
