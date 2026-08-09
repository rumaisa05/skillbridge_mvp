"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api, setAuth } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState({ name: "", email: "", password: "", role: "participant" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

const roleMeta: Record<string, { label: string; desc: string }> = {
    participant: { label: "Participant", desc: "I want to solve challenges & build my portfolio" },
    organization: { label: "Organization", desc: "I want to post challenges & find solutions" },
  };

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const { data } = await api.post("/api/auth/register", form);
      setAuth(data.access_token, data.user);
      router.push("/challenges");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4 py-8">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-md border border-slate-200 p-8">
        <div className="flex items-center gap-2 mb-6 justify-center">
          <div className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center text-white font-bold">S</div>
          <span className="font-bold text-xl">Skill<span className="text-brand-600">Bridge</span></span>
        </div>
        <h1 className="text-2xl font-bold text-center mb-6">Create your account</h1>
        {error && <div className="bg-red-50 text-red-600 text-sm p-3 rounded-lg mb-4">{error}</div>}
        <form onSubmit={submit} className="space-y-4">
          <input type="text" placeholder="Full name" required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })}
            className="w-full border border-slate-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500" />
          <input type="email" placeholder="Email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })}
            className="w-full border border-slate-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500" />
          <input type="password" placeholder="Password (min 6 chars)" required minLength={6} value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })}
            className="w-full border border-slate-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500" />

          <div className="space-y-2">
            <p className="text-sm font-medium text-slate-700">I am a...</p>
            {Object.entries(roleMeta).map(([key, meta]) => (
              <label key={key} onClick={() => setForm({ ...form, role: key })}
                className={`flex items-start gap-3 border rounded-lg p-3 cursor-pointer ${form.role === key ? "border-brand-500 bg-brand-50" : "border-slate-200"}`}>
                <input type="radio" name="role" className="mt-1 accent-brand-600" checked={form.role === key} onChange={() => setForm({ ...form, role: key })} />
                <div>
                  <p className="font-medium text-sm">{meta.label}</p>
                  <p className="text-xs text-slate-500">{meta.desc}</p>
                </div>
              </label>
            ))}
          </div>

          <button disabled={loading} className="w-full bg-brand-600 text-white py-2.5 rounded-lg font-medium hover:bg-brand-700 disabled:opacity-50">
            {loading ? "Creating account..." : "Create Account"}
          </button>
        </form>
        <p className="text-sm text-center text-slate-500 mt-4">
          Already have an account?{" "}
          <Link href="/login" className="text-brand-600 font-medium">Login</Link>
        </p>
      </div>
    </div>
  );
}
