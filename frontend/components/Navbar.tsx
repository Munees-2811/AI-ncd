"use client";

import Link from "next/link";
import { Shield } from "lucide-react";
import { useI18n } from "@/lib/i18n";
import { ThemeToggle } from "./ThemeToggle";
import { LanguageSwitcher } from "./LanguageSwitcher";

export function Navbar() {
  const { t } = useI18n();
  return (
    <header className="sticky top-0 z-40 border-b border-ink-200/60 bg-white/70 backdrop-blur-xl dark:border-white/[0.06] dark:bg-ink-950/70">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-3.5">
        <Link href="/" className="group flex items-center gap-2.5 font-semibold">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-brand-600 text-white shadow-glow transition group-hover:scale-105">
            <Shield className="h-5 w-5" />
          </span>
          <span className="text-[17px] tracking-tight">NCD Shield AI</span>
        </Link>
        <nav className="hidden items-center gap-8 text-sm font-medium text-ink-500 dark:text-ink-300 md:flex">
          <Link href="/#features" className="transition hover:text-ink-900 dark:hover:text-white">{t("nav.features")}</Link>
          <Link href="/#about" className="transition hover:text-ink-900 dark:hover:text-white">{t("nav.about")}</Link>
          <Link href="/#faq" className="transition hover:text-ink-900 dark:hover:text-white">{t("nav.faq")}</Link>
        </nav>
        <div className="flex items-center gap-2">
          <LanguageSwitcher />
          <ThemeToggle />
          <Link href="/login" className="btn-ghost hidden sm:inline-flex">
            {t("nav.login")}
          </Link>
          <Link href="/register" className="btn-primary">
            {t("nav.getStarted")}
          </Link>
        </div>
      </div>
    </header>
  );
}
