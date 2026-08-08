"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import Nav from "@/components/Nav";
import ScoreRadar from "@/components/RadarChart";
import Typewriter from "@/components/Typewriter";
import { api } from "@/lib/api";

type HeroStat = {
  value: number;
  suffix?: string;
  label: string;
};

const HERO_STATS: HeroStat[] = [
  { value: 0, suffix: " yrs", label: "experience needed" },
  { value: 7, label: "AI scoring dimensions" },
  { value: 3, suffix: " steps", label: "challenge to portfolio" },
  { value: 1, suffix: "x", label: "AI-evaluated portfolio snapshot" },
];

function AnimatedCounter({
  value,
  suffix = "",
  duration = 1200,
}: {
  value: number;
  suffix?: string;
  duration?: number;
}) {
  const [count, setCount] = useState(0);
  const ref = useRef<HTMLSpanElement | null>(null);
  const animatedRef = useRef(false);

  useEffect(() => {
    const node = ref.current;
    if (!node) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (!entry.isIntersecting || animatedRef.current) return;

        animatedRef.current = true;
        const start = performance.now();

        const tick = (now: number) => {
          const progress = Math.min((now - start) / duration, 1);
          const eased = 1 - Math.pow(1 - progress, 3);
          setCount(value * eased);

          if (progress < 1) {
            requestAnimationFrame(tick);
          }
        };

        requestAnimationFrame(tick);
        observer.disconnect();
      },
      { threshold: 0.3 }
    );

    observer.observe(node);
    return () => observer.disconnect();
  }, [duration, value]);

  return (
    <span ref={ref} aria-label={`${value}${suffix}`}>
      {Math.round(count)}
      {suffix}
    </span>
  );
}

