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
      <h1 className="text-2xl font-bold md:text-3xl">Admin Panel</h1>
      <p className="mt-1 text-sm text-slate-500">System analytics & model performance.</p>

      {error && (
        <div className="mt-6 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-600 dark:bg-red-900/20">
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
                  <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                  <XAxis dataKey="name" fontSize={12} />
                  <YAxis fontSize={12} allowDecimals={false} />
                  <Tooltip />
                  <Bar dataKey="value" fill="#0d9488" radius={[6, 6, 0, 0]} />
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
    <div className="glass p-5">
      <div className="flex items-center justify-between">
        <span className="text-sm text-slate-500">{label}</span>
        <Icon className="h-5 w-5 text-brand-600" />
      </div>
      <div className="mt-2 text-2xl font-extrabold capitalize">{value}</div>
    </div>
  );
}

function Row({ label, value }: { label: string; value: any }) {
  return (
    <div className="flex justify-between border-b border-slate-200 pb-2 dark:border-slate-700">
      <dt className="text-slate-500">{label}</dt>
      <dd className="font-semibold capitalize">{String(value)}</dd>
    </div>
  );
}
