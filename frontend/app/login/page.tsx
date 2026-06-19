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
        <Link href="/" className="mb-6 flex items-center justify-center gap-2 font-bold">
          <Shield className="h-8 w-8 text-brand-600" />
          <span className="text-xl">NCD Shield AI</span>
        </Link>
        <h1 className="text-center text-2xl font-bold">Welcome back</h1>
        <p className="mt-1 text-center text-sm text-slate-500">Log in to your dashboard</p>

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

        <div className="mt-4 flex justify-between text-sm">
          <Link href="/forgot-password" className="text-brand-600 hover:underline">
            Forgot password?
          </Link>
          <Link href="/register" className="text-brand-600 hover:underline">
            Create account
          </Link>
        </div>
        <p className="mt-6 text-center text-xs text-slate-400">
          Demo admin: admin@ncdshield.ai / Admin@12345
        </p>
      </div>
    </div>
  );
}
