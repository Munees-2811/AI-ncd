"use client";

import { RadialBar, RadialBarChart, PolarAngleAxis, ResponsiveContainer } from "recharts";

export function RiskGauge({ score, level }: { score: number; level: string }) {
  const color = level.startsWith("Low")
    ? "#16a34a"
    : level.startsWith("Moderate")
    ? "#d97706"
    : "#dc2626";

  return (
    <div className="relative h-48 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <RadialBarChart
          innerRadius="70%"
          outerRadius="100%"
          data={[{ value: score, fill: color }]}
          startAngle={210}
          endAngle={-30}
        >
          <PolarAngleAxis type="number" domain={[0, 100]} tick={false} />
          <RadialBar background dataKey="value" cornerRadius={20} />
        </RadialBarChart>
      </ResponsiveContainer>
      <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-4xl font-extrabold" style={{ color }}>{score}%</span>
        <span className="text-sm font-medium text-slate-500">{level}</span>
      </div>
    </div>
  );
}
