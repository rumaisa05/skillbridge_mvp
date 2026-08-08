"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api, setAuth } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const { data } = await api.post("/api/auth/login", form);
      setAuth(data.access_token, data.user);
      router.push("/challenges");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-md border border-slate-200 p-8">
        <div className="flex items-center gap-2 mb-6 justify-center">
          <div className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center text-white font-bold">S</div>
          <span className="font-bold text-xl">Skill<span className="text-brand-600">Bridge</span></span>
        </div>
        <h1 className="text-2xl font-bold text-center mb-6">Welcome back</h1>
        {error && <div className="bg-red-50 text-red-600 text-sm p-3 rounded-lg mb-4">{error}</div>}
        <form onSubmit={submit} className="space-y-4">
          <input type="email" placeholder="Email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })}
            className="w-full border border-slate-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500" />
          <input type="password" placeholder="Password" required value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })}
            className="w-full border border-slate-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500" />
          <button disabled={loading} className="w-full bg-brand-600 text-white py-2.5 rounded-lg font-medium hover:bg-brand-700 disabled:opacity-50">
            {loading ? "Signing in..." : "Login"}
          </button>
        </form>
        <p className="text-sm text-center text-slate-500 mt-4">
          Don&apos;t have an account?{" "}
          <Link href="/register" className="text-brand-600 font-medium">Register</Link>
        </p>
        <div className="mt-4 bg-slate-50 rounded-lg p-3 text-xs text-slate-500">
          <p className="font-medium mb-1">Demo organization:</p>
          <p>ngo@skillbridge.test / password123</p>
        </div>
      </div>
    </div>
  );
}
