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
    <section className="animate-rise py-8 md:py-16">
      <p className="text-xs uppercase tracking-[0.36em] text-brass">
        Conversational intelligence
      </p>
      <h2 className="mt-4 max-w-3xl font-display text-5xl leading-none text-stone-100 md:text-7xl">
        Turn plain questions into governed answers.
      </h2>
      <p className="mt-6 max-w-2xl text-lg leading-8 text-stone-300">
        Start with a retail sales question. DataWhisper will generate safe SQL,
        execute it for your signed-in user, and return a summary with evidence.
      </p>
      <div className="mt-8 flex flex-wrap gap-3">
        {STARTERS.map((query) => (
          <button
            className="rounded-full border border-white/10 bg-white/[0.04] px-4 py-2 text-left text-sm text-stone-200 transition hover:border-brass hover:text-brass"
            key={query}
            onClick={() => onSelect(query)}
            type="button"
          >
            {query}
          </button>
        ))}
      </div>
    </section>
  )
}
