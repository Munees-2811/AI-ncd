"use client";

import Link from "next/link";
import { Shield } from "lucide-react";
import { useI18n } from "@/lib/i18n";
import { ThemeToggle } from "./ThemeToggle";
import { LanguageSwitcher } from "./LanguageSwitcher";

export function Navbar() {
  const { t } = useI18n();
  return (
    <header className="sticky top-0 z-40 border-b border-white/30 bg-white/60 backdrop-blur-xl dark:border-white/10 dark:bg-slate-950/60">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
        <Link href="/" className="flex items-center gap-2 font-bold">
          <Shield className="h-7 w-7 text-brand-600" />
          <span className="text-lg">NCD Shield AI</span>
        </Link>
        <nav className="hidden items-center gap-6 text-sm font-medium md:flex">
          <Link href="/#features" className="hover:text-brand-600">{t("nav.features")}</Link>
          <Link href="/#about" className="hover:text-brand-600">{t("nav.about")}</Link>
          <Link href="/#faq" className="hover:text-brand-600">{t("nav.faq")}</Link>
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
