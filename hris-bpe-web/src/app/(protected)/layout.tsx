"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { AppShell } from "@/components/layout/app-shell";
import { useAuthStore } from "@/store/auth-store";

export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const hydrated = useAuthStore((state) => state.hydrated);
  const session = useAuthStore((state) => state.session);

  useEffect(() => {
    if (hydrated && !session) {
      router.replace("/login");
    }
  }, [hydrated, router, session]);

  return <AppShell>{children}</AppShell>;
}
