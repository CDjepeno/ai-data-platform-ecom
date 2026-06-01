"use client";

import { useEffect, useState } from "react";
import type { ChatMessage } from "@/app/hooks/use-chat-hook";
import { AssistantMessage } from "@/app/chat/assistant-message";

type ChatMessageBubbleProps = {
  message: ChatMessage;
  isStreaming?: boolean;
  hideSteps?: boolean;
};

export function ChatMessageBubble({
  message,
  isStreaming = false,
  hideSteps = false,
}: ChatMessageBubbleProps) {

  const [stepsVisible, setStepsVisible] = useState(true);
  const [fadingOut, setFadingOut] = useState(false);

  useEffect(() => {
    if (!hideSteps) return;

    // ✅ Les deux setState dans le même setTimeout
    const fadeTimer = setTimeout(() => {
      setFadingOut(true);
    }, 0); // déclenche immédiatement mais de façon asynchrone

    const hideTimer = setTimeout(() => {
      setStepsVisible(false);
    }, 400);

    return () => {
      clearTimeout(fadeTimer);
      clearTimeout(hideTimer);
    };
  }, [hideSteps]);

  if (message.role === "user") {
    return (
      <div className="flex flex-col items-end gap-3">

      {/* Question */}
      <div className="max-w-3xl rounded-3xl bg-white px-5 py-4 text-black shadow-lg shadow-white/5">
        <p className="text-base leading-relaxed whitespace-pre-wrap">
          {message.content}
        </p>
      </div>

      {/* Steps */}
      {message.steps && message.steps.length > 0 && stepsVisible && (
        <div
          className="w-full max-w-3xl rounded-2xl border border-emerald-500/20 bg-emerald-500/5 px-4 py-3"
          style={{
            transition: "opacity 0.4s ease, transform 0.4s ease",
            opacity: fadingOut ? 0 : 1,
            transform: fadingOut ? "translateY(-6px)" : "translateY(0)",
          }}
        >
          <div className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-emerald-400">
            Live execution
          </div>
          <div className="flex flex-col gap-2">
            {message.steps.map((step) => (
              <div
                key={step.id}
                className="flex items-center gap-2 text-sm text-zinc-400"
              >
                <div className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400" />
                <span>{step.label}</span>
              </div>
            ))}
          </div>
        </div>
      )}

    </div>
    );
  }

  return (
    <div className="flex gap-4">
      <div
        className="
          flex
          size-10
          shrink-0
          items-center
          justify-center
          rounded-2xl
          border
          border-emerald-500/20
          bg-emerald-500/10
          text-xs
          font-semibold
          text-emerald-400
        "
        aria-hidden
      >
        AI
      </div>

      <div
        className="
          min-w-0
          max-w-3xl
          flex-1
          rounded-3xl
          border
          border-white/10
          bg-gradient-to-br
          from-white/[0.06]
          to-white/[0.02]
          px-5
          py-4
          shadow-lg
          shadow-black/20
        "
      >
        <AssistantMessage
          content={message.content}
          isStreaming={isStreaming}
        />
      </div>
    </div>
  );
}