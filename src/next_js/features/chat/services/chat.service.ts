import { SendMessagePayload } from "@/app/chat/chat.types";

export async function sendMessage(payload: SendMessagePayload) {
  const response = await fetch(
    "http://localhost:8000/ask",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    }
  );

  return response.json();
}