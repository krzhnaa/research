import { useState } from "react";
import { Send } from "lucide-react";
import ModelSelector from "./ModelSelector";

interface Props {
  onSubmit: (input: string, model: string) => void;
  disabled: boolean;
}

export default function InputBar({ onSubmit, disabled }: Props) {
  const [input, setInput] = useState("");
  const [model, setModel] = useState("openai/gpt-oss-120b:free");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim() || disabled) return;
    onSubmit(input.trim(), model);
    setInput("");
  }

  return (
    <form onSubmit={handleSubmit} className="border-t border-slate-200/80 bg-white/80 px-4 py-5 backdrop-blur-xl md:px-10">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-4">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="field-label">Prompt</p>
            <p className="mt-1 text-sm text-slate-500">Enter a company name or website to start a new brief.</p>
          </div>
          <ModelSelector value={model} onChange={setModel} />
        </div>

        <div className="panel flex flex-col gap-3 p-3 sm:flex-row sm:items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Enter a company name (e.g. Tesla) or website URL (e.g. https://tesla.com)"
            disabled={disabled}
            className="text-input flex-1 border-0 bg-transparent shadow-none disabled:cursor-not-allowed disabled:opacity-60"
          />
          <button
            type="submit"
            disabled={disabled || !input.trim()}
            className="inline-flex items-center justify-center gap-2 rounded-2xl bg-sky-500 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-sky-200 transition hover:-translate-y-0.5 hover:bg-sky-600 disabled:cursor-not-allowed disabled:opacity-40 sm:min-w-36"
          >
            <Send className="h-4 w-4" />
            Send
          </button>
        </div>
      </div>
    </form>
  );
}
