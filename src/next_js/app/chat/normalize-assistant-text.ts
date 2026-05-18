/**
 * Répare le texte collé souvent produit par le streaming de tokens LLM.
 */
export function normalizeAssistantText(text: string): string {
  let normalized = text.trim();

  normalized = normalized
    .replace(/([^\s*])(\*\*)/g, "$1 $2")
    .replace(/(\*\*)([^\s*])/g, "$1 $2")
    .replace(/(\*\*[^*]+\*\*)([a-zA-ZÀ-ÿ])/g, "$1 $2")
    .replace(/(\d)([A-Za-zÀ-ÿ])/g, "$1 $2")
    .replace(/([A-Za-zÀ-ÿ])(\d)/g, "$1 $2");

  normalized = normalized.replace(
    /([a-zÀ-ÿ])(have|total|customers?|in)(?=[\s*.!,]|$)/gi,
    "$1 $2"
  );

  normalized = normalized.replace(/(in)(total)/gi, "$1 $2");
  normalized = normalized.replace(/^we(?=have)/i, "We ");

  return normalized.replace(/\s{2,}/g, " ");
}
