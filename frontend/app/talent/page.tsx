"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Nav from "@/components/Nav";
import { api, getAuthUser } from "@/lib/api";

type TalentResult = {
  id: number;
  participant_id: number;
  participant_name: string;
  participant_email: string;
  participant_bio: string;
  participant_github: string;
  title: string;
  description: string;
  skills_proven: string[];
  score: number;
  challenge_title: string;
  organization_feedback: string;
  is_winner: number;
  created_at: string;
};

export default function TalentPage() {
  const [results, setResults] = useState<TalentResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [skills, setSkills] = useState("");
  const [minScore, setMinScore] = useState(0);
  const [searched, setSearched] = useState(false);

  const user = getAuthUser();
  const isOrganization = user?.role === "organization";

  const search = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setLoading(true);
    setSearched(true);
    try {
      const params: any = {};
      if (skills.trim()) params.skills = skills.trim();
      if (minScore > 0) params.min_score = minScore;
      const { data } = await api.get("/api/talent/search", { params });
      setResults(data);
    } catch {
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    search();
  }, []);

  return (
    <>
      <Nav />
      <main className="max-w-6xl mx-auto px-4 py-10">
        <h1 className="text-3xl font-extrabold mb-2">Find Verified Talent</h1>
        <p className="text-slate-500 mb-8">
          Discover challenge winners who have been verified by the organizations that ran the challenges.
        </p>

        <form onSubmit={search} className="bg-white border border-slate-200 rounded-2xl p-4 mb-8 flex flex-col md:flex-row gap-3">
          <input
            type="text"
            placeholder="Search by skills (e.g. python, react, ui)"
            value={skills}
            onChange={(e) => setSkills(e.target.value)}
            className="flex-1 border border-slate-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500"
          />
          <select
            value={minScore}
            onChange={(e) => setMinScore(Number(e.target.value))}
            className="border border-slate-300 rounded-lg px-4 py-2.5"
          >
            <option value={0}>Any score</option>
            <option value={50}>50+</option>
            <option value={60}>60+</option>
            <option value={70}>70+</option>
            <option value={80}>80+</option>
            <option value={90}>90+</option>
          </select>
          <button className="bg-brand-600 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-brand-700">
            Search
          </button>
        </form>

        {loading ? (
          <p className="text-slate-500">Searching talent...</p>
        ) : results.length === 0 ? (
          <div className="bg-white border border-slate-200 rounded-2xl p-12 text-center">
            <p className="text-slate-500">
              {searched ? "No matching verified talent found. Try different skills or a lower minimum score." : "No verified portfolio entries yet."}
            </p>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {results.map((r) => (
              <div key={r.id} className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm hover:shadow-md transition">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="font-bold text-lg">{r.participant_name}</h3>
                    <p className="text-xs text-slate-400">{r.challenge_title}</p>
                  </div>
                  <span className={`text-lg font-extrabold ${r.score >= 75 ? "text-emerald-600" : r.score >= 50 ? "text-amber-600" : "text-red-500"}`}>
                    {r.score}
                  </span>
                </div>
                {r.is_winner ? (
                  <span className="inline-flex items-center gap-1 text-xs bg-emerald-100 text-emerald-700 px-2.5 py-1 rounded-full mb-3">
                    Organization Verified
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1 text-xs bg-slate-100 text-slate-500 px-2.5 py-1 rounded-full mb-3">
                    AI-Evaluated
                  </span>
                )}
                <p className="text-slate-600 text-sm mb-3 line-clamp-2">{r.description}</p>
                <div className="flex flex-wrap gap-2 mb-3">
                  {r.skills_proven.map((s: string) => (
                    <span key={s} className="text-xs bg-brand-50 text-brand-700 px-2.5 py-1 rounded-full capitalize">
                      {s.replace(/_/g, " ")}
                    </span>
                  ))}
                </div>
                <div className="flex items-center gap-3 text-xs text-slate-400">
                  {r.participant_github && (
                    <a href={r.participant_github} target="_blank" rel="noopener noreferrer" className="text-brand-600 hover:underline">
                      GitHub
                    </a>
                  )}
<span>{r.is_winner ? "Organization-verified project" : "AI-evaluated project"}</span>
                </div>
                {isOrganization && (
                  <Link
                    href={`/profile/${r.participant_id}`}
                    className="mt-4 inline-flex items-center justify-center gap-2 w-full bg-brand-600 text-white px-4 py-2.5 rounded-lg font-medium hover:bg-brand-700 transition"
                  >
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                      <path d="M2.003 5.884 10 9.882l7.997-3.998A2 2 0 0 0 16 4H4a2 2 0 0 0-1.997 1.884Z" />
                      <path d="m18 8.118-8 4-8-4V14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8.118Z" />
                    </svg>
                    Contact
                  </Link>
                )}
              </div>
            ))}
          </div>
        )}
      </main>
    </>
  );
}
