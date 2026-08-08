"use client";

import { useEffect, useState } from "react";
import Nav from "@/components/Nav";
import { api, getAuthUser } from "@/lib/api";

type UserSummary = {
  users: number;
  participants: number;
  organizations: number;
  challenges: number;
  submissions: number;
};

type UserRow = {
  id: number;
  email: string;
  name: string;
  role: string;
  bio: string;
  skills: string;
  github_url: string;
  avatar_url: string;
};

export default function AdminPage() {
  const user = getAuthUser();
  const [summary, setSummary] = useState<UserSummary | null>(null);
  const [users, setUsers] = useState<UserRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user) return;
    if (user.role !== "admin") {
      setError("Admin access required");
      setLoading(false);
      return;
    }

    const fetchData = async () => {
      try {
        const [summaryRes, usersRes] = await Promise.all([
          api.get("/api/admin/summary"),
          api.get("/api/admin/users"),
        ]);
        setSummary(summaryRes.data);
        setUsers(usersRes.data);
      } catch (err: any) {
        setError(err.response?.data?.detail || "Failed to load admin data");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [user]);

  return (
    <>
      <Nav />
      <main className="max-w-6xl mx-auto px-4 py-10">
        <h1 className="text-3xl font-extrabold mb-3">Admin Dashboard</h1>
        <p className="text-slate-500 mb-8">View platform-wide metrics and user data for moderation.</p>

        {!user ? (
          <div className="rounded-2xl border border-slate-200 bg-white p-8 text-center">
            <p className="text-slate-500">Please log in as an admin to view this page.</p>
          </div>
        ) : loading ? (
          <p className="text-slate-500">Loading admin data...</p>
        ) : error ? (
          <div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-red-700">
            {error}
          </div>
        ) : (
          <div className="space-y-10">
            <section className="grid sm:grid-cols-5 gap-4">
              {[
                { label: "Users", value: summary?.users ?? 0 },
                { label: "Participants", value: summary?.participants ?? 0 },
                { label: "Organizations", value: summary?.organizations ?? 0 },
                { label: "Challenges", value: summary?.challenges ?? 0 },
                { label: "Submissions", value: summary?.submissions ?? 0 },
              ].map((item) => (
                <div key={item.label} className="rounded-3xl border border-slate-200 bg-white p-6 text-center shadow-sm">
                  <p className="text-4xl font-extrabold text-brand-600">{item.value}</p>
                  <p className="mt-2 text-sm text-slate-500">{item.label}</p>
                </div>
              ))}
            </section>

            <section className="bg-white border border-slate-200 rounded-3xl p-6 shadow-sm">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-xl font-bold">User directory</h2>
                  <p className="text-sm text-slate-500">All registered accounts with sanitized profile fields.</p>
                </div>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
                  <thead className="bg-slate-50">
                    <tr>
                      <th className="px-4 py-3 font-medium text-slate-600">ID</th>
                      <th className="px-4 py-3 font-medium text-slate-600">Name</th>
                      <th className="px-4 py-3 font-medium text-slate-600">Email</th>
                      <th className="px-4 py-3 font-medium text-slate-600">Role</th>
                      <th className="px-4 py-3 font-medium text-slate-600">Skills</th>
                      <th className="px-4 py-3 font-medium text-slate-600">GitHub</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200">
                    {users.map((u) => (
                      <tr key={u.id} className="hover:bg-slate-50">
                        <td className="px-4 py-3 text-slate-700">{u.id}</td>
                        <td className="px-4 py-3 text-slate-700">{u.name}</td>
                        <td className="px-4 py-3 text-slate-700">{u.email}</td>
                        <td className="px-4 py-3 text-slate-700 capitalize">{u.role}</td>
                        <td className="px-4 py-3 text-slate-700 lowercase">{typeof u.skills === "string" ? u.skills : JSON.stringify(u.skills)}</td>
                        <td className="px-4 py-3 text-slate-700 break-all">{u.github_url || "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          </div>
        )}
      </main>
    </>
  );
}
