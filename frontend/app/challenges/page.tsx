"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import Nav from "@/components/Nav";

const CATEGORY_COLORS: Record<string, string> = {
  web: "bg-blue-100 text-blue-700",
  mobile: "bg-purple-100 text-purple-700",
  ai: "bg-pink-100 text-pink-700",
  automation: "bg-amber-100 text-amber-700",
  data: "bg-emerald-100 text-emerald-700",
  design: "bg-orange-100 text-orange-700",
  other: "bg-slate-100 text-slate-700",
};

const CATEGORIES = ["web", "mobile", "ai", "automation", "data", "design", "other"];
const DIFFICULTIES = ["easy", "medium", "hard"];

type Challenge = {
  id: number;
  title: string;
  description: string;
  category: string;
  difficulty: string;
  reward: string;
  org_name: string;
  status: string;
};

export default function ChallengesPage() {
  const [challenges, setChallenges] = useState<Challenge[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [difficulty, setDifficulty] = useState("");
  const [status, setStatus] = useState("");
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);

  useEffect(() => {
    setLoading(true);
    const params: Record<string, string> = {};
    if (search) params.search = search;
    if (category) params.category = category;
    if (difficulty) params.difficulty = difficulty;
    if (status) params.status = status;
    params.page = String(page);
    params.limit = "20";

    const qs = new URLSearchParams(params).toString();
    api.get(`/api/challenges?${qs}`)
      .then(({ data }) => {
        setChallenges(data);
        setHasMore(data.length === 20);
      })
      .catch(() => setChallenges([]))
      .finally(() => setLoading(false));
  }, [search, category, difficulty, status, page]);

  const resetPage = () => setPage(1);

  return (
    <>
      <Nav />
      <main className="max-w-6xl mx-auto px-4 py-10">
        <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
          <div>
            <h1 className="text-3xl font-extrabold">Open Challenges</h1>
            <p className="text-slate-500 mt-1">Solve a real problem and prove your skills.</p>
          </div>
        </div>

        {/* Search & Filters */}
        <div className="bg-white border border-slate-200 rounded-2xl p-4 mb-8 grid md:grid-cols-4 gap-3">
          <input
            type="text"
            placeholder="Search challenges..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); resetPage(); }}
            className="border border-slate-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500 col-span-1 md:col-span-2"
          />
          <select
            value={category}
            onChange={(e) => { setCategory(e.target.value); resetPage(); }}
            className="border border-slate-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500"
          >
            <option value="">All Categories</option>
            {CATEGORIES.map((c) => <option key={c} value={c} className="capitalize">{c}</option>)}
          </select>
          <select
            value={difficulty}
            onChange={(e) => { setDifficulty(e.target.value); resetPage(); }}
            className="border border-slate-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500"
          >
            <option value="">All Difficulties</option>
            {DIFFICULTIES.map((d) => <option key={d} value={d} className="capitalize">{d}</option>)}
          </select>
        </div>

        {loading && <p className="text-slate-500">Loading challenges...</p>}

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {challenges.map((c) => (
            <Link key={c.id} href={`/challenges/${c.id}`} className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm hover:shadow-md hover:border-brand-300 transition">
              <div className="flex items-start justify-between mb-3">
                <span className={`text-xs font-medium px-2.5 py-1 rounded-full capitalize ${CATEGORY_COLORS[c.category] || CATEGORY_COLORS.other}`}>{c.category}</span>
                <span className="text-xs text-slate-400 capitalize">{c.difficulty}</span>
              </div>
              <h3 className="font-bold text-lg mb-2">{c.title}</h3>
              <p className="text-slate-600 text-sm mb-4 line-clamp-3">{c.description}</p>
              <div className="flex items-center justify-between text-sm">
                <span className="text-slate-500">by {c.org_name || "Organization"}</span>
                {c.reward && <span className="text-brand-600 font-medium">🏆 {c.reward}</span>}
              </div>
            </Link>
          ))}
        </div>

        {!loading && challenges.length === 0 && (
          <p className="text-slate-500 text-center py-16">No challenges found. Try adjusting your filters.</p>
        )}

        {/* Pagination */}
        {!loading && challenges.length > 0 && (
          <div className="flex justify-center gap-3 mt-10">
            <button
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page === 1}
              className="px-4 py-2 border border-slate-300 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-100 disabled:opacity-50"
            >
              Previous
            </button>
            <span className="px-4 py-2 text-sm text-slate-500">Page {page}</span>
            <button
              onClick={() => setPage(page + 1)}
              disabled={!hasMore}
              className="px-4 py-2 border border-slate-300 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-100 disabled:opacity-50"
            >
              Next
            </button>
          </div>
        )}
      </main>
    </>
  );
}