type Challenge = {
  id: number;
  title: string;
  description: string;
  category: string;
  difficulty: string;
  reward: string;
  org_name: string;
  status: string;
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

const DEMO_RADAR = {
  code_quality: 8,
  creativity: 9,
  documentation: 7,
  technical_complexity: 8,
  security: 7,
  ui_ux: 9,
  completeness: 8,
};

const STEPS = [
  {
    icon: "ClipboardIcon",
    step: "01",
    title: "Discover a Challenge",
    desc: "Organizations post real-world problems they need solved — websites, apps, AI tools, data analysis, and more.",
  },
  {
    icon: "WrenchIcon",
    step: "02",
    title: "Build Your Solution",
    desc: "Submit your own independent solution. No experience required — just build, document, and share your work.",
  },
  {
    icon: "ChipIcon",
    step: "03",
    title: "Get AI Evaluation",
    desc: "Our AI evaluates code quality, creativity, security, UI/UX and more, generating a personalized evaluation report.",
  },
  {
    icon: "RocketIcon",
    step: "04",
    title: "Grow & Get Discovered",
    desc: "Create an AI-evaluated portfolio entry and present project outcomes for employer review.",
  },
];

const ICONS: Record<string, React.ReactNode> = {
  ClipboardIcon: (
    <svg xmlns="http://www.w3.org/2000/svg" className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
    </svg>
  ),
  WrenchIcon: (
    <svg xmlns="http://www.w3.org/2000/svg" className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M11.42 15.17L17.25 21A2.652 2.652 0 0021 17.25l-5.877-5.877M11.42 15.17l2.496-3.03c.317-.384.74-.626 1.208-.766M11.42 15.17l-4.655 5.653a2.548 2.548 0 11-3.586-3.586l6.837-5.63m5.108-.233c.55-.164 1.163-.188 1.743-.14a4.5 4.5 0 004.486-6.336l-3.276 3.277a3.004 3.004 0 01-2.25-2.25l3.276-3.276a4.5 4.5 0 00-6.336 4.486c.091 1.076-.071 2.264-.904 2.95l-.102.085" />
    </svg>
  ),
  ChipIcon: (
    <svg xmlns="http://www.w3.org/2000/svg" className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 7h10v10H7V7z" />
    </svg>
  ),
  RocketIcon: (
    <svg xmlns="http://www.w3.org/2000/svg" className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M15.59 14.37a6 6 0 01-5.84 7.38v-4.8m5.84-2.58a14.98 14.98 0 006.16-12.12A14.98 14.98 0 009.631 8.41m5.96 5.96a14.926 14.926 0 01-5.841 2.58m-.119-8.54a6 6 0 00-7.381 5.84h4.8m2.581-5.84a14.927 14.927 0 00-2.58 5.84m2.699 2.7c-.103.021-.207.041-.311.06a15.09 15.09 0 01-2.448-2.448 14.9 14.9 0 01.06-.312m-2.24 2.39a4.493 4.493 0 00-1.757 4.306 4.493 4.493 0 004.306-1.758M16.5 9a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0z" />
    </svg>
  ),
};

const TESTIMONIALS = [
  {
    name: "Amina K.",
    role: "CS Student",
    quote: "I had no internships and no experience. Two SkillBridge challenges later, I had an AI-evaluated portfolio and a job offer.",
    avatar: "AK",
  },
  {
    name: "GreenFuture Foundation",
    role: "Community NGO",
    quote: "We got a donation platform built by talented students for a fraction of agency cost — and their work was evaluated through the challenge flow.",
    avatar: "GF",
  },
  {
    name: "Daniel O.",
    role: "Startup Founder",
    quote: "SkillBridge let me find a UI/UX designer based on AI-generated evaluation reports instead of guessing from a resume.",
    avatar: "DO",
  },
];

export default function Home() {
  const [challenges, setChallenges] = useState<Challenge[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get("/api/challenges")
      .then(({ data }) => setChallenges(data.slice(0, 3)))
      .catch(() => setChallenges([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <>
      <Nav />

      {/* ── HERO ─────────────────────────────────────────── */}
      <section className="relative overflow-hidden bg-slate-950 text-white">
        <div className="absolute inset-0 opacity-20 bg-[radial-gradient(circle_at_top_right,#6366f1,transparent_50%),radial-gradient(circle_at_bottom_left,#2563eb,transparent_50%)]" />
        <div className="relative max-w-6xl mx-auto px-4 py-24 md:py-32 text-center">
          <p className="inline-flex items-center gap-2 text-xs font-medium uppercase tracking-widest text-indigo-300 bg-white/10 border border-white/10 rounded-full px-4 py-1.5 mb-6 animate-fade-in-up">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            AI-Powered Evaluation
          </p>
          <h1 className="text-4xl md:text-6xl font-extrabold leading-tight tracking-tight animate-fade-in-up delay-100ms animate-float">
            <Typewriter
              text={[
                { text: "Prove What You Can", className: "text-white" },
                {
                  text: " Build.",
                  className: "bg-gradient-to-r from-indigo-400 via-blue-400 to-indigo-400 bg-clip-text text-transparent",
                },
              ]}
              speed={70}
              startDelay={800}
              className="text-white"
              cursorClassName="text-indigo-300"
            />
          </h1>
          <p className="mt-6 text-lg md:text-xl text-slate-300 max-w-2xl mx-auto animate-fade-in-up delay-200ms">
            Break the “no experience, no job” cycle. Solve real challenges from real
            organizations, get an AI-generated evaluation report, and build a portfolio
            snapshot employers can review.
          </p>
          <div className="mt-10 flex flex-wrap justify-center gap-4">
            <Link
              href="/challenges"
              className="bg-indigo-500 hover:bg-indigo-400 text-white px-7 py-3.5 rounded-xl font-semibold shadow-lg shadow-indigo-500/30 transition"
            >
              Find Challenges
            </Link>
            <Link
              href="/register?role=organization"
              className="bg-white/10 hover:bg-white/20 border border-white/20 text-white px-7 py-3.5 rounded-xl font-semibold transition"
            >
              Post a Challenge
            </Link>
          </div>
          <div className="mt-14 grid grid-cols-2 md:grid-cols-4 gap-6 max-w-3xl mx-auto text-sm">
            {HERO_STATS.map((stat, index) => (
              <div
                key={stat.label}
                className="stat-card bg-white/5 border border-white/10 rounded-xl py-4 px-3"
                style={{ animationDelay: `${index * 120}ms` }}
              >
                <p className="text-2xl font-extrabold text-white">
                  <AnimatedCounter value={stat.value} suffix={stat.suffix ?? ""} />
                </p>
                <p className="text-slate-400 mt-1">{stat.label}</p>
                <p className="mt-2 text-[10px] uppercase tracking-[0.2em] text-indigo-300/80">Demo</p>
              </div>
            ))}
          </div>
          <p className="mt-4 text-[10px] font-medium uppercase tracking-[0.24em] text-slate-400">
            Example values shown for illustration
          </p>
        </div>
      </section>

      {/* ── HOW IT WORKS ─────────────────────────────────── */}
      <section className="max-w-6xl mx-auto px-4 py-20">
        <div className="text-center mb-12">
          <p className="text-sm font-semibold text-indigo-600 uppercase tracking-widest animate-fade-in-up">How it works</p>
          <h2 className="text-3xl md:text-4xl font-extrabold mt-2 animate-fade-in-up delay-100ms">
            From challenge to career
          </h2>
          <p className="text-slate-500 mt-3 max-w-xl mx-auto animate-fade-in-up delay-200ms">
            A complete cycle of real-world experience, AI evaluation, continuous learning, and opportunity.
          </p>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {STEPS.map((s) => (
            <div key={s.step} className="relative bg-white border border-slate-200 rounded-2xl p-6 hover:shadow-lg transition shadow-sm">
<span className="absolute top-4 right-5 text-4xl font-extrabold text-slate-100">{s.step}</span>
              <div className="text-indigo-600 mb-4">{ICONS[s.icon]}</div>
              <h3 className="font-bold text-lg mb-2">{s.title}</h3>
              <p className="text-slate-600 text-sm leading-relaxed">{s.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── FEATURED CHALLENGES ───────────────────────────── */}
      <section className="bg-slate-50 border-y border-slate-200 py-20">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex flex-col md:flex-row md:items-end justify-between mb-10 gap-4">
            <div>
              <p className="text-sm font-semibold text-indigo-600 uppercase tracking-widest animate-fade-in-up">Featured challenges</p>
              <h2 className="text-3xl md:text-4xl font-extrabold mt-2 animate-fade-in-up delay-100ms">Real problems, real impact</h2>
            </div>
            <Link href="/challenges" className="text-indigo-600 font-semibold hover:underline animate-fade-in-up delay-200ms">
              View all challenges
            </Link>
          </div>
          {loading && <p className="text-slate-500">Loading challenges...</p>}
          <div className="grid md:grid-cols-3 gap-6">
            {challenges.map((c) => (
              <Link
                key={c.id}
                href={`/challenges/${c.id}`}
                className="group bg-white border border-slate-200 rounded-2xl p-6 shadow-sm hover:shadow-lg hover:-translate-y-1 transition"
              >
                <div className="flex items-start justify-between mb-3">
                  <span className={`text-xs font-medium px-2.5 py-1 rounded-full capitalize ${CATEGORY_COLORS[c.category] || CATEGORY_COLORS.other}`}>
                    {c.category}
                  </span>
                  <span className="text-xs text-slate-400 capitalize">{c.difficulty}</span>
                </div>
                <h3 className="font-bold text-lg mb-2 group-hover:text-indigo-600 transition">{c.title}</h3>
                <p className="text-slate-600 text-sm mb-4 line-clamp-3">{c.description}</p>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-slate-500">by {c.org_name || "Organization"}</span>
{c.reward && <span className="text-indigo-600 font-medium">{c.reward}</span>}
                </div>
              </Link>
            ))}
          </div>
          {!loading && challenges.length === 0 && (
            <p className="text-slate-500 text-center py-10">No challenges yet — check back soon.</p>
          )}
        </div>
      </section>

      {/* ── AI EVALUATION ───────────────────────────────── */}
      <section className="max-w-6xl mx-auto px-4 py-20 grid md:grid-cols-2 gap-12 items-center">
        <div>
          <p className="text-sm font-semibold text-indigo-600 uppercase tracking-widest">AI evaluation</p>
          <h2 className="text-3xl md:text-4xl font-extrabold mt-2">
            Recognized for what you build, not just what you studied
          </h2>
          <p className="text-slate-500 mt-4 leading-relaxed">
            Instead of relying on degrees or certificates, show your abilities by
            solving real-world challenges. Every submission is analyzed by AI across
            seven weighted dimensions.
          </p>
          <ul className="mt-6 space-y-3">
            {[
              "Code quality & maintainability",
              "Creativity & technical complexity",
              "Documentation & project completeness",
              "Security & UI/UX best practices",
            ].map((item) => (
              <li key={item} className="flex items-center gap-3 text-slate-700">
                <span className="w-6 h-6 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center text-sm">•</span>
                {item}
              </li>
            ))}
          </ul>
        </div>
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-lg">
          <p className="font-semibold mb-4 text-center">Sample AI Skill Profile</p>
          <ScoreRadar scores={DEMO_RADAR} />
          <div className="mt-4 grid grid-cols-2 gap-2 text-sm">
            {Object.entries(DEMO_RADAR).map(([k, v]) => (
              <div key={k} className="flex justify-between bg-slate-50 rounded-lg px-3 py-2">
                <span className="text-slate-500 capitalize">{k.replace(/_/g, " ")}</span>
                <span className="font-bold text-indigo-600">{v}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── AI REPORT PREVIEW ─────────────────────────────── */}
      <section className="bg-gradient-to-br from-indigo-600 to-blue-600 text-white py-20">
        <div className="max-w-6xl mx-auto px-4 grid md:grid-cols-2 gap-12 items-center">
          <div>
            <p className="text-sm font-semibold uppercase tracking-widest text-indigo-200">AI evaluation report</p>
            <h2 className="text-3xl md:text-4xl font-extrabold mt-2">
              Personalized feedback, real learning
            </h2>
            <p className="mt-4 text-indigo-100 leading-relaxed">
              Every participant receives a detailed AI evaluation with strengths, areas
              to improve, and actionable learning recommendations — plus an AI-evaluated
              portfolio entry for practical experience.
            </p>
            <div className="mt-8 grid sm:grid-cols-3 gap-4">
              {[
                ["Strengths", "Know what you excel at"],
                ["Improvements", "Targeted weak spots"],
                ["Roadmap", "Next learning steps"],
              ].map(([t, d]) => (
                <div key={t} className="bg-white/10 border border-white/20 rounded-xl p-4">
                  <p className="font-bold">{t}</p>
                  <p className="text-sm text-indigo-100 mt-1">{d}</p>
                </div>
              ))}
            </div>
          </div>
          <div className="bg-white text-slate-900 rounded-2xl p-6 shadow-2xl">
            <div className="flex items-center justify-between mb-4">
              <p className="font-bold">Your Report</p>
              <span className="text-xs bg-emerald-100 text-emerald-700 px-2.5 py-1 rounded-full font-medium">AI Evaluated</span>
            </div>
            {[
              { label: "Overall Score", value: "86/100", color: "text-indigo-600" },
              { label: "Code Quality", value: "8/10", color: "text-emerald-600" },
              { label: "UI/UX Design", value: "9/10", color: "text-emerald-600" },
              { label: "Documentation", value: "7/10", color: "text-amber-600" },
            ].map((r) => (
              <div key={r.label} className="flex items-center justify-between border-b border-slate-100 py-3 last:border-0">
                <span className="text-slate-600">{r.label}</span>
                <span className={`font-bold ${r.color}`}>{r.value}</span>
              </div>
            ))}
            <div className="mt-4 bg-slate-50 rounded-xl p-4 text-sm text-slate-600">
<p className="font-semibold text-slate-800 mb-1">Recommendation</p>
              Strengthen security practices by reviewing OWASP Top 10 and adding input sanitization.
            </div>
          </div>
        </div>
      </section>

      {/* ── PORTFOLIO SHOWCASE ───────────────────────────── */}
      <section className="max-w-6xl mx-auto px-4 py-20">
        <div className="text-center mb-12">
          <p className="text-sm font-semibold text-indigo-600 uppercase tracking-widest animate-fade-in-up">Portfolio snapshots</p>
          <h2 className="text-3xl md:text-4xl font-extrabold mt-2 animate-fade-in-up delay-100ms">Project outcomes employers can review</h2>
          <p className="text-slate-500 mt-3 max-w-xl mx-auto animate-fade-in-up delay-200ms">
            Every portfolio entry reflects an AI evaluation of a submitted project, rather than an independent external audit.
          </p>
        </div>
        <div className="grid md:grid-cols-3 gap-6">
          {[
            { name: "Sara M.", role: "Full-Stack Developer", skills: ["React", "Node.js", "PostgreSQL"], score: 92 },
            { name: "James L.", role: "UI/UX Designer", skills: ["Figma", "Design Systems", "Prototyping"], score: 88 },
            { name: "Priya R.", role: "Data Analyst", skills: ["Python", "SQL", "Visualization"], score: 85 },
          ].map((p) => (
            <div key={p.name} className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm hover:shadow-lg transition">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold">
                  {p.name.split(" ").map((n) => n[0]).join("")}
                </div>
                <div>
                  <p className="font-bold">{p.name}</p>
                  <p className="text-sm text-slate-500">{p.role}</p>
                </div>
                <span className="ml-auto text-sm font-bold text-emerald-600">{p.score}%</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {p.skills.map((s) => (
                  <span key={s} className="text-xs bg-slate-100 text-slate-700 px-2.5 py-1 rounded-full">{s}</span>
                ))}
              </div>
              <div className="flex items-center gap-1 mt-4 text-xs text-slate-400">
                <span className="w-2 h-2 rounded-full bg-emerald-500" /> AI-evaluated portfolio snapshot
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── EMPLOYER SECTION ──────────────────────────────── */}
      <section className="bg-slate-950 text-white py-20">
        <div className="max-w-6xl mx-auto px-4 grid md:grid-cols-2 gap-12 items-center">
          <div>
            <p className="text-sm font-semibold uppercase tracking-widest text-indigo-300">For employers</p>
            <h2 className="text-3xl md:text-4xl font-extrabold mt-2">
              Discover proven talent, not just resumes
            </h2>
            <p className="mt-4 text-slate-300 leading-relaxed">
              Search portfolio snapshots, project history, and AI-generated evaluation
              summaries to understand each participant's challenge results and strengths.
            </p>
            <ul className="mt-6 space-y-3">
              {[
                "Browse AI-generated skill summaries",
                "Review project snapshots and challenge outcomes",
                "See organization feedback & reviews",
                "Connect with talent based on challenge evidence",
              ].map((item) => (
                <li key={item} className="flex items-center gap-3 text-slate-200">
                  <span className="w-6 h-6 rounded-full bg-indigo-500 text-white flex items-center justify-center text-sm">•</span>
                  {item}
                </li>
              ))}
            </ul>
          </div>
          <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
            <p className="text-sm text-slate-400 mb-4">Search for talent</p>
            <div className="bg-white/10 border border-white/10 rounded-xl p-4 text-slate-200 text-sm">
              <span className="font-semibold text-white">Skills:</span> React, Node.js, UI/UX, Python
            </div>
            <div className="mt-3 space-y-3">
              {[
                ["Full-Stack Developer", "92% · 3 AI-evaluated projects", "Available"],
                ["UI/UX Designer", "88% · 2 AI-evaluated projects", "Available"],
                ["Data Analyst", "85% · 4 AI-evaluated projects", "Open to offers"],
              ].map(([r, m, s]) => (
                <div key={r} className="bg-slate-800/60 rounded-xl p-4 flex items-center justify-between">
                  <div>
                    <p className="font-semibold">{r}</p>
                    <p className="text-xs text-slate-400 mt-0.5">{m}</p>
                  </div>
                  <span className="text-xs text-emerald-400">{s}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ── TESTIMONIALS ──────────────────────────────────── */}
      <section className="max-w-6xl mx-auto px-4 py-20">
        <div className="text-center mb-12">
          <p className="text-sm font-semibold text-indigo-600 uppercase tracking-widest animate-fade-in-up">Testimonials</p>
          <h2 className="text-3xl md:text-4xl font-extrabold mt-2 animate-fade-in-up delay-100ms">Loved by builders & organizations</h2>
        </div>
        <div className="grid md:grid-cols-3 gap-6">
          {TESTIMONIALS.map((t) => (
            <div key={t.name} className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
              <div className="text-amber-400 mb-3">*****</div>
              <p className="text-slate-600 leading-relaxed mb-5">“{t.quote}”</p>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-sm">
                  {t.avatar}
                </div>
                <div>
                  <p className="font-bold text-sm">{t.name}</p>
                  <p className="text-xs text-slate-500">{t.role}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── CTA ───────────────────────────────────────────── */}
      <section className="max-w-6xl mx-auto px-4 pb-20">
        <div className="bg-gradient-to-br from-indigo-600 to-blue-600 rounded-3xl p-10 md:p-16 text-center text-white shadow-2xl">
          <h2 className="text-3xl md:text-4xl font-extrabold animate-fade-in-up">Ready to prove what you can build?</h2>
          <p className="mt-4 text-indigo-100 max-w-xl mx-auto animate-fade-in-up delay-100ms">
            Join SkillBridge today. Solve a real challenge, receive an AI-generated
            evaluation report, and open doors that resumes couldn't.
          </p>
          <div className="mt-8 flex flex-wrap justify-center gap-4">
            <Link href="/register" className="bg-white text-indigo-700 px-7 py-3.5 rounded-xl font-semibold hover:bg-indigo-50 transition">
              Get Started Free
            </Link>
            <Link href="/challenges" className="bg-white/10 border border-white/30 px-7 py-3.5 rounded-xl font-semibold hover:bg-white/20 transition">
              Browse Challenges
            </Link>
          </div>
        </div>
      </section>

      {/* ── FOOTER ────────────────────────────────────────── */}
      <footer className="bg-slate-950 text-slate-400 py-12">
        <div className="max-w-6xl mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center gap-2 mb-3">
                <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold">S</div>
                <span className="font-bold text-white text-lg">Skill<span className="text-indigo-400">Bridge</span></span>
              </div>
              <p className="text-sm leading-relaxed">
                An AI-powered community innovation platform. Recognized for what you build, not just what you studied.
              </p>
            </div>
            <div>
              <p className="font-semibold text-white mb-3">Platform</p>
              <ul className="space-y-2 text-sm">
                <li><Link href="/challenges" className="hover:text-white">Find Challenges</Link></li>
                <li><Link href="/register?role=organization" className="hover:text-white">Post a Challenge</Link></li>
                <li><Link href="/portfolio" className="hover:text-white">Portfolio Snapshots</Link></li>
              </ul>
            </div>
            <div>
              <p className="font-semibold text-white mb-3">For Talent</p>
              <ul className="space-y-2 text-sm">
                <li><Link href="/register" className="hover:text-white">Get Started</Link></li>
                <li><Link href="/challenges" className="hover:text-white">Browse Challenges</Link></li>
                <li><Link href="/register" className="hover:text-white">Build Your Portfolio</Link></li>
              </ul>
            </div>
            <div>
              <p className="font-semibold text-white mb-3">For Employers</p>
              <ul className="space-y-2 text-sm">
                <li><Link href="/register?role=employer" className="hover:text-white">Hire Talent</Link></li>
                <li><Link href="/register?role=organization" className="hover:text-white">Partner With Us</Link></li>
              </ul>
            </div>
          </div>
          <div className="mt-10 pt-6 border-t border-slate-800 flex flex-col md:flex-row items-center justify-between gap-4 text-sm">
            <p>© {new Date().getFullYear()} SkillBridge. All rights reserved.</p>
            <div className="flex gap-6">
              <span className="hover:text-white cursor-pointer">Privacy</span>
              <span className="hover:text-white cursor-pointer">Terms</span>
              <span className="hover:text-white cursor-pointer">Contact</span>
            </div>
          </div>
        </div>
      </footer>
    </>
  );
}
