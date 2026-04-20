"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { AuthUser, LoginResponse } from "@/lib/types";

export type AuthSession = LoginResponse;

type AuthStore = {
  session: AuthSession | null;
  hydrated: boolean;
  setSession: (session: AuthSession) => void;
  updateUser: (user: AuthUser) => void;
  clearSession: () => void;
  setHydrated: (hydrated: boolean) => void;
};

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      session: null,
      hydrated: false,
      setSession: (session) => set({ session }),
      updateUser: (user) =>
        set((state) =>
          state.session
            ? {
                session: {
                  ...state.session,
                  user,
                },
              }
            : state,
        ),
      clearSession: () => set({ session: null }),
      setHydrated: (hydrated) => set({ hydrated }),
    }),
    {
      name: "hris-bpe-web-auth",
      partialize: (state) => ({ session: state.session }),
      onRehydrateStorage: () => (state) => {
        state?.setHydrated(true);
      },
    },
  ),
);
