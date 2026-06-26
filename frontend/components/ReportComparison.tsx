"use client";

import { ArrowDownRight, ArrowUpRight, Minus, TrendingDown, TrendingUp } from "lucide-react";

type Metric = {
  key: string;
  label: string;
  unit: string;
  current: number;
  previous: number;
  delta: number;
  direction: "up" | "down" | "same";
  better: boolean | null;
};

type Comparison = {
  available: boolean;
  verdict?: "improved" | "declined" | "unchanged";
  summary?: string;
  improved_count?: number;
  worsened_count?: number;
  current?: { created_at?: string; risk_level?: string };
  previous?: { created_at?: string; risk_level?: string };
  metrics?: Metric[];
};

const VERDICT = {
  improved: { label: "Improved", cls: "text-emerald-600 dark:text-emerald-400", Icon: TrendingUp },
  declined: { label: "Declined", cls: "text-rose-600 dark:text-rose-400", Icon: TrendingDown },
  unchanged: { label: "Unchanged", cls: "text-ink-500", Icon: Minus },
};

function fmtDate(s?: string) {
  if (!s) return "—";
  try {
    return new Date(s).toLocaleDateString();
  } catch {
    return "—";
  }
}

export function ReportComparison({ data }: { data: Comparison | null }) {
  if (!data || !data.available || !data.metrics) return null;

  const v = VERDICT[data.verdict || "unchanged"];

  return (
    <div className="glass mt-6 p-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 className="font-semibold">Report Comparison</h3>
          <p className="mt-1 text-sm text-ink-500">
            Latest ({fmtDate(data.current?.created_at)}) vs previous ({fmtDate(data.previous?.created_at)})
          </p>
        </div>
        <span className={`inline-flex items-center gap-1.5 rounded-full border border-ink-200/70 bg-white/60 px-3 py-1 text-sm font-semibold dark:border-white/10 dark:bg-white/[0.04] ${v.cls}`}>
          <v.Icon className="h-4 w-4" />
          {v.label}
        </span>
      </div>

      {data.summary && (
        <p className="mt-4 rounded-xl border border-ink-200/60 bg-ink-100/40 px-4 py-3 text-sm text-ink-600 dark:border-white/[0.06] dark:bg-white/[0.02] dark:text-ink-200">
          {data.summary}
          {typeof data.improved_count === "number" && (
            <span className="ml-1 text-ink-400">
              ({data.improved_count} improved · {data.worsened_count} worsened)
            </span>
          )}
        </p>
      )}

      <div className="mt-4 grid gap-2.5 sm:grid-cols-2 lg:grid-cols-3">
        {data.metrics.map((m) => {
          const tone =
            m.better === true
              ? "text-emerald-600 dark:text-emerald-400"
              : m.better === false
              ? "text-rose-600 dark:text-rose-400"
              : "text-ink-400";
          const Arrow =
            m.direction === "up" ? ArrowUpRight : m.direction === "down" ? ArrowDownRight : Minus;
          return (
            <div
              key={m.key}
              className="rounded-xl border border-ink-200/70 bg-white/40 p-3 dark:border-white/[0.06] dark:bg-white/[0.02]"
            >
              <div className="flex items-center justify-between">
                <span className="text-[13px] font-medium text-ink-500">{m.label}</span>
                <span className={`inline-flex items-center gap-0.5 text-xs font-semibold ${tone}`}>
                  <Arrow className="h-3.5 w-3.5" />
                  {m.delta > 0 ? "+" : ""}
                  {m.delta}
                  {m.unit && <span className="ml-0.5 font-normal text-ink-400">{m.unit}</span>}
                </span>
              </div>
              <div className="mt-1.5 flex items-baseline gap-2">
                <span className="font-display text-lg font-bold tracking-tight tabular-nums">
                  {m.current}
                </span>
                <span className="text-xs text-ink-400">from {m.previous}{m.unit}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
