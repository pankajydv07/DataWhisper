import type { ChatMessage as ChatMessageType } from "@/lib/types"

import { ResultChart } from "./ResultChart"
import { ResultTable } from "./ResultTable"
import { SqlBlock } from "./SqlBlock"

export function ChatMessage({ message }: { message: ChatMessageType }) {
  const isUser = message.role === "user"

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

        {message.response?.suggested_queries?.length ? (
          <div className="mt-4 flex flex-wrap gap-2">
            {message.response.suggested_queries.map((query) => (
              <span
                className="rounded-full border border-white/10 px-3 py-1 text-xs text-stone-300"
                key={query}
              >
                {query}
              </span>
            ))}
          </div>
        ) : null}

        {message.response?.sql ? (
          <SqlBlock
            explanation={message.response.sql_explanation}
            sql={message.response.sql}
          />
        ) : null}

        {message.response?.table ? (
          <ResultTable table={message.response.table} />
        ) : null}

        {message.response?.chart && message.response.table ? (
          <ResultChart
            chart={message.response.chart}
            table={message.response.table}
          />
        ) : null}
      </div>
    </article>
  )
}
