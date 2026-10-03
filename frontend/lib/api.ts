"use client";

import axios from "axios";
import { useEffect, useState } from "react";

const DEFAULT_API_URL = "http://localhost:8000";
const API_URL = process.env.NEXT_PUBLIC_API_URL || DEFAULT_API_URL;

// Warn when the API URL is missing or still points to localhost in production.
// This is a common cause of the "Loading..." hang on deployed sites: if the env
// var is not provided at build time, every request silently targets the user's
// own machine (or fails DNS resolution) instead of the real backend.
if (typeof window !== "undefined" && process.env.NODE_ENV === "production") {
  if (!process.env.NEXT_PUBLIC_API_URL) {
    console.warn(
      "[SkillBridge] NEXT_PUBLIC_API_URL is not set. API requests will fall back to " +
        `${DEFAULT_API_URL}, which is unreachable in production. Set NEXT_PUBLIC_API_URL ` +
        "at build/deploy time to your deployed backend URL."
    );
  } else if (API_URL.includes("localhost") || API_URL.includes("127.0.0.1")) {
    console.warn(
      "[SkillBridge] NEXT_PUBLIC_API_URL is still pointing to a local address: " +
        `${API_URL}. This will not work on the deployed site. Point it to your deployed ` +
        "backend URL (e.g. https://your-backend.example.com)."
    );
  }
}

export const api = axios.create({
  baseURL: API_URL,
  timeout: 60000, // free hosts can take ~60 s to wake from sleep; still fail eventually
  headers: { "Content-Type": "application/json" },
});

// Surface network/CORS errors with a clear message instead of a generic one.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === "ECONNABORTED") {
      console.error("[SkillBridge] API request timed out:", error.config?.url);
    } else if (!error.response) {
      console.error(
        "[SkillBridge] API request failed (network/CORS/no response):",
        error.config?.url
      );
    }
    return Promise.reject(error);
  }
);

// Attach token to every request
api.interceptors.request.use((config) => {
  const token = typeof window !== "undefined" ? localStorage.getItem("skillbridge_token") : null;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export function setAuth(token: string, user: any) {
  localStorage.setItem("skillbridge_token", token);
  localStorage.setItem("skillbridge_user", JSON.stringify(user));
}

export function getAuthUser(): any | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem("skillbridge_user");
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function clearAuth() {
  localStorage.removeItem("skillbridge_token");
  localStorage.removeItem("skillbridge_user");
}

/**
 * Turn any error from an API call into a plain string that is safe to render.
 *
 * Why: FastAPI returns `detail` as a STRING for errors we raise ourselves
 * (e.g. "Invalid credentials") but as an ARRAY of objects for validation
 * errors (422). Putting an array of objects into React state and rendering it
 * crashes the page, so we always convert to text here.
 */
export function getErrorMessage(err: unknown, fallback = "Something went wrong. Please try again."): string {
  const e = err as any;

  if (e?.code === "ECONNABORTED") {
    return "The server took too long to respond. Free hosting can need up to a minute to wake up - please try again.";
  }
  if (e && !e.response && (e.request || e.message === "Network Error")) {
    return "Cannot reach the server. Check your internet connection, or the backend may be offline or still starting.";
  }

  const detail = e?.response?.data?.detail;
  if (typeof detail === "string" && detail.trim()) return detail;

  if (Array.isArray(detail) && detail.length > 0) {
    const parts = detail
      .map((item: any) => {
        if (typeof item === "string") return item;
        if (item && typeof item.msg === "string") {
          const loc: any[] = Array.isArray(item.loc) ? item.loc : [];
          const field = [...loc].reverse().find((x) => typeof x === "string" && x !== "body");
          const msg = item.msg.replace(/^Value error, /, "");
          return field ? `${field}: ${msg}` : msg;
        }
        return "";
      })
      .filter(Boolean);
    if (parts.length > 0) return parts.join("; ");
  }

  if (detail && typeof detail === "object" && typeof (detail as any).msg === "string") {
    return (detail as any).msg;
  }

  return fallback;
}

/**
 * Read the logged-in user from localStorage ONCE, after the page has mounted.
 *
 * Why not just call getAuthUser() in the component body? It returns a brand-new
 * object on every render, so using it in a useEffect dependency array makes the
 * effect re-run after every render -> endless API requests. Reading it once in
 * an effect also avoids server/browser HTML mismatches (the server has no
 * localStorage). `ready` is false until the first read has finished.
 */
export function useAuthUser(): { user: any | null; ready: boolean } {
  const [user, setUser] = useState<any | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    setUser(getAuthUser());
    setReady(true);
  }, []);

  return { user, ready };
}
