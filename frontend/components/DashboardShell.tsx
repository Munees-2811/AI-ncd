"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import {
  ClipboardPlus,
  LayoutDashboard,
  LogOut,
  Shield,
  ShieldCheck,
} from "lucide-react";
import { ThemeToggle } from "./ThemeToggle";
import { LanguageSwitcher } from "./LanguageSwitcher";
import { cn } from "@/lib/utils";

const nav = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/assess", label: "New Assessment", icon: ClipboardPlus },
  { href: "/admin", label: "Admin", icon: ShieldCheck },
];

export function DashboardShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    if (!localStorage.getItem("ncd_token")) router.push("/login");
  }, [router]);

  const logout = () => {
    localStorage.removeItem("ncd_token");
    router.push("/login");
  };

  return (
    <div className="mesh min-h-screen">
      <div className="mx-auto flex max-w-7xl gap-6 px-4 py-6">
        <aside className="glass sticky top-6 hidden h-[calc(100vh-3rem)] w-60 flex-col p-4 md:flex">
          <Link href="/" className="mb-8 flex items-center gap-2 px-2 font-bold">
            <Shield className="h-7 w-7 text-brand-600" />
            <span>NCD Shield AI</span>
          </Link>
          <nav className="flex-1 space-y-1">
            {nav.map((n) => (
              <Link
                key={n.href}
                href={n.href}
                className={cn(
                  "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition",
                  pathname === n.href
                    ? "bg-brand-600 text-white shadow-lg shadow-brand-600/30"
                    : "hover:bg-slate-100 dark:hover:bg-slate-800"
                )}
              >
                <n.icon className="h-5 w-5" />
                {n.label}
              </Link>
            ))}
          </nav>
          <div className="flex items-center gap-2">
            <LanguageSwitcher />
            <ThemeToggle />
          </div>
          <button onClick={logout} className="btn-ghost mt-3 w-full">
            <LogOut className="h-4 w-4" /> Logout
          </button>
        </aside>

        <main className="min-w-0 flex-1">{children}</main>
      </div>
    </div>
  );
}
