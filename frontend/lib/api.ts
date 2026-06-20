"use client";

// Absolute backend URL. Locally defaults to the FastAPI dev server; in
// production (e.g. Netlify) set NEXT_PUBLIC_API_URL to your deployed backend.
const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type AssessmentInput = {
  age: number;
  gender: "male" | "female";
  height_cm: number;
  weight_kg: number;
  systolic_bp: number;
  blood_sugar: number;
  cholesterol: number;
  smoking: boolean;
  alcohol: boolean;
  exercise_freq: number;
  sleep_hours: number;
  stress_level: "low" | "moderate" | "high";
  family_history: boolean;
  existing_diseases: string[];
};

export type PredictionResult = {
  id: number;
  risk_level: string;
  risk_class: number;
  risk_score: number;
  health_score: number;
  bmi: number;
  probabilities: Record<string, number>;
  explanation: { feature: string; label: string; importance: number; contribution: string }[];
  recommendations: { category: string; title: string; detail: string; priority: string }[];
  disclaimer: string;
  created_at: string;
};

function token() {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("ncd_token");
}

async function request<T>(path: string, opts: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(opts.headers as Record<string, string>),
  };
  const t = token();
  if (t) headers["Authorization"] = `Bearer ${t}`;

  const res = await fetch(`${BASE}${path}`, { ...opts, headers });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      detail = (await res.json()).detail || detail;
    } catch {}
    throw new Error(typeof detail === "string" ? detail : "Request failed");
  }
  return res.json();
}

export const api = {
  register: (full_name: string, email: string, password: string) =>
    request<{ access_token: string }>("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({ full_name, email, password }),
    }),

  login: async (email: string, password: string) => {
    const form = new URLSearchParams({ username: email, password });
    const res = await fetch(`${BASE}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: form,
    });
    if (!res.ok) throw new Error((await res.json()).detail || "Login failed");
    return res.json() as Promise<{ access_token: string }>;
  },

  forgotPassword: (email: string) =>
    request<{ message: string; reset_token?: string }>("/api/auth/forgot-password", {
      method: "POST",
      body: JSON.stringify({ email }),
    }),

  profile: () => request<any>("/api/profile"),

  predict: (input: AssessmentInput) =>
    request<PredictionResult>("/api/predict", {
      method: "POST",
      body: JSON.stringify(input),
    }),

  history: () => request<any[]>("/api/history"),

  chatbot: (message: string) =>
    request<{ reply: string; disclaimer: string; suggestions: string[] }>("/api/chatbot", {
      method: "POST",
      body: JSON.stringify({ message }),
    }),

  reportUrl: (id: number) => `${BASE}/api/report/${id}`,

  adminStats: () => request<any>("/api/admin/stats"),
};
