"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Shield } from "lucide-react";
import { api } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const { access_token } = await api.login(email, password);
      localStorage.setItem("ncd_token", access_token);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mesh flex min-h-screen items-center justify-center px-4">
      <div className="glass w-full max-w-md p-8">
        <Link href="/" className="mb-6 flex items-center justify-center gap-2.5 font-semibold">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-600 text-white shadow-glow">
            <Shield className="h-5 w-5" />
          </span>
          <span className="text-xl tracking-tight">NCD Shield AI</span>
        </Link>
        <h1 className="text-center text-2xl font-bold tracking-tight">Welcome back</h1>
        <p className="mt-1.5 text-center text-sm text-ink-500">Log in to your dashboard</p>

        {error && (
          <div className="mt-4 rounded-xl bg-red-50 px-4 py-2 text-sm text-red-600 dark:bg-red-900/20">
            {error}
          </div>
        )}

        <form onSubmit={submit} className="mt-6 space-y-4">
          <div>
            <label className="label">Email</label>
            <input className="input" type="email" required value={email}
              onChange={(e) => setEmail(e.target.value)} />
          </div>
          <div>
            <label className="label">Password</label>
            <input className="input" type="password" required value={password}
              onChange={(e) => setPassword(e.target.value)} />
          </div>
          <button className="btn-primary w-full" disabled={loading}>
            {loading ? "Logging in…" : "Login"}
          </button>
        </form>

        <div className="mt-5 flex justify-between text-sm">
          <Link href="/forgot-password" className="font-medium text-brand-600 hover:underline dark:text-brand-300">
            Forgot password?
          </Link>
          <Link href="/register" className="font-medium text-brand-600 hover:underline dark:text-brand-300">
            Create account
          </Link>
        </div>
        <p className="mt-6 rounded-lg border border-ink-200/70 bg-ink-100/40 px-3 py-2 text-center text-xs text-ink-400 dark:border-white/[0.06] dark:bg-white/[0.02]">
          Demo admin: admin@ncdshield.ai / Admin@12345
        </p>
      </div>
    </div>
  );
}
