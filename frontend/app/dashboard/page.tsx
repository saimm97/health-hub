"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import NavBar from "@/components/NavBar";
import { api, type Me, type WeeklySummary } from "@/lib/api";
import { getAccess } from "@/lib/auth";

export default function DashboardPage() {
  const router = useRouter();
  const [me, setMe] = useState<Me | null>(null);
  const [summary, setSummary] = useState<WeeklySummary | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!getAccess()) {
      router.replace("/login");
      return;
    }
    Promise.all([
      api.get<Me>("/accounts/me/"),
      api.get<WeeklySummary>("/fitness/workout-logs/weekly_summary/"),
    ])
      .then(([m, s]) => {
        setMe(m);
        setSummary(s);
      })
      .catch(() => setError("Could not load your data. Is the API running?"));
  }, [router]);

  return (
    <div className="min-h-screen flex flex-col">
      <NavBar />
      <main className="flex-1 max-w-6xl mx-auto w-full px-4 py-8">
        {error && <p className="text-red-600 text-sm">{error}</p>}
        {me && summary && (
          <>
            <h1 className="text-2xl font-semibold text-slate-900">
              Welcome{me.full_name ? `, ${me.full_name}` : ""}
            </h1>
            <p className="text-sm text-slate-500 mb-6">Your last 7 days at a glance.</p>
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <Stat label="Workouts (7d)" value={summary.workout_sessions} />
              <Stat label="Latest weight" value={summary.latest_weight_kg ?? "—"} suffix=" kg" />
              <Stat label="Avg reps" value={summary.avg_reps ? Math.round(summary.avg_reps) : "—"} />
              <Stat label="Role" value={me.role} />
            </div>
            <div className="mt-8 bg-white border border-slate-200 rounded-2xl p-6 max-w-md">
              <h2 className="font-semibold text-slate-900 mb-4">Profile</h2>
              <dl className="space-y-2 text-sm">
                <Row k="Email" v={me.email} />
                <Row k="Age" v={me.profile.age ?? "—"} />
                <Row k="Activity" v={me.profile.activity_level} />
                <Row k="Goal" v={me.profile.goal || "Not set"} />
              </dl>
            </div>
          </>
        )}
      </main>
    </div>
  );
}

function Stat({ label, value, suffix }: { label: string; value: React.ReactNode; suffix?: string }) {
  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-5">
      <p className="text-xs uppercase tracking-wide text-slate-400">{label}</p>
      <p className="mt-1 text-3xl font-semibold text-slate-900">
        {value}
        {suffix && <span className="text-base text-slate-400">{suffix}</span>}
      </p>
    </div>
  );
}

function Row({ k, v }: { k: string; v: React.ReactNode }) {
  return (
    <div className="flex justify-between">
      <dt className="text-slate-500">{k}</dt>
      <dd className="font-medium">{v}</dd>
    </div>
  );
}
