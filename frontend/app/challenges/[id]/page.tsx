"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import Nav from "@/components/Nav";
import { api, getAuthUser, getErrorMessage } from "@/lib/api";

type Challenge = {
  id: number;
  title: string;
  description: string;
  category: string;
  difficulty: string;
  reward: string;
  status: string;
  org_name: string;
  org_id: number;
};

const CATEGORY_COLORS: Record<string, string> = {
  web: "bg-blue-100 text-blue-700",
  mobile: "bg-purple-100 text-purple-700",
  ai: "bg-pink-100 text-pink-700",
  automation: "bg-amber-100 text-amber-700",
  data: "bg-emerald-100 text-emerald-700",
  design: "bg-orange-100 text-orange-700",
  other: "bg-slate-100 text-slate-700",
};

export default function ChallengeDetail() {
  const { id } = useParams();
  const router = useRouter();
  const [challenge, setChallenge] = useState<Challenge | null>(null);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({ repo_url: "", demo_url: "", description: "" });
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  useEffect(() => {
    if (id) {
      api.get(`/api/challenges/${id}`)
        .then(({ data }) => setChallenge(data))
        .catch(() => setChallenge(null))
        .finally(() => setLoading(false));
    }
  }, [id]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    const user = getAuthUser();
    if (!user) {
      router.push("/login");
      return;
    }
    setSubmitting(true);
    setMessage(null);
    try {
      const { data } = await api.post("/api/submissions", {
        challenge_id: Number(id),
        repo_url: form.repo_url,
        demo_url: form.demo_url,
        description: form.description,
      });
      setMessage({ type: "success", text: "Submission accepted! Your AI evaluation report is being generated." });
      setTimeout(() => router.push(`/report/${data.id}`), 1200);
    } catch (err: any) {
      setMessage({ type: "error", text: getErrorMessage(err, "Submission failed") });
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <><Nav /><p className="max-w-3xl mx-auto px-4 py-10">Loading...</p></>;

  if (!challenge) return <><Nav /><p className="max-w-3xl mx-auto px-4 py-10">Challenge not found.</p></>;

  const user = getAuthUser();
  const isParticipant = user && user.role === "participant";
  const isOrgOwner = user && (user.role === "organization" || user.role === "admin") && (user.role === "admin" || user.id === challenge.org_id);

  const closeChallenge = async () => {
    if (!confirm("Close this challenge? Submissions will no longer be accepted.")) return;
    try {
      await api.put(`/api/challenges/${challenge.id}`, {
        title: challenge.title,
        description: challenge.description,
        category: challenge.category,
        difficulty: challenge.difficulty,
        reward: challenge.reward,
        status: "closed",
      });
      setChallenge({ ...challenge, status: "closed" });
      setMessage({ type: "success", text: "Challenge closed." });
    } catch (err: any) {
      setMessage({ type: "error", text: getErrorMessage(err, "Failed to close challenge") });
    }
  };

  const deleteChallenge = async () => {
    if (!confirm("Delete this challenge? This cannot be undone.")) return;
    try {
      await api.delete(`/api/challenges/${challenge.id}`);
      router.push("/challenges");
    } catch (err: any) {
      setMessage({ type: "error", text: getErrorMessage(err, "Failed to delete challenge") });
    }
  };

  return (
    <>
      <Nav />
      <main className="max-w-3xl mx-auto px-4 py-10">
        <div className="flex items-start justify-between gap-4">
          <div>
            <span className="text-sm text-brand-600 capitalize">{challenge.category} · {challenge.difficulty}</span>
            <h1 className="text-3xl font-extrabold mt-2">{challenge.title}</h1>
            <p className="text-slate-500 mt-1">by {challenge.org_name}</p>
            {challenge.reward && <div className="mt-3 inline-block bg-amber-50 text-amber-700 text-sm font-medium px-3 py-1.5 rounded-lg">{challenge.reward}</div>}
            {challenge.status !== "open" && (
              <span className="mt-3 inline-block bg-slate-100 text-slate-600 text-xs font-medium px-3 py-1 rounded-full ml-2 capitalize">{challenge.status}</span>
            )}
          </div>
          {isOrgOwner && (
            <div className="shrink-0 flex flex-col gap-2">
              <Link
                href={`/challenges/${challenge.id}/submissions`}
                className="bg-brand-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-brand-700 text-center"
              >
                View Submissions
              </Link>
              <div className="flex gap-2">
                {challenge.status === "open" && (
                  <button
                    onClick={closeChallenge}
                    className="bg-amber-100 text-amber-700 px-3 py-2 rounded-lg text-sm font-medium hover:bg-amber-200"
                  >
                    Close
                  </button>
                )}
                <button
                  onClick={deleteChallenge}
                  className="bg-red-50 text-red-600 px-3 py-2 rounded-lg text-sm font-medium hover:bg-red-100"
                >
                  Delete
                </button>
              </div>
            </div>
          )}
        </div>

        <div className="mt-6 bg-white border border-slate-200 rounded-2xl p-6 whitespace-pre-line">
          <p className="text-slate-700 leading-relaxed">{challenge.description}</p>
        </div>

        {isParticipant && (
          <div className="mt-8 bg-white border border-slate-200 rounded-2xl p-6">
            <h2 className="font-bold text-xl mb-4">Submit Your Solution</h2>
            {message && (
              <div className={`mb-4 p-3 rounded-lg text-sm ${message.type === "success" ? "bg-emerald-50 text-emerald-700" : "bg-red-50 text-red-600"}`}>
                {message.text}
              </div>
            )}
            <form onSubmit={submit} className="space-y-4">
              <input type="url" placeholder="Repository URL (GitHub, GitLab...)" value={form.repo_url} onChange={(e) => setForm({ ...form, repo_url: e.target.value })}
                className="w-full border border-slate-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500" />
              <input type="url" placeholder="Live demo / screenshots URL (optional)" value={form.demo_url} onChange={(e) => setForm({ ...form, demo_url: e.target.value })}
                className="w-full border border-slate-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500" />
              <textarea placeholder="Describe your solution: features, tech stack, architecture, what you're proud of..." rows={6} required value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })}
                className="w-full border border-slate-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500" />
              <button disabled={submitting} className="w-full sm:w-auto bg-brand-600 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-brand-700 disabled:opacity-50">
                {submitting ? "Submitting & analyzing..." : "Submit Solution"}
              </button>
            </form>
          </div>
        )}

        {!isParticipant && (
          <div className="mt-8 bg-white border border-slate-200 rounded-2xl p-6">
            <h2 className="font-bold text-xl mb-2">Submit Your Solution</h2>
            <p className="text-sm text-slate-500">
              Only participants (students/individuals) can submit solutions to challenges.
              If you are a student or individual, please register or log in as a Participant to submit.
            </p>
          </div>
        )}
      </main>
    </>
  );
}
