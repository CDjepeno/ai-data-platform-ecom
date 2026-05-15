"use client";

import { useState } from "react";
import { useChatHook } from "@/features/chat/hooks/use-chat-hook";
import { ChatMessage } from "./chat/chat.types";

export default function AIChatDashboard() {
  const { messages, loading, handleSendMessage } =
    useChatHook();

  const [input, setInput] = useState<string>("");

  const conversations = [
    {
      id: 1,
      title: "Analyse ventes Q1",
      time: "2m ago",
    },
    {
      id: 2,
      title: "Pipeline dbt marketing",
      time: "1h ago",
    },
    {
      id: 3,
      title: "SQL optimisation",
      time: "Yesterday",
    },
  ];

  const handleSubmit = async () => {
    if (!input.trim()) return;

    await handleSendMessage(input);

    setInput("");
  };

  return (
    <div className="flex h-screen overflow-hidden bg-zinc-950 text-zinc-100">
      {/* SIDEBAR */}
      <aside className="flex w-[300px] flex-col border-r border-white/10 bg-black/30 backdrop-blur-xl">
        <div className="border-b border-white/10 p-4">
          <button className="w-full rounded-2xl bg-white py-3 font-medium text-black transition hover:opacity-90">
            + Nouveau chat
          </button>
        </div>

        <div className="flex-1 space-y-2 overflow-y-auto px-3 py-4">
          {conversations.map((chat) => (
            <button
              key={chat.id}
              className="w-full rounded-2xl border border-white/5 bg-white/[0.03] p-4 text-left transition hover:bg-white/[0.06]"
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="line-clamp-1 text-sm font-medium">
                    {chat.title}
                  </p>

                  <p className="mt-1 text-xs text-zinc-500">
                    {chat.time}
                  </p>
                </div>
              </div>
            </button>
          ))}
        </div>

        <div className="border-t border-white/10 p-4">
          <div className="rounded-2xl border border-white/5 bg-white/[0.03] p-4">
            <p className="text-sm font-medium">
              LLM Connected
            </p>

            <p className="mt-1 text-xs text-zinc-500">
              FastAPI + LangGraph + dbt
            </p>
          </div>
        </div>
      </aside>

      {/* MAIN CHAT */}
      <main className="relative flex flex-1 flex-col">
        {/* HEADER */}
        <header className="flex h-16 items-center justify-between border-b border-white/10 bg-zinc-950/70 px-6 backdrop-blur-xl">
          <div>
            <h1 className="text-lg font-semibold">
              AI Data Assistant
            </h1>

            <p className="text-xs text-zinc-500">
              Analyse • SQL • dbt • LangGraph
            </p>
          </div>

          <div className="flex items-center gap-2">
            <div className="h-2 w-2 animate-pulse rounded-full bg-green-500" />

            <span className="text-sm text-zinc-400">
              Online
            </span>
          </div>
        </header>

        {/* MESSAGES */}
        <div className="flex-1 overflow-y-auto px-6 py-8">
          <div className="mx-auto max-w-4xl space-y-8">
            {messages.map((message: ChatMessage) => (
              <div
                key={message.id}
                className={`flex ${
                  message.role === "user"
                    ? "justify-end"
                    : "justify-start"
                }`}
              >
                <div
                  className={`max-w-2xl rounded-3xl border px-5 py-4 ${
                    message.role === "user"
                      ? "border-white bg-white text-black"
                      : "border-white/10 bg-white/[0.03]"
                  }`}
                >
                  <p className="text-sm leading-7 md:text-base">
                    {message.content}
                  </p>

                  {message.steps &&
                    message.steps.length > 0 && (
                      <div className="mt-5 space-y-2 border-t border-white/10 pt-4">
                        <p className="text-xs uppercase tracking-wide text-zinc-500">
                          Agent workflow
                        </p>

                        {message.steps.map((step) => (
                          <div
                            key={step.id}
                            className="flex items-center gap-3 text-sm text-zinc-300"
                          >
                            <div
                              className={`h-2 w-2 rounded-full ${
                                step.status === "completed"
                                  ? "bg-green-500"
                                  : step.status === "running"
                                  ? "bg-yellow-500"
                                  : "bg-zinc-500"
                              }`}
                            />

                            <span>{step.label}</span>
                          </div>
                        ))}
                      </div>
                    )}
                </div>
              </div>
            ))}

            {/* Typing */}
            {loading && (
              <div className="flex justify-start">
                <div className="flex items-center gap-2 rounded-3xl border border-white/10 bg-white/[0.03] px-5 py-4">
                  <div className="h-2 w-2 animate-bounce rounded-full bg-zinc-400" />

                  <div className="h-2 w-2 animate-bounce rounded-full bg-zinc-400 delay-100" />

                  <div className="h-2 w-2 animate-bounce rounded-full bg-zinc-400 delay-200" />
                </div>
              </div>
            )}
          </div>
        </div>

        {/* INPUT */}
        <div className="border-t border-white/10 bg-zinc-950/80 p-6 backdrop-blur-xl">
          <div className="mx-auto max-w-4xl">
            {/* Suggestions */}
            <div className="mb-4 flex flex-wrap gap-2">
              {[
                "Analyse mes KPIs",
                "Explique ce modèle dbt",
                "Génère une requête SQL",
                "Résume les anomalies",
              ].map((suggestion: string) => (
                <button
                  key={suggestion}
                  onClick={() => setInput(suggestion)}
                  className="rounded-full border border-white/10 bg-white/[0.03] px-4 py-2 text-sm transition hover:bg-white/[0.06]"
                >
                  {suggestion}
                </button>
              ))}
            </div>

            {/* Chat Input */}
            <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-3 shadow-2xl shadow-black/20">
              <div className="flex items-end gap-3">
                {/* Upload button */}
                <button className="flex h-11 w-11 items-center justify-center rounded-2xl bg-white/[0.05] text-xl transition hover:bg-white/[0.08]">
                  +
                </button>

                {/* Textarea */}
                <textarea
                  value={input}
                  onChange={(
                    e: React.ChangeEvent<HTMLTextAreaElement>
                  ) => setInput(e.target.value)}
                  onKeyDown={async (
                    e: React.KeyboardEvent<HTMLTextAreaElement>
                  ) => {
                    if (
                      e.key === "Enter" &&
                      !e.shiftKey
                    ) {
                      e.preventDefault();

                      await handleSubmit();
                    }
                  }}
                  placeholder="Ask anything about your data..."
                  rows={1}
                  className="max-h-40 flex-1 resize-none bg-transparent pt-3 text-sm outline-none placeholder:text-zinc-500"
                />

                {/* Send button */}
                <button
                  onClick={handleSubmit}
                  disabled={loading}
                  className="h-11 rounded-2xl bg-white px-5 font-medium text-black transition hover:opacity-90 disabled:opacity-50"
                >
                  {loading ? "..." : "Send"}
                </button>
              </div>

              <div className="mt-3 flex items-center justify-between px-1">
                <div className="flex items-center gap-2 text-xs text-zinc-500">
                  <span>Image upload ready</span>

                  <span>•</span>

                  <span>Streaming enabled</span>
                </div>

                <div className="text-xs text-zinc-500">
                  GPT + LangGraph Agent
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}