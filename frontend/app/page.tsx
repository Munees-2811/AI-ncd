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
      <section className="mx-auto max-w-7xl px-4 pb-20 pt-16 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <span className="inline-flex items-center gap-2 rounded-full border border-brand-200 bg-brand-50 px-4 py-1.5 text-sm font-medium text-brand-700 dark:border-brand-700 dark:bg-brand-900/30 dark:text-brand-100">
            <ShieldCheck className="h-4 w-4" /> AI-Powered Preventive Health
          </span>
          <h1 className="mx-auto mt-6 max-w-4xl text-4xl font-extrabold leading-tight md:text-6xl">
            {t("hero.title")}
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-600 dark:text-slate-300">
            {t("hero.subtitle")}
          </p>
          <div className="mt-8 flex flex-wrap justify-center gap-4">
            <Link href="/register" className="btn-primary text-lg">{t("hero.cta")}</Link>
            <a href="#features" className="btn-ghost text-lg">{t("hero.secondary")}</a>
          </div>
          <p className="mx-auto mt-6 max-w-xl text-xs text-slate-500">⚠️ {t("disclaimer")}</p>
        </motion.div>
      </section>

      {/* Stats */}
      <section className="mx-auto max-w-7xl px-4 pb-16">
        <div className="glass grid grid-cols-2 gap-6 p-8 md:grid-cols-4">
          {stats.map((s) => (
            <div key={s.label} className="text-center">
              <div className="text-4xl font-extrabold text-brand-600">{s.value}</div>
              <div className="mt-1 text-sm text-slate-500">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section id="features" className="mx-auto max-w-7xl px-4 py-16">
        <h2 className="text-center text-3xl font-bold md:text-4xl">Everything you need to stay ahead</h2>
        <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {features.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.05 }}
              className="glass p-6"
            >
              <f.icon className="h-10 w-10 text-brand-600" />
              <h3 className="mt-4 text-lg font-semibold">{f.title}</h3>
              <p className="mt-2 text-sm text-slate-500">{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* About */}
      <section id="about" className="mx-auto max-w-5xl px-4 py-16">
        <div className="glass p-10 text-center">
          <h2 className="text-3xl font-bold">About the project</h2>
          <p className="mx-auto mt-4 max-w-3xl text-slate-600 dark:text-slate-300">
            Non-Communicable Diseases account for a majority of deaths worldwide, yet many are
            preventable with early action. NCD Shield AI brings explainable machine learning to
            preventive health — turning everyday lifestyle data into clear, personalized risk
            insights so you can act early and talk to your doctor with confidence.
          </p>
        </div>
      </section>

      {/* FAQ */}
      <section id="faq" className="mx-auto max-w-4xl px-4 py-16">
        <h2 className="text-center text-3xl font-bold">Frequently asked questions</h2>
        <div className="mt-10 space-y-4">
          {faqs.map((f) => (
            <details key={f.q} className="glass group p-6">
              <summary className="cursor-pointer list-none font-semibold marker:hidden">
                {f.q}
              </summary>
              <p className="mt-3 text-sm text-slate-500">{f.a}</p>
            </details>
          ))}
        </div>
      </section>

      {/* Contact / Footer */}
      <footer id="contact" className="border-t border-white/20 py-10 text-center text-sm text-slate-500">
        <p className="font-semibold text-brand-600">NCD Shield AI</p>
        <p className="mt-2">Questions? contact@ncdshield.ai</p>
        <p className="mx-auto mt-4 max-w-xl text-xs">⚠️ {t("disclaimer")}</p>
        <p className="mt-4">© {new Date().getFullYear()} NCD Shield AI · Built for hackathons & portfolios.</p>
      </footer>
    </div>
  );
}
