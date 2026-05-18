import type { ChatMessage } from "@/app/hooks/use-chat-hook";

import { AssistantMessage } from "@/app/chat/assistant-message";

type ChatMessageBubbleProps = {
  message: ChatMessage;
  isStreaming?: boolean;
};

export function ChatMessageBubble({
  message,
  isStreaming = false,
}: ChatMessageBubbleProps) {
  if (message.role === "user") {
    return (
      <div className="flex justify-end">
        <div className="max-w-3xl rounded-3xl bg-white px-5 py-4 text-black shadow-lg shadow-white/5">
          <p className="text-[15px] leading-relaxed whitespace-pre-wrap">
            {message.content}
          </p>
        </div>
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
