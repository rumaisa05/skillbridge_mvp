"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Nav from "@/components/Nav";
import { api, getAuthUser } from "@/lib/api";

export default function NewChallengePage() {
  const router = useRouter();
  const user = getAuthUser();
  const [form, setForm] = useState({ title: "", description: "", category: "web", difficulty: "medium", reward: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user || user.role !== "organization") {
      router.push("/register");
      return;
    }
    setLoading(true);
    setError("");
    try {
      await api.post("/api/challenges", form);
      router.push("/challenges");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to create challenge");
    } finally {
      setLoading(false);
    }
  };

  if (!user || user.role !== "organization") {
    return (
      <>
        <Nav />
        <div className="max-w-md mx-auto px-4 py-16 text-center">
          <p className="text-slate-600 mb-4">Only organizations can post challenges.</p>
          <button onClick={() => router.push("/register")} className="text-brand-600 font-medium">Register as an organization</button>
        </div>
      </>
    );
  }

  return (
    <>
      <Nav />
      <main className="max-w-2xl mx-auto px-4 py-10">
        <h1 className="text-3xl font-extrabold mb-6">Post a New Challenge</h1>
        {error && <div className="bg-red-50 text-red-600 p-3 rounded-lg mb-4 text-sm">{error}</div>}
        <form onSubmit={submit} className="bg-white border border-slate-200 rounded-2xl p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Title</label>
            <input type="text" required placeholder="e.g. Build a donation management website" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })}
              className="w-full border border-slate-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-brand-500" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Description</label>
            <textarea required rows={6} placeholder="Describe the problem, requirements, and what a great solution looks like." value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })}
              className="w-full border border-slate-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-brand-500" />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Category</label>
              <select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}
                className="w-full border border-slate-300 rounded-lg px-4 py-2.5">
                <option value="web">Web</option>
                <option value="mobile">Mobile</option>
                <option value="ai">AI</option>
                <option value="automation">Automation</option>
                <option value="data">Data</option>
                <option value="design">UI/UX Design</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Difficulty</label>
              <select value={form.difficulty} onChange={(e) => setForm({ ...form, difficulty: e.target.value })}
                className="w-full border border-slate-300 rounded-lg px-4 py-2.5">
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Reward / Incentive</label>
            <input type="text" placeholder="e.g. Certification, recommendation letter, internship" value={form.reward} onChange={(e) => setForm({ ...form, reward: e.target.value })}
              className="w-full border border-slate-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-brand-500" />
          </div>
          <button disabled={loading} className="w-full bg-brand-600 text-white py-2.5 rounded-lg font-medium hover:bg-brand-700 disabled:opacity-50">
            {loading ? "Posting..." : "Post Challenge"}
          </button>
        </form>
      </main>
    </>
  );
}
