import type { ReactNode } from "react";

import { normalizeAssistantText } from "@/app/chat/normalize-assistant-text";

type Block =
  | { type: "paragraph"; text: string }
  | { type: "list"; items: string[] };

function splitBlocks(content: string): Block[] {
  const lines = content.split("\n");
  const blocks: Block[] = [];
  let paragraph: string[] = [];
  let list: string[] = [];

  const flushParagraph = () => {
    const text = paragraph.join(" ").trim();
    if (text) {
      blocks.push({ type: "paragraph", text });
    }
    paragraph = [];
  };

  const flushList = () => {
    if (list.length > 0) {
      blocks.push({ type: "list", items: [...list] });
      list = [];
    }
  };

  for (const line of lines) {
    const trimmed = line.trim();

    if (/^[-*]\s+/.test(trimmed)) {
      flushParagraph();
      list.push(trimmed.replace(/^[-*]\s+/, ""));
      continue;
    }

    flushList();

    if (!trimmed) {
      flushParagraph();
      continue;
    }

    paragraph.push(trimmed);
  }

  flushList();
  flushParagraph();

  return blocks;
}

function highlightNumbers(text: string, keyPrefix: number): ReactNode[] {
  const parts: ReactNode[] = [];
  const regex = /\d[\d,]*(?:\.\d+)?%?/g;
  let lastIndex = 0;
  let match: RegExpExecArray | null;
  let key = 0;

  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(
        <span key={`${keyPrefix}-t-${key++}`}>
          {text.slice(lastIndex, match.index)}
        </span>
      );
    }

    parts.push(
      <span
        key={`${keyPrefix}-n-${key++}`}
        className="font-semibold text-emerald-400 tabular-nums"
      >
        {match[0]}
      </span>
    );

    lastIndex = match.index + match[0].length;
  }

  if (lastIndex < text.length) {
    parts.push(
      <span key={`${keyPrefix}-t-${key++}`}>
        {text.slice(lastIndex)}
      </span>
    );
  }

  return parts.length > 0 ? parts : [text];
}

function parseInline(text: string, keyPrefix: number): ReactNode[] {
  const parts: ReactNode[] = [];
  const regex = /\*\*(.+?)\*\*/g;
  let lastIndex = 0;
  let match: RegExpExecArray | null;
  let key = 0;

  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(
        ...highlightNumbers(
          text.slice(lastIndex, match.index),
          keyPrefix * 100 + key++
        )
      );
    }

    parts.push(
      <strong
        key={`${keyPrefix}-b-${key++}`}
        className="font-semibold text-white"
      >
        {highlightNumbers(match[1], keyPrefix * 100 + key++)}
      </strong>
    );

    lastIndex = match.index + match[0].length;
  }

  if (lastIndex < text.length) {
    parts.push(
      ...highlightNumbers(
        text.slice(lastIndex),
        keyPrefix * 100 + key++
      )
    );
  }

  return parts.length > 0 ? parts : highlightNumbers(text, keyPrefix);
}

type AssistantMessageProps = {
  content: string;
  isStreaming?: boolean;
};

export function AssistantMessage({
  content,
  isStreaming = false,
}: AssistantMessageProps) {
  const normalized = normalizeAssistantText(content);
  const blocks = splitBlocks(normalized);

  if (!normalized) {
    return (
      <div className="flex items-center gap-1.5 py-1">
        <span className="size-2 animate-pulse rounded-full bg-white/40" />
        <span className="size-2 animate-pulse rounded-full bg-white/40 [animation-delay:150ms]" />
        <span className="size-2 animate-pulse rounded-full bg-white/40 [animation-delay:300ms]" />
      </div>
    );
  }

  return (
    <div className="space-y-3 text-[15px] leading-relaxed text-zinc-300">
      {blocks.map((block, index) => {
        if (block.type === "list") {
          return (
            <ul
              key={index}
              className="ml-1 list-inside list-disc space-y-1.5 text-zinc-300"
            >
              {block.items.map((item, itemIndex) => (
                <li key={itemIndex}>
                  {parseInline(item, index * 10 + itemIndex)}
                </li>
              ))}
            </ul>
          );
        }

        return (
          <p key={index}>{parseInline(block.text, index)}</p>
        );
      })}

      {isStreaming ? (
        <span
          className="ml-0.5 inline-block h-4 w-0.5 animate-pulse bg-emerald-400/80 align-middle"
          aria-hidden
        />
      ) : null}
    </div>
  );
}
