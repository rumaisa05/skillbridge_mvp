"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { getAuthUser, clearAuth } from "@/lib/api";

export default function Nav() {
  const router = useRouter();
  const user = getAuthUser();
  const [menuOpen, setMenuOpen] = useState(false);

  const logout = () => {
    clearAuth();
    setMenuOpen(false);
    router.push("/");
    router.refresh();
  };

  const closeMenu = () => setMenuOpen(false);

  return (
    <nav className="bg-white border-b border-slate-200 sticky top-0 z-10">
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2" onClick={closeMenu}>
          <div className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center text-white font-bold">S</div>
          <span className="font-bold text-lg">Skill<span className="text-brand-600">Bridge</span></span>
        </Link>

        {/* Desktop nav */}
        <div className="hidden md:flex items-center gap-4">
          <Link href="/challenges" className="text-sm font-medium text-slate-600 hover:text-brand-600">Challenges</Link>
          {user && (user.role === "organization" || user.role === "admin") && (
            <Link href="/talent" className="text-sm font-medium text-slate-600 hover:text-brand-600">Find Talent</Link>
          )}
          {user ? (
            <>
              {user.role === "participant" && (
                <Link href="/portfolio" className="text-sm font-medium text-slate-600 hover:text-brand-600">My Portfolio</Link>
              )}
              {user.role === "organization" && (
                <Link href="/challenges/new" className="text-sm font-medium text-slate-600 hover:text-brand-600">Post Challenge</Link>
              )}
              {user.role === "admin" && (
                <Link href="/admin" className="text-sm font-medium text-slate-600 hover:text-brand-600">Admin</Link>
              )}
              <Link href="/profile" className="text-sm font-medium text-slate-600 hover:text-brand-600">Profile</Link>
              <span className="text-sm text-slate-500">Hi, {user.name}</span>
              <button onClick={logout} className="text-sm text-slate-500 hover:text-red-500">Logout</button>
            </>
          ) : (
            <>
              <Link href="/login" className="text-sm font-medium text-slate-600 hover:text-brand-600">Login</Link>
              <Link href="/register" className="text-sm font-medium bg-brand-600 text-white px-4 py-2 rounded-lg hover:bg-brand-700">Get Started</Link>
            </>
          )}
        </div>

        {/* Mobile hamburger */}
        <button
          onClick={() => setMenuOpen(!menuOpen)}
          className="md:hidden p-2 rounded-lg hover:bg-slate-100 text-slate-600"
          aria-label="Toggle menu"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            {menuOpen ? (
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
            )}
          </svg>
        </button>
      </div>

      {/* Mobile dropdown menu */}
      {menuOpen && (
        <div className="md:hidden border-t border-slate-200 bg-white px-4 py-3 space-y-2">
          <Link href="/challenges" onClick={closeMenu} className="block text-sm font-medium text-slate-600 hover:text-brand-600 py-1.5">Challenges</Link>
          {user && (user.role === "organization" || user.role === "admin") && (
            <Link href="/talent" onClick={closeMenu} className="block text-sm font-medium text-slate-600 hover:text-brand-600 py-1.5">Find Talent</Link>
          )}
          {user ? (
            <>
              {user.role === "participant" && (
                <Link href="/portfolio" onClick={closeMenu} className="block text-sm font-medium text-slate-600 hover:text-brand-600 py-1.5">My Portfolio</Link>
              )}
              {user.role === "organization" && (
                <Link href="/challenges/new" onClick={closeMenu} className="block text-sm font-medium text-slate-600 hover:text-brand-600 py-1.5">Post Challenge</Link>
              )}
              {user.role === "admin" && (
                <Link href="/admin" onClick={closeMenu} className="block text-sm font-medium text-slate-600 hover:text-brand-600 py-1.5">Admin</Link>
              )}
              <Link href="/profile" onClick={closeMenu} className="block text-sm font-medium text-slate-600 hover:text-brand-600 py-1.5">Profile</Link>
              <div className="text-sm text-slate-500 py-1.5">Hi, {user.name}</div>
              <button onClick={logout} className="block text-sm text-slate-500 hover:text-red-500 py-1.5">Logout</button>
            </>
          ) : (
            <>
              <Link href="/login" onClick={closeMenu} className="block text-sm font-medium text-slate-600 hover:text-brand-600 py-1.5">Login</Link>
              <Link href="/register" onClick={closeMenu} className="block text-sm font-medium bg-brand-600 text-white px-4 py-2 rounded-lg hover:bg-brand-700 text-center">Get Started</Link>
            </>
          )}
        </div>
      )}
    </nav>
  );
}
