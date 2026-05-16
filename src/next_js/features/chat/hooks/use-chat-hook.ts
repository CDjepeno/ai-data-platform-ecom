"use client";

import { useState } from "react";

import {
  ChatMessage,
  MessageRole,
} from "@/app/chat/chat.types";

export function useChatHook() {

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSendMessage = async (
    content: string
  ) => {

    if (!content.trim()) return;

    setLoading(true);

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: MessageRole.USER,
      content,
      createdAt: new Date().toISOString(),
    };

    setMessages((prev) => [
      ...prev,
      userMessage,
    ]);

    const assistantId = crypto.randomUUID();

    const assistantMessage: ChatMessage = {
      id: assistantId,
      role: MessageRole.ASSISTANT,
      content: "",
      createdAt: new Date().toISOString(),
    };

    setMessages((prev) => [
      ...prev,
      assistantMessage,
    ]);

    try {

      const response = await fetch(
        "http://127.0.0.1:8000/ask",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            question: content,
          }),
        }
      );

      if (!response.body) {
        throw new Error("No response body");
      }

      const reader = response.body.getReader();

      const decoder = new TextDecoder();

      let done = false;

      let buffer = "";

    while (!done) {

      const result = await reader.read();

      done = result.done;

      const chunk = decoder.decode(
        result.value || new Uint8Array(),
        {
          stream: true,
        }
      );

      if (!chunk) {
        continue;
      }

      buffer += chunk;

      const lines = buffer.split("\n");

      // keep incomplete line in buffer
      buffer = lines.pop() || "";

      for (const line of lines) {

        const trimmed = line.trim();

        if (!trimmed) {
          continue;
        }

        if (!trimmed.startsWith("data: ")) {
          continue;
        }

        const token = trimmed.replace(
          "data: ",
          ""
        );

        setMessages((prev) =>
          prev.map((message) =>
            message.id === assistantId
              ? {
                  ...message,
                  content:
                    message.content + token,
                }
              : message
          )
        );
      }
    }

    } catch (error) {

      console.error(error);

    } finally {

      setLoading(false);
    }
  };

  return {
    messages,
    loading,
    handleSendMessage,
  };
}