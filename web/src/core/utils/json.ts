import { parse } from "best-effort-json-parser";

export function parseJSON<T>(json: string | null | undefined, fallback: T) {
  if (!json) {
    return fallback;
  }
  try {
    const raw = json
      .trim()
      .replace(/^```js\s*/, "")
      .replace(/^```json\s*/, "")
      .replace(/^```ts\s*/, "")
      .replace(/^```plaintext\s*/, "")
      .replace(/^```\s*/, "")
      .replace(/\s*```$/, "")
      .replace(/\(\)$/, "");
    
    return parse(raw) as T;
  } catch (error) {
    return fallback;
  }
}
