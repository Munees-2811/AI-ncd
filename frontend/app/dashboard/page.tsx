"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Activity, ClipboardPlus, FileText, HeartPulse } from "lucide-react";
import { DashboardShell } from "@/components/DashboardShell";
import { Chatbot } from "@/components/Chatbot";
import { api } from "@/lib/api";
import { riskColor } from "@/lib/utils";

const RISK_PALETTE: Record<string, string> = {
  "Low Risk": "#059669",
  "Moderate Risk": "#f59e0b",
  "High Risk": "#f43f5e",
};

export default function DashboardPage() {
  const [profile, setProfile] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.profile(), api.history()])
      .then(([p, h]) => {
        setProfile(p);
        setHistory(h);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const trend = [...history]
    .reverse()
    .map((h, i) => ({
      name: `#${i + 1}`,
      health: h.health_score,
      risk: h.risk_score,
    }));

  const distribution = Object.entries(
    history.reduce((acc: Record<string, number>, h) => {
      acc[h.risk_level] = (acc[h.risk_level] || 0) + 1;
      return acc;
    }, {})
  ).map(([name, value]) => ({ name, value }));

  const bmiData = [...history].reverse().map((h, i) => ({ name: `#${i + 1}`, bmi: h.bmi }));
  const latest = history[0];

  return (
    <DashboardShell>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight md:text-[1.9rem]">
            Welcome{profile?.user ? `, ${profile.user.full_name.split(" ")[0]}` : ""} 👋
          </h1>
          <p className="mt-1 text-sm text-ink-500">Your health overview at a glance.</p>
        </div>
        <Link href="/assess" className="btn-primary">
          <ClipboardPlus className="h-4 w-4" /> New Assessment
        </Link>
      </div>

      {loading ? (
        <p className="mt-10 text-ink-500">Loading…</p>
      ) : history.length === 0 ? (
        <div className="glass mt-8 p-12 text-center">
          <span className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl border border-brand-200/70 bg-brand-50 text-brand-600 dark:border-brand-500/20 dark:bg-brand-500/10 dark:text-brand-300">
            <HeartPulse className="h-7 w-7" />
          </span>
          <h2 className="mt-5 text-xl font-semibold">No assessments yet</h2>
          <p className="mt-2 text-sm text-ink-500">
            Run your first AI health assessment to see your risk insights here.
          </p>
          <Link href="/assess" className="btn-primary mt-6">Start Assessment</Link>
        </div>
      ) : (
        <>
          {/* Summary cards */}
          <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <SummaryCard icon={Activity} label="Health Score"
              value={`${latest.health_score}`} sub="/ 100" />
            <SummaryCard icon={HeartPulse} label="Latest Risk"
              value={latest.risk_level} valueClass={riskColor(latest.risk_level)} />
            <SummaryCard icon={Activity} label="Current BMI" value={`${latest.bmi}`} />
            <SummaryCard icon={FileText} label="Assessments"
              value={`${profile?.total_predictions ?? history.length}`} />
          </div>

          {/* Charts */}
          <div className="mt-6 grid gap-6 lg:grid-cols-2">
            <div className="glass p-6">
              <h3 className="mb-4 font-semibold">Risk & Health Trend</h3>
              <ResponsiveContainer width="100%" height={240}>
                <AreaChart data={trend}>
                  <defs>
                    <linearGradient id="g1" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#6c5cf0" stopOpacity={0.55} />
                      <stop offset="95%" stopColor="#6c5cf0" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="g2" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.45} />
                      <stop offset="95%" stopColor="#f43f5e" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                  <XAxis dataKey="name" fontSize={12} stroke="#9494a6" />
                  <YAxis domain={[0, 100]} fontSize={12} stroke="#9494a6" />
                  <Tooltip contentStyle={{ borderRadius: 12, border: "1px solid rgba(120,120,140,0.2)", fontSize: 12 }} />
                  <Area type="monotone" dataKey="health" stroke="#6c5cf0" strokeWidth={2} fill="url(#g1)" />
                  <Area type="monotone" dataKey="risk" stroke="#f43f5e" strokeWidth={2} fill="url(#g2)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            <div className="glass p-6">
              <h3 className="mb-4 font-semibold">Risk Distribution</h3>
              <ResponsiveContainer width="100%" height={240}>
                <PieChart>
                  <Pie data={distribution} dataKey="value" nameKey="name" innerRadius={55}
                    outerRadius={90} paddingAngle={3}>
                    {distribution.map((d) => (
                      <Cell key={d.name} fill={RISK_PALETTE[d.name] || "#64748b"} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="glass p-6 lg:col-span-2">
              <h3 className="mb-4 font-semibold">BMI History</h3>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={bmiData}>
                  <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                  <XAxis dataKey="name" fontSize={12} stroke="#9494a6" />
                  <YAxis fontSize={12} stroke="#9494a6" />
                  <Tooltip contentStyle={{ borderRadius: 12, border: "1px solid rgba(120,120,140,0.2)", fontSize: 12 }} cursor={{ fill: "rgba(108,92,240,0.06)" }} />
                  <Bar dataKey="bmi" fill="#6c5cf0" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Previous predictions */}
          <div className="glass mt-6 p-6">
            <h3 className="mb-4 font-semibold">Previous Assessments</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="text-left text-xs uppercase tracking-wide text-ink-400">
                  <tr>
                    <th className="pb-3 font-medium">Date</th>
                    <th className="font-medium">Risk</th>
                    <th className="font-medium">Score</th>
                    <th className="font-medium">Health</th>
                    <th className="font-medium">BMI</th>
                    <th className="font-medium">Report</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((h) => (
                    <tr key={h.id} className="hairline border-t transition hover:bg-ink-100/40 dark:hover:bg-white/[0.02]">
                      <td className="py-3 text-ink-600 dark:text-ink-300">{new Date(h.created_at).toLocaleDateString()}</td>
                      <td className={`font-medium ${riskColor(h.risk_level)}`}>{h.risk_level}</td>
                      <td className="tabular-nums">{h.risk_score}%</td>
                      <td className="tabular-nums">{h.health_score}</td>
                      <td className="tabular-nums">{h.bmi}</td>
                      <td>
                        <a className="font-medium text-brand-600 hover:underline dark:text-brand-300" target="_blank"
                          rel="noreferrer" href={api.reportUrl(h.id)}>
                          PDF
                        </a>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      <Chatbot />
    </DashboardShell>
  );
}

function SummaryCard({ icon: Icon, label, value, sub, valueClass }: any) {
  return (
    <div className="glass card-hover p-5">
      <div className="flex items-center justify-between">
        <span className="text-[13px] font-medium text-ink-500">{label}</span>
        <span className="flex h-8 w-8 items-center justify-center rounded-lg border border-brand-200/60 bg-brand-50 text-brand-600 dark:border-brand-500/20 dark:bg-brand-500/10 dark:text-brand-300">
          <Icon className="h-4 w-4" />
        </span>
      </div>
      <div className={`mt-3 font-display text-2xl font-bold tracking-tight ${valueClass || ""}`}>
        {value}
        {sub && <span className="text-sm font-normal text-ink-400"> {sub}</span>}
      </div>
    </div>
  );
}
