"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/auth-store";

export default function Home() {
  const router = useRouter();
  const hydrated = useAuthStore((state) => state.hydrated);
  const session = useAuthStore((state) => state.session);

  useEffect(() => {
    if (!hydrated) {
      return;
    }
    router.replace(session ? "/dashboard" : "/login");
  }, [hydrated, router, session]);

  return (
    <main className="flex min-h-screen items-center justify-center px-6">
      <div className="rounded-md border border-[color:var(--border)] bg-[color:var(--surface)] px-5 py-4 text-sm text-[color:var(--muted-foreground)] shadow-sm">
        Menyiapkan HRIS BPE Web...
      </div>
    </main>
  );
}
