"use client";

import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  ResponsiveContainer,
} from "recharts";

const LABELS: Record<string, string> = {
  code_quality: "Code",
  creativity: "Creativity",
  documentation: "Docs",
  technical_complexity: "Complexity",
  security: "Security",
  ui_ux: "UI/UX",
  completeness: "Completeness",
};

export default function ScoreRadar({ scores }: { scores: Record<string, number> }) {
  const data = Object.entries(scores).map(([key, value]) => ({
    subject: LABELS[key] || key,
    value,
    fullMark: 10,
  }));

  return (
    <ResponsiveContainer width="100%" height={280}>
      <RadarChart data={data} outerRadius="70%">
        <PolarGrid />
        <PolarAngleAxis dataKey="subject" />
        <Radar dataKey="value" stroke="#4f46e5" fill="#6366f1" fillOpacity={0.5} />
      </RadarChart>
    </ResponsiveContainer>
  );
}
