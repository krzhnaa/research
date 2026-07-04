import { Menu, Plus, Settings, Sparkles, X } from "lucide-react";
import { useEffect, useState } from "react";
import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";

const links = [
  { to: "/", label: "Research", icon: Sparkles },
  { to: "/settings", label: "Settings", icon: Settings },
];

export default function AppShell() {
  const navigate = useNavigate();
  const location = useLocation();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const pageTitle = location.pathname === "/settings" ? "Settings" : "Research Workspace";

  useEffect(() => {
    setIsSidebarOpen(false);
  }, [location.pathname]);

  function startNewResearch() {
    window.dispatchEvent(new CustomEvent("new-research"));
    navigate("/");
    setIsSidebarOpen(false);
  }

  return (
    <div className="page-shell min-h-screen text-slate-900">
      <aside className="fixed inset-y-0 left-0 z-40 hidden w-72 border-r border-slate-200/70 bg-white/75 backdrop-blur-xl md:flex md:flex-col">
        <div className="flex h-full flex-col px-6 py-7">
          <div className="flex items-center gap-3 border-b border-slate-200 pb-6">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-sky-500 to-cyan-400 text-white shadow-lg shadow-sky-200">
              <Sparkles className="h-5 w-5" />
            </div>
            <div>
              <p className="text-base font-semibold text-slate-900">Company Research AI</p>
              <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-slate-500">Analyst Desk</p>
            </div>
          </div>

          <button
            type="button"
            onClick={startNewResearch}
            className="mt-6 inline-flex items-center justify-center gap-2 rounded-2xl bg-sky-500 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-sky-200 transition hover:-translate-y-0.5 hover:bg-sky-600"
          >
            <Plus className="h-4 w-4" />
            New Research
          </button>

          <nav className="mt-6 space-y-2">
            {links.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-2xl border px-4 py-3 text-sm font-medium transition ${
                    isActive
                      ? "border-sky-200 bg-sky-50 text-sky-700 shadow-sm"
                      : "border-transparent text-slate-600 hover:border-slate-200 hover:bg-white hover:text-slate-900"
                  }`
                }
              >
                <Icon className="h-4 w-4" />
                {label}
              </NavLink>
            ))}
          </nav>

          <div className="panel mt-8 p-5">
            <p className="field-label">Workspace</p>
            <p className="mt-3 text-sm leading-6 text-slate-600">
              Generate research briefs, scan crawl activity, and package competitor intelligence into export-ready reports.
            </p>
          </div>

          <div className="mt-auto rounded-[24px] border border-slate-200 bg-gradient-to-br from-slate-900 to-slate-800 p-5 text-white shadow-xl shadow-slate-200">
            <p className="field-label">Mode</p>
            <p className="mt-2 text-sm font-semibold text-white">{pageTitle}</p>
            <p className="mt-2 text-sm text-slate-300">Persistent navigation stays pinned while the workspace scrolls.</p>
          </div>
        </div>
      </aside>

      {isSidebarOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          <button
            type="button"
            className="absolute inset-0 bg-slate-900/25 backdrop-blur-sm"
            onClick={() => setIsSidebarOpen(false)}
            aria-label="Close navigation"
          />
          <aside className="relative h-full w-72 border-r border-slate-200 bg-white px-6 py-7 shadow-2xl">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-sky-500 to-cyan-400 text-white">
                  <Sparkles className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-slate-900">Company Research AI</p>
                  <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-slate-500">Analyst Desk</p>
                </div>
              </div>
              <button
                type="button"
                className="rounded-xl border border-slate-200 p-2 text-slate-500"
                onClick={() => setIsSidebarOpen(false)}
                aria-label="Close navigation"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <button
              type="button"
              onClick={startNewResearch}
              className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-sky-500 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-sky-200 transition hover:bg-sky-600"
            >
              <Plus className="h-4 w-4" />
              New Research
            </button>

            <nav className="mt-6 space-y-2">
              {links.map(({ to, label, icon: Icon }) => (
                <NavLink
                  key={to}
                  to={to}
                  className={({ isActive }) =>
                    `flex items-center gap-3 rounded-2xl border px-4 py-3 text-sm font-medium transition ${
                      isActive
                        ? "border-sky-200 bg-sky-50 text-sky-700"
                        : "border-transparent text-slate-600 hover:border-slate-200 hover:bg-slate-50 hover:text-slate-900"
                    }`
                  }
                >
                  <Icon className="h-4 w-4" />
                  {label}
                </NavLink>
              ))}
            </nav>
          </aside>
        </div>
      )}

      <div className="md:pl-72">
        <header className="sticky top-0 z-30 flex h-24 items-center justify-between border-b border-slate-200/70 bg-white/70 px-4 backdrop-blur-xl md:px-10">
          <div className="flex items-center gap-3">
            <button
              type="button"
              className="rounded-xl border border-slate-200 bg-white p-2 text-slate-600 md:hidden"
              onClick={() => setIsSidebarOpen(true)}
              aria-label="Open navigation"
            >
              <Menu className="h-4 w-4" />
            </button>
            <div>
              <p className="field-label">Workspace</p>
              <h1 className="mt-1 text-3xl font-semibold tracking-tight text-slate-900">{pageTitle}</h1>
            </div>
          </div>

          <div className="hidden rounded-full border border-sky-100 bg-sky-50 px-4 py-2 text-sm font-medium text-sky-700 md:block">
            Clean, export-ready company reports
          </div>
        </header>

        <main className="min-w-0">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
