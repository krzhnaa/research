import { AlertCircle, Bot, User } from "lucide-react";
import { ChatMessage as ChatMessageType } from "../types";
import ProgressSteps from "./ProgressSteps";
import ReportCard from "./ReportCard";

export default function ChatMessage({ message }: { message: ChatMessageType }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}>
      {!isUser && (
        <div className="flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-2xl bg-white shadow-md shadow-slate-200">
          <Bot className="h-4 w-4 text-sky-500" />
        </div>
      )}

      <div className={`max-w-4xl ${isUser ? "order-first" : ""}`}>
        {message.type === "text" && (
          <div
            className={`float-in rounded-[24px] border px-5 py-4 text-sm leading-7 shadow-sm ${
              isUser
                ? "border-sky-200 bg-sky-500 text-white shadow-sky-100"
                : "border-slate-200 bg-white text-slate-700"
            }`}
          >
            {message.content}
          </div>
        )}

        {message.type === "progress" && message.progressStep && (
          <ProgressSteps currentStep={message.progressStep} />
        )}

        {message.type === "report" && message.report && <ReportCard result={message.report} />}

        {message.type === "error" && (
          <div className="float-in flex items-start gap-2 rounded-[24px] border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
            <AlertCircle className="mt-0.5 h-4 w-4 flex-shrink-0" />
            {message.content}
          </div>
        )}
      </div>

      {isUser && (
        <div className="flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-2xl bg-slate-900 text-white shadow-md shadow-slate-200">
          <User className="h-4 w-4" />
        </div>
      )}
    </div>
  );
}
