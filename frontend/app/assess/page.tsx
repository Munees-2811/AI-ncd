"use client";

import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import { Download, Sparkles } from "lucide-react";
import { DashboardShell } from "@/components/DashboardShell";
import { Chatbot } from "@/components/Chatbot";
import { RiskGauge } from "@/components/RiskGauge";
import { api, AssessmentInput, PredictionResult } from "@/lib/api";
import { riskColor } from "@/lib/utils";

const initial: AssessmentInput = {
  age: 35,
  gender: "male",
  height_cm: 170,
  weight_kg: 70,
  systolic_bp: 120,
  blood_sugar: 95,
  cholesterol: 180,
  smoking: false,
  alcohol: false,
  exercise_freq: 3,
  sleep_hours: 7,
  stress_level: "moderate",
  family_history: false,
  existing_diseases: [],
};

const diseaseOptions = ["Diabetes", "Hypertension", "Heart Disease", "Kidney Disease", "None"];

export default function AssessPage() {
  const [form, setForm] = useState<AssessmentInput>(initial);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const bmi = useMemo(
    () => (form.weight_kg / (form.height_cm / 100) ** 2).toFixed(1),
    [form.height_cm, form.weight_kg]
  );

  const set = (k: keyof AssessmentInput, v: any) => setForm((f) => ({ ...f, [k]: v }));

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await api.predict(form);
      setResult(res);
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardShell>
      <h1 className="text-2xl font-bold tracking-tight md:text-[1.9rem]">Health Assessment</h1>
      <p className="mt-1 text-sm text-ink-500">
        Fill in your details for an AI-powered NCD risk screening. BMI is calculated automatically.
      </p>

      {result && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass mt-6 p-6"
        >
          <div className="grid gap-6 md:grid-cols-2">
            <div>
              <RiskGauge score={result.risk_score} level={result.risk_level} />
              <div className="mt-2 flex justify-around text-center text-sm">
                <div>
                  <div className="font-bold">{result.health_score}</div>
                  <div className="text-xs text-ink-500">Health Score</div>
                </div>
                <div>
                  <div className="font-bold">{result.bmi}</div>
                  <div className="text-xs text-ink-500">BMI</div>
                </div>
                <div>
                  <div className={`font-bold ${riskColor(result.risk_level)}`}>
                    {result.risk_level}
                  </div>
                  <div className="text-xs text-ink-500">Risk</div>
                </div>
              </div>
            </div>
            <div>
              <h3 className="font-semibold">Why this result?</h3>
              <ul className="mt-3 space-y-2 text-sm">
                {result.explanation.slice(0, 5).map((e) => (
                  <li key={e.feature} className="flex items-center justify-between gap-2">
                    <span className="text-ink-600 dark:text-ink-200">{e.label}</span>
                    <span className="flex items-center gap-2">
                      <span className="h-1.5 w-20 overflow-hidden rounded-full bg-ink-200 dark:bg-white/10">
                        <span
                          className="block h-full rounded-full bg-brand-500"
                          style={{ width: `${Math.min(100, e.importance * 300)}%` }}
                        />
                      </span>
                      <span
                        className={
                          e.contribution === "increases"
                            ? "text-rose-500"
                            : e.contribution === "decreases"
                            ? "text-emerald-500"
                            : "text-ink-400"
                        }
                      >
                        {e.contribution === "increases" ? "↑" : e.contribution === "decreases" ? "↓" : "•"}
                      </span>
                    </span>
                  </li>
                ))}
              </ul>
              <a
                href={api.reportUrl(result.id)}
                className="btn-primary mt-4"
                target="_blank"
                rel="noreferrer"
              >
                <Download className="h-4 w-4" /> Download PDF Report
              </a>
            </div>
          </div>

          <h3 className="mt-6 font-semibold">Personalized recommendations</h3>
          <div className="mt-3 grid gap-3 sm:grid-cols-2">
            {result.recommendations.map((r, i) => (
              <div key={i} className="rounded-xl border border-ink-200/70 bg-white/40 p-3.5 transition hover:border-brand-300/50 dark:border-white/[0.06] dark:bg-white/[0.02]">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-sm font-semibold">{r.title}</span>
                  <span
                    className={`rounded-full px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide ${
                      r.priority === "high"
                        ? "bg-rose-100 text-rose-600 dark:bg-rose-500/15 dark:text-rose-300"
                        : r.priority === "medium"
                        ? "bg-amber-100 text-amber-600 dark:bg-amber-500/15 dark:text-amber-300"
                        : "bg-ink-100 text-ink-500 dark:bg-white/[0.06] dark:text-ink-300"
                    }`}
                  >
                    {r.priority}
                  </span>
                </div>
                <p className="mt-1.5 text-xs leading-relaxed text-ink-500">{r.detail}</p>
              </div>
            ))}
          </div>
          <p className="mt-5 text-xs text-ink-400">⚠️ {result.disclaimer}</p>
        </motion.div>
      )}

      {error && (
        <div className="mt-4 rounded-xl bg-red-50 px-4 py-2 text-sm text-red-600 dark:bg-red-900/20">
          {error}
        </div>
      )}

      <form onSubmit={submit} className="glass mt-6 grid gap-4 p-6 sm:grid-cols-2 lg:grid-cols-3">
        <div>
          <label className="label">Age</label>
          <input type="number" className="input" value={form.age}
            onChange={(e) => set("age", +e.target.value)} min={1} max={120} required />
        </div>
        <div>
          <label className="label">Gender</label>
          <select className="input" value={form.gender} onChange={(e) => set("gender", e.target.value)}>
            <option value="male">Male</option>
            <option value="female">Female</option>
          </select>
        </div>
        <div>
          <label className="label">BMI (auto)</label>
          <input className="input bg-ink-100/60 font-medium dark:bg-white/[0.04]" value={bmi} readOnly />
        </div>
        <div>
          <label className="label">Height (cm)</label>
          <input type="number" className="input" value={form.height_cm}
            onChange={(e) => set("height_cm", +e.target.value)} required />
        </div>
        <div>
          <label className="label">Weight (kg)</label>
          <input type="number" className="input" value={form.weight_kg}
            onChange={(e) => set("weight_kg", +e.target.value)} required />
        </div>
        <div>
          <label className="label">Systolic BP (mmHg)</label>
          <input type="number" className="input" value={form.systolic_bp}
            onChange={(e) => set("systolic_bp", +e.target.value)} required />
        </div>
        <div>
          <label className="label">Blood Sugar (mg/dL)</label>
          <input type="number" className="input" value={form.blood_sugar}
            onChange={(e) => set("blood_sugar", +e.target.value)} required />
        </div>
        <div>
          <label className="label">Cholesterol (mg/dL)</label>
          <input type="number" className="input" value={form.cholesterol}
            onChange={(e) => set("cholesterol", +e.target.value)} required />
        </div>
        <div>
          <label className="label">Exercise (days/week)</label>
          <input type="number" className="input" value={form.exercise_freq} min={0} max={7}
            onChange={(e) => set("exercise_freq", +e.target.value)} required />
        </div>
        <div>
          <label className="label">Sleep (hours)</label>
          <input type="number" step="0.5" className="input" value={form.sleep_hours}
            onChange={(e) => set("sleep_hours", +e.target.value)} required />
        </div>
        <div>
          <label className="label">Stress Level</label>
          <select className="input" value={form.stress_level}
            onChange={(e) => set("stress_level", e.target.value)}>
            <option value="low">Low</option>
            <option value="moderate">Moderate</option>
            <option value="high">High</option>
          </select>
        </div>
        <div>
          <label className="label">Existing Conditions</label>
          <select className="input" value={form.existing_diseases[0] ?? "None"}
            onChange={(e) => set("existing_diseases", e.target.value === "None" ? [] : [e.target.value])}>
            {diseaseOptions.map((d) => <option key={d} value={d}>{d}</option>)}
          </select>
        </div>

        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={form.smoking}
            onChange={(e) => set("smoking", e.target.checked)} /> Smoking
        </label>
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={form.alcohol}
            onChange={(e) => set("alcohol", e.target.checked)} /> Alcohol
        </label>
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={form.family_history}
            onChange={(e) => set("family_history", e.target.checked)} /> Family History
        </label>

        <div className="sm:col-span-2 lg:col-span-3">
          <button className="btn-primary w-full" disabled={loading}>
            <Sparkles className="h-4 w-4" />
            {loading ? "Analyzing…" : "Run AI Assessment"}
          </button>
        </div>
      </form>

      <Chatbot />
    </DashboardShell>
  );
}
