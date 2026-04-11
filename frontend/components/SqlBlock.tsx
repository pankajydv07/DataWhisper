"use client"

import { ChevronDown } from "lucide-react"
import { useState } from "react"

export function SqlBlock({
  sql,
  explanation,
}: {
  sql: string
  explanation: string
}) {
  const [open, setOpen] = useState(false)

  return (
    <section className="mt-4 rounded-2xl border border-white/10 bg-ink/70">
      <button
        className="flex w-full items-center justify-between px-4 py-3 text-left text-sm font-medium text-stone-200"
        onClick={() => setOpen((current) => !current)}
        type="button"
      >
        Generated SQL
        <ChevronDown
          className={`transition ${open ? "rotate-180" : ""}`}
          size={16}
        />
      </button>
      {open ? (
        <pre className="overflow-x-auto border-t border-white/10 px-4 py-3 text-xs leading-6 text-brass">
          {sql}
        </pre>
      ) : null}
      {explanation ? (
        <p className="border-t border-white/10 px-4 py-3 text-sm leading-6 text-stone-300">
          {explanation}
        </p>
      ) : null}
    </section>
  )
}
