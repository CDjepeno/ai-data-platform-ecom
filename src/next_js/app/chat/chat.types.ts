export enum MessageRole {
  USER = "user",
  ASSISTANT = "assistant",
  SYSTEM = "system",
}

export interface AgentStep {
  id: string;
  label: string;
  status: "pending" | "running" | "completed";
}

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;

  imageUrl?: string;

  steps?: AgentStep[];

  createdAt: string;
}

export interface SendMessagePayload {
  question: string;
}