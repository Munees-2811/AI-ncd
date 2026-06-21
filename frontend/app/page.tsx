"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import {
  Activity,
  Brain,
  FileText,
  HeartPulse,
  Languages,
  Lock,
  MessageCircle,
  ShieldCheck,
  TrendingUp,
} from "lucide-react";
import { Navbar } from "@/components/Navbar";
import { useI18n } from "@/lib/i18n";

const features = [
  { icon: Brain, title: "Explainable AI", desc: "Multi-model ML engine with per-prediction feature-importance explanations." },
  { icon: HeartPulse, title: "4 NCDs Covered", desc: "Diabetes, Hypertension, Heart Disease, and Chronic Kidney Disease." },
  { icon: TrendingUp, title: "Risk Trends", desc: "Track your health score and risk trajectory over time with rich charts." },
  { icon: FileText, title: "PDF Reports", desc: "Download professional, shareable screening reports for your doctor." },
  { icon: MessageCircle, title: "Health Chatbot", desc: "Get general wellness guidance — it never diagnoses, always discloses." },
  { icon: Languages, title: "Multi-language", desc: "Available in English and Tamil with an instant language switcher." },
  { icon: Lock, title: "Secure by Design", desc: "JWT auth, hashed passwords, rate limiting, and input validation." },
  { icon: Activity, title: "Personalized Tips", desc: "Actionable, prioritized lifestyle recommendations tailored to you." },
];

const stats = [
  { value: "4", label: "NCDs Screened" },
  { value: "14", label: "Health Factors" },
  { value: "4", label: "ML Models Compared" },
  { value: "100%", label: "Free to Use" },
];

const faqs = [
  { q: "Is this a medical diagnosis?", a: "No. NCD Shield AI is strictly an early-screening and risk-prediction tool. Always consult a qualified physician for diagnosis and treatment." },
  { q: "How is my risk calculated?", a: "We train and compare Random Forest, XGBoost, Logistic Regression, and Decision Tree models, automatically selecting the best performer to estimate your risk." },
  { q: "Is my data safe?", a: "Your data is protected with JWT authentication, hashed passwords, and validated inputs. We never share your information." },
  { q: "What languages are supported?", a: "English and Tamil, with more planned. Switch instantly from the navigation bar." },
];

export default function Landing() {
  const { t } = useI18n();
  return (
    <div className="mesh min-h-screen">
      <Navbar />

      {/* Hero */}
      <section className="mx-auto max-w-7xl px-5 pb-24 pt-20 text-center md:pt-28">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <span className="badge">
            <span className="relative flex h-1.5 w-1.5">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-brand-500 opacity-75" />
              <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-brand-500" />
            </span>
            <ShieldCheck className="h-3.5 w-3.5 text-brand-500" /> AI-Powered Preventive Health
          </span>
          <h1 className="text-balance mx-auto mt-7 max-w-4xl text-[2.6rem] font-bold leading-[1.05] tracking-tightest text-gradient md:text-[4.2rem]">
            {t("hero.title")}
          </h1>
          <p className="text-balance mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-ink-500 dark:text-ink-300">
            {t("hero.subtitle")}
          </p>
          <div className="mt-9 flex flex-wrap justify-center gap-3">
            <Link href="/register" className="btn-primary px-6 py-3 text-base">{t("hero.cta")}</Link>
            <a href="#features" className="btn-ghost px-6 py-3 text-base">{t("hero.secondary")}</a>
          </div>
          <p className="mx-auto mt-8 max-w-xl text-xs text-ink-400">⚠️ {t("disclaimer")}</p>
        </motion.div>
      </section>

      {/* Stats */}
      <section className="mx-auto max-w-6xl px-5 pb-20">
        <div className="glass grid grid-cols-2 divide-x divide-y divide-ink-200/60 overflow-hidden p-0 dark:divide-white/[0.06] md:grid-cols-4 md:divide-y-0">
          {stats.map((s) => (
            <div key={s.label} className="p-8 text-center">
              <div className="font-display text-4xl font-bold tracking-tight text-brand-600 dark:text-brand-300">{s.value}</div>
              <div className="mt-2 text-sm text-ink-500">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section id="features" className="mx-auto max-w-7xl px-5 py-20">
        <div className="text-center">
          <span className="badge mb-4">Capabilities</span>
          <h2 className="text-balance text-3xl font-bold tracking-tight md:text-[2.6rem]">Everything you need to stay ahead</h2>
        </div>
        <div className="mt-14 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {features.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.05 }}
              className="glass card-hover p-6"
            >
              <span className="flex h-11 w-11 items-center justify-center rounded-xl border border-brand-200/70 bg-brand-50 text-brand-600 dark:border-brand-500/20 dark:bg-brand-500/10 dark:text-brand-300">
                <f.icon className="h-5 w-5" />
              </span>
              <h3 className="mt-5 text-[15px] font-semibold">{f.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-ink-500">{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* About */}
      <section id="about" className="mx-auto max-w-5xl px-5 py-20">
        <div className="glass relative overflow-hidden p-10 text-center md:p-14">
          <div className="pointer-events-none absolute -right-24 -top-24 h-64 w-64 rounded-full bg-brand-500/10 blur-3xl" />
          <span className="badge mb-4">Our mission</span>
          <h2 className="text-3xl font-bold tracking-tight">Preventive health, made intelligible</h2>
          <p className="text-balance mx-auto mt-5 max-w-3xl text-lg leading-relaxed text-ink-500 dark:text-ink-300">
            Non-Communicable Diseases account for a majority of deaths worldwide, yet many are
            preventable with early action. NCD Shield AI brings explainable machine learning to
            preventive health — turning everyday lifestyle data into clear, personalized risk
            insights so you can act early and talk to your doctor with confidence.
          </p>
        </div>
      </section>

      {/* FAQ */}
      <section id="faq" className="mx-auto max-w-3xl px-5 py-20">
        <h2 className="text-center text-3xl font-bold tracking-tight">Frequently asked questions</h2>
        <div className="mt-10 space-y-3">
          {faqs.map((f) => (
            <details key={f.q} className="glass group p-6 transition hover:border-brand-300/50">
              <summary className="flex cursor-pointer list-none items-center justify-between font-semibold marker:hidden">
                {f.q}
                <span className="ml-4 text-ink-400 transition group-open:rotate-45">+</span>
              </summary>
              <p className="mt-3 text-sm leading-relaxed text-ink-500">{f.a}</p>
            </details>
          ))}
        </div>
      </section>

      {/* Contact / Footer */}
      <footer id="contact" className="hairline border-t py-12 text-center text-sm text-ink-500">
        <div className="flex items-center justify-center gap-2">
          <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-brand-600 text-white">
            <ShieldCheck className="h-4 w-4" />
          </span>
          <p className="font-display font-semibold text-ink-900 dark:text-white">NCD Shield AI</p>
        </div>
        <p className="mt-3">Questions? contact@ncdshield.ai</p>
        <p className="mx-auto mt-4 max-w-xl text-xs text-ink-400">⚠️ {t("disclaimer")}</p>
        <p className="mt-4 text-xs text-ink-400">© {new Date().getFullYear()} NCD Shield AI · Built for hackathons & portfolios.</p>
      </footer>
    </div>
  );
}
