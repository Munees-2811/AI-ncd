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
        <Link href="/" className="mb-6 flex items-center justify-center gap-2 font-bold">
          <Shield className="h-8 w-8 text-brand-600" />
          <span className="text-xl">NCD Shield AI</span>
        </Link>
        <h1 className="text-center text-2xl font-bold">Reset your password</h1>
        <p className="mt-1 text-center text-sm text-slate-500">
          Enter your email and we&apos;ll send reset instructions.
        </p>

        {message && (
          <div className="mt-4 break-words rounded-xl bg-brand-50 px-4 py-2 text-sm text-brand-700 dark:bg-brand-900/20">
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

        <p className="mt-4 text-center text-sm">
          <Link href="/login" className="text-brand-600 hover:underline">Back to login</Link>
        </p>
      </div>
    </div>
  );
}
