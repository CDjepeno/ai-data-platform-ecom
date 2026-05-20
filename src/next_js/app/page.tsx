"use client";

import { ChatMessageBubble } from "@/app/chat/chat-message";
import { useChatHook } from "@/app/hooks/use-chat-hook";
import { useEffect, useRef, useState } from "react";

export default function HomePage() {

  const {
    messages,
    loading,
    handleSendMessage,
    completedMessageIds,
  } = useChatHook();

  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async () => {
    if (!input.trim()) return;
    await handleSendMessage(input);
    setInput("");
  };

  return (
    <div className="flex h-screen overflow-hidden bg-[#080810] text-white">

      {/* Gradient orbs background */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -top-40 -left-40 h-96 w-96 rounded-full bg-violet-600/10 blur-3xl" />
        <div className="absolute top-1/2 -right-40 h-80 w-80 rounded-full bg-blue-600/8 blur-3xl" />
        <div className="absolute -bottom-40 left-1/3 h-96 w-96 rounded-full bg-emerald-600/8 blur-3xl" />
      </div>

      {/* Sidebar */}
      <aside className="relative hidden w-64 shrink-0 border-r border-white/5 bg-white/[0.02] lg:flex lg:flex-col">

        <div className="p-4">
          <button
            type="button"
            className="group w-full rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-left text-base text-white/70 transition-all duration-200 hover:border-white/20 hover:bg-white/[0.07] hover:text-white cursor-pointer"
          >
            <span className="mr-2 text-white/40 group-hover:text-white/60">+</span>
            New chat
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-3 pb-4">
          <p className="mb-2 px-2 text-[11px] font-medium uppercase tracking-widest text-white/20">
            Recent
          </p>
          <div className="space-y-1">
            {[
              "Q1 Sales Analysis",
              "dbt Marketing Pipeline",
              "SQL Optimization",
            ].map((item, index) => (
              <div
                key={index}
                className="cursor-pointer rounded-lg px-3 py-2.5 text-[15px] text-white/40 transition-all duration-150 hover:bg-white/[0.04] hover:text-white/70"
              >
                {item}
              </div>
            ))}
          </div>
        </div>

        {/* Sidebar bottom */}
        <div className="border-t border-white/5 p-4">
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" />
            <span className="text-sm text-white/30">Pipeline connected</span>
          </div>
        </div>
      </aside>

      {/* Main */}
      <main className="relative flex min-h-0 min-w-0 flex-1 flex-col">

        {/* Header */}
        <header className="shrink-0 border-b border-white/5 px-8 py-5">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-violet-500 to-blue-500 text-sm font-bold">
              AI
            </div>
            <h1 className="bg-gradient-to-r from-white via-white/90 to-white/50 bg-clip-text text-2xl font-semibold text-transparent">
              AI Data Assistant
            </h1>
          </div>
        </header>

        {/* Messages */}
        <section className="min-h-0 flex-1 overflow-y-auto px-8 py-8 [scrollbar-width:thin] [scrollbar-color:rgba(255,255,255,0.08)_transparent]">
          <div className="mx-auto flex max-w-3xl flex-col gap-8">

            {messages.length === 0 && (
              <div className="flex flex-col items-center justify-center py-24 text-center">
                <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-violet-500/20 to-blue-500/20 text-2xl">
                  ✦
                </div>
                <p className="text-lg font-medium text-white/40">
                  Ask a question about your data
                </p>
                <p className="mt-2 text-base text-white/20">
                  Revenue, orders, customers — ask in natural language
                </p>
              </div>
            )}

            {messages.map((message, index) => {
              const isLastMessage = index === messages.length - 1;
              const isStreaming = loading && isLastMessage && message.role === "assistant";
              return (
                <ChatMessageBubble
                  key={message.id}
                  message={message}
                  isStreaming={isStreaming}
                  hideSteps={completedMessageIds.has(message.id)}
                />
              );
            })}

            <div ref={bottomRef} />
          </div>
        </section>

        {/* Footer */}
        <footer className="shrink-0 px-8 py-5">
          <div className="mx-auto max-w-3xl">

            <div
              className="relative rounded-2xl p-[1px]"
              style={{
                background: "linear-gradient(135deg, rgba(139,92,246,0.4), rgba(59,130,246,0.3), rgba(52,211,153,0.2))",
              }}
            >
              <div className="rounded-2xl bg-[#0d0d18] px-4 py-3">
                <div className="flex items-end gap-3">
                  <textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={async (e) => {
                      if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        await handleSubmit();
                      }
                    }}
                    placeholder="Ask a question about your data..."
                    rows={1}
                    className="flex-1 resize-none bg-transparent py-2 text-base text-white/80 outline-none placeholder:text-white/20"
                    style={{ lineHeight: "1.6" }}
                  />
                  <button
                    type="button"
                    onClick={handleSubmit}
                    disabled={loading}
                    className="shrink-0 cursor-pointer rounded-xl bg-gradient-to-r from-violet-600 to-blue-600 px-5 py-2.5 text-base font-medium text-white transition-all duration-200 hover:opacity-90 hover:-translate-y-0.5 active:translate-y-0 disabled:cursor-not-allowed disabled:opacity-30"
                  >
                    {loading ? (
                      <span className="flex items-center gap-1.5">
                        <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-white" style={{ animationDelay: "0ms" }} />
                        <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-white" style={{ animationDelay: "150ms" }} />
                        <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-white" style={{ animationDelay: "300ms" }} />
                      </span>
                    ) : "Send"}
                  </button>
                </div>
              </div>
            </div>

            <p className="mt-2 text-center text-xs text-white/15">
              Connected to dbt MetricFlow · Trino · Iceberg
            </p>
          </div>
        </footer>

      </main>
    </div>
  );
}