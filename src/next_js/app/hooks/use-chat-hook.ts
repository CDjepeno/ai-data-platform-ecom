"use client";

import { useState } from "react";
import { v4 as uuidv4 } from "uuid";

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  steps?: ChatStep[];
};

export type ChatStep = {
  id: string;
  label: string;
};

export function useChatHook() {

  const [messages, setMessages] =
    useState<ChatMessage[]>([]);

  const [steps, setSteps] =
    useState<ChatStep[]>([]);

  const [loading, setLoading] =
    useState(false);

  const [completedMessageIds, setCompletedMessageIds] = useState<Set<string>>(new Set());

  const handleSendMessage = async (
    question: string
  ) => {

    if (!question.trim() || loading) {
      return;
    }

    // RESET STEPS
    setSteps([]);

    // USER MESSAGE
    const userMessage: ChatMessage = {
      id: uuidv4(),
      role: "user",
      content: question,
    };

    setMessages((prev) => [
      ...prev,
      userMessage,
    ]);

    // ASSISTANT PLACEHOLDER
    const assistantId =
      uuidv4();

    const assistantMessage: ChatMessage = {
      id: assistantId,
      role: "assistant",
      content: "",
    };

    setMessages((prev) => [
      ...prev,
      assistantMessage,
    ]);

    setLoading(true);

    try {

      const FASTAPI_URL = process.env.NEXT_PUBLIC_FASTAPI_URL ?? "http://api.ecom.local:8888";

      const response = await fetch(
        `${FASTAPI_URL}/ask`,
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            question,
          }),
        }
      );

      if (!response.body) {
        throw new Error(
          "No response body"
        );
      }

      const reader =
        response.body.getReader();

      const decoder =
        new TextDecoder();

      let buffer = "";

      let assistantContent = "";

      const updateAssistantMessage = () => {

        setMessages((prev) =>
          prev.map((message) =>
            message.id === assistantId
              ? {
                  ...message,
                  content:
                    assistantContent,
                }
              : message
          )
        );
      };

      const addStep = (label: string) => {
      setMessages((prev) =>
        prev.map((message) =>
          message.id === userMessage.id
            ? {
                ...message,
                steps: [
                  ...(message.steps ?? []),
                  { id: uuidv4(), label },
                ],
              }
            : message
        )
      );
    };

      const parseSseLine = (
        line: string
      ) => {

        if (
          !line.startsWith("data:")
        ) {
          return;
        }

        const token = line
          .replace(/^data:\s*/, "");

        if (!token.trim()) {
          return;
        }

        // STEP EVENT
        if (
          token.startsWith("[STEP]")
        ) {

          const cleanStep =
            token.replace(
              "[STEP]",
              ""
            );

          addStep(cleanStep);

          return;
        }

        // ERROR EVENT
        if (
          token.startsWith("[ERROR]")
        ) {

          assistantContent =
            "An error occurred.";

          updateAssistantMessage();

          return;
        }

        // NORMAL AI TOKEN
        assistantContent +=
          token + " ";

        updateAssistantMessage();
      };

      while (true) {

        const {
          done,
          value,
        } = await reader.read();

        if (done) {
          break;
        }

        buffer += decoder.decode(
          value,
          {
            stream: true,
          }
        );

        const lines =
          buffer.split("\n");

        buffer =
          lines.pop() ?? "";

        for (const line of lines) {

          parseSseLine(line);
        }
      }

      // flush final buffer
      if (buffer.trim()) {

        parseSseLine(buffer);
      }

    } catch (error) {

      console.error(error);

    } finally {

      setLoading(false);

      setTimeout(() => {
        setCompletedMessageIds(prev => new Set([...prev, userMessage.id]));
      }, 2000);
    }
  };

  return {
    messages,
    loading,
    handleSendMessage,
    completedMessageIds
  };
}