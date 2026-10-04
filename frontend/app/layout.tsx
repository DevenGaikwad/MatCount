import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/lib/auth";
import { ToastProvider } from "@/components/toast";

export const metadata: Metadata = {
  title: { default: "SEMS", template: "%s | SEMS" },
  description: "Smart Electronics Management System — professional laboratory operations platform.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body><AuthProvider><ToastProvider>{children}</ToastProvider></AuthProvider></body>
    </html>
  );
}
