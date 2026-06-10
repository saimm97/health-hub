// Minimal JWT auth against the Django SimpleJWT endpoints.
// Tokens are kept in localStorage for this starter; for production prefer
// httpOnly cookies (noted in the frontend README).

const ACCESS = "hh_access";
const REFRESH = "hh_refresh";

export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000/api/v1";

export function getAccess(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(ACCESS);
}

function getRefresh(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(REFRESH);
}

function store(access: string, refresh?: string) {
  localStorage.setItem(ACCESS, access);
  if (refresh) localStorage.setItem(REFRESH, refresh);
}

export function logout() {
  localStorage.removeItem(ACCESS);
  localStorage.removeItem(REFRESH);
}

export async function login(email: string, password: string): Promise<void> {
  const res = await fetch(`${API_BASE}/auth/token/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error("Invalid email or password");
  const data = await res.json();
  store(data.access, data.refresh);
}

// Try to refresh the access token; returns the new token or null.
export async function refresh(): Promise<string | null> {
  const token = getRefresh();
  if (!token) return null;
  const res = await fetch(`${API_BASE}/auth/token/refresh/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh: token }),
  });
  if (!res.ok) return null;
  const data = await res.json();
  store(data.access);
  return data.access;
}
