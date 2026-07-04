import { Download, Globe, MapPin, Phone, Send } from "lucide-react";
import { useState } from "react";
import { ResearchResult, downloadPdf, sendToDiscord } from "../api/client";
import { useToast } from "./ToastProvider";

export default function ReportCard({ result }: { result: ResearchResult }) {
  const [downloading, setDownloading] = useState(false);
  const [showDiscordForm, setShowDiscordForm] = useState(false);
  const [applicantName, setApplicantName] = useState("");
  const [applicantEmail, setApplicantEmail] = useState("");
  const [sending, setSending] = useState(false);
  const [sentStatus, setSentStatus] = useState<"idle" | "success" | "error">("idle");
  const { showToast } = useToast();

  const { company, competitors } = result;

  async function handleDownload() {
    setDownloading(true);
    try {
      const blob = await downloadPdf(result);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${company.company_name.replace(/\s+/g, "_")}_report.pdf`;
      a.click();
      window.URL.revokeObjectURL(url);
      showToast({
        variant: "success",
        title: "PDF ready",
        description: `Downloaded ${company.company_name} research report.`,
      });
    } catch {
      showToast({
        variant: "error",
        title: "PDF generation failed",
        description: "Please try downloading the report again.",
      });
    } finally {
      setDownloading(false);
    }
  }

  async function handleDiscordSend() {
    const botToken = localStorage.getItem("discord_bot_token") || "";
    const channelId = localStorage.getItem("discord_channel_id") || "";

    if (!botToken || !channelId) {
      showToast({
        variant: "info",
        title: "Discord settings required",
        description: "Add your bot token and channel ID in Settings before sending reports.",
      });
      return;
    }

    if (!applicantName || !applicantEmail) {
      showToast({
        variant: "info",
        title: "Applicant details required",
        description: "Enter both your name and email before sending this report.",
      });
      return;
    }

    setSending(true);
    setSentStatus("idle");

    try {
      await sendToDiscord(botToken, channelId, { name: applicantName, email: applicantEmail }, result);
      setSentStatus("success");
      showToast({
        variant: "success",
        title: "Report sent",
        description: `${company.company_name} was delivered to Discord successfully.`,
      });
    } catch {
      setSentStatus("error");
      showToast({
        variant: "error",
        title: "Discord send failed",
        description: "Check your saved Discord configuration and try again.",
      });
    } finally {
      setSending(false);
    }
  }

  const facts = [
    { label: "Website", value: company.website, href: company.website, icon: Globe },
    { label: "Phone", value: company.phone, icon: Phone },
    { label: "Industry", value: company.industry },
    { label: "Address", value: company.address, icon: MapPin },
  ].filter((fact) => fact.value);

  return (
    <div className="panel-raised float-in max-w-5xl p-6 md:p-8">
      <div className="mb-6 flex items-start justify-between gap-4">
        <div>
          <p className="field-label">Company Report</p>
          <h3 className="mt-2 text-3xl font-semibold tracking-tight text-slate-900">{company.company_name}</h3>
          {company.industry && (
            <span className="mt-3 inline-flex rounded-full border border-sky-200 bg-sky-50 px-3 py-1 text-xs font-medium text-sky-700">
              {company.industry}
            </span>
          )}
        </div>
      </div>

      <div className="mb-6 grid gap-3 md:grid-cols-2">
        {facts.map((fact) => {
          const Icon = fact.icon;
          return (
            <div key={fact.label} className="lift-card rounded-[22px] border border-slate-200 bg-white/85 px-4 py-4">
              <div className="flex items-center gap-3">
                {Icon ? <Icon className="h-4 w-4 text-sky-500" /> : <div className="h-4 w-4" />}
                <span className="font-mono text-[11px] uppercase tracking-[0.22em] text-slate-500">{fact.label}</span>
              </div>
              {fact.href ? (
                <a
                  href={fact.href}
                  target="_blank"
                  rel="noreferrer"
                  className="mt-2 block break-all font-mono text-sm text-slate-900 transition hover:text-sky-600"
                >
                  {fact.value}
                </a>
              ) : (
                <p className="mt-2 font-mono text-sm text-slate-900">{fact.value}</p>
              )}
            </div>
          );
        })}
      </div>

      <div className="mb-6 rounded-[24px] border border-slate-200 bg-white/85 p-5">
        <p className="field-label">Summary</p>
        <p className="mt-3 text-sm leading-7 text-slate-600">{company.summary}</p>
      </div>

      <div className="mb-6 rounded-[24px] border border-slate-200 bg-white/85 p-5">
        <h4 className="text-sm font-semibold text-slate-900">Products & Services</h4>
        <div className="flex flex-wrap gap-1.5">
          {company.products_services.map((product, index) => (
            <span key={index} className="mt-3 rounded-full border border-sky-100 bg-sky-50 px-3 py-1.5 text-xs font-medium text-sky-700">
              {product}
            </span>
          ))}
        </div>
      </div>

      <div className="mb-6 rounded-[24px] border border-slate-200 bg-white/85 p-5">
        <h4 className="text-sm font-semibold text-slate-900">AI-Identified Pain Points</h4>
        <ul className="space-y-1">
          {company.pain_points.map((painPoint, index) => (
            <li key={index} className="mt-3 flex gap-3 text-sm text-slate-600">
              <span className="text-sky-500">&bull;</span>
              <span className="leading-7">{painPoint}</span>
            </li>
          ))}
        </ul>
      </div>

      {competitors.length > 0 && (
        <div className="mb-6 rounded-[24px] border border-slate-200 bg-white/85 p-5">
          <h4 className="text-sm font-semibold text-slate-900">Competitors</h4>
          <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2">
            {competitors.map((competitor, index) => (
              <a
                key={index}
                href={competitor.website}
                target="_blank"
                rel="noreferrer"
                className="lift-card rounded-[22px] border border-slate-200 bg-slate-50 px-4 py-3 text-sm transition hover:text-sky-600"
              >
                <div className="font-medium text-slate-900">{competitor.name}</div>
                <div className="mt-1 truncate font-mono text-xs text-slate-500">{competitor.website}</div>
              </a>
            ))}
          </div>
        </div>
      )}

      <div className="border-t border-slate-200 pt-5">
        <div className="flex flex-col gap-3 sm:flex-row">
          <button
            onClick={handleDownload}
            disabled={downloading}
            className="inline-flex items-center justify-center gap-2 rounded-2xl bg-sky-500 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-sky-100 transition hover:-translate-y-0.5 hover:bg-sky-600 disabled:opacity-50"
          >
            <Download className="h-4 w-4" />
            {downloading ? "Generating PDF..." : "Download PDF Report"}
          </button>

          {!showDiscordForm ? (
            <button
              onClick={() => setShowDiscordForm(true)}
              className="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-600 transition hover:border-sky-200 hover:text-slate-900"
            >
              Send to Discord (optional)
            </button>
          ) : (
            <div className="grid flex-1 gap-3 pt-2">
              <input
                type="text"
                placeholder="Your Name"
                value={applicantName}
                onChange={(e) => setApplicantName(e.target.value)}
                className="text-input"
              />
              <input
                type="email"
                placeholder="Your Email"
                value={applicantEmail}
                onChange={(e) => setApplicantEmail(e.target.value)}
                className="text-input"
              />
              <button
                onClick={handleDiscordSend}
                disabled={sending}
                className="inline-flex w-full items-center justify-center gap-2 rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm font-semibold text-emerald-700 transition hover:bg-emerald-100 disabled:opacity-50"
              >
                <Send className="h-4 w-4" />
                {sending ? "Sending..." : "Send Report"}
              </button>
              {sentStatus === "success" && (
                <p className="text-xs text-emerald-600">Report sent to Discord successfully.</p>
              )}
              {sentStatus === "error" && (
                <p className="text-xs text-rose-600">Failed to send. Check your Discord settings.</p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
