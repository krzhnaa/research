// frontend/src/types.ts
export type MessageRole = "user" | "assistant" | "system";

export interface ChatMessage {
  id: string;
  role: MessageRole;
  type: "text" | "progress" | "report" | "error";
  content?: string;
  progressStep?: string;
  report?: import("./api/client").ResearchResult;
}

export const AVAILABLE_MODELS = [
  { id: "openai/gpt-oss-120b:free", label: "GPT-OSS 120B (Free)" },
  { id: "openai/gpt-oss-20b:free", label: "GPT-OSS 20B (Free, faster)" },
  { id: "z-ai/glm-4.5-air:free", label: "GLM 4.5 Air (Free)" },
  { id: "nvidia/nemotron-3-super-120b-a12b:free", label: "Nemotron 3 Super (Free)" },
];