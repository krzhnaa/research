import { Save } from "lucide-react";
import { useState } from "react";
import { useToast } from "../components/ToastProvider";

export default function Settings() {
  const [botToken, setBotToken] = useState(localStorage.getItem("discord_bot_token") || "");
  const [channelId, setChannelId] = useState(localStorage.getItem("discord_channel_id") || "");
  const { showToast } = useToast();

  function handleSave() {
    localStorage.setItem("discord_bot_token", botToken);
    localStorage.setItem("discord_channel_id", channelId);
    showToast({
      variant: "success",
      title: "Configuration saved",
      description: "Discord bot token and channel ID were stored locally for future sends.",
    });
  }

  return (
    <div className="px-4 py-6 md:px-10 md:py-10">
      <div className="mx-auto max-w-4xl">
        <div className="panel-raised float-in p-6 md:p-8">
          <p className="field-label">Integrations</p>
          <h2 className="mt-3 text-3xl font-semibold tracking-tight text-slate-900">Discord Delivery</h2>
          <p className="mt-2 max-w-2xl text-sm leading-7 text-slate-600">
            Configure your Discord bot to automatically receive generated reports.
          </p>

          <div className="mt-8 grid gap-5 md:grid-cols-2">
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-900">Discord Bot Token</label>
              <input
                type="password"
                value={botToken}
                onChange={(e) => setBotToken(e.target.value)}
                placeholder="Paste your bot token"
                className="text-input"
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-900">Discord Channel ID</label>
              <input
                type="text"
                value={channelId}
                onChange={(e) => setChannelId(e.target.value)}
                placeholder="Paste your channel ID"
                className="text-input font-mono"
              />
            </div>
          </div>

          <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center">
            <button
              onClick={handleSave}
              className="inline-flex items-center justify-center gap-2 rounded-2xl bg-sky-500 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-sky-100 transition hover:-translate-y-0.5 hover:bg-sky-600"
            >
              <Save className="h-4 w-4" />
              Save Configuration
            </button>
            <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-500">
              Stored locally in your browser for quick reuse.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
