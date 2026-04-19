"use client"

import { SendHorizontal } from "lucide-react"
import { FormEvent, useState } from "react"

export function ChatInput({
  disabled,
  onSend,
}: {
  disabled?: boolean
  onSend: (question: string) => void
}) {
  const [value, setValue] = useState("")

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const question = value.trim()
    if (!question || disabled) {
      return
    }

    onSend(question)
    setValue("")
  }

  return (
    <form
      className="flex items-center gap-3 rounded-full border border-line bg-paper/[0.055] p-2 shadow-2xl shadow-black/25 transition focus-within:border-brass/50 focus-within:bg-paper/[0.075]"
      onSubmit={handleSubmit}
    >
      <input
        className="min-w-0 flex-1 bg-transparent px-4 py-3 text-sm text-paper outline-none placeholder:text-paper-muted/[0.55]"
        disabled={disabled}
        placeholder="Ask: What was total revenue last month?"
        value={value}
        onChange={(event) => setValue(event.target.value)}
      />
      <button
        className="inline-flex h-11 items-center gap-2 rounded-full bg-brass px-5 text-sm font-semibold text-ink transition hover:bg-brass-soft disabled:cursor-not-allowed disabled:opacity-50"
        disabled={disabled}
        type="submit"
      >
        Send
        <SendHorizontal size={16} />
      </button>
    </form>
  )
}
