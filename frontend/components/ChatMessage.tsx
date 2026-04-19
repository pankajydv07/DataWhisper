import type { ReactNode } from "react"
import type { ChatMessage as ChatMessageType } from "@/lib/types"

import { ComparisonView } from "./ComparisonView"
import { InsightBadge } from "./InsightBadge"
import { ResultChart } from "./ResultChart"
import { ResultTable } from "./ResultTable"
import { SqlBlock } from "./SqlBlock"

export function ChatMessage({ message }: { message: ChatMessageType }) {
  const isUser = message.role === "user"
  const response = message.response

  return (
    <article
      className={`animate-rise ${
        isUser ? "ml-auto max-w-3xl" : "mr-auto w-full max-w-6xl"
      }`}
    >
      <div
        className={
          isUser
            ? "rounded-[1.35rem] bg-brass px-5 py-4 text-ink shadow-[0_18px_55px_rgba(216,166,63,0.16)]"
            : "border-y border-line bg-paper/[0.025] px-0 py-6 text-paper backdrop-blur md:px-6"
        }
      >
        <div className="flex items-start justify-between gap-5">
          <p className={`leading-7 ${isUser ? "" : "text-xl md:text-2xl"}`}>
            {message.content}
          </p>
          <time className="shrink-0 text-xs opacity-55">
            {message.timestamp.toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </time>
        </div>

        {!isUser && response ? (
          <div className="mt-5 flex flex-wrap items-center gap-2 border-y border-line py-3">
            <InsightBadge intent={response.intent} />
            <Pill>{response.execution_time_ms} ms</Pill>
            {response.cached ? <Pill>Cached</Pill> : null}
            {response.data_sources.length ? <Pill>{response.data_sources.join(", ")}</Pill> : null}
          </div>
        ) : null}

        {response?.clarification_question ? (
          <div className="mt-5 border-l border-warning bg-warning/10 px-4 py-3 text-sm text-paper">
            {response.clarification_question}
          </div>
        ) : null}

        {response?.metric_definitions.length ? (
          <div className="mt-5 flex flex-wrap gap-2">
            {response.metric_definitions.map((metric) => (
              <span
                className="rounded-full border border-line bg-paper/[0.04] px-3 py-1 text-xs text-paper-muted transition hover:border-brass/40 hover:text-paper"
                key={metric.key}
                title={metric.formula ?? metric.definition}
              >
                {metric.label}
              </span>
            ))}
          </div>
        ) : null}

        {response?.assumptions.length ? (
          <div className="mt-5 border-l border-line bg-black/[0.15] px-4 py-3">
            <p className="text-xs uppercase tracking-[0.22em] text-paper-muted">Assumptions</p>
            <ul className="mt-2 space-y-2 text-sm text-paper-muted">
              {response.assumptions.map((assumption) => (
                <li key={assumption}>{assumption}</li>
              ))}
            </ul>
          </div>
        ) : null}

        {response?.comparison ? <ComparisonView comparison={response.comparison} /> : null}

        {response?.suggested_queries?.length ? (
          <div className="mt-5 flex flex-wrap gap-2">
            {response.suggested_queries.map((query) => (
              <span
                className="rounded-full border border-line px-3 py-1 text-xs text-paper-muted"
                key={query}
              >
                {query}
              </span>
            ))}
          </div>
        ) : null}

        {response?.sql ? (
          <SqlBlock explanation={response.sql_explanation} sql={response.sql} />
        ) : null}

        {response?.table ? <ResultTable table={response.table} /> : null}

        {response?.chart && response.table ? (
          <ResultChart chart={response.chart} table={response.table} />
        ) : null}
      </div>
    </article>
  )
}

function Pill({ children }: { children: ReactNode }) {
  return (
    <span className="rounded-full border border-line px-3 py-1 text-[11px] uppercase tracking-[0.18em] text-paper-muted">
      {children}
    </span>
  )
}
