"use client";

import { MessageCircle, Send, X } from "lucide-react";
import { useState } from "react";
import { api } from "@/lib/api";

type Msg = { role: "user" | "bot"; text: string };

export function Chatbot() {
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<Msg[]>([
    { role: "bot", text: "Hi! I'm your health assistant. Ask me about lifestyle, nutrition, or NCD awareness. I never diagnose." },
  ]);

  const send = async (text: string) => {
    if (!text.trim()) return;
    setMessages((m) => [...m, { role: "user", text }]);
    setInput("");
    setLoading(true);
    try {
      const res = await api.chatbot(text);
      setMessages((m) => [...m, { role: "bot", text: res.reply }]);
    } catch {
      setMessages((m) => [...m, { role: "bot", text: "Sorry, I couldn't reach the assistant. Please log in and try again." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <button
        onClick={() => setOpen((o) => !o)}
        className="fixed bottom-6 right-6 z-50 flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-600 text-white shadow-glow transition hover:scale-105 hover:bg-brand-500"
        aria-label="Open chatbot"
      >
        {open ? <X className="h-6 w-6" /> : <MessageCircle className="h-6 w-6" />}
      </button>

      {open && (
        <div className="glass fixed bottom-24 right-6 z-50 flex h-[28rem] w-[22rem] flex-col p-4 shadow-card-lg">
          <h3 className="mb-3 flex items-center gap-2 font-semibold">
            <span className="h-2 w-2 rounded-full bg-emerald-500" />
            Health Assistant
          </h3>
          <div className="flex-1 space-y-3 overflow-y-auto pr-1 text-sm">
            {messages.map((m, i) => (
              <div
                key={i}
                className={`max-w-[85%] rounded-2xl px-3.5 py-2 leading-relaxed ${
                  m.role === "user"
                    ? "ml-auto bg-brand-600 text-white"
                    : "bg-ink-100 dark:bg-white/[0.06]"
                }`}
              >
                {m.text}
              </div>
            ))}
            {loading && <div className="text-xs text-ink-400">typing…</div>}
          </div>
          <form
            onSubmit={(e) => { e.preventDefault(); send(input); }}
            className="mt-3 flex gap-2"
          >
            <input
              className="input py-2 text-sm"
              placeholder="Ask a health question…"
              value={input}
              onChange={(e) => setInput(e.target.value)}
            />
            <button className="btn-primary px-3" aria-label="Send">
              <Send className="h-4 w-4" />
            </button>
          </form>
          <p className="mt-2 text-[10px] text-ink-400">
            Not medical advice. For emergencies call your local emergency number.
          </p>
        </div>
      )}
    </>
  );
}
