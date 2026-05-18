
export async function sendMessageStream(
  question: string,
  onChunk: (chunk: string) => void
) {
  const response = await fetch("http://localhost:8000/ask", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      question,
    }),
  });

  if (!response.body) {
    throw new Error("No response body");
  }

  const reader = response.body.getReader();

  const decoder = new TextDecoder();

  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();

    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (!line.startsWith("data:")) {
        continue;
      }

      const clean = line.replace(/^data:\s*/, "").trim();

      if (clean) {
        onChunk(clean);
      }
    }
  }

  if (buffer.trim() && buffer.startsWith("data:")) {
    const clean = buffer.replace(/^data:\s*/, "").trim();

    if (clean) {
      onChunk(clean);
    }
  }
}