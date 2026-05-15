"use client";

import { useState } from "react";
import { sendMessage } from "../services/chat.service";
import { ChatMessage, MessageRole } from "@/app/chat/chat.types";

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
    
    try {
        const data = await sendMessage({
            question: content,
      });
      
    const assistantMessage = {
        id: crypto.randomUUID(),
        role: MessageRole.ASSISTANT,
        content: data.response,
        createdAt: new Date().toISOString(),
      };

      setMessages((prev) => [
        ...prev,
        assistantMessage,
      ]);
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