"use client"

import { Pencil, Trash2 } from "lucide-react"

import type { ChatSessionSummary } from "@/lib/types"

export function SessionListItem({
  session,
  active,
  onSelect,
  onRename,
  onDelete,
}: {
  session: ChatSessionSummary
  active: boolean
  onSelect: (sessionId: string) => void
  onRename: (session: ChatSessionSummary) => void
  onDelete: (session: ChatSessionSummary) => void
}) {
  return (
    <div
      className={`group flex items-center gap-2 rounded-2xl px-3 py-2 transition ${
        active ? "bg-white/[0.08]" : "hover:bg-white/[0.04]"
      }`}
    >
      <button
        className="min-w-0 flex-1 text-left"
        onClick={() => onSelect(session.session_id)}
        type="button"
      >
        <p className="truncate text-sm text-stone-100">{session.title}</p>
      </button>
      <button
        className="opacity-0 transition group-hover:opacity-100"
        onClick={() => onRename(session)}
        type="button"
      >
        <Pencil className="text-stone-500 hover:text-stone-200" size={14} />
      </button>
      <button
        className="opacity-0 transition group-hover:opacity-100"
        onClick={() => onDelete(session)}
        type="button"
      >
        <Trash2 className="text-stone-500 hover:text-stone-200" size={14} />
      </button>
    </div>
  )
}
