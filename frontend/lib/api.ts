// Typed fetch wrapper that attaches the JWT and transparently refreshes once
// on a 401. All API calls in the app go through `api()`.
import { API_BASE, getAccess, refresh } from "./auth";

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

async function request<T>(
  path: string,
  options: RequestInit,
  retry = true,
): Promise<T> {
  const access = getAccess();
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(access ? { Authorization: `Bearer ${access}` } : {}),
      ...(options.headers ?? {}),
    },
  });

  if (res.status === 401 && retry) {
    const newToken = await refresh();
    if (newToken) return request<T>(path, options, false);
  }

  if (!res.ok) {
    throw new ApiError(res.status, `Request failed (${res.status})`);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  get: <T>(path: string) => request<T>(path, { method: "GET" }),
  post: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "POST", body: JSON.stringify(body) }),
};

// ---- API response types (mirror the DRF serializers) ----
export interface Profile {
  date_of_birth: string | null;
  sex: string;
  height_cm: number | null;
  activity_level: string;
  goal: string;
  age: number | null;
}

export interface Me {
  id: number;
  email: string;
  full_name: string;
  role: string;
  profile: Profile;
}

export interface WeeklySummary {
  workout_sessions: number;
  last_workout: string | null;
  avg_reps: number | null;
  latest_weight_kg: number | null;
}

export interface CoachMessage {
  id: number;
  role: "user" | "assistant" | "system";
  content: string;
  was_blocked: boolean;
  block_reason: string;
  created: string;
}

export interface Conversation {
  id: number;
  title: string;
  created: string;
}
