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
      className={`group flex items-center gap-2 border-l px-3 py-2 transition ${
        active
          ? "border-brass bg-paper/[0.06]"
          : "border-transparent hover:border-line hover:bg-paper/[0.03]"
      }`}
    >
      <button
        className="min-w-0 flex-1 text-left"
        onClick={() => onSelect(session.session_id)}
        type="button"
      >
        <p className="truncate text-sm text-paper">{session.title}</p>
      </button>
      <button
        className="opacity-0 transition group-hover:opacity-100"
        onClick={() => onRename(session)}
        type="button"
      >
        <Pencil className="text-paper-muted/60 hover:text-paper" size={14} />
      </button>
      <button
        className="opacity-0 transition group-hover:opacity-100"
        onClick={() => onDelete(session)}
        type="button"
      >
        <Trash2 className="text-paper-muted/60 hover:text-danger" size={14} />
      </button>
    </div>
  )
}
