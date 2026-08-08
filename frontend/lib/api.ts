"use client";

import axios from "axios";

export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" },
});

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

