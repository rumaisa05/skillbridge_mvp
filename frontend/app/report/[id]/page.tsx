"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import Nav from "@/components/Nav";
import ScoreRadar from "@/components/RadarChart";
import { api, getAuthUser, getErrorMessage } from "@/lib/api";

type Report = {
  overall_score: number;
  dimension_scores: string;
  summary: string;
  strengths: string;
  weaknesses: string;
  recommendations: string;
  model_used: string;
};

export default function ReportPage() {
  const { id } = useParams();
  const router = useRouter();
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);
  const [portfolioMsg, setPortfolioMsg] = useState("");

  useEffect(() => {
    if (id) {
      api.get(`/api/submissions/${id}/report`)
        .then(({ data }) => setReport(data))
        .catch(() => setReport(null))
        .finally(() => setLoading(false));
    }
  }, [id]);

  const addToPortfolio = async () => {
    try {
      const { data } = await api.post(`/api/submissions/${id}/portfolio`);
      setPortfolioMsg(data.message || "Added to portfolio");
    } catch (e: any) {
      setPortfolioMsg(getErrorMessage(e, "Could not add to portfolio"));
    }
  };

  if (loading) return <><Nav /><p className="max-w-3xl mx-auto px-4 py-10">Generating report...</p></>;
  if (!report) return <><Nav /><p className="max-w-3xl mx-auto px-4 py-10">Report not found.</p></>;

  const dims = JSON.parse(report.dimension_scores || "{}");
  const strengths = JSON.parse(report.strengths || "[]");
  const weaknesses = JSON.parse(report.weaknesses || "[]");
  const recs = JSON.parse(report.recommendations || "[]");

  const scoreColor = report.overall_score >= 75 ? "text-emerald-600" : report.overall_score >= 50 ? "text-amber-600" : "text-red-500";

  return (
    <>
      <Nav />
      <main className="max-w-4xl mx-auto px-4 py-10">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <h1 className="text-2xl sm:text-3xl font-extrabold">Your AI Evaluation Report</h1>
          <button onClick={addToPortfolio} className="bg-emerald-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-emerald-700 w-full sm:w-auto">
            + Add to Portfolio
          </button>
        </div>
        {portfolioMsg && <div className="mb-4 bg-emerald-50 text-emerald-700 p-3 rounded-lg text-sm">{portfolioMsg}</div>}

        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <div className="bg-white border border-slate-200 rounded-2xl p-6 flex flex-col items-center justify-center">
            <p className="text-sm text-slate-500">Overall Evaluation Score</p>
            <p className={`text-6xl font-extrabold ${scoreColor}`}>{report.overall_score}</p>
            <p className="text-xs text-slate-400 mt-1">Model: {report.model_used}</p>
          </div>
          <div className="bg-white border border-slate-200 rounded-2xl p-4">
            {Object.keys(dims).length > 0 && <ScoreRadar scores={dims} />}
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-6 mb-6">
          <h2 className="font-bold text-lg mb-3">Per-Dimension Scores</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {Object.entries(dims).map(([key, value]) => (
              <div key={key} className="bg-slate-50 rounded-lg p-3 flex justify-between items-center">
                <span className="text-sm capitalize text-slate-600">{key.replace(/_/g, " ")}</span>
                <span className="font-bold text-brand-600">{(value as number)}/10</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-6 mb-6">
          <h2 className="font-bold text-lg mb-3">Summary</h2>
          <p className="text-slate-600 leading-relaxed">{report.summary}</p>
        </div>

        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-6">
            <h3 className="font-bold mb-3 text-emerald-800">Strengths</h3>
            <ul className="space-y-2 text-sm text-emerald-800">
              {strengths.map((s: string, i: number) => <li key={i}>• {s}</li>)}
            </ul>
          </div>
          <div className="bg-amber-50 border border-amber-200 rounded-2xl p-6">
            <h3 className="font-bold mb-3 text-amber-800">Areas to Improve</h3>
            <ul className="space-y-2 text-sm text-amber-800">
              {weaknesses.map((s: string, i: number) => <li key={i}>• {s}</li>)}
            </ul>
          </div>
          <div className="bg-blue-50 border border-blue-200 rounded-2xl p-6">
            <h3 className="font-bold mb-3 text-blue-800">Recommendations</h3>
            <ul className="space-y-2 text-sm text-blue-800">
              {recs.map((s: string, i: number) => <li key={i}>• {s}</li>)}
            </ul>
          </div>
        </div>

        <div className="text-center">
          <Link href="/portfolio" className="text-brand-600 font-medium hover:underline">View my portfolio</Link>
        </div>
      </main>
    </>
  );
}
