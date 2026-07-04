import { useEffect, useRef, useState } from "react";
import { v4 as uuidv4 } from "uuid";
import ChatMessage from "./ChatMessage";
import InputBar from "./InputBar";
import { ChatMessage as ChatMessageType } from "../types";
import { researchCompany } from "../api/client";
import ReportSkeleton from "./ReportSkeleton";

export default function ChatWindow() {
  const [messages, setMessages] = useState<ChatMessageType[]>([
    {
      id: uuidv4(),
      role: "assistant",
      type: "text",
      content:
        "Hi! I'm your AI company research assistant. Enter a company name or website URL below, and I'll research it, find competitors, and generate a downloadable PDF report.",
    },
  ]);
  const [isProcessing, setIsProcessing] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleNewResearch() {
      setMessages([
        {
          id: uuidv4(),
          role: "assistant",
          type: "text",
          content:
            "Fresh workspace ready. Enter a company name or website URL and I'll assemble a company brief, competitor snapshot, and PDF report.",
        },
      ]);
      setIsProcessing(false);
    }

    window.addEventListener("new-research", handleNewResearch);
    return () => window.removeEventListener("new-research", handleNewResearch);
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleSubmit(input: string, model: string) {
    const userMsg: ChatMessageType = { id: uuidv4(), role: "user", type: "text", content: input };
    const progressMsgId = uuidv4();

    setMessages((prev) => [
      ...prev,
      userMsg,
      { id: progressMsgId, role: "assistant", type: "progress", progressStep: "resolving_website" },
    ]);
    setIsProcessing(true);

    const stepSequence = ["resolving_website", "crawling", "analyzing", "finding_competitors"];
    let stepIndex = 0;
    const interval = setInterval(() => {
      stepIndex = Math.min(stepIndex + 1, stepSequence.length - 1);
      setMessages((prev) =>
        prev.map((m) => (m.id === progressMsgId ? { ...m, progressStep: stepSequence[stepIndex] } : m))
      );
    }, 3500);

    try {
      const result = await researchCompany(input, model);
      clearInterval(interval);
      setMessages((prev) =>
        prev.map((m) => (m.id === progressMsgId ? { ...m, progressStep: "done" } : m))
      );
      setTimeout(() => {
        setMessages((prev) => [...prev, { id: uuidv4(), role: "assistant", type: "report", report: result }]);
      }, 500);
    } catch (err: any) {
      clearInterval(interval);
      const detail = err?.response?.data?.detail || "Something went wrong. Please try again.";
      setMessages((prev) =>
        prev.filter((m) => m.id !== progressMsgId).concat({
          id: uuidv4(),
          role: "assistant",
          type: "error",
          content: typeof detail === "string" ? detail : JSON.stringify(detail),
        })
      );
    } finally {
      setIsProcessing(false);
    }
  }

  return (
    <div className="flex min-h-[calc(100vh-6rem)] flex-col">
      <div className="flex-1 overflow-y-auto px-4 py-6 md:px-10 md:py-10">
        <div className="mx-auto flex w-full max-w-6xl flex-col gap-8">
          <section className="panel-raised float-in p-8 md:p-10">
            <div className="grid gap-6 lg:grid-cols-[1.4fr_0.8fr] lg:items-end">
              <div>
                <p className="field-label">Research Brief</p>
                <h2 className="mt-3 text-4xl font-semibold tracking-tight text-slate-900">
                  Ask for a company and get a structured intelligence report.
                </h2>
                <p className="mt-4 max-w-3xl text-base leading-8 text-slate-600">
                  The assistant resolves the company site, crawls public pages, extracts market context, highlights likely pain points, and prepares a report you can export or send to Discord.
                </p>
              </div>

              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-1">
                <div className="lift-card rounded-[24px] border border-slate-200 bg-white/90 p-5">
                  <p className="field-label">Output</p>
                  <p className="mt-3 text-2xl font-semibold text-slate-900">PDF + Discord</p>
                  <p className="mt-2 text-sm text-slate-500">Export reports or send them directly to your intake workflow.</p>
                </div>
                <div className="lift-card rounded-[24px] border border-slate-200 bg-white/90 p-5">
                  <p className="field-label">Coverage</p>
                  <p className="mt-3 text-2xl font-semibold text-slate-900">Website + Competitors</p>
                  <p className="mt-2 text-sm text-slate-500">Summaries, pain points, products, and market peers in one place.</p>
                </div>
              </div>
            </div>
          </section>

          <div className="space-y-5">
            {messages.map((msg) => (
              <ChatMessage key={msg.id} message={msg} />
            ))}
            {isProcessing && <ReportSkeleton />}
            <div ref={bottomRef} />
          </div>
        </div>
      </div>

      <InputBar onSubmit={handleSubmit} disabled={isProcessing} />
    </div>
  );
}
