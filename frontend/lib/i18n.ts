"use client";

import { createContext, useContext } from "react";

export type Locale = "en" | "ta";

export const translations: Record<Locale, Record<string, string>> = {
  en: {
    "nav.features": "Features",
    "nav.about": "About",
    "nav.faq": "FAQ",
    "nav.login": "Login",
    "nav.getStarted": "Get Started",
    "hero.title": "AI-Powered Early Screening for Non-Communicable Diseases",
    "hero.subtitle":
      "Estimate your risk of Diabetes, Hypertension, Heart Disease, and Chronic Kidney Disease — with personalized, explainable guidance.",
    "hero.cta": "Start Free Assessment",
    "hero.secondary": "Learn More",
    "disclaimer":
      "NCD Shield AI is an early screening and risk-prediction system — NOT a medical diagnosis tool.",
    "assess.title": "Health Assessment",
    "dashboard.title": "Your Health Dashboard",
  },
  ta: {
    "nav.features": "அம்சங்கள்",
    "nav.about": "பற்றி",
    "nav.faq": "கேள்விகள்",
    "nav.login": "உள்நுழை",
    "nav.getStarted": "தொடங்கு",
    "hero.title": "தொற்றா நோய்களுக்கான AI அடிப்படையிலான ஆரம்ப பரிசோதனை",
    "hero.subtitle":
      "நீரிழிவு, உயர் இரத்த அழுத்தம், இதய நோய் மற்றும் சிறுநீரக நோய் ஆபத்தை மதிப்பிடுங்கள் — தனிப்பயன் வழிகாட்டுதலுடன்.",
    "hero.cta": "இலவச மதிப்பீட்டைத் தொடங்கு",
    "hero.secondary": "மேலும் அறிக",
    "disclaimer":
      "NCD Shield AI ஒரு ஆரம்ப பரிசோதனை அமைப்பு — இது மருத்துவ நோயறிதல் கருவி அல்ல.",
    "assess.title": "சுகாதார மதிப்பீடு",
    "dashboard.title": "உங்கள் சுகாதார டாஷ்போர்டு",
  },
};

export const I18nContext = createContext<{
  locale: Locale;
  setLocale: (l: Locale) => void;
  t: (key: string) => string;
}>({ locale: "en", setLocale: () => {}, t: (k) => k });

export const useI18n = () => useContext(I18nContext);
