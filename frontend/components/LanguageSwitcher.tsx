"use client";

import { Languages } from "lucide-react";
import { useI18n } from "@/lib/i18n";

export function LanguageSwitcher() {
  const { locale, setLocale } = useI18n();
  return (
    <button
      onClick={() => setLocale(locale === "en" ? "ta" : "en")}
      className="inline-flex items-center gap-1.5 rounded-xl border border-ink-200 bg-white/60 px-3 py-2 text-sm font-medium text-ink-600 transition hover:bg-white hover:text-ink-900 dark:border-white/10 dark:bg-white/[0.02] dark:text-ink-300 dark:hover:bg-white/[0.06] dark:hover:text-white"
      aria-label="Switch language"
    >
      <Languages className="h-4 w-4" />
      {locale === "en" ? "தமிழ்" : "EN"}
    </button>
  );
}
