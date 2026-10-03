"use client";

import { useEffect, useState } from "react";
import Nav from "@/components/Nav";
import { api, useAuthUser } from "@/lib/api";

type Entry = {
  id: number;
  title: string;
  description: string;
  score: number;
  skills_proven: string;
  challenge_title: string;
  is_winner: number;
};

export default function PortfolioPage() {
  // Read the user once (see useAuthUser) so the effect below runs once, not forever.
  const { user, ready } = useAuthUser();
  const [entries, setEntries] = useState<Entry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!ready) return;
    if (user) {
      api.get("/api/portfolio/mine")
        .then(({ data }) => setEntries(data))
        .catch(() => setEntries([]))
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [user, ready]);

  return (
    <>
      <Nav />
      <main className="max-w-4xl mx-auto px-4 py-10">
        <h1 className="text-3xl font-extrabold mb-2">My Portfolio</h1>
        <p className="text-slate-500 mb-8">Your AI-evaluated challenge history and project snapshots.</p>

        {!ready ? (
          <p className="text-slate-500">Loading...</p>
        ) : !user ? (
          <div className="bg-white border border-slate-200 rounded-2xl p-8 text-center">
            <p className="text-slate-500 mb-4">Please log in to view your portfolio.</p>
          </div>
        ) : loading ? (
          <p className="text-slate-500">Loading...</p>
        ) : entries.length === 0 ? (
          <div className="bg-white border border-slate-200 rounded-2xl p-12 text-center">
            <p className="text-slate-500 mb-4">You haven&apos;t added any portfolio entries yet.</p>
            <p className="text-sm text-slate-400">Submit a solution to a challenge and it will appear here.</p>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 gap-6">
            {entries.map((e) => {
              const skills = JSON.parse(e.skills_proven || "[]");
              return (
                <div key={e.id} className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-bold text-lg">{e.title}</h3>
                    <span className={`text-lg font-extrabold ${e.score >= 75 ? "text-emerald-600" : "text-amber-600"}`}>{e.score}</span>
                  </div>
                  {e.is_winner ? (
                    <span className="inline-flex items-center gap-1 text-xs bg-emerald-100 text-emerald-700 px-2.5 py-1 rounded-full mb-2">
                      Organization Verified
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 text-xs bg-slate-100 text-slate-500 px-2.5 py-1 rounded-full mb-2">
                      AI-Evaluated
                    </span>
                  )}
                  <p className="text-xs text-slate-400 mb-2">Challenge: {e.challenge_title}</p>
                  <p className="text-slate-600 text-sm mb-4 line-clamp-3">{e.description}</p>
                  <div className="flex flex-wrap gap-2">
                    {skills.map((s: string) => (
                      <span key={s} className="text-xs bg-brand-50 text-brand-700 px-2.5 py-1 rounded-full capitalize">
                        {(s as string).replace(/_/g, " ")}
                      </span>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </main>
    </>
  );
}
