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
        isUser ? "ml-auto max-w-3xl" : "mr-auto w-full max-w-5xl"
      }`}
    >
      <div
        className={
          isUser
            ? "rounded-[1.4rem] bg-brass px-5 py-4 text-ink"
            : "rounded-[1.4rem] border border-white/10 bg-white/[0.055] p-5 text-stone-100 backdrop-blur"
        }
      >
        <div className="flex items-start justify-between gap-4">
          <p className="leading-7">{message.content}</p>
          <time className="shrink-0 text-xs opacity-50">
            {message.timestamp.toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </time>
        </div>

        {!isUser && response ? (
          <div className="mt-4 flex flex-wrap items-center gap-2">
            <InsightBadge intent={response.intent} />
            <Pill>{response.execution_time_ms} ms</Pill>
            {response.cached ? <Pill>Cached</Pill> : null}
            {response.data_sources.length ? <Pill>{response.data_sources.join(", ")}</Pill> : null}
          </div>
        ) : null}

        {response?.clarification_question ? (
          <div className="mt-4 rounded-2xl border border-amber-300/20 bg-amber-300/10 p-4 text-sm text-amber-100">
            {response.clarification_question}
          </div>
        ) : null}

        {response?.metric_definitions.length ? (
          <div className="mt-4 flex flex-wrap gap-2">
            {response.metric_definitions.map((metric) => (
              <span
                className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-xs text-stone-200"
                key={metric.key}
                title={metric.formula ?? metric.definition}
              >
                {metric.label}
              </span>
            ))}
          </div>
        ) : null}

        {response?.assumptions.length ? (
          <div className="mt-4 rounded-2xl border border-white/10 bg-black/15 p-4">
            <p className="text-xs uppercase tracking-[0.18em] text-stone-400">Assumptions</p>
            <ul className="mt-2 space-y-2 text-sm text-stone-300">
              {response.assumptions.map((assumption) => (
                <li key={assumption}>{assumption}</li>
              ))}
            </ul>
          </div>
        ) : null}

        {response?.comparison ? <ComparisonView comparison={response.comparison} /> : null}

        {response?.suggested_queries?.length ? (
          <div className="mt-4 flex flex-wrap gap-2">
            {response.suggested_queries.map((query) => (
              <span
                className="rounded-full border border-white/10 px-3 py-1 text-xs text-stone-300"
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
    <span className="rounded-full border border-white/10 px-3 py-1 text-[11px] uppercase tracking-[0.16em] text-stone-300">
      {children}
    </span>
  )
}
