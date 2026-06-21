"use client";

import { RadialBar, RadialBarChart, PolarAngleAxis, ResponsiveContainer } from "recharts";

export function RiskGauge({ score, level }: { score: number; level: string }) {
  const color = level.startsWith("Low")
    ? "#059669"
    : level.startsWith("Moderate")
    ? "#f59e0b"
    : "#f43f5e";

  return (
    <div className="relative h-48 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <RadialBarChart
          innerRadius="72%"
          outerRadius="100%"
          data={[{ value: score, fill: color }]}
          startAngle={210}
          endAngle={-30}
        >
          <PolarAngleAxis type="number" domain={[0, 100]} tick={false} />
          <RadialBar background={{ fill: "rgba(120,120,140,0.12)" }} dataKey="value" cornerRadius={20} />
        </RadialBarChart>
      </ResponsiveContainer>
      <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-display text-[2.6rem] font-bold tracking-tight" style={{ color }}>{score}%</span>
        <span className="text-sm font-medium text-ink-500">{level}</span>
      </div>
    </div>
  );
}
