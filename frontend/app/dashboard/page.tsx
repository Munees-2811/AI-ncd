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
  "Low Risk": "#16a34a",
  "Moderate Risk": "#d97706",
  "High Risk": "#dc2626",
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
          <h1 className="text-2xl font-bold md:text-3xl">
            Welcome{profile?.user ? `, ${profile.user.full_name.split(" ")[0]}` : ""} 👋
          </h1>
          <p className="mt-1 text-sm text-slate-500">Your health overview at a glance.</p>
        </div>
        <Link href="/assess" className="btn-primary">
          <ClipboardPlus className="h-4 w-4" /> New Assessment
        </Link>
      </div>

      {loading ? (
        <p className="mt-10 text-slate-500">Loading…</p>
      ) : history.length === 0 ? (
        <div className="glass mt-8 p-10 text-center">
          <HeartPulse className="mx-auto h-12 w-12 text-brand-600" />
          <h2 className="mt-4 text-xl font-semibold">No assessments yet</h2>
          <p className="mt-2 text-sm text-slate-500">
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
                      <stop offset="5%" stopColor="#14b8a6" stopOpacity={0.6} />
                      <stop offset="95%" stopColor="#14b8a6" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="g2" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#dc2626" stopOpacity={0.5} />
                      <stop offset="95%" stopColor="#dc2626" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                  <XAxis dataKey="name" fontSize={12} />
                  <YAxis domain={[0, 100]} fontSize={12} />
                  <Tooltip />
                  <Area type="monotone" dataKey="health" stroke="#14b8a6" fill="url(#g1)" />
                  <Area type="monotone" dataKey="risk" stroke="#dc2626" fill="url(#g2)" />
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
                  <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                  <XAxis dataKey="name" fontSize={12} />
                  <YAxis fontSize={12} />
                  <Tooltip />
                  <Bar dataKey="bmi" fill="#0d9488" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Previous predictions */}
          <div className="glass mt-6 p-6">
            <h3 className="mb-4 font-semibold">Previous Assessments</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="text-left text-slate-500">
                  <tr>
                    <th className="py-2">Date</th>
                    <th>Risk</th>
                    <th>Score</th>
                    <th>Health</th>
                    <th>BMI</th>
                    <th>Report</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((h) => (
                    <tr key={h.id} className="border-t border-slate-200 dark:border-slate-700">
                      <td className="py-2">{new Date(h.created_at).toLocaleDateString()}</td>
                      <td className={riskColor(h.risk_level)}>{h.risk_level}</td>
                      <td>{h.risk_score}%</td>
                      <td>{h.health_score}</td>
                      <td>{h.bmi}</td>
                      <td>
                        <a className="text-brand-600 hover:underline" target="_blank"
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
    <div className="glass p-5">
      <div className="flex items-center justify-between">
        <span className="text-sm text-slate-500">{label}</span>
        <Icon className="h-5 w-5 text-brand-600" />
      </div>
      <div className={`mt-2 text-2xl font-extrabold ${valueClass || ""}`}>
        {value}
        {sub && <span className="text-sm font-normal text-slate-400"> {sub}</span>}
      </div>
    </div>
  );
}
