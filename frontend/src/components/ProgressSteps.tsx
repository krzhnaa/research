import { CheckCircle2, Loader2 } from "lucide-react";

const STEPS = [
  { key: "resolving_website", label: "Resolving official website" },
  { key: "crawling", label: "Crawling website pages" },
  { key: "analyzing", label: "Analyzing with AI" },
  { key: "finding_competitors", label: "Identifying competitors" },
  { key: "done", label: "Finalizing report" },
];

export default function ProgressSteps({ currentStep }: { currentStep: string }) {
  const currentIndex = STEPS.findIndex((s) => s.key === currentStep);

  return (
    <div className="panel float-in max-w-4xl p-6">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className="field-label">Activity Log</p>
          <p className="mt-2 text-sm text-slate-500">Live crawl and analysis status from the current run.</p>
        </div>
        <span className="rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 font-mono text-[11px] uppercase tracking-[0.22em] text-emerald-600">
          Running
        </span>
      </div>

      <div className="space-y-3 font-mono text-sm">
        {STEPS.map((step, i) => {
          const isDone = i < currentIndex || currentStep === "done";
          const isActive = i === currentIndex && currentStep !== "done";
          return (
            <div key={step.key} className="lift-card flex items-center gap-3 rounded-[20px] border border-slate-200 bg-slate-50/80 px-4 py-3">
              <span className="text-slate-400">{String(i + 1).padStart(2, "0")}</span>
              {isDone ? (
                <CheckCircle2 className="h-5 w-5 flex-shrink-0 text-emerald-500" />
              ) : isActive ? (
                <Loader2 className="h-5 w-5 animate-spin flex-shrink-0 text-sky-500" />
              ) : (
                <div className="h-5 w-5 flex-shrink-0 rounded-full border border-slate-300" />
              )}
              <span
                className={`${
                  isDone ? "text-slate-500" : isActive ? "text-slate-900" : "text-slate-400"
                }`}
              >
                {isDone ? "[done]" : isActive ? "[live]" : "[queued]"} {step.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
