"use client";

import { useEffect, useState } from "react";
import { I18nContext, Locale, translations } from "@/lib/i18n";

export function Providers({ children }: { children: React.ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>("en");

  useEffect(() => {
    const stored = (localStorage.getItem("ncd_locale") as Locale) || "en";
    setLocaleState(stored);
    const theme = localStorage.getItem("ncd_theme");
    if (theme === "dark" || (!theme && window.matchMedia("(prefers-color-scheme: dark)").matches)) {
      document.documentElement.classList.add("dark");
    }
  }, []);

  const setLocale = (l: Locale) => {
    setLocaleState(l);
    localStorage.setItem("ncd_locale", l);
  };

  const t = (key: string) => translations[locale][key] ?? translations.en[key] ?? key;

  return (
    <I18nContext.Provider value={{ locale, setLocale, t }}>{children}</I18nContext.Provider>
  );
}
