const STARTERS = [
  "What was total revenue last month?",
  "Show top 5 customers by order value",
  "Which product category has the highest sales?",
  "Compare revenue by region for 2025",
  "How many orders were cancelled this quarter?",
]

export function SuggestedQueries({
  onSelect,
}: {
  onSelect: (query: string) => void
}) {
  return (
    <section className="animate-rise py-10 md:py-20">
      <p className="text-xs uppercase tracking-[0.38em] text-brass">
        Analyst prompt shelf
      </p>
      <h2 className="mt-5 max-w-4xl font-display text-5xl leading-none tracking-tight text-paper md:text-7xl">
        Start with the question the room is already asking.
      </h2>
      <p className="mt-6 max-w-2xl text-lg leading-8 text-paper-muted">
        Start with a retail sales question. DataWhisper will generate safe SQL,
        execute it for your signed-in user, and return a summary with evidence.
      </p>
      <div className="mt-9 grid gap-3 md:grid-cols-2">
        {STARTERS.map((query) => (
          <button
            className="group border border-line bg-paper/[0.025] px-5 py-4 text-left text-sm text-paper transition hover:border-brass/50 hover:bg-paper/[0.055]"
            key={query}
            onClick={() => onSelect(query)}
            type="button"
          >
            <span className="block text-[11px] uppercase tracking-[0.24em] text-brass transition group-hover:text-brass-soft">
              Query
            </span>
            <span className="mt-2 block text-base">{query}</span>
          </button>
        ))}
      </div>
    </section>
  )
}
