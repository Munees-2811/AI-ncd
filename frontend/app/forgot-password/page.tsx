"use client";

import Link from "next/link";
import { useState } from "react";
import { Shield } from "lucide-react";
import { api } from "@/lib/api";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await api.forgotPassword(email);
      setMessage(res.message + (res.reset_token ? ` (demo token: ${res.reset_token})` : ""));
    } catch (err: any) {
      setMessage(err.message);
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
        <h1 className="text-center text-2xl font-bold tracking-tight">Reset your password</h1>
        <p className="mt-1.5 text-center text-sm text-ink-500">
          Enter your email and we&apos;ll send reset instructions.
        </p>

        {message && (
          <div className="mt-4 break-words rounded-xl border border-brand-200/60 bg-brand-50 px-4 py-2.5 text-sm text-brand-700 dark:border-brand-500/20 dark:bg-brand-500/10 dark:text-brand-200">
            {message}
          </div>
        )}

        <form onSubmit={submit} className="mt-6 space-y-4">
          <div>
            <label className="label">Email</label>
            <input className="input" type="email" required value={email}
              onChange={(e) => setEmail(e.target.value)} />
          </div>
          <button className="btn-primary w-full" disabled={loading}>
            {loading ? "Sending…" : "Send reset link"}
          </button>
        </form>

        <p className="mt-5 text-center text-sm text-ink-500">
          <Link href="/login" className="font-medium text-brand-600 hover:underline dark:text-brand-300">Back to login</Link>
        </p>
      </div>
    </div>
  );
}
