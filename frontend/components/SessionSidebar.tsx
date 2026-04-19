"use client"

import { Plus } from "lucide-react"

import { SessionList } from "./SessionList"

import type { ChatSessionSummary } from "@/lib/types"

export function SessionSidebar({
  sessions,
  activeSessionId,
  onNewChat,
  onSelect,
  onRename,
  onDelete,
}: {
  sessions: ChatSessionSummary[]
  activeSessionId: string | null
  onNewChat: () => void
  onSelect: (sessionId: string) => void
  onRename: (session: ChatSessionSummary) => void
  onDelete: (session: ChatSessionSummary) => void
}) {
  return (
    <aside className="flex h-full flex-col border-r border-line bg-black/[0.16] px-3 py-4 backdrop-blur-xl">
      <button
        className="mb-5 flex items-center justify-center gap-2 rounded-full border border-line bg-paper/[0.035] px-4 py-3 text-sm font-medium text-paper transition hover:border-brass/40 hover:bg-paper/[0.07]"
        onClick={onNewChat}
        type="button"
      >
        <Plus size={16} />
        New Chat
      </button>

      <div className="mb-5 px-3">
        <p className="font-display text-2xl tracking-tight text-paper">DataWhisper</p>
        <p className="mt-2 text-xs uppercase leading-5 tracking-[0.22em] text-brass">
          Retail analytics desk
        </p>
        <p className="mt-3 text-sm leading-6 text-paper-muted">
          Persistent conversations grouped by recency.
        </p>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto pr-1">
        <SessionList
          activeSessionId={activeSessionId}
          onDelete={onDelete}
          onRename={onRename}
          onSelect={onSelect}
          sessions={sessions}
        />
      </div>
    </aside>
  )
}
