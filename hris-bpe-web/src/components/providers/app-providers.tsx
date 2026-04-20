"use client";

import { useEffect } from "react";
import { QueryProvider } from "@/lib/query";
import { useAuthStore } from "@/store/auth-store";

export function AppProviders({ children }: { children: React.ReactNode }) {
  const hydrated = useAuthStore((state) => state.hydrated);
  const session = useAuthStore((state) => state.session);

  useEffect(() => {
    if (!hydrated) {
      return;
    }

    document.documentElement.lang = session?.user.preferred_language ?? "id";
    document.documentElement.dataset.theme =
      session?.user.preferred_theme ?? "theme_1";
  }, [
    hydrated,
    session?.user.preferred_language,
    session?.user.preferred_theme,
  ]);

  return <QueryProvider>{children}</QueryProvider>;
}
