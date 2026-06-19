import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function riskColor(level: string) {
  if (level.startsWith("Low")) return "text-emerald-500";
  if (level.startsWith("Moderate")) return "text-amber-500";
  return "text-red-500";
}

export function riskBg(level: string) {
  if (level.startsWith("Low")) return "bg-emerald-500";
  if (level.startsWith("Moderate")) return "bg-amber-500";
  return "bg-red-500";
}
