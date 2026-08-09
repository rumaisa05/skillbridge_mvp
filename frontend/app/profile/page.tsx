"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Nav from "@/components/Nav";
import { api, getAuthUser, setAuth } from "@/lib/api";

export default function ProfilePage() {
  const router = useRouter();
  const [user] = useState(getAuthUser());
  const isParticipant = user?.role === "participant";
  const [form, setForm] = useState({
    name: "",
    bio: "",
    skills: "",
    github_url: "",
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  useEffect(() => {
    if (!user) {
      router.push("/login");
      return;
    }
    const fetchProfile = async () => {
      try {
        const { data } = await api.get("/api/users/me");
        let skills = data.skills || "[]";
        if (typeof skills === "string") {
          try {
            skills = JSON.parse(skills).join(", ");
          } catch {
            skills = "";
          }
        } else if (Array.isArray(skills)) {
          skills = skills.join(", ");
        }
        setForm({
          name: data.name || "",
          bio: data.bio || "",
          skills: skills || "",
          github_url: data.github_url || "",
        });
      } catch {
        setMessage({ type: "error", text: "Failed to load profile" });
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, [user, router]);

  const save = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage(null);
    try {
      const payload: any = { name: form.name };
      if (isParticipant) {
        const skillsArray = form.skills.split(",").map(s => s.trim()).filter(Boolean);
        payload.bio = form.bio;
        payload.skills = JSON.stringify(skillsArray);
        payload.github_url = form.github_url;
      }
      const { data } = await api.put("/api/users/me", payload);
      // Update stored user info
      const newUser = { ...user, ...data };
      const token = localStorage.getItem("skillbridge_token");
      if (token) setAuth(token, newUser);
      setMessage({ type: "success", text: "Profile updated successfully!" });
    } catch (err: any) {
      setMessage({ type: "error", text: err.response?.data?.detail || "Failed to update profile" });
    } finally {
      setSaving(false);
    }
  };

  if (!user) {
    return (
      <>
        <Nav />
        <div className="max-w-md mx-auto px-4 py-16 text-center">
          <p className="text-slate-600 mb-4">Please login to view your profile.</p>
          <button onClick={() => router.push("/login")} className="text-brand-600 font-medium">Login</button>
        </div>
      </>
    );
  }

  return (
    <>
      <Nav />
      <main className="max-w-2xl mx-auto px-4 py-10">
        <h1 className="text-3xl font-extrabold mb-2">Edit Profile</h1>
        <p className="text-slate-500 mb-8">
          {isParticipant
            ? "Update your personal information and skills."
            : "Update your organization information."}
        </p>

        {loading ? (
          <p className="text-slate-500">Loading profile...</p>
        ) : (
          <form onSubmit={save} className="bg-white border border-slate-200 rounded-2xl p-6 space-y-4">
            {message && (
              <div className={`p-3 rounded-lg text-sm ${message.type === "success" ? "bg-emerald-50 text-emerald-700" : "bg-red-50 text-red-600"}`}>
                {message.text}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                {isParticipant ? "Full Name" : "Organization Name"}
              </label>
              <input
                type="text"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                className="w-full border border-slate-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500"
                required
              />
            </div>

            {isParticipant && (
              <>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Bio</label>
                  <textarea
                    rows={4}
                    value={form.bio}
                    onChange={(e) => setForm({ ...form, bio: e.target.value })}
                    placeholder="Tell us about yourself, your skills, and what you're working on..."
                    className="w-full border border-slate-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Skills (comma-separated)</label>
                  <input
                    type="text"
                    value={form.skills}
                    onChange={(e) => setForm({ ...form, skills: e.target.value })}
                    placeholder="e.g. Python, React, UI/UX, Data Analysis"
                    className="w-full border border-slate-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">GitHub URL</label>
                  <input
                    type="url"
                    value={form.github_url}
                    onChange={(e) => setForm({ ...form, github_url: e.target.value })}
                    placeholder="https://github.com/yourusername"
                    className="w-full border border-slate-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500"
                  />
                </div>
              </>
            )}

            <div className="flex items-center gap-3 pt-2">
              <button
                type="submit"
                disabled={saving}
                className="bg-brand-600 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-brand-700 disabled:opacity-50"
              >
                {saving ? "Saving..." : "Save Changes"}
              </button>
              <button
                type="button"
                onClick={() => router.push("/portfolio")}
                className="text-slate-500 hover:text-slate-700 font-medium"
              >
                Cancel
              </button>
            </div>
          </form>
        )}
      </main>
    </>
  );
}
