import type { Metadata } from "next";
import { AppProviders } from "@/components/providers/app-providers";
import "./globals.css";

export const metadata: Metadata = {
  title: "HRIS BPE Web",
  description: "UI Basic untuk HRIS BPE phase 11.5",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="id" data-theme="theme_1">
      <body>
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}
