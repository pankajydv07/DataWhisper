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
      className="flex items-center gap-3 rounded-3xl border border-white/10 bg-white/[0.06] p-2 shadow-2xl shadow-black/20"
      onSubmit={handleSubmit}
    >
      <input
        className="min-w-0 flex-1 bg-transparent px-4 py-3 text-sm text-stone-50 outline-none placeholder:text-stone-500"
        disabled={disabled}
        placeholder="Ask: What was total revenue last month?"
        value={value}
        onChange={(event) => setValue(event.target.value)}
      />
      <button
        className="inline-flex h-11 items-center gap-2 rounded-2xl bg-brass px-4 text-sm font-semibold text-ink transition hover:bg-[#efc25d] disabled:cursor-not-allowed disabled:opacity-50"
        disabled={disabled}
        type="submit"
      >
        Send
        <SendHorizontal size={16} />
      </button>
    </form>
  )
}
