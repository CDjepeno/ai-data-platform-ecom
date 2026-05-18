"use client";

import { ChatMessageBubble } from "@/app/chat/chat-message";
import { useChatHook } from "@/app/hooks/use-chat-hook";
import { useEffect, useRef, useState } from "react";

export default function HomePage() {

  const {
    messages,
    steps,
    loading,
    handleSendMessage,
  } = useChatHook();

  const [input, setInput] =
    useState("");

  const bottomRef =
    useRef<HTMLDivElement>(null);

  useEffect(() => {

    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
    });

  }, [messages, steps]);

  const handleSubmit = async () => {

    if (!input.trim()) {
      return;
    }

    await handleSendMessage(
      input
    );

    setInput("");
  };

  return (

    <div
      className="
        flex
        h-screen
        overflow-hidden
        bg-black
        text-white
      "
    >

      {/* Sidebar */}

      <aside
        className="
          hidden
          w-72
          shrink-0
          border-r
          border-white/10
          bg-zinc-950
          lg:flex
          lg:flex-col
        "
      >

        <div className="p-4">

          <button
            type="button"
            className="
              w-full
              rounded-2xl
              bg-white
              px-4
              py-4
              text-black
            "
          >
            + Nouveau chat
          </button>

        </div>

        <div
          className="
            flex-1
            overflow-y-auto
            px-3
          "
        >

          <div className="space-y-3">

            {[
              "Analyse ventes Q1",
              "Pipeline dbt marketing",
              "SQL optimisation",
            ].map((item, index) => (

              <div
                key={index}
                className="
                  rounded-3xl
                  border
                  border-white/10
                  bg-white/[0.02]
                  p-4
                  transition
                  hover:bg-white/[0.04]
                "
              >

                <p className="text-sm">
                  {item}
                </p>

              </div>

            ))}

          </div>

        </div>

      </aside>

      {/* Main */}

      <main
        className="
          flex
          min-h-0
          min-w-0
          flex-1
          flex-col
        "
      >

        {/* Header */}

        <header
          className="
            shrink-0
            border-b
            border-white/10
            px-6
            py-5
          "
        >

          <h1
            className="
              text-3xl
              font-semibold
            "
          >
            AI Data Assistant
          </h1>

        </header>

        {/* Messages */}

        <section
          className="
            min-h-0
            flex-1
            overflow-y-auto
            px-6
            py-8
          "
        >

          <div
            className="
              mx-auto
              flex
              max-w-4xl
              flex-col
              gap-6
            "
          >

            {/* STEPS */}

            {loading && steps.length > 0 && (

              <div
                className="
                  mb-2
                  rounded-3xl
                  border
                  border-emerald-500/20
                  bg-emerald-500/5
                  p-5
                "
              >

                <div
                  className="
                    mb-3
                    text-xs
                    font-semibold
                    uppercase
                    tracking-wider
                    text-emerald-400
                  "
                >
                  Live execution
                </div>

                <div
                  className="
                    flex
                    flex-col
                    gap-3
                  "
                >

                  {steps.map((step) => (

                    <div
                      key={step.id}
                      className="
                        flex
                        items-center
                        gap-3
                        text-sm
                        text-zinc-300
                      "
                    >

                      <div
                        className="
                          h-2
                          w-2
                          animate-pulse
                          rounded-full
                          bg-emerald-400
                        "
                      />

                      <span>
                        {step.label}
                      </span>

                    </div>

                  ))}

                </div>

              </div>

            )}

            {/* MESSAGES */}

            {messages.map((message, index) => {

              const isLastMessage =
                index ===
                messages.length - 1;

              const isStreaming =
                loading &&
                isLastMessage &&
                message.role ===
                  "assistant";

              return (

                <ChatMessageBubble
                  key={message.id}
                  message={message}
                  isStreaming={
                    isStreaming
                  }
                />

              );
            })}

            <div ref={bottomRef} />

          </div>

        </section>

        {/* Footer */}

        <footer
          className="
            shrink-0
            border-t
            border-white/10
            bg-zinc-950
            p-6
          "
        >

          <div
            className="
              mx-auto
              max-w-4xl
            "
          >

            <div
              className="
                rounded-3xl
                border
                border-white/10
                bg-white/[0.03]
                p-3
              "
            >

              <div
                className="
                  flex
                  items-end
                  gap-3
                "
              >

                <textarea
                  value={input}
                  onChange={(e) =>
                    setInput(
                      e.target.value
                    )
                  }
                  onKeyDown={async (
                    e
                  ) => {

                    if (
                      e.key ===
                        "Enter" &&
                      !e.shiftKey
                    ) {

                      e.preventDefault();

                      await handleSubmit();
                    }
                  }}
                  placeholder="
Pose une question sur tes données...
"
                  rows={1}
                  className="
                    flex-1
                    resize-none
                    bg-transparent
                    py-3
                    text-sm
                    outline-none
                  "
                />

                <button
                  type="button"
                  onClick={
                    handleSubmit
                  }
                  disabled={loading}
                  className="
                    shrink-0
                    rounded-2xl
                    bg-white
                    px-5
                    py-3
                    text-black
                    transition
                    hover:opacity-90
                    disabled:opacity-50
                  "
                >
                  {loading
                    ? "..."
                    : "Send"}
                </button>

              </div>

            </div>

          </div>

        </footer>

      </main>

    </div>
  );
}