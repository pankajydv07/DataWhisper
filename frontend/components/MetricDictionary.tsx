import type { MetricDefinitionRef } from "@/lib/types"

export function MetricDictionary({
  metrics,
  open,
  onClose,
}: {
  metrics: MetricDefinitionRef[]
  open: boolean
  onClose: () => void
}) {
  return (
    <aside
      className={`fixed right-0 top-0 z-30 h-full w-full max-w-md border-l border-line bg-ink/95 p-6 backdrop-blur-xl transition-transform duration-300 ${
        open ? "translate-x-0" : "translate-x-full"
      }`}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.34em] text-brass">Trust Layer</p>
          <h2 className="mt-2 font-display text-3xl tracking-tight text-paper">Metric Dictionary</h2>
        </div>
        <button
          className="rounded-full border border-line px-3 py-1 text-sm text-paper-muted transition hover:border-brass/40 hover:text-paper"
          onClick={onClose}
          type="button"
        >
          Close
        </button>
      </div>

      <div className="mt-7 space-y-4 overflow-y-auto pb-10">
        {metrics.map((metric) => (
          <article className="border border-line bg-paper/[0.03] p-4" key={metric.key}>
            <div className="flex items-center justify-between gap-4">
              <h3 className="font-medium text-paper">{metric.label}</h3>
              {metric.default_time_grain ? (
                <span className="rounded-full border border-line px-2 py-1 text-[11px] uppercase tracking-[0.16em] text-paper-muted">
                  {metric.default_time_grain}
                </span>
              ) : null}
            </div>
            <p className="mt-2 text-sm leading-6 text-paper-muted">{metric.definition}</p>
            {metric.formula ? (
              <p className="mt-3 bg-black/[0.24] px-3 py-2 font-mono text-xs leading-5 text-paper-muted">
                {metric.formula}
              </p>
            ) : null}
            {metric.source_tables.length ? (
              <p className="mt-3 text-xs uppercase tracking-[0.16em] text-paper-muted/[0.8]">
                Sources: {metric.source_tables.join(", ")}
              </p>
            ) : null}
          </article>
        ))}
      </div>
    </aside>
  )
}
