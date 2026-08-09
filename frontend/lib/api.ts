"use client";

import axios from "axios";

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
  timeout: 10000, // surface failures instead of hanging forever
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

