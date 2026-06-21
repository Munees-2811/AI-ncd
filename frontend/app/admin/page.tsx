"use client";

import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Activity, Brain, Users } from "lucide-react";
import { DashboardShell } from "@/components/DashboardShell";
import { api } from "@/lib/api";

export default function AdminPage() {
  const [stats, setStats] = useState<any>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.adminStats().then(setStats).catch((e) => setError(e.message));
  }, []);

  const dist = stats
    ? Object.entries(stats.risk_distribution).map(([name, value]) => ({ name, value }))
    : [];

  return (
    <DashboardShell>
      <h1 className="text-2xl font-bold tracking-tight md:text-[1.9rem]">Admin Panel</h1>
      <p className="mt-1 text-sm text-ink-500">System analytics & model performance.</p>

      {error && (
        <div className="mt-6 rounded-xl border border-rose-200/60 bg-rose-50 px-4 py-3 text-sm text-rose-600 dark:border-rose-500/20 dark:bg-rose-500/10 dark:text-rose-300">
          {error} — admin access required. Log in with the admin account.
        </div>
      )}

      {stats && (
        <>
          <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <Card icon={Users} label="Total Users" value={stats.total_users} />
            <Card icon={Activity} label="Total Predictions" value={stats.total_predictions} />
            <Card icon={Brain} label="Best Model" value={stats.model_name} />
            <Card
              icon={Brain}
              label="Model Accuracy"
              value={stats.model_accuracy != null ? `${(stats.model_accuracy * 100).toFixed(1)}%` : "—"}
            />
          </div>

          <div className="mt-6 grid gap-6 lg:grid-cols-2">
            <div className="glass p-6">
              <h3 className="mb-4 font-semibold">Risk Distribution</h3>
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={dist}>
                  <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                  <XAxis dataKey="name" fontSize={12} stroke="#9494a6" />
                  <YAxis fontSize={12} allowDecimals={false} stroke="#9494a6" />
                  <Tooltip contentStyle={{ borderRadius: 12, border: "1px solid rgba(120,120,140,0.2)", fontSize: 12 }} cursor={{ fill: "rgba(108,92,240,0.06)" }} />
                  <Bar dataKey="value" fill="#6c5cf0" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="glass p-6">
              <h3 className="mb-4 font-semibold">Model & System</h3>
              <dl className="space-y-3 text-sm">
                <Row label="Selected Model" value={stats.model_name} />
                <Row label="Weighted F1" value={stats.model_f1 ?? "—"} />
                <Row label="Avg Health Score" value={stats.avg_health_score ?? "—"} />
                <Row label="Total Users" value={stats.total_users} />
                <Row label="Total Predictions" value={stats.total_predictions} />
              </dl>
            </div>
          </div>
        </>
      )}
    </DashboardShell>
  );
}

function Card({ icon: Icon, label, value }: any) {
  return (
    <div className="glass card-hover p-5">
      <div className="flex items-center justify-between">
        <span className="text-[13px] font-medium text-ink-500">{label}</span>
        <span className="flex h-8 w-8 items-center justify-center rounded-lg border border-brand-200/60 bg-brand-50 text-brand-600 dark:border-brand-500/20 dark:bg-brand-500/10 dark:text-brand-300">
          <Icon className="h-4 w-4" />
        </span>
      </div>
      <div className="mt-3 font-display text-2xl font-bold capitalize tracking-tight">{value}</div>
    </div>
  );
}

function Row({ label, value }: { label: string; value: any }) {
  return (
    <div className="hairline flex justify-between border-b pb-2.5 last:border-0">
      <dt className="text-ink-500">{label}</dt>
      <dd className="font-semibold capitalize tabular-nums">{String(value)}</dd>
    </div>
  );
}
