"use client";

import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import { t } from "@/lib/i18n";
import { navItems } from "@/lib/navigation";
import { secondaryButtonClass } from "@/lib/ui";
import { useAuthStore } from "@/store/auth-store";

function LoadingPane({ message }: { message: string }) {
  return (
    <div className="flex min-h-screen items-center justify-center px-6">
      <div className="rounded-md border border-[color:var(--border)] bg-[color:var(--surface)] px-5 py-4 text-sm text-[color:var(--muted-foreground)] shadow-sm">
        {message}
      </div>
    </div>
  );
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [logoutBusy, setLogoutBusy] = useState(false);
  const hydrated = useAuthStore((state) => state.hydrated);
  const session = useAuthStore((state) => state.session);
  const clearSession = useAuthStore((state) => state.clearSession);
  const updateUser = useAuthStore((state) => state.updateUser);

  const language = session?.user.preferred_language ?? "id";

  const meQuery = useQuery({
    queryKey: ["auth", "me", session?.access_token],
    queryFn: () => api.auth.me(session!.access_token),
    enabled: hydrated && Boolean(session?.access_token),
    retry: false,
  });

  useEffect(() => {
    if (meQuery.data) {
      updateUser(meQuery.data);
    }
  }, [meQuery.data, updateUser]);

  useEffect(() => {
    if (!(meQuery.error instanceof ApiError)) {
      return;
    }

    if (meQuery.error.status === 401) {
      clearSession();
      router.replace("/login");
    }
  }, [clearSession, meQuery.error, router]);

  async function handleLogout() {
    if (!session?.access_token) {
      clearSession();
      router.replace("/login");
      return;
    }

    try {
      setLogoutBusy(true);
      await api.auth.logout(session.access_token);
    } catch {
      // Ignore logout API failure, local session still needs to be cleared.
    } finally {
      clearSession();
      router.replace("/login");
      setLogoutBusy(false);
    }
  }

  if (!hydrated) {
    return <LoadingPane message="Menyiapkan session..." />;
  }

  if (!session) {
    return <LoadingPane message="Mengalihkan ke login..." />;
  }

  return (
    <div className="min-h-screen bg-[color:var(--background)]">
      <div className="mx-auto flex min-h-screen max-w-[1600px] flex-col md:flex-row">
        <aside className="border-b border-[color:var(--border)] bg-[color:var(--surface)] px-4 py-4 md:min-h-screen md:w-64 md:border-b-0 md:border-r">
          <div className="border-b border-[color:var(--border)] pb-4">
            <p className="text-xs font-semibold uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
              {t(language, "app.name")}
            </p>
            <p className="mt-2 text-sm text-[color:var(--muted-foreground)]">
              Basic admin UI untuk validasi flow operasional.
            </p>
          </div>

          <nav className="mt-4 grid gap-2">
            {navItems.map((item) => {
              const active = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`rounded-md px-3 py-2 text-sm font-medium transition ${
                    active
                      ? "bg-[color:var(--accent)] text-white"
                      : "text-[color:var(--foreground)] hover:bg-[color:var(--muted-surface)]"
                  }`}
                >
                  {t(language, item.labelKey)}
                </Link>
              );
            })}
          </nav>
        </aside>

        <div className="flex flex-1 flex-col">
          <header className="border-b border-[color:var(--border)] bg-[color:var(--surface)] px-4 py-4">
            <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.08em] text-[color:var(--muted-foreground)]">
                  {t(language, "layout.profile")}
                </p>
                <p className="mt-1 text-base font-semibold text-[color:var(--foreground)]">
                  {session.user.username}
                </p>
                <p className="text-sm text-[color:var(--muted-foreground)]">
                  {session.user.email} · {session.user.role_codes.join(", ")}
                </p>
              </div>

              <div className="flex flex-wrap gap-2">
                {meQuery.error && !(meQuery.error instanceof ApiError && meQuery.error.status === 401) ? (
                  <span className="rounded-md bg-[color:var(--danger)]/10 px-3 py-2 text-sm text-[color:var(--danger)]">
                    Profil user gagal disinkronkan.
                  </span>
                ) : null}
                <button
                  type="button"
                  onClick={handleLogout}
                  disabled={logoutBusy}
                  className={secondaryButtonClass}
                >
                  {logoutBusy ? "Memproses..." : t(language, "layout.logout")}
                </button>
              </div>
            </div>
          </header>

          <main className="flex-1 px-4 py-6">{children}</main>
        </div>
      </div>
    </div>
  );
}
