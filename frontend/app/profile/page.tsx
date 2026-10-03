"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Nav from "@/components/Nav";
import { api, clearAuth, getAuthUser, setAuth, getErrorMessage } from "@/lib/api";

const ORG_TYPES = ["school", "ngo", "hospital", "startup", "company", "other"];

export default function ProfilePage() {
  const router = useRouter();
  const [user] = useState(getAuthUser());
  const isParticipant = user?.role === "participant";
  const [form, setForm] = useState({
    name: "",
    bio: "",
    skills: "",
    github_url: "",
    org_type: "",
    website: "",
  });
  const [originalForm, setOriginalForm] = useState({
    name: "",
    bio: "",
    skills: "",
    github_url: "",
    org_type: "",
    website: "",
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
        const loaded = {
          name: data.name || "",
          bio: data.bio || "",
          skills: skills || "",
          github_url: data.github_url || "",
          org_type: data.org_type || "",
          website: data.website || "",
        };
        setForm(loaded);
        setOriginalForm(loaded);
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
      } else {
        payload.org_type = form.org_type;
        payload.website = form.website;
      }
      const { data } = await api.put("/api/users/me", payload);
      // Normalize skills to an array before storing in localStorage so it stays
      // consistent with what other components expect from getAuthUser().skills.
      const normalized = { ...data };
      if (typeof normalized.skills === "string") {
        try {
          normalized.skills = JSON.parse(normalized.skills || "[]");
        } catch {
          normalized.skills = [];
        }
      }
      const newUser = { ...user, ...normalized };
      const token = localStorage.getItem("skillbridge_token");
      if (token) setAuth(token, newUser);
      setMessage({ type: "success", text: "Profile updated successfully!" });
    } catch (err: any) {
      setMessage({ type: "error", text: getErrorMessage(err, "Failed to update profile") });
    } finally {
      setSaving(false);
    }
  };

  const cancel = () => {
    // Discard unsaved changes and return to the profile page.
    // Never rely on router.back() which can land on an unrelated page (e.g. /portfolio).
    setForm(originalForm);
    setMessage(null);
    router.push("/profile");
  };

  const deleteAccount = async () => {
    if (!window.confirm("Delete your account? This cannot be undone.")) {
      return;
    }
    setSaving(true);
    setMessage(null);
    try {
      await api.delete("/api/users/me");
      clearAuth();
      router.push("/login");
    } catch (err: any) {
      setMessage({ type: "error", text: getErrorMessage(err, "Failed to delete account") });
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

            {isParticipant ? (
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
            ) : (
              <>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Organization Type</label>
                  <select
                    value={form.org_type}
                    onChange={(e) => setForm({ ...form, org_type: e.target.value })}
                    className="w-full border border-slate-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500 capitalize"
                  >
                    <option value="">Select type...</option>
                    {ORG_TYPES.map((t) => (
                      <option key={t} value={t} className="capitalize">{t}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Website</label>
                  <input
                    type="url"
                    value={form.website}
                    onChange={(e) => setForm({ ...form, website: e.target.value })}
                    placeholder="https://yourorganization.com"
                    className="w-full border border-slate-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500"
                  />
                </div>
              </>
            )}

            <div className="flex flex-col gap-3 pt-2 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex gap-3">
                <button
                  type="submit"
                  disabled={saving}
                  className="bg-brand-600 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-brand-700 disabled:opacity-50"
                >
                  {saving ? "Saving..." : "Save Changes"}
                </button>
                <button
                  type="button"
                  onClick={cancel}
                  className="text-slate-500 hover:text-slate-700 font-medium"
                >
                  Cancel
                </button>
              </div>
              <button
                type="button"
                onClick={deleteAccount}
                disabled={saving}
                className="text-red-600 hover:text-red-800 font-medium"
              >
                Delete account
              </button>
            </div>
          </form>
        )}
      </main>
    </>
  );
}
