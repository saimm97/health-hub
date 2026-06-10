"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import NavBar from "@/components/NavBar";
import { api, type Conversation, type CoachMessage } from "@/lib/api";
import { getAccess } from "@/lib/auth";

export default function CoachPage() {
  const router = useRouter();
  const [convo, setConvo] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<CoachMessage[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  // Get (or create) the user's conversation and load its messages.
  useEffect(() => {
    if (!getAccess()) {
      router.replace("/login");
      return;
    }
    (async () => {
      const list = await api.get<{ results: Conversation[] }>("/coach/conversations/");
      const c =
        list.results[0] ??
        (await api.post<Conversation>("/coach/conversations/", { title: "Coaching session" }));
      setConvo(c);
      const msgs = await api.get<CoachMessage[]>(`/coach/conversations/${c.id}/messages/`);
      setMessages(msgs);
    })().catch(() => {});
  }, [router]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function send(e: React.FormEvent) {
    e.preventDefault();
    if (!convo || !input.trim()) return;
    const text = input.trim();
    setInput("");
    setBusy(true);
    // Optimistically show the user's message.
    setMessages((m) => [
      ...m,
      { id: Date.now(), role: "user", content: text, was_blocked: false, block_reason: "", created: "" },
    ]);
    try {
      const reply = await api.post<CoachMessage>(`/coach/conversations/${convo.id}/send/`, { text });
      setMessages((m) => [...m, reply]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      <NavBar />
      <main className="flex-1 max-w-2xl mx-auto w-full px-4 py-8">
        <h1 className="text-2xl font-semibold text-slate-900">AI Coach</h1>
        <p className="text-sm text-slate-500 mb-4">
          Ask about workouts, nutrition and habits. Medical questions are redirected to a doctor.
        </p>

        <div className="bg-slate-50 border border-slate-200 rounded-2xl flex flex-col h-[60vh]">
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {messages.length === 0 && (
              <p className="text-center text-sm text-slate-400 mt-8">
                Try: “Suggest a beginner full-body routine”
              </p>
            )}
            {messages.map((m) => (
              <Bubble key={m.id} m={m} />
            ))}
            <div ref={endRef} />
          </div>

          <form onSubmit={send} className="border-t border-slate-200 p-3 flex gap-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask your coach…"
              className="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-brand-500 focus:ring-1 focus:ring-brand-500 outline-none"
            />
            <button
              type="submit"
              disabled={busy}
              className="bg-brand-600 hover:bg-brand-700 disabled:opacity-60 text-white text-sm font-medium rounded-lg px-4"
            >
              Send
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}

function Bubble({ m }: { m: CoachMessage }) {
  if (m.role === "user") {
    return (
      <div className="flex justify-end">
        <div className="max-w-[80%] bg-brand-600 text-white rounded-2xl rounded-br-sm px-4 py-2.5 text-sm">
          {m.content}
        </div>
      </div>
    );
  }
  return (
    <div className="flex justify-start">
      <div
        className={`max-w-[80%] rounded-2xl rounded-bl-sm px-4 py-2.5 text-sm ${
          m.was_blocked
            ? "bg-amber-50 text-amber-900 border border-amber-200"
            : "bg-white text-slate-700 border border-slate-200"
        }`}
      >
        {m.was_blocked && (
          <p className="text-xs font-medium text-amber-700 mb-1">⚠ Safety guardrail</p>
        )}
        {m.content}
      </div>
    </div>
  );
}
