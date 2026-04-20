"use client";

import { useEffect } from "react";
import { QueryProvider } from "@/lib/query";
import { useAuthStore } from "@/store/auth-store";

export function AppProviders({ children }: { children: React.ReactNode }) {
  const hydrated = useAuthStore((state) => state.hydrated);
  const session = useAuthStore((state) => state.session);
  const setHydrated = useAuthStore((state) => state.setHydrated);

  useEffect(() => {
    setHydrated(useAuthStore.persist.hasHydrated());

    const unsubscribeHydrate = useAuthStore.persist.onHydrate(() => {
      setHydrated(false);
    });
    const unsubscribeFinishHydration = useAuthStore.persist.onFinishHydration(() => {
      setHydrated(true);
    });

    void useAuthStore.persist.rehydrate();

    return () => {
      unsubscribeHydrate();
      unsubscribeFinishHydration();
    };
  }, [setHydrated]);

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
