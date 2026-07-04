export default function ReportSkeleton() {
  return (
    <div className="panel float-in animate-pulse p-5">
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <div className="h-4 w-20 rounded bg-slate-200" />
          <div className="h-7 w-64 rounded bg-slate-200" />
        </div>
        <div className="h-9 w-32 rounded bg-slate-200" />
      </div>

      <div className="mt-5 grid gap-4 lg:grid-cols-[1.4fr_0.9fr]">
        <div className="space-y-4">
          <div className="rounded-panel border border-slate-200 bg-white p-4">
            <div className="mb-3 h-3 w-28 rounded bg-slate-200" />
            <div className="space-y-2">
              <div className="h-3 w-full rounded bg-slate-200" />
              <div className="h-3 w-5/6 rounded bg-slate-200" />
              <div className="h-3 w-4/6 rounded bg-slate-200" />
            </div>
          </div>
          <div className="rounded-panel border border-slate-200 bg-white p-4">
            <div className="mb-3 h-3 w-32 rounded bg-slate-200" />
            <div className="flex flex-wrap gap-2">
              {Array.from({ length: 6 }).map((_, index) => (
                <div key={index} className="h-8 w-28 rounded bg-slate-200" />
              ))}
            </div>
          </div>
        </div>

        <div className="rounded-panel border border-slate-200 bg-white p-4">
          <div className="mb-3 h-3 w-24 rounded bg-slate-200" />
          <div className="space-y-3">
            {Array.from({ length: 5 }).map((_, index) => (
              <div key={index} className="h-14 rounded bg-slate-200" />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
