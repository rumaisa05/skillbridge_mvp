"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Nav from "@/components/Nav";
import { api } from "@/lib/api";

type UserProfile = {
  id: number;
  email: string;
  name: string;
  role: string;
  bio: string;
  skills: string;
  github_url: string;
  org_type: string;
  website: string;
};

type PortfolioEntry = {
  id: number;
  title: string;
  description: string;
  score: number;
  challenge_title: string;
  organization_feedback: string;
  is_winner: number;
  created_at: string;
};

export default function PublicProfilePage() {
  const params = useParams();
  const router = useRouter();
  const userId = Number(params?.id);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [portfolio, setPortfolio] = useState<PortfolioEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!userId || Number.isNaN(userId)) {
      setError("Invalid profile id.");
      setLoading(false);
      return;
    }

    const load = async () => {
      setLoading(true);
      setError("");

      try {
        const [{ data: profileData }, { data: portfolioData }] = await Promise.all([
          api.get(`/api/users/${userId}`),
          api.get(`/api/portfolio/user/${userId}`),
        ]);
        setProfile(profileData);
        setPortfolio(portfolioData);
      } catch (err: any) {
        if (err.response?.status === 404) {
          setError("Profile not found.");
        } else {
          setError("Failed to load profile.");
        }
      } finally {
        setLoading(false);
      }
    };

    load();
  }, [userId]);

  const skills = (() => {
    if (!profile?.skills) return [];
    try {
      const parsed = JSON.parse(profile.skills);
      return Array.isArray(parsed) ? parsed : [];
    } catch {
      return profile.skills.split(",").map((s) => s.trim()).filter(Boolean);
    }
  })();

  return (
    <>
      <Nav />
      <main className="max-w-6xl mx-auto px-4 py-10">
        <button
          type="button"
          onClick={() => router.back()}
          className="text-brand-600 hover:text-brand-700 mb-6"
        >
          &larr; Back to talent search
        </button>

        {loading ? (
          <p className="text-slate-500">Loading profile...</p>
        ) : error ? (
          <div className="bg-white border border-slate-200 rounded-2xl p-12 text-center">
            <p className="text-red-600">{error}</p>
          </div>
        ) : profile ? (
          <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
            <section className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
              <div className="flex flex-col gap-2 mb-4">
                <h1 className="text-3xl font-bold">{profile.name}</h1>
                <p className="text-sm text-slate-500 capitalize">{profile.role}</p>
              </div>

              {profile.bio && (
                <div className="mb-6">
                  <h2 className="text-lg font-semibold mb-2">About</h2>
                  <p className="text-slate-600 whitespace-pre-line">{profile.bio}</p>
                </div>
              )}

              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <h2 className="text-sm font-semibold text-slate-700 mb-2">Email</h2>
                  <p className="text-slate-600 break-words">{profile.email}</p>
                </div>
                {profile.github_url && (
                  <div>
                    <h2 className="text-sm font-semibold text-slate-700 mb-2">GitHub</h2>
                    <a
                      href={profile.github_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-brand-600 hover:underline"
                    >
                      {profile.github_url}
                    </a>
                  </div>
                )}

                {profile.website && (
                  <div>
                    <h2 className="text-sm font-semibold text-slate-700 mb-2">Website</h2>
                    <a
                      href={profile.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-brand-600 hover:underline"
                    >
                      {profile.website}
                    </a>
                  </div>
                )}

                {profile.role === "organization" && profile.org_type && (
                  <div>
                    <h2 className="text-sm font-semibold text-slate-700 mb-2">Organization Type</h2>
                    <p className="text-slate-600 capitalize">{profile.org_type}</p>
                  </div>
                )}
              </div>

              {skills.length > 0 && (
                <div className="mt-6">
                  <h2 className="text-lg font-semibold mb-3">Skills</h2>
                  <div className="flex flex-wrap gap-2">
                    {skills.map((skill) => (
                      <span key={skill} className="text-xs bg-brand-50 text-brand-700 px-2.5 py-1 rounded-full capitalize">
                        {skill.replace(/_/g, " ")}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </section>

            <section className="space-y-4">
              <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
                <h2 className="text-xl font-semibold mb-3">Portfolio</h2>
                {portfolio.length === 0 ? (
                  <p className="text-slate-500">No portfolio entries have been published yet.</p>
                ) : (
                  <div className="space-y-4">
                    {portfolio.map((entry) => (
                      <div key={entry.id} className="border border-slate-200 rounded-2xl p-4">
                        <div className="flex items-start justify-between gap-4">
                          <div>
                            <h3 className="font-semibold">{entry.title}</h3>
                            <p className="text-sm text-slate-500">{entry.challenge_title}</p>
                          </div>
                          <span className={`text-sm font-semibold ${entry.score >= 75 ? "text-emerald-600" : entry.score >= 50 ? "text-amber-600" : "text-red-500"}`}>
                            {entry.score}
                          </span>
                        </div>
                        <p className="text-slate-600 text-sm mt-2">{entry.description}</p>
                        {entry.organization_feedback && (
                          <p className="text-slate-500 text-xs mt-3">Feedback: {entry.organization_feedback}</p>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </section>
          </div>
        ) : null}
      </main>
    </>
  );
}
