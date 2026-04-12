import type { QueryIntent } from "@/lib/types"

const LABELS: Record<QueryIntent, string> = {
  change: "Change",
  compare: "Compare",
  breakdown: "Breakdown",
  summarize: "Summary",
  general: "Answer",
  clarify: "Clarify",
}

export function InsightBadge({ intent }: { intent: QueryIntent }) {
  return (
    <span className="rounded-full border border-brass/35 bg-brass/10 px-3 py-1 text-[11px] uppercase tracking-[0.18em] text-brass">
      {LABELS[intent]}
    </span>
  )
}
