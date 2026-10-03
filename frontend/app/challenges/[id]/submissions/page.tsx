"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import Nav from "@/components/Nav";
import { api, getErrorMessage, useAuthUser } from "@/lib/api";

type Submission = {
  id: number;
  challenge_id: number;
  participant_id: number;
  participant_name: string;
  repo_url: string;
  description: string;
  demo_url: string;
  docs_url: string;
  status: string;
  is_winner: number;
  created_at: string;
};

export default function SubmissionsPage() {
  const { id } = useParams();
  const router = useRouter();
  // Read the user once (see useAuthUser). Calling getAuthUser() here made a new
  // object every render and re-ran the effect below forever.
  const { user, ready } = useAuthUser();
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  useEffect(() => {
    if (!ready) return;
    if (!user || user.role !== "organization") {
      router.push("/login");
      return;
    }
    api.get(`/api/submissions?challenge_id=${id}`)
      .then(({ data }) => setSubmissions(data))
      .catch(() => setSubmissions([]))
      .finally(() => setLoading(false));
  }, [id, user, ready, router]);

  const selectWinner = async (submissionId: number) => {
    setMessage(null);
    try {
      const { data } = await api.post(`/api/challenges/${id}/select-winner?submission_id=${submissionId}`);
      setMessage({ type: "success", text: data.message || "Winner selected!" });
      // Refresh list to update is_winner flags
      const res = await api.get(`/api/submissions?challenge_id=${id}`);
      setSubmissions(res.data);
    } catch (err: any) {
      setMessage({ type: "error", text: getErrorMessage(err, "Failed to select winner") });
    }
  };

  if (!ready) {
    return (
      <>
        <Nav />
        <p className="max-w-4xl mx-auto px-4 py-10 text-slate-500">Loading...</p>
      </>
    );
  }

  if (!user || user.role !== "organization") {
    return (
      <>
        <Nav />
        <div className="max-w-md mx-auto px-4 py-16 text-center">
          <p className="text-slate-600 mb-4">Only organizations can view submissions.</p>
          <button onClick={() => router.push("/login")} className="text-brand-600 font-medium">Login as organization</button>
        </div>
      </>
    );
  }

  return (
    <>
      <Nav />
      <main className="max-w-4xl mx-auto px-4 py-10">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-extrabold">Submissions</h1>
            <p className="text-slate-500 mt-1">Review solutions and select a winner.</p>
          </div>
          <Link href={`/challenges/${id}`} className="text-brand-600 font-medium text-sm hover:underline">
            &larr; Back to challenge
          </Link>
        </div>

        {message && (
          <div className={`mb-4 p-3 rounded-lg text-sm ${message.type === "success" ? "bg-emerald-50 text-emerald-700" : "bg-red-50 text-red-600"}`}>
            {message.text}
          </div>
        )}

        {loading ? (
          <p className="text-slate-500">Loading submissions...</p>
        ) : submissions.length === 0 ? (
          <div className="bg-white border border-slate-200 rounded-2xl p-12 text-center">
            <p className="text-slate-500">No submissions yet for this challenge.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {submissions.map((s) => (
              <div key={s.id} className={`bg-white border rounded-2xl p-6 shadow-sm ${s.is_winner ? "border-emerald-400 bg-emerald-50/50" : "border-slate-200"}`}>
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="font-bold text-lg">{s.participant_name || "Participant"}</h3>
                    <p className="text-xs text-slate-400">
                      Submitted {new Date(s.created_at).toLocaleDateString()} · Status: {s.status}
                    </p>
                  </div>
                  {s.is_winner ? (
                    <span className="bg-emerald-100 text-emerald-700 text-xs font-medium px-3 py-1 rounded-full">Organizer Winner</span>
                  ) : (
                    <span className="bg-slate-100 text-slate-600 text-xs font-medium px-3 py-1 rounded-full">Submitted</span>
                  )}
                </div>

                <p className="text-slate-600 text-sm mb-4 whitespace-pre-line">{s.description}</p>

                <div className="flex flex-wrap gap-2 mb-4">
                  {s.repo_url && (
                    <a href={s.repo_url} target="_blank" rel="noopener noreferrer" className="text-xs bg-blue-50 text-blue-700 px-3 py-1.5 rounded-lg font-medium hover:bg-blue-100">
                      Repository
                    </a>
                  )}
                  {s.demo_url && (
                    <a href={s.demo_url} target="_blank" rel="noopener noreferrer" className="text-xs bg-purple-50 text-purple-700 px-3 py-1.5 rounded-lg font-medium hover:bg-purple-100">
                      Live Demo
                    </a>
                  )}
                  {s.docs_url && (
                    <a href={s.docs_url} target="_blank" rel="noopener noreferrer" className="text-xs bg-amber-50 text-amber-700 px-3 py-1.5 rounded-lg font-medium hover:bg-amber-100">
                      Docs
                    </a>
                  )}
                </div>

                <div className="flex items-center gap-3">
                  <Link href={`/report/${s.id}`} className="text-sm text-brand-600 font-medium hover:underline">
                    View AI Report
                  </Link>
                  {!s.is_winner && s.status === "analyzed" && (
                    <button
                      onClick={() => selectWinner(s.id)}
                      className="bg-emerald-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-emerald-700"
                    >
                      Select as Challenge Winner
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </>
  );
}
